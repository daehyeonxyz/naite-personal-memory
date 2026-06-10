# /wiki lint

Health-check the wiki. Report, never auto-fix.

Optional flag:

- `/wiki lint --daily` - daily automation profile. Run the same checks, but spend extra reading budget on the findings most likely to change user decisions. Also write a durable report under `exports/daily/YYYY-MM-DD-lint.md`.

Default output is a single markdown report printed to the conversation (not written to a file). In `--daily`, print the report and also write it to `exports/daily/YYYY-MM-DD-lint.md`. If the user wants to act on findings, they direct the fixes in subsequent commands. Lint appends one entry to `wiki/log.md`:

```
## [YYYY-MM-DD] lint | <N> findings
- orphans: N
- stubs: N
- ontology — frontmatter incomplete: N
- ontology — subject tree drift: N
- ontology — topic uncanonicalized: N (P promotion candidates)
- ontology — domain cache stale: N
- ontology — BOM-prefixed: N
- ontology — legacy collection drift: N
- slug collisions: N
- index drift: N
- secrets: N
- binary creep: N
- skill candidates: N
- failure patterns: N
- user model refresh: yes | skipped
- post-ingest residue: N
- stale archive dirs: N
- course archive coherence: N
- output quality guard: N
- synapse coverage issues: N
- high-degree neurons: top-N listed
- autonomy garbage: N (low-use canonical: a, trivial narrower: b, orphan spawn: c)
- context maps: refreshed | stale | missing
- daily report: exports/daily/YYYY-MM-DD-lint.md | n/a
```

## Token budget tiers

Lint already has broad mechanical coverage. Quality comes from spending reading tokens where mechanical counts need judgement, not from adding more checks.

### Tier 1 - deep evidence review

Always spend extra reading budget on these four areas when findings exist:

1. **Missing targets / stubs**: for each meaningful missing target, open at least one source page that links to it. Classify whether it is a historical `log.md` link, a placeholder/template artifact, an intentional plain-text/external reference candidate, a real broken wikilink, or a new concept-page candidate.
2. **Output quality guard**: for each hit, read nearby context before and after the line, not just the matched phrase. Decide whether it is a real source/process-voice problem or a false positive caused by technical usage.
3. **Synapse coverage**: separate standalone `kind=decision` pages from embedded decision-shape prose in concept/entity/source-record/project pages. Apply the decision-page standard most strictly to standalone decision pages.
4. **Autonomy garbage**: verify the 30-day window, usage count, and inbound count before surfacing a cleanup candidate. Do not report a topic, narrower, or spawned concept as garbage from count alone.

### Tier 2 - conditional deep review

Read deeper only when the first pass shows a repeated signal:

1. **Skill candidates**: if the last ~50 log entries show a repeated manual procedure, read enough adjacent entries to identify the actual procedure, not just the repeated op name.
2. **Failure patterns**: if aborted or failure-like entries cluster, read surrounding log entries to identify the root cause and prevention point.

### Count-only signal

`§ 13 High-degree neurons` stays count-only. Do not add qualitative interpretation to that section. Use high-degree counts only as a priority signal for other findings, for example when an output-quality issue affects a major hub.

## Finding classification

Each non-zero finding should carry one of these labels when the distinction affects user action:

- `blocker`: must stop commit or repair flow until the user acts, usually secrets or data safety.
- `false-positive`: matched mechanically but is not a wiki defect after context review.
- `intentional-debt`: known or deliberate residue, such as historical `log.md` links preserved for audit value.
- `repair-candidate`: a concrete page, link, source-voice, or workflow issue that can be fixed in a later user-directed pass.
- `schema-pressure`: repeated evidence that may justify ontology, workflow, or lint-rule evolution, subject to the schema evolution rules.

For `--daily`, the report should end with **우선 검토 후보 3개**. These are not automatic fixes. They are the three most useful items for a human or later `/wiki curate --daily` review.

## Checks

Run all of these in one pass. Don't short-circuit on failures; gather everything.

### 0. Context maps

Read `CONTEXT.md`. Then refresh and read the generated operating maps:

```powershell
python scripts/build-wiki-manifest.py
python scripts/build-wiki-dependencies.py
```

Use `ontology/wiki-manifest.json` for page coordinates and `ontology/wiki-dependencies.json` for inbound/outbound link data. The maps are tracked generated files, not hand-edited canonical vocabularies.

Report the generated map status in the lint report:

- `manifest pages: N`
- `dependency edges: N`
- `dependency missing targets: N`
- `dependency orphans: N`

For `--daily`, include a short delta note:

- `git log --since <last-run>` if the automation supplies a last-run timestamp.
- whether generated-map diffs are timestamp-only or graph-count changes.
- whether the hard blocker counts changed since the prior daily memory/report when available.

### 1. Orphans

Pages in `wiki/` (excluding `index.md`, `log.md`, `_stubs.md`) with **zero inbound wikilinks** from other pages in `wiki/`.

Use `ontology/wiki-dependencies.json` as the primary source. If the map is unavailable, fall back to Grep across `wiki/*.md` for `\[\[<slug>` and `\[\[<slug>\|`. If no match exists outside the page itself (and outside `index.md`/`log.md`/`_stubs.md`), it's an orphan.

Report: list orphan slugs and their domains. Suggest which might be candidates for linking or deletion. Note: course meta pages (`course-{slug}-00-index.md`) are typically only linked from `index.md § Courses` — these are not orphans even with low inbound from content pages.

### 2. Stubs

- Read `wiki/_stubs.md`. List entries still unresolved.
- Scan all pages for concept mentions. If a noun phrase appears as **bold**, as a wikilink target that doesn't exist, or in plain text **≥3 times across ≥2 pages** without a corresponding `wiki/<slug>.md`, propose it as a new stub.

For missing targets from `ontology/wiki-dependencies.json`, apply Tier 1 review before proposing stubs. Do not promote `log.md` historical entries, placeholders, or intentionally uncreated external organization names into stubs without page evidence.

Report: unresolved stubs + newly proposed stubs.

### 3. Ontology validation

매 페이지의 frontmatter 5 facet (`kind`, `form`, `topics`, `subject`, `source-types`) + cached `domains` + dates 를 ontology spec (`CONVENTIONS.md § Ontology`, `ontology/subject-tree.md`, `ontology/topics.md`) 에 비교한다. 자세한 capability spec: `ARCHITECTURE.md § 4.2 / § 6.2`.

**Schema rule**:
- 유효 schema: `kind` / `form` / `source-types`.
- legacy schema (`type` / `role` / `source-type` singular) 는 **error**. legacy 가 surface 되면 = drift signal, 해당 페이지를 새 schema 로 수동 전환.
- **mixed schema** (한 페이지 안에 kind+role 또는 type+form 혼재) = drift, error. 수동 fix 필요.
- 새 페이지 작성 시 항상 새 schema 만 사용.

**Helper**: `scripts/lint-ontology.py` 는 deterministic Python validator 로 3a~3j 의 기계 검사와 § 7 non-wiki dirt 검사를 수행. Cluster detection (Louvain) 과 topic alias clustering 같은 무거운 작업은 LLM-driven 으로 별도.

```
python scripts/lint-ontology.py                # report only
python scripts/lint-ontology.py --strip-bom    # also normalize BOM in-place
python scripts/lint-ontology.py --refresh-domains   # domains cache 갱신 안내
```

#### 3a. Frontmatter completeness

모든 content page (`index.md` / `log.md` / `_stubs.md` 제외) 가 다음 필수 facet 보유 + valid enum:

- `kind`: enum `concept | entity | source-record | project | decision | insight | comparison`
- `form`: enum `prose | index`
- `topics`: list (페이지당 0-5 entries, 빈 배열 OK)
- `subject`: list (1+ SKOS-lite path)
- `source-types`: list of enum values `course | conversation | paper | article | docs | book | essay | external` (single-element list OK, 항상 list)
- `domains`: list (cached, lint 가 derive)
- `created`, `updated`: `YYYY-MM-DD`

미보유 / 잘못된 enum / 빈 subject 발견 시 surface (incomplete).

**Legacy schema 는 error**. 다음이 발견되면 incomplete 로 surface 하고 새 schema 로 수동 전환한다:
- `type` / `role` / `source-type` (singular) 가 있고 `kind` 가 없음 → legacy schema (incomplete)
- `kind` 와 `role` 또는 `type` 과 `form` 둘 다 있음 → mixed schema (incomplete, drift signal)

`scripts/lint-ontology.py` 가 `detect_schema()` helper 로 자동 감지.

#### 3b. Subject tree validation

각 페이지의 `subject` field 의 모든 path 가 `ontology/subject-tree.md` 의 canonical tree 에 존재해야 함:
- Top-level 이 `subjects:` 의 key 거나 어느 도메인의 `altLabels` 안에 있음.
- Path 가 narrower (`parent/narrower`) 면 `narrower` 가 그 parent 의 `narrower:` 리스트에 있음.

미등록 path → drift. AltLabel 통해 resolve 가능하면 alias hit 으로 분류 (canonical 로 점진 갱신 권장 — 강제 X).

**Promotion candidate**: 어느 narrower 후보가 ≥ 5 페이지에 등장하는데 canonical 에 없으면 surface (사용자 결정 후 `ontology/subject-tree.md` 에 추가). Cluster detection (Louvain modularity on wikilink graph) 결과와 cross-reference.

#### 3c. Topic canonical validation

각 페이지의 `topics` 의 모든 entry 가 `ontology/topics.md` 의 `canonical_topics` 에 있거나 `aliases` map 의 key 여야 함:
- 미등록 topic → **warn (block 아님)** — folksonomy 철학 (CONVENTIONS.md § Ontology).
- ≥ 3 페이지 등장 → promotion candidate (사용자 confirm 후 canonical 추가).
- Levenshtein ≤ 2 인 페어 (topic 끼리 또는 topic vs canonical) → alias 후보 surface.
- Topic 이 broad domain 명 (`ml`, `statistics` 등) 이거나 페이지-specific (`course-ma101-ch03-binomial`) 이면 misuse 로 surface — `topics` 는 reusable concept-level.

#### 3d. Domain cache freshness

각 페이지의 `domains` cache 가 `subject` 로부터 정확히 derive 됐는지:
- 기대값: `domains == derive_domains(subject)` — first-occurrence order, dedupe.
- 불일치 → cache 갱신 필요. `python scripts/lint-ontology.py --refresh-domains` 안내를 따라 갱신.

#### 3e. Kind / form / source-types distribution

매 lint 가 enum 별 count 표 surface — 새 enum 도입 압력 감지:

- `kind` distribution: `concept` / `entity` / `source-record` / `project` / `decision` / `insight` / `comparison` 별 count.
- `form` distribution: `prose` / `index` 별 count.
- `source-types` distribution: `course` / `conversation` / `paper` / `article` / `docs` / `book` / `essay` / `external` 별 count (한 페이지가 multi-value 가질 수 있어 합계 ≠ 페이지 수).

**Promotion candidate**: 본문 분석에서 자주 등장하는 page-shape pattern 이 기존 enum 에 안 맞으면 surface (예: tutorial-shape, literature-review-shape, video-source 등). 누적 ≥ 5 페이지면 사용자 결정 후 `CONVENTIONS.md § Ontology` enum 에 추가.

#### 3i. Schema integrity (drift detector)

alias phase 가 종료됐고 wiki 가 모두 새 schema. 다음 metric 은 0 이어야 정상:
- `legacy_schema_count`: type/role/source-type (singular) 만 있는 페이지. > 0 이면 신규 페이지가 옛 schema 로 작성됨 → 해당 페이지를 새 schema 로 수동 전환.
- `mixed_schema_count`: kind+role 또는 type+form 혼재. > 0 이면 manual fix.
- `unknown_count`: 어느 schema field 도 없음. > 0 이면 frontmatter parse 오류 또는 incomplete page.

#### 3j. Output quality contract guard

`CONVENTIONS.md § Output quality contract` 의 deterministic subset 을 surface. 품질 평가가 아니라 body hygiene guard 다. False positive 는 가능하지만, 새 producer output 과 touched course pages 에서는 발견 즉시 고친다.

Scan target:

- 모든 `wiki/course-*.md` 의 body before trailing `## Source`
- 최근 변경된 일반 wiki pages when a workflow just wrote them

Flag:

- raw/source path leakage before `## Source`: `raw/`, `` `raw` ``, `Staging`, `Source Staging`, `Archived source bundle`
- source/process voice: `PDF page`, `raw PDF`, `source PDF`, `source page`, `lecture notes`, `page range`, `render`, `image-read`, `backfill`, `run-log`, `extraction`
- Korean source voice: `필기에는`, `필기에서`, `강의 노트`, `노트에서는`, `원문에서는`, `원자료`, `자료에서는`, `페이지에서는`, `이 페이지에서는`, `이 자료`
- mojibake markers: `???`, `�`, `Ã`, `Â`
- generic English course headings: `Status`, `Scope`, `Chapters`, `Projects`, `Connections`, `Also known as`, `Overview`, `Related`, `Sequence Logic`, `Practice & Assignments`, `Course Bridges`, `Concept Extraction`, `Source Staging`, `Names`, `Maps to`

Do not flag:

- paths inside the trailing `## Source` block
- formulas, code fences, commands, model names, method names, technical English terms, or course-native English titles
- the word `source` when it is a technical concept (for example source node, source distribution, source coding) rather than provenance/process voice

Report file, line, matched phrase, and whether it is before `## Source`. For touched producer output, treat as must-fix-before-completion. For full lint, report as findings and let the user decide the repair scope.

For `--daily`, include classification for each distinct output-quality cluster: `false-positive`, `intentional-debt`, or `repair-candidate`.

#### 3f. BOM detection

UTF-8 BOM (`EF BB BF`) prefix 검출:
- `wiki/*.md` 어떤 페이지든 BOM 가지면 surface.
- `python scripts/lint-ontology.py --strip-bom` 으로 in-place normalize.
- 정상 운영 상태에선 0 이어야 함 (migration 시 strip 됨).

#### 3g. Course / collection / source 명을 frontmatter 에 사용 (legacy drift)

`course`, `course-{slug}`, `anthropic-academy`, `ode`, `laplace-transform` 같은 컬렉션·entity·하위주제 명을 `domains` 또는 `subject` 에 박은 케이스 — 항상 0 이어야 함. 발견 시 즉시 surface.

#### 3h. Language-shape review candidates

`CONVENTIONS.md § Naming` 의 *Korean prose + English headings/terms* 정책 drift **후보** 를 surface. 품질 평가 아님 — 정책 compliance 의 후보 검토 단계. 비율·grade·threshold·점수 없음.

Surface 룰 (단순 presence, false positive expected):

- prose context 줄 (heading 아니고 code-block / math-block 밖, 알파벳·한글이 있는 줄) 에 Hangul 부재 → candidate
- heading context 줄 (`^#+ ` 시작) 에 Latin letters 부재 → candidate

수식 라인, 영어 인용 라인, 영어 정의 라인, 외국어 hub entity 등은 false positive 일 수 있다. 사람이 직접 검토 후 *정책 위반인 경우만* 수정한다. lint 자체는 line 위치만 surface 한다.

blocker 아님 (secrets 만 blocker). report 는 candidate line 의 위치만 출력.

#### 3 종합 Report format

```
## Ontology validation
| Sub-check | Count | Action |
|---|---|---|
| 3a frontmatter incomplete | N | fix per page |
| 3b subject tree drift | N | resolve via altLabel or migrate |
| 3c topic uncanonicalized | N | surface promotion / alias candidates |
| 3d domain cache stale | N | run --refresh-domains |
| 3e kind/form/source-types distribution | (table) | surface enum-add candidates |
| 3f BOM-prefixed files | N | --strip-bom |
| 3g legacy collection/entity drift | N | manual migration |
| 3h language-shape review candidates | N lines | manual review (false positive expected) |
| 3i schema integrity (drift detector) | legacy N / mixed M | both must be 0; if > 0 fix pages to the new schema |
| 3j output quality contract guard | N lines | fix source/process voice and raw leakage |
```

3i 의 legacy/mixed count = 0 이 정상 상태. > 0 이면 새 페이지가 옛 schema 로 작성됐다는 drift signal.

### 4. Slug collisions

- **Case-insensitive**: `Attention.md` vs `attention.md` — but the project convention is lowercase-kebab-case, so any file not already matching that convention is a violation too.
- **Near-duplicate**: pairs of slugs with Levenshtein distance ≤ 2 (e.g. `attention.md` vs `attentions.md`) or where one is a strict suffix/prefix of another (`attention.md` vs `attention-mechanism.md`). Course chapter/subchapter pages with identical short titles across different chapters (e.g. `course-ma101-ch02-01-basic-concepts` ↔ `course-ma101-ch03-01-basic-concepts`) are intentional convention and not flagged.

Report: flagged pairs. Do not auto-merge — ask user which is canonical.

### 5. Index drift

`index.md` 는 **curated landing page** 다 — 모든 페이지를 enumerate 하지 않는다 (`CONVENTIONS.md § index.md discipline` 참조). 따라서 lint 의 "missing/ghost" 의미가 바뀌었다.

**Curated coverage 검사:**
- **Domain 노출 임계 (CONVENTIONS.md § index.md discipline 의 *Domain inclusion criteria* 와 동기화)**: subject-tree top-level 중 **kind=concept + kind=entity 페이지 합 ≥ 10 AND 그 중 inbound 최고치 ≥ 10** 을 만족하는 도메인은 `## Knowledge domains` 아래 `### <domain>` 섹션을 가져야 한다.
  - 임계 통과인데 미노출 = **drift** (도메인 섹션 추가 candidate).
  - 임계 미달인데 노출 = **약화 신호** (페이지 삭제·rename 으로 도메인이 얇아진 경우, 사용자에게 유지/제거 결정 요청).
  - 임계 미달은 코스 drill-down 으로만 접근 (예: 단일 코스 하나에만 콘텐츠가 묶인 도메인). 신규 코스 추가로 임계 통과 시 본 surface 가 트리거.
- **Hub 누락**: 각 노출 도메인의 inbound link top 5 페이지 중 `### <domain>` 의 "주요" 라인에 등장하지 않는 페이지가 있으면 후보로 surface (auto-add 금지 — 사용자가 hub 인지 결정).
- **Course 누락**: 모든 `course-{slug}-00-index.md` 는 `## Courses § <institution>` 섹션에 등장해야 한다. 누락 시 어느 institution 섹션에 들어갈지 사용자에게 물음.

**Noise 검사** (이전 schema 잔재):
- **챕터·서브챕터 등록**: `course-{slug}-ch{NN}-*` 페이지가 index.md 에 등장하면 noise — 제거 권장. course meta 페이지의 Chapters 섹션이 진실 단일 소스.
- **`## Domain:` prefix**: index.md 에 `## Domain:` 헤딩이 남아있으면 schema migration 미완료. `## Knowledge domains § <domain>` 또는 `## Courses § <institution>` 으로 교체.
- **`## Domain: course-{slug}` 섹션**: post-2026-04-28 schema 에서 폐기됐다. 발견 시 제거 권장.

**Ghost in index**: every slug referenced in `index.md` must have a corresponding `wiki/<slug>.md`. List ghost entries (단, 페이지 시작부 format example block 의 `[[page-slug]]` placeholder 는 false positive — 첫 코드블록 외 등장만 카운트).

**Summary drift**: hub 페이지의 첫 paragraph 가 `index.md` 의 한 줄 요약과 본질적으로 어긋나면 surface (heuristic: index summary hasn't been updated since `updated:` in frontmatter).

### 6. Secrets scan

Regex-scan everything under `raw/` and `wiki/` for:

- `sk-[A-Za-z0-9]{20,}`
- `ghp_[A-Za-z0-9]{36,}`
- `xoxb-[A-Za-z0-9-]+`
- `AKIA[0-9A-Z]{16}`
- Lines matching `(?i)(password|api[_-]?key|secret|token)[:=]\s*\S{8,}` where the value isn't an obvious placeholder (`xxx`, `<redacted>`, `your-key-here`).
- High-entropy base64-ish strings of length ≥ 40 that aren't obviously URLs or hashes.

If **any** match: this becomes a blocker. Halt any in-flight git operation, report the file + line, and ask the user to redact before proceeding.

### 7. Binary creep + non-wiki dirt

**Binary creep**:
- List files under `raw/assets/` larger than 1 MB. Ask whether to introduce Git LFS (Phase 2 decision) or convert/resize.
- Flag any non-markdown files under `wiki/` (should be zero).
- PDF 가 git tracked 인지 확인 — `*.pdf` 는 `.gitignore` 로 차단돼야 함 (AGENTS.md § Binary files). tracked PDF 발견 시 즉시 surface.

**Non-wiki scratch dirt** (agent / IDE / 패키지 매니저 scratch 가 wiki repo 에 누적되는 패턴):
- 다음이 git tracked 면 surface:
  - `.codex-cache/` — codex CLI cache.
  - `.aider/`, `.cursor/`, `.windsurfai/` — 다른 agent / IDE local state.
  - **`node_modules/` at any depth** — 가장 강한 dirt 신호, 의도적 keep 사례 거의 없음.
  - 프로젝트 root 의 `gpt-*.md`, `claude-*.md` 같은 ad-hoc scratch markdown.
- `.codex-work/` 는 의도적으로 list 에서 *제외*. 사용자가 codex 서브-프로젝트 workspace 로 의도적 사용할 수 있어, 일괄 flag 하면 false positive. `node_modules/` 가 그 안에 들어 있으면 그 경로만 flag 됨.
- 발견 시 권장 조치: 해당 path 를 `.gitignore` 추가 + tracked 항목 `git rm --cached` 후 commit. blocker 아님 (warn).
- `course-backfill.md § Contamination guards § Codex scratch 격리` 와 연계.

### 8. Skill promotion candidates

Read the last ~50 entries of `wiki/log.md`. Group entries by their `op | title` shape and look for **recurring manual procedures** — same sequence of operations executed ≥ 3 times without a dedicated skill file under `.agents/skills/wiki/`.

Heuristics:
- Repeated `ingest` runs that always touch the same kind of source (e.g. YouTube transcripts) with a common pre-step the user keeps redoing.
- Repeated `query` + file-back patterns on a specific topic (suggests a domain-specific query skill).
- User-reported "I keep doing X" in recent captures.

Report: the candidate procedure, how many times it recurred, and a proposed skill file name. Do not write the skill — propose it for the user to greenlight. Follow `AGENTS.md` § Phase co-evolution.

### 9. Failure patterns

Grep `wiki/log.md` for `- aborted:` lines in the last ~50 entries. Cluster by root cause keyword (e.g. "secrets", "extraction", "schema conflict"). If any cluster has ≥ 3 occurrences, surface it as a systemic failure pattern.

Report: cluster, count, entries. Suggest a preventive change (a pre-step, a skill update, or a AGENTS.md rule). Do not auto-fix.

### 10. User model refresh (optional)

Skip unless the wiki has **≥ 10 pages** and **≥ 5 ingest entries** in `log.md`. Also skip if the most recent `lint | user model refresh: yes` entry was < ~3 weeks ago (rough cadence).

When not skipped:

- Walk the last ~20 log entries + the frontmatter of recent pages.
- Summarize for the user:
  - Which domains they've been pulling into the wiki most heavily.
  - Concepts ingested but never cross-referenced (possibly shallow interest).
  - Recurring judgment criteria visible in capture files (e.g. "user consistently prefers X over Y reasoning").
  - Gaps: topics frequently queried but never filed.
- **Offer** to append the summary as a dated block to the project's user-profile memory (the `memory/user_profile.md` Codex maintains for this project). Do **not** overwrite existing content — append only, with a `## [YYYY-MM-DD] refresh` header. Never touch `wiki/` or `raw/` during this check.

If the user declines the memory append, still surface the summary in the lint report.

### 11. Post-ingest residue + stale archive dirs

This wiki has **no generic `_archive/` layer** (per `CONVENTIONS.md § Post-ingest handling`). The only legitimate archive path is `raw/courses/_archive/{slug}/`, populated by `course-finish`. Everything else is drift.

Check two things:

**11a. Stale archive directories** — any `_archive/` under `raw/articles/` or `raw/conversations/` is residue from the old convention or a cowork mistake. Flag as schema drift.

**11b. Uncleaned conversation claim summaries** — for every `YYYY-MM-DD-<slug>.md` under `raw/conversations/` (top level, not under `_transcripts/`), cross-reference `log.md` for an `ingest` entry touching that slug or its derived wiki pages. If ingested but not deleted, flag as "post-ingest residue" — the ingest step 8 cleanup didn't run to completion.

**11c. Course archive coherence** — for each `raw/courses/_archive/{slug}/`, verify a corresponding `course-finish` entry exists in `log.md`. If the archive dir exists but no `course-finish` entry does, or vice versa, flag.

**11d. Stale source paths** — course chapter/subchapter pages 의 `## Source` 섹션이 `raw/courses/{slug}/...` 를 가리키지만 실제 파일이 `raw/courses/_archive/{slug}/...` 에 있으면 stale. course-finish 후 source 경로 일괄 갱신 누락 신호.

Report: list flagged paths + reason. Recommend either removing the stale dir / completing the cleanup, or re-running the op. Do not auto-resolve — user picks. For residue pre-dating the "no generic archive" decision, a one-shot migration clean-up may be warranted; log that as a `migration` candidate.

### 12. Synapse coverage

Health-check for **decision-shape pages** (CONVENTIONS.md § Decision thread shape). A page is detected as decision-shape if the body contains ≥ 2 of:

- Headers `## Decision`, `## Trade-off`, `## Failure mode`, `## Invariant`, `## Rationale`, `## Mechanism`, `## Reusability`
- Prose idioms: `decided ... over`, `failed when`, `trade-off:`, `validates`, `falsifies`

For each detected page, verify:

- **Outbound wikilinks ≥ 3.** Decision pages with too few cross-links are orphaned synapses — they fail at the core purpose (connecting concepts).
- **Failure condition stated explicitly.** A page with Decision + Rationale but no Failure mode is a too-clean DMU — flag for follow-up. Real decisions have known failure conditions.
- **Trade-off prose present.** A `decided X over Y when ...` or equivalent must appear in body. Decision without articulated trade-off = surface rationale.
- **Mechanism articulated.** The body has prose explaining *why* the decision works structurally, not just *what* was done.

Report: per-page list of missing items. Do not auto-fix. Users can re-run `/wiki synapse <slug>` on the page to fill gaps.

For `--daily`, prioritize standalone `kind=decision` pages first. Embedded decision-shape prose is still useful, but it should not crowd out formal decision pages unless it affects a high-value project or hub.

### 13. High-degree neurons (emergent priority)

Compute inbound `[[wikilink]]` counts for every concept page in `wiki/`. Surface:

Use `ontology/wiki-dependencies.json` as the primary source for inbound counts.

- **Top 10 most-referenced** — these are the user's decision-critical neurons, the implicit anchors of their reasoning. No action needed; this is self-knowledge surface. Hub candidates for `index.md § Knowledge domains § <domain>` "주요" 리스트.
- **Bottom distribution** — pages with inbound count 0 (already covered by § 1 Orphans) and 1~2 (weakly connected). Useful for spotting concepts that haven't woven into the synapse layer yet.

Report format: simple ranked list. Inbound count is the only signal — don't editorialize.

This check has no auto-action; it exists to make the link graph's emergent structure visible. Pair it with § 12 to see "what concepts your decisions lean on" and "are those decision pages well-connected?"

### 14. Autonomous addition garbage collector

`CONVENTIONS.md § Schema evolution` 의 autonomy A/B 추가물에 대한 사후 품질 검증. 자율 추가는 일관성 속도를 만드는 대신 *premature 추가* 위험을 안기 — lint 가 30 일 윈도우로 garbage 후보 surface. 모든 항목 warn (not blocker). `git log --diff-filter=A -- ontology/topics.md ontology/subject-tree.md wiki/<slug>.md | head -1` 로 추가 시점 확인.

#### 14a. Canonical topic 저사용 (autonomy A garbage)

`ontology/topics.md § canonical_topics` 의 각 토픽에 대해:
- `git log` 으로 추가 시점 확인 → ≥30 일 전
- `wiki/*.md` 의 `topics:` field 사용 카운트 < 3
→ surface as **"low-usage canonical"** 후보. 사용자 결정: alias 로 redirect, 다른 canonical 로 통합, 또는 keep (도메인이 작아서 정상). LLM 의 입자도 판단 미스 신호일 수 있음.

#### 14b. Autonomously-added narrower 의 trivial split (autonomy B garbage)

`ontology/subject-tree.md` 의 각 `narrower:` entry 에 대해:
- `git log` 으로 추가 시점 확인 → ≥30 일 전
- 그 path 를 `subject:` 로 쓰는 페이지 ≤ 1
→ surface as **"trivial narrower"** 후보. 사용자 결정: 트리에서 제거, 또는 부모 narrower 로 흡수, 또는 keep (의도된 좁은 분류).

#### 14c. Autonomous 일반 개념 페이지의 orphan (autonomy A garbage)

§ 1 Orphans 와 cross-reference. autonomy A 로 spawn 된 일반 개념 페이지 (course skill `subchapter-note § step 5`, ingest skill `§ 5`) 가:
- `git log` 으로 생성 시점 확인 → ≥30 일 전
- inbound `[[wikilink]]` count == 0 (`index.md` / `_stubs.md` / `log.md` 외)
→ surface as **"orphan spawn"** 후보. 입자도 미스 또는 너무 좁은 추출 신호. 사용자 결정: 페이지 삭제, 본문 흡수해서 다른 페이지로 merge, 또는 다른 페이지에서 명시적 cross-link 추가.

**철학**: autonomy A/B 의 *option value* (빠른 schema 진화) 를 보존하면서 누적 카오스를 방지. 자율 추가가 잘못되어도 lint 가 30 일 후 잡고 사용자가 정리. ingest 시점에 "확실하지 않으면 추가하지 마" 보다 "추가하고 lint 가 청소" 가 노드 연결을 치밀하게 유지하는 데 유리하다 — `ARCHITECTURE.md § 2.3` 의 folksonomy 철학과 일치.

## Report format

```markdown
# Lint report — YYYY-MM-DD

## Daily delta
- last run: YYYY-MM-DDTHH:MM:SSZ | unknown | n/a
- commits since last run: N
- map diff: timestamp-only | graph-count changed | not compared
- hard blocker delta: unchanged | changed | not compared

## Context maps
- manifest pages: N
- dependency edges: N
- dependency missing targets: N
- dependency orphans: N

## Orphans (N)
- [[slug-a]] (domain: x) — no inbound links
- ...

## Stubs (N unresolved, M proposed)
- unresolved: [[missing-slug]] — from [[source-page]]
- proposed: [[attention-heads]] — mentioned 4x across [[transformer]], [[multi-head]]

## Domain drift
| domain | count | known? | notes |
|---|---|---|---|
| ai-fluency | 42 | ✓ | ok |
| ml | 15 | ✓ | ok |
| engineering-math | 37 | ✓ | ok |
| course-ma101 | 42 | ✗ | unknown — collection tag, migrate out |
| ...

## Slug collisions (N)
- attention.md ⇔ Attention.md (case violation)
- k-means.md ⇔ kmeans.md (distance 1)

## Index drift
- domain missing: ml has no `### ml` section under `## Knowledge domains`
- hub missing from index: [[generative-ai]] (inbound 6, top-10) but absent from `### ai-fluency` 주요
- chapter noise: [[course-ma101-ch01-00-index]] in index.md — should only be in course-ma101-00-index Chapters
- legacy: `## Domain:` prefix at line 12 — migrate to `## Knowledge domains` / `## Courses`

## Secrets (N) ⚠
- raw/conversations/2026-04-15-foo.md:23 — matched /sk-[A-Za-z0-9]+/
**BLOCKER** — halt commits until resolved.

## Binary creep
- raw/assets/big.png (2.3 MB) — consider resize or LFS
- raw/courses/ma101/ch01-lecture.pdf — git tracked PDF (gitignore violation)

## Post-ingest residue (N)
- raw/conversations/2026-04-24-foo.md — log shows ingest 2026-04-24 but file still present. Cleanup (delete claim summary) never ran.

## Stale archive dirs (N)
- raw/conversations/_archive/ — not a legitimate archive location per CONVENTIONS.md § Post-ingest handling. Recommend removing (files inside may be cleanup residue).

## Course archive coherence (N)
- raw/courses/_archive/aa101/ exists but no `course-finish | course-aa101` entry in log.md. Verify or log retroactively.
- stale source: course-ma101-ch02-* pages reference `raw/courses/ma101/ch02-*.pdf` but file is at `raw/courses/_archive/ma101/ch02-*.pdf`.

## Output quality guard (N)
- wiki/course-ma101-ch02-03-foo.md:42 — `필기에는` before `## Source`; absorb the note insight into prose.
- wiki/course-ma101-ch03-00-index.md:18 — generic English heading `Overview`; use a Korean heading unless course-native.

## Synapse coverage (N issues across M decision pages)
- [[rag-reranker-2026q2-decision]]: missing Failure mode, only 2 outbound wikilinks (need ≥3).
- [[chose-postgres-over-mysql]]: trade-off prose absent (no `decided X over Y when ...`).

## High-degree neurons (top 10)
| rank | page | inbound count |
|---|---|---|
| 1 | [[ai-fluency-framework]] | 24 |
| 2 | [[ai-fluency-description]] | 12 |
| ... | | |

Weakly connected (inbound 1~2): N pages.

## Autonomy garbage (N)
- low-use canonical: `posterior-probability` added 2026-04-01, used by 1 page after 33 days. Recommend: keep | redirect-to-`bayes-theorem` | remove.
- trivial narrower: `ml/agents/orchestrator-pattern` added 2026-04-05, used by 1 subject. Recommend: absorb into `ml/agents` or keep.
- orphan spawn: [[posterior-probability]] created 2026-04-01 (autonomy A), 0 inbound after 33 days. Recommend: cross-link from [[bayes-theorem]] | merge into [[bayes-theorem]] body | delete.

## Skill candidates (N)
- recurring: `ingest` on YouTube transcripts (5x) — propose `.agents/skills/wiki/ingest-transcript.md`

## Failure patterns (N)
- extraction (3x): PDF text extraction aborted on scanned docs → propose OCR pre-step in `study.md`

## User model refresh
- (skipped / summary block)

## 우선 검토 후보 3개
- [repair-candidate] [[page-or-target]] - why this is worth reviewing first.
- [schema-pressure] <topic or workflow> - what repeated evidence suggests.
- [intentional-debt] <artifact> - why it is intentionally left alone.
```

## What this command never does

- Never modifies pages, `index.md`, or `_stubs.md`.
- Never auto-resolves anything.
- Never commits.
- Never skips the secrets check — it runs every time, and any hit is a hard stop.
- Never writes to memory files without explicit user consent.
