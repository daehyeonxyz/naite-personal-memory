# /naite care --check

점검 모드 계약. `care.md` 가 `--check` 또는 "점검만 / 상태 봐줘" 의도를 감지하면 이 파일을 읽고 그대로 따른다. Health-check the tree. Report, never auto-fix.

Optional flag:

- `/naite care --check --daily` - daily automation profile. Run the same checks, but spend extra reading budget on the findings most likely to change user decisions. Also write a durable report under `.naite/reports/daily/YYYY-MM-DD-care-check.md`.

Default output is a single markdown report printed to the conversation (not written to a file). In `--daily`, print the report and also write it to `.naite/reports/daily/YYYY-MM-DD-care-check.md`. If the user wants to act on findings, they direct the fixes in subsequent commands. Care --check appends one entry to `tree/rings.md`:

```
## [YYYY-MM-DD] care-check | <N> findings
- orphans: N
- stubs: N
- ontology — frontmatter incomplete: N
- ontology — subject tree drift: N
- ontology — topic uncanonicalized: N (P promotion candidates)
- ontology — domain cache stale: N
- ontology — BOM-prefixed: N
- ontology — legacy collection drift: N
- slug collisions: N
- trunk drift: N
- secrets: N
- binary creep: N
- skill candidates: N
- failure patterns: N
- user model refresh: yes | skipped
- post-grow residue: N
- stale archive dirs: N
- branch archive coherence: N
- output quality guard: N
- body em dash: N
- study-note quality issues: N (markdown form: a, study effectiveness: b, content composition: c, writing manner: d)
- decision/insight quality issues: N (decision: a, insight: b)
- high-degree neurons: top-N listed
- autonomy garbage: N (low-use canonical: a, trivial narrower: b, orphan spawn: c)
- context maps: refreshed | stale | missing
- daily report: .naite/reports/daily/YYYY-MM-DD-care-check.md | n/a
```

## Token budget tiers

care --check already has broad mechanical coverage. Quality comes from spending reading tokens where mechanical counts need judgement, not from adding more checks.

### Tier 1 - deep evidence review

Always spend extra reading budget on these four areas when findings exist:

1. **Missing targets / stubs**: for each meaningful missing target, open at least one source page that links to it. Classify whether it is a historical `rings.md` link, a placeholder/template artifact, an intentional plain-text/external reference candidate, a real broken wikilink, or a new concept-page candidate.
2. **Output and study-note quality**: for each deterministic hit, read nearby context before and after the line, not just the matched phrase. Then judge Markdown form, study effectiveness, content composition, and writing manner independently. A clean guard result is not evidence that the page teaches well.
3. **Decision and insight quality**: separate standalone `kind=decision` and `kind=insight` pages from embedded reasoning in other kinds. Read enough body context to distinguish absent evidence from a weak template. Unknown or untested state is valid when explicit; guessed completeness is a defect.
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
- `false-positive`: matched mechanically but is not a tree defect after context review.
- `intentional-debt`: known or deliberate residue, such as historical `rings.md` links preserved for audit value.
- `repair-candidate`: a concrete page, link, source-voice, or workflow issue that can be fixed in a later user-directed pass.
- `source-risk`: a fidelity-sensitive page (formulas, definitions, theorems, conditions, numbers) that reads well but must not be rewritten without source review; defer repair (`docs/CONVENTIONS.md § Output quality contract`, source-fidelity ceiling).
- `schema-pressure`: repeated evidence that may justify ontology, workflow, or check-rule evolution, subject to the schema evolution rules.

For `--daily`, the report should end with **우선 검토 후보 3개**. These are not automatic fixes. They are the three most useful items for a human or later `/naite care --daily` review.

## Checks

Run all of these in one pass. Don't short-circuit on failures; gather everything.

### 0. Context maps

Read `docs/CONTEXT.md`. Then refresh and read the generated operating maps:

```powershell
python .naite/scripts/build-tree-manifest.py
python .naite/scripts/build-tree-dependencies.py
```

Use `.naite/ontology/tree-manifest.json` for page coordinates and `.naite/ontology/tree-dependencies.json` for inbound/outbound link data. The maps are tracked generated files, not hand-edited canonical vocabularies.

Report the generated map status in the care-check report:

- `manifest pages: N`
- `dependency edges: N`
- `dependency missing targets: N`
- `dependency orphans: N`

For `--daily`, include a short delta note:

- `git log --since <last-run>` if the automation supplies a last-run timestamp.
- whether generated-map diffs are timestamp-only or graph-count changes.
- whether the hard blocker counts changed since the prior daily memory/report when available.

Also: for `--daily`, the companion `/naite care --daily` triage will read `.naite/reports/daily/YYYY-MM-DD-care-check.md` and write its own `.naite/reports/daily/YYYY-MM-DD-care.md`.

### 1. Orphans

Pages in `tree/` (excluding `trunk.md`, `rings.md`, `seeds.md`) with **zero inbound wikilinks** from other pages in `tree/`.

Use `.naite/ontology/tree-dependencies.json` as the primary source. If the map is unavailable, fall back to Grep across `tree/*.md` for `\[\[<slug>` and `\[\[<slug>\|`. If no match exists outside the page itself (and outside `trunk.md`/`rings.md`/`seeds.md`), it's an orphan.

Report: list orphan slugs and their domains. Suggest which might be candidates for linking or deletion. Note: branch meta pages (`course-{slug}-00-index.md`) are typically only linked from `trunk.md § Branches` — these are not orphans even with low inbound from content pages.

### 2. Stubs

- Read `tree/seeds.md`. List entries still unresolved.
- Scan all pages for concept mentions. If a noun phrase appears as **bold**, as a wikilink target that doesn't exist, or in plain text **≥3 times across ≥2 pages** without a corresponding `tree/<slug>.md`, propose it as a new stub.

For missing targets from `.naite/ontology/tree-dependencies.json`, apply Tier 1 review before proposing stubs. Do not promote `rings.md` historical entries, placeholders, or intentionally uncreated external organization names into stubs without page evidence.

Report: unresolved stubs + newly proposed stubs.

### 3. Ontology validation

매 페이지의 frontmatter 5 facet (`kind`, `form`, `topics`, `subject`, `source-types`) + cached `domains` + dates 를 ontology spec (`docs/CONVENTIONS.md § Ontology`, `.naite/ontology/subject-tree.md`, `.naite/ontology/topics.md`) 에 비교한다. 자세한 capability spec: `docs/ARCHITECTURE.md § 4.2 / § 5.2`.

**Schema rule**:
- 유효 schema: `kind` / `form` / `source-types`.
- legacy schema (`type` / `role` / `source-type` singular) 는 **error**. legacy 가 surface 되면 = drift signal, 해당 페이지를 새 schema 로 수동 전환.
- **mixed schema** (한 페이지 안에 kind+role 또는 type+form 혼재) = drift, error. 수동 fix 필요.
- 새 페이지 작성 시 항상 새 schema 만 사용.

**Helper**: `.naite/scripts/lint-ontology.py` 는 deterministic Python validator 로 3a~3k 의 기계 검사 (3k = form=prose leaf-depth warn) 와 § 7 non-tree dirt 검사를 수행. Cluster detection (Louvain) 과 topic alias clustering 같은 무거운 작업은 LLM-driven 으로 별도.

```
python .naite/scripts/lint-ontology.py                # report only
```

`--strip-bom` 과 `--refresh-domains` 는 파일을 쓰는 수선 플래그이므로 care-check 에서 실행하거나 안내하지 않는다. 발견 건수와 대상만 보고하고, 사용자가 수선을 승인하면 `/naite care` Repair 모드로 넘긴다.

#### 3a. Frontmatter completeness

모든 content page (`trunk.md` / `rings.md` / `seeds.md` 제외) 가 다음 필수 facet 보유 + valid enum:

- `kind`: enum `concept | entity | source-record | project | decision | insight | comparison | essay | personal`
- `form`: enum `prose | index`
- `topics`: list (페이지당 0-5 entries, 빈 배열 OK)
- `subject`: list (1+ SKOS-lite path)
- `source-types`: list of enum values `course | conversation | paper | article | docs | book | essay | external` (single-element list OK, 항상 list)
- `domains`: list (cached, `subject` top-level 에서 기계적으로 도출; care-check 는 stale 여부만 보고)
- `created`, `updated`: `YYYY-MM-DD`

미보유 / 잘못된 enum / 빈 subject 발견 시 surface (incomplete).

**Legacy schema 는 error**. 다음이 발견되면 incomplete 로 surface 하고 새 schema 로 수동 전환한다:
- `type` / `role` / `source-type` (singular) 가 있고 `kind` 가 없음 → legacy schema (incomplete)
- `kind` 와 `role` 또는 `type` 과 `form` 둘 다 있음 → mixed schema (incomplete, drift signal)

`.naite/scripts/lint-ontology.py` 가 `detect_schema()` helper 로 자동 감지.

#### 3b. Subject tree validation

각 페이지의 `subject` field 의 모든 path 가 `.naite/ontology/subject-tree.md` 의 canonical tree 에 존재해야 함:
- Top-level 이 `subjects:` 의 key 거나 어느 도메인의 `altLabels` 안에 있음.
- Path 가 narrower (`parent/narrower`) 면 `narrower` 가 그 parent 의 `narrower:` 리스트에 있음.

미등록 path → drift. AltLabel 통해 resolve 가능하면 alias hit 으로 분류 (canonical 로 점진 갱신 권장 — 강제 X).

**Promotion candidate**: 어느 narrower 후보가 ≥ 5 페이지에 등장하는데 canonical 에 없으면 surface (사용자 결정 후 `.naite/ontology/subject-tree.md` 에 추가). Cluster detection (Louvain modularity on wikilink graph) 결과와 cross-reference.

#### 3c. Topic canonical validation

각 페이지의 `topics` 의 모든 entry 가 `.naite/ontology/topics.md` 의 `canonical_topics` 에 있거나 `aliases` map 의 key 여야 함:
- 미등록 topic → **warn (block 아님)** — folksonomy 철학 (docs/CONVENTIONS.md § Ontology).
- ≥ 3 페이지 등장 → promotion candidate (사용자 confirm 후 canonical 추가).
- Levenshtein ≤ 2 인 페어 (topic 끼리 또는 topic vs canonical) → alias 후보 surface.
- Topic 이 broad domain 명 (`ml`, `statistics` 등) 이거나 페이지-specific (`course-ma101-ch03-binomial`) 이면 misuse 로 surface — `topics` 는 reusable concept-level.

#### 3d. Domain cache freshness

각 페이지의 `domains` cache 가 `subject` 로부터 정확히 derive 됐는지:
- 기대값: `domains == derive_domains(subject)` — first-occurrence order, dedupe.
- 불일치 → cache 갱신이 필요한 repair candidate 로 surface. care-check 에서는 쓰지 않고, 사용자 승인 후 `/naite care` Repair 모드에서 갱신.

#### 3e. Kind / form / source-types distribution

매 care-check 가 enum 별 count 표 surface — 새 enum 도입 압력 감지:

- `kind` distribution: `concept` / `entity` / `source-record` / `project` / `decision` / `insight` / `comparison` / `essay` / `personal` 별 count.
- `form` distribution: `prose` / `index` 별 count.
- `source-types` distribution: `course` / `conversation` / `paper` / `article` / `docs` / `book` / `essay` / `external` 별 count (한 페이지가 multi-value 가질 수 있어 합계 ≠ 페이지 수).

**Promotion candidate**: 본문 분석에서 자주 등장하는 page-shape pattern 이 기존 enum 에 안 맞으면 surface (예: tutorial-shape, literature-review-shape, video-source 등). 누적 ≥ 5 페이지면 사용자 결정 후 `docs/CONVENTIONS.md § Ontology` enum 에 추가.

#### 3i. Schema integrity (drift detector)

alias phase 가 종료됐고 tree 가 모두 새 schema. 다음 metric 은 0 이어야 정상:
- `legacy_schema_count`: type/role/source-type (singular) 만 있는 페이지. > 0 이면 신규 페이지가 옛 schema 로 작성됨 → 해당 페이지를 새 schema 로 수동 전환.
- `mixed_schema_count`: kind+role 또는 type+form 혼재. > 0 이면 manual fix.
- `unknown_count`: 어느 schema field 도 없음. > 0 이면 frontmatter parse 오류 또는 incomplete page.

#### 3j. Output quality contract guard

`docs/CONVENTIONS.md § Output quality contract` 의 deterministic subset 을 surface. 품질 평가가 아니라 body hygiene guard 다. False positive 는 가능하지만, 새 producer output 과 touched course pages 에서는 발견 즉시 고친다.

Scan target:

- 모든 content page와 `tree/trunk.md`, `tree/seeds.md`의 body before trailing `## Source`: em dash (`—`, U+2014)
- append-only `tree/rings.md`: 기존 이력의 em dash는 소급 수정하지 않고 별도 intentional debt로 계수한다. 새로 쓰는 항목은 em dash 0건이어야 한다.
- 모든 `tree/course-*.md` 의 body before trailing `## Source`: 기존 raw/source-process voice, mojibake, generic English course heading 규칙
- 최근 변경된 일반 tree pages when a workflow just wrote them: 기존 output-quality pattern도 함께 확인

Flag:

- em dash (`—`, U+2014): 모든 page kind의 body와 수정 가능한 special page에서 금지. 쉼표, 마침표, 콜론, 괄호, 줄바꿈 중 논리 관계에 맞는 표현으로 고치며 하이픈 일괄 치환은 금지
- roots/source path leakage before `## Source`: `roots/`, `` `raw` ``, `Staging`, `Source Staging`, `Archived source bundle`
- source/process voice: `PDF page`, `raw PDF`, `source PDF`, `source page`, `lecture notes`, `page range`, `render`, `image-read`, `backfill`, `run-log`, `extraction`
- Korean source voice: `필기에는`, `필기에서`, `강의 노트`, `노트에서는`, `원문에서는`, `원자료`, `자료에서는`, `페이지에서는`, `이 페이지에서는`, `이 자료`
- mojibake markers: `???`, `�`, `Ã`, `Â`
- generic English course headings: `Status`, `Scope`, `Chapters`, `Projects`, `Connections`, `Also known as`, `Overview`, `Related`, `Sequence Logic`, `Practice & Assignments`, `Course Bridges`, `Concept Extraction`, `Source Staging`, `Names`, `Maps to`

Do not flag:

- `course-*-00-index.md` meta pages, except for mojibake: their templates (`grow-branch.md § Templates`) mandate the generic headings (`Also known as` / `Overview` / `Scope` / `Chapters` / `Related` / `Subchapters` / `Chapter summary` / `Maps to`) and a `Staging: roots/...` pointer, so heading/leakage rules do not apply there
- paths inside the trailing `## Source` block
- formulas, code fences, commands, model names, method names, technical English terms, or course-native English titles
- the word `source` when it is a technical concept (for example source node, source distribution, source coding) rather than provenance/process voice

Report file, line, matched phrase, and whether it is before `## Source`. For touched producer output, treat as must-fix-before-completion. Em dash findings are blocking because the rule is universal and deterministic. Other findings remain report-only in a full care-check run unless the active workflow is already repairing them.

For `--daily`, include classification for each distinct output-quality cluster: `false-positive`, `intentional-debt`, or `repair-candidate`.

#### 3k. Leaf-depth guard

warn-only proxy check. `form=prose` 잎 페이지에 대해 두 가지를 감지한다.

- 본문 (frontmatter 제외, `## Source` 이전) 에 `[[wikilink]]` 가 0 개인 경우
- 본문 산문 글자 수가 대략 400 자 미만인 경우 (thin body)

두 항목 모두 정밀 판정이 아니라 coarse proxy 다. 실제 깊이 판정 기준은 작성 시점 self-check (`docs/QUALITY.md § 4` LEAF-1~6) 이며 care-check 는 report-only 로만 surface 한다. blocker 가 아니고 자동 수정도 없다.

#### 3f. BOM detection

UTF-8 BOM (`EF BB BF`) prefix 검출:
- `tree/*.md` 어떤 페이지든 BOM 가지면 surface.
- 발견 파일을 in-place normalization 이 필요한 repair candidate 로 surface. care-check 에서는 쓰지 않고, 사용자 승인 후 `/naite care` Repair 모드에서 정규화.
- 정상 운영 상태에선 0 이어야 함 (migration 시 strip 됨).

#### 3g. Course / collection / source 명을 frontmatter 에 사용 (legacy drift)

`course`, `course-{slug}`, `anthropic-academy`, `ode`, `laplace-transform` 같은 컬렉션·entity·하위주제 명을 `domains` 또는 `subject` 에 박은 케이스 — 항상 0 이어야 함. 발견 시 즉시 surface.

#### 3h. Language-shape review candidates

`docs/CONVENTIONS.md § Naming` 의 *Korean prose + English headings/terms* 정책 drift **후보** 를 surface. 품질 평가 아님 — 정책 compliance 의 후보 검토 단계. 비율·grade·threshold·점수 없음.

Surface 룰 (단순 presence, false positive expected):

- prose context 줄 (heading 아니고 code-block / math-block 밖, 알파벳·한글이 있는 줄) 에 Hangul 부재 → candidate
- heading context 줄 (`^#+ ` 시작) 에 Latin letters 부재 → candidate

수식 라인, 영어 인용 라인, 영어 정의 라인, 외국어 hub entity 등은 false positive 일 수 있다. 사람이 직접 검토 후 *정책 위반인 경우만* 수정한다. care-check 자체는 line 위치만 surface 한다.

blocker 아님 (secrets 만 blocker). report 는 candidate line 의 위치만 출력.

#### 3 종합 Report format

```
## Ontology validation
| Sub-check | Count | Action |
|---|---|---|
| 3a frontmatter incomplete | N | fix per page |
| 3b subject tree drift | N | resolve via altLabel or migrate |
| 3c topic uncanonicalized | N | surface promotion / alias candidates |
| 3d domain cache stale | N | route to care Repair |
| 3e kind/form/source-types distribution | (table) | surface enum-add candidates |
| 3f BOM-prefixed files | N | route to care Repair |
| 3g legacy collection/entity drift | N | manual migration |
| 3h language-shape review candidates | N lines | manual review (false positive expected) |
| 3i schema integrity (drift detector) | legacy N / mixed M | both must be 0; if > 0 fix pages to the new schema |
| 3j output quality contract guard | N lines | fix source/process voice and raw leakage |
| 3k leaf-depth guard | N findings | warn-only; thin/unlinked prose leaves (real bar: write-time self-check) |
```

3i 의 legacy/mixed count = 0 이 정상 상태. > 0 이면 새 페이지가 옛 schema 로 작성됐다는 drift signal.

### 4. Slug collisions

- **Case-insensitive**: `Attention.md` vs `attention.md` — but the project convention is lowercase-kebab-case, so any file not already matching that convention is a violation too.
- **Near-duplicate**: pairs of slugs with Levenshtein distance ≤ 2 (e.g. `attention.md` vs `attentions.md`) or where one is a strict suffix/prefix of another (`attention.md` vs `attention-mechanism.md`). Course chapter/subchapter pages with identical short titles across different chapters (e.g. `course-ma101-ch02-01-basic-concepts` ↔ `course-ma101-ch03-01-basic-concepts`) are intentional convention and not flagged.

Report: flagged pairs. Do not auto-merge — ask user which is canonical.

### 5. Trunk drift

`trunk.md` 는 **curated landing page** 다 — 모든 페이지를 enumerate 하지 않는다 (`docs/CONVENTIONS.md § trunk.md discipline` 참조). 따라서 care --check 의 "missing/ghost" 의미가 바뀌었다.

**Curated coverage 검사:**
- **Domain 노출 임계 (docs/CONVENTIONS.md § trunk.md discipline 의 *Domain inclusion criteria* 와 동기화)**: subject-tree top-level 중 **kind=concept + kind=entity 페이지 합 ≥ 10 AND 그 중 inbound 최고치 ≥ 10** 을 만족하는 도메인은 `## Knowledge domains` 아래 `### <domain>` 섹션을 가져야 한다.
  - 임계 통과인데 미노출 = **drift** (도메인 섹션 추가 candidate).
  - 임계 미달인데 노출 = **약화 신호** (페이지 삭제·rename 으로 도메인이 얇아진 경우, 사용자에게 유지/제거 결정 요청).
  - 임계 미달은 branch drill-down 으로만 접근 (예: 단일 branch 하나에만 콘텐츠가 묶인 도메인). 신규 branch 추가로 임계 통과 시 본 surface 가 트리거.
- **Hub 누락**: 각 노출 도메인의 inbound link top 5 페이지 중 `### <domain>` 의 "주요" 라인에 등장하지 않는 페이지가 있으면 후보로 surface (auto-add 금지 — 사용자가 hub 인지 결정).
- **Branch 누락**: 모든 `course-{slug}-00-index.md` 는 `## Branches § <institution>` 섹션에 등장해야 한다. 누락 시 어느 institution 섹션에 들어갈지 사용자에게 물음.

**Noise 검사** (이전 schema 잔재):
- **챕터·서브챕터 등록**: `course-{slug}-ch{NN}-*` 페이지가 trunk.md 에 등장하면 noise — 제거 권장. branch meta 페이지의 Chapters 섹션이 진실 단일 소스.
- **`## Domain:` prefix**: trunk.md 에 `## Domain:` 헤딩이 남아있으면 schema migration 미완료. `## Knowledge domains § <domain>` 또는 `## Branches § <institution>` 으로 교체.
- **`## Domain: course-{slug}` 섹션**: post-2026-04-28 schema 에서 폐기됐다. 발견 시 제거 권장.

**Ghost in trunk**: every slug referenced in `trunk.md` must have a corresponding `tree/<slug>.md`. List ghost entries (단, 페이지 시작부 format example block 의 `[[page-slug]]` placeholder 는 false positive — 첫 코드블록 외 등장만 카운트).

**Summary drift**: hub 페이지의 첫 paragraph 가 `trunk.md` 의 한 줄 요약과 본질적으로 어긋나면 surface (heuristic: trunk summary hasn't been updated since `updated:` in frontmatter).

### 6. Secrets + PII scan

This is an **LLM-performed** pass, not the deterministic gate — the deterministic gate is the `.naite/hooks` pre-commit/pre-push guard, whose shared scan logic lives in `.naite/hooks/_naite_guard.sh`. Regex-scan everything under `roots/` and `tree/` for at least the **same token families the guard blocks** (keep this list in step with `.naite/hooks/_naite_guard.sh`, the single source of truth):

- `sk-[A-Za-z0-9_-]{20,}` (OpenAI/Anthropic `sk-`, `sk-ant-`, `sk-proj-`, `sk-svcacct-`), Stripe `(sk|pk|rk)_(live|test)_...`
- GitHub `ghp_`/`gho_`/`ghs_`/`ghr_`/`ghu_` classic + `github_pat_...` fine-grained, GitLab `glpat-...`
- Slack `xox[baprs]-...` / `xapp-...` and Slack webhook URLs (`hooks.slack.com/services/...`)
- AWS `AKIA[0-9A-Z]{16}`, Google `AIza[0-9A-Za-z_-]{35}` / `GOCSPX-...`
- HuggingFace `hf_...`, Databricks `dapi...`, SendGrid `SG....`, DigitalOcean `dop_v1_...`, Linear `lin_api_...`
- npm `npm_...`, PyPI `pypi-...`
- JWT `eyJ...\.eyJ...\....`, PEM `-----BEGIN ... PRIVATE KEY-----`
- Lines matching `(?i)(password|passwd|secret|api[_-]?key|access[_-]?token|authorization)[:=]\s*\S{8,}` where the value isn't an obvious placeholder (`xxx`, `<redacted>`, `your-key-here`, `changeme`, `example`).
- High-entropy base64-ish strings of length ≥ 40 that aren't obviously URLs or hashes.
- **PII**: Korean RRN (`\d{6}-\d{7}`), phone numbers, 16-digit card-shaped runs, full addresses, national ID numbers. (Deterministic layers do not catch PII; this scan is the durable PII check.)

Coverage note: this regex scan reads text (`.md`) under `roots/`/`tree/`. It **cannot see inside binaries** — a force-tracked PDF (`.gitignore` allows `git add -f` for small finished PDFs) with a secret/PII in its text layer is invisible here; surface tracked PDFs (§ 7) and ask the user to confirm they are clean.

If **any** match: this becomes a blocker. Halt any in-flight git operation, report the file + line, and ask the user to redact before proceeding. If the match is in `roots/conversations/_transcripts/` (permanent) or already in a prior commit, redacting the working copy is not enough — advise the user to **rotate the exposed credential** and, if it is already committed, to rewrite history before any push.

### 7. Binary creep + non-tree dirt

**Binary creep**:
- List files under `roots/assets/` larger than 1 MB. Ask whether to introduce Git LFS (Phase 2 decision) or convert/resize.
- Flag any non-markdown files under `tree/` (should be zero).
- PDF 가 git tracked 인지 확인. `*.pdf` 는 기본적으로 `.gitignore` 로 차단되지만, `.gitignore` 는 작은 완성 PDF 의 `git add -f` 를 명시적으로 허용한다 (AGENTS.md § Binary files). 따라서 tracked PDF 는 **위반이 아니라 확인 대상**으로 surface 한다: 의도된 force-track 인지, 그리고 § 6 이 들여다볼 수 없는 텍스트 레이어에 secret/PII 가 없는지 사용자에게 확인한다.

**Non-tree scratch dirt** (agent / IDE / 패키지 매니저 scratch 가 tree repo 에 누적되는 패턴):
- 다음이 git tracked 면 surface:
  - `.codex-cache/` — codex CLI cache.
  - `.aider/`, `.cursor/`, `.windsurfai/` — 다른 agent / IDE local state.
  - **`node_modules/` at any depth** — 가장 강한 dirt 신호, 의도적 keep 사례 거의 없음.
  - 프로젝트 root 의 `gpt-*.md`, `claude-*.md` 같은 ad-hoc scratch markdown.
- `.codex-work/` 는 의도적으로 list 에서 *제외*. 사용자가 codex 서브-프로젝트 workspace 로 의도적 사용할 수 있어, 일괄 flag 하면 false positive. `node_modules/` 가 그 안에 들어 있으면 그 경로만 flag 됨.
- 발견 시 권장 조치: 해당 path 를 `.gitignore` 추가 + tracked 항목 `git rm --cached` 후 commit. blocker 아님 (warn).
- `grow-backfill.md § Contamination guards § Codex scratch 격리` 와 연계.

### 8. Skill promotion candidates

Read the last ~50 entries of `tree/rings.md`. Group entries by their `op | title` shape and look for **recurring manual procedures** — same sequence of operations executed ≥ 3 times without a dedicated skill file under `.agents/skills/naite/`.

Heuristics:
- Repeated `grow` runs that always touch the same kind of source (e.g. YouTube transcripts) with a common pre-step the user keeps redoing.
- Repeated `ask` + file-back patterns on a specific topic (suggests a domain-specific ask skill).
- User-reported "I keep doing X" in recent captures.

Report: the candidate procedure, how many times it recurred, and a proposed skill file name. Do not write the skill — propose it for the user to greenlight. Follow `AGENTS.md § Schema discipline` for anything that touches the schema; harness contributions go through `CONTRIBUTING.md`.

### 9. Failure patterns

Grep `tree/rings.md` for `- aborted:` lines in the last ~50 entries. Cluster by root cause keyword (e.g. "secrets", "extraction", "schema conflict"). If any cluster has ≥ 3 occurrences, surface it as a systemic failure pattern.

Report: cluster, count, entries. Suggest a preventive change (a pre-step, a skill update, or a AGENTS.md rule). Do not auto-fix.

### 10. User model refresh (optional)

Skip unless the tree has **≥ 10 pages** and **≥ 5 grow entries** in `rings.md`. Also skip if the most recent `care-check | user model refresh: yes` entry was < ~3 weeks ago (rough cadence).

When not skipped:

- Walk the last ~20 rings entries + the frontmatter of recent pages.
- Summarize for the user:
  - Which domains they've been pulling into the tree most heavily.
  - Concepts grown but never cross-referenced (possibly shallow interest).
  - Recurring judgment criteria visible in capture files (e.g. "user consistently prefers X over Y reasoning").
  - Gaps: topics frequently asked but never filed.
- **Offer** to append the summary as a dated block to the vault's operating-memory surface, `MEMORY.md` (the instruction surface defined in `docs/CONVENTIONS.md § Instruction surfaces`; template at `.naite/templates/MEMORY.md`). Do **not** overwrite existing content — append only, with a `## [YYYY-MM-DD] refresh` header. If the user has no `MEMORY.md`, offer to create one from the template first. Never touch `tree/` or `roots/` during this check.

If the user declines the memory append, still surface the summary in the care --check report.

### 11. Post-grow residue + stale archive dirs

This tree has **no generic `_archive/` layer** (per `docs/CONVENTIONS.md § Post-grow handling`). The only legitimate archive path is `roots/courses/_archive/{slug}/`, populated by `branch-finish`. Everything else is drift.

Check two things:

**11a. Stale archive directories** — any `_archive/` under `roots/articles/` or `roots/conversations/` is residue from the old convention or a cowork mistake. Flag as schema drift.

**11b. Uncleaned conversation claim summaries** — for every `YYYY-MM-DD-<slug>.md` under `roots/conversations/` (top level, not under `_transcripts/`), cross-reference `rings.md` for a `grow` entry touching that slug or its derived tree pages. If grown but not deleted, flag as "post-grow residue" — the grow step 8 cleanup didn't run to completion.

**11c. Branch archive coherence** — for each `roots/courses/_archive/{slug}/`, verify a corresponding `branch-finish` entry exists in `rings.md`. If the archive dir exists but no `branch-finish` entry does, or vice versa, flag.

**11d. Stale source paths** — branch chapter/subchapter pages 의 `## Source` 섹션이 `roots/courses/{slug}/...` 를 가리키지만 실제 파일이 `roots/courses/_archive/{slug}/...` 에 있으면 stale. branch-finish 후 source 경로 일괄 갱신 누락 신호.

Report: list flagged paths + reason. Recommend either removing the stale dir / completing the cleanup, or re-running the op. Do not auto-resolve — user picks. For residue pre-dating the "no generic archive" decision, a one-shot migration clean-up may be warranted; log that as a `migration` candidate.

### 12. Study-note, decision, and insight quality

Apply `docs/CONVENTIONS.md § Study-note quality dimensions` to every page in the requested review scope. In a whole-tree review, do not substitute a sample or a thin-body proxy for page-by-page judgement. Record the page verdict and the failing axis so that a later Writer knows whether the defect is structural, pedagogical, substantive, or stylistic.

- **Markdown form**: one H1; natural H2/H3/H4 nesting with no skipped level; headings name the content rather than a generic rubric; no empty or one-line decorative leaf section; a parent heading may directly group meaningful child headings; `## Source` is trailing. Tables compare the same axes, bullets contain parallel items rather than fragmented argument, code fences preserve code or literal structure and carry a language tag when one exists, blockquotes preserve actual quoted speech, GFM alerts carry notes or warnings, and formulas and emphasis serve their semantic job.
- **Study effectiveness**: the reader can recover definition, problem, mechanism, formal terms, a worked interpretation or application, limits, likely confusion, and conceptual connections without reopening the source. Not every item requires its own heading, but absent reasoning is a defect.
- **Content composition**: definition, intuition, formalism, example, and boundary each add a distinct unit; prerequisites are linked while the page's own mechanism is explained locally; source claim, observation, interpretation, and hypothesis stay distinguishable.
- **Writing manner**: Korean lecture-note prose explains why and therefore, not only what; transitions expose causal, conditional, comparative, or extension relations; the page avoids dictionary stubs, marketing voice, repetitive importance claims, translationese, and rubric-shaped bullet dumps.

For a concept page, compare the learning sequence to the strongest course-note pages in the same tree, not merely to the shortest acceptable leaf. The target is reconstructible understanding, not uniform length or a copied heading template.

In addition, use frontmatter `kind` as the primary selector for decision and insight pages. Embedded decision-shape or insight-shape prose in other kinds can still be reviewed when it affects a high-value project or hub, but it must not displace standalone pages from the queue. Apply `docs/CONVENTIONS.md § Page-kind quality contracts`; do not infer quality from section count, word count, or required English idioms.

For each `kind=decision` page, verify the decision kernel:

- **Choice and current state** are explicit: chosen, rejected, deferred, reversed, or provisional.
- **Context and binding constraint** explain what made the decision necessary and what actually separated the options.
- **Credible alternatives** are recorded, or the page explicitly says why no meaningful alternative was considered. Never require invented alternatives.
- **Expected mechanism** explains why the choice should produce the intended effect.
- **Validation state** distinguishes observed outcome, interpretation, and untested expectation.
- **Failure, rollback, or revisit condition** gives an observable signal or context change that would reopen the decision.
- **Links are load-bearing**: they connect the actual project, constraint, mechanism, option, or affected concept. There is no outbound-link count threshold.

For each `kind=insight` page, verify:

- **Claim**: one clear statement that can be examined, not only a slogan.
- **Evidence anchor**: the observation, source, repeated case, or decision that produced the claim.
- **Mechanism or interpretation**: why the pattern may hold.
- **Scope and uncertainty**: boundary, counterexample, alternative explanation, or explicit hypothesis status.
- **Consequence**: how the insight changes future action, interpretation, or a related project.
- **Links are load-bearing**: they connect the evidence, mechanism, application, or concept being revised.

Report a per-page list of missing information units and classify each as `repair-candidate`, `source-risk`, or `intentional-debt`. Do not auto-fix. Route decision gaps to `/naite fruit <slug>` and broader prose repair to `/naite care <slug>`.

For `--daily`, prioritize pages where missing validation or scope could change an active decision. A sparse but honest provisional record is lower priority than a polished page that presents inference as observed fact.

### 13. High-degree neurons (emergent priority)

Compute inbound `[[wikilink]]` counts for every concept page in `tree/`. Surface:

Use `.naite/ontology/tree-dependencies.json` as the primary source for inbound counts.

- **Top 10 most-referenced** — these are the user's decision-critical neurons, the implicit anchors of their reasoning. No action needed; this is self-knowledge surface. Hub candidates for `trunk.md § Knowledge domains § <domain>` "주요" 리스트.
- **Bottom distribution** — pages with inbound count 0 (already covered by § 1 Orphans) and 1~2 (weakly connected). Useful for spotting concepts that haven't woven into the synapse layer yet.

Report format: simple ranked list. Inbound count is the only signal — don't editorialize.

This check has no auto-action; it exists to make the link graph's emergent structure visible. Pair it with § 12 to see which concepts support decisions and insights, then judge the prose relation rather than the raw count.

### 14. Autonomous addition garbage collector

`docs/CONVENTIONS.md § Schema evolution` 의 autonomy A/B 추가물에 대한 사후 품질 검증. 자율 추가는 일관성 속도를 만드는 대신 *premature 추가* 위험을 안기 — care --check 가 30 일 윈도우로 garbage 후보 surface. 모든 항목 warn (not blocker). 추가 시점은 **파일 생성이 아니라 그 topic/narrower 줄이 들어온 커밋**으로 봐야 한다: `git log -1 --format=%cs -S'<정확한 topic 또는 narrower 문자열>' -- .naite/ontology/topics.md .naite/ontology/subject-tree.md` (해당 문자열이 도입된 마지막 커밋의 날짜). tree 페이지의 나이는 그 페이지의 `git log -1 --format=%cs -- tree/<slug>.md` 로 본다. `--diff-filter=A` 는 파일이 처음 추가된 커밋만 잡아 개별 append 시점을 놓치므로 쓰지 않는다.

#### 14a. Canonical topic 저사용 (autonomy A garbage)

`.naite/ontology/topics.md § canonical_topics` 의 각 토픽에 대해:
- `git log` 으로 추가 시점 확인 → ≥30 일 전
- `tree/*.md` 의 `topics:` field 사용 카운트 < 3
→ surface as **"low-usage canonical"** 후보. 사용자 결정: alias 로 redirect, 다른 canonical 로 통합, 또는 keep (도메인이 작아서 정상). LLM 의 입자도 판단 미스 신호일 수 있음.

#### 14b. Autonomously-added narrower 의 trivial split (autonomy B garbage)

`.naite/ontology/subject-tree.md` 의 각 `narrower:` entry 에 대해:
- `git log` 으로 추가 시점 확인 → ≥30 일 전
- 그 path 를 `subject:` 로 쓰는 페이지 ≤ 1
→ surface as **"trivial narrower"** 후보. 사용자 결정: 트리에서 제거, 또는 부모 narrower 로 흡수, 또는 keep (의도된 좁은 분류).

#### 14c. Autonomous 일반 개념 페이지의 orphan (autonomy A garbage)

§ 1 Orphans 와 cross-reference. autonomy A 로 spawn 된 일반 개념 페이지 (branch skill `subchapter-note § step 5`, `ingest.md § 5`) 가:
- `git log` 으로 생성 시점 확인 → ≥30 일 전
- inbound `[[wikilink]]` count == 0 (`trunk.md` / `seeds.md` / `rings.md` 외)
→ surface as **"orphan spawn"** 후보. 입자도 미스 또는 너무 좁은 추출 신호. 사용자 결정: 페이지 삭제, 본문 흡수해서 다른 페이지로 merge, 또는 다른 페이지에서 명시적 cross-link 추가.

**철학**: autonomy A/B 의 *option value* (빠른 schema 진화) 를 보존하면서 누적 카오스를 방지. 자율 추가가 잘못되어도 care --check 가 30 일 후 잡고 사용자가 정리. grow 시점에 "확실하지 않으면 추가하지 마" 보다 "추가하고 care --check 가 청소" 가 노드 연결을 치밀하게 유지하는 데 유리하다 — `docs/ARCHITECTURE.md § 2.3` 의 folksonomy 철학과 일치.

### 15. Forest health (optional, report-only)

vault 가 숲으로 분화 중이거나 분화 압력을 점검할 때 실행한다. **report-only** — 자동 분할·병합·재배정은 없다 (C급, 사용자 결정). 근거: `docs/CONVENTIONS.md § Forest layer`, `docs/ARCHITECTURE.md § 9`.

실행 도구 (모두 `tree/` 에 read-only):

- `python .naite/scripts/forest-communities.py` — S1 구조 신호. 군집별 conductance·지배 도메인·hub. 새 저-conductance 군집은 분화 후보, 높은 conductance 줄기는 아직 미성숙.
- `python .naite/scripts/forest-assign.py --write` — 개념 계보 배정 (`forest-config.json` seed + label propagation). `forest-manifest.json` 갱신.
- `python .naite/scripts/forest-dashboard.py` — 나이테 대시보드 (`.naite/forest/dashboard.md`) 갱신.

의존성: `.naite/scripts/requirements.txt` (`networkx>=3.0`, `numpy`, `scikit-learn`).

surface 할 압력:

- **분화 압력**: 한 나무 안에 size ≥ floor 이면서 conductance ≤ 임계인 군집이 새로 자랐는가.
- **병합 압력**: 두 나무가 두꺼운 `inter_tree_edges` 로 붙었는가.
- **재배정 압력**: flip 페이지 — 과목 라벨과 링크 계보가 어긋난 페이지 (걸침 개념 메커니즘의 flip 부류).
- `forest-config.json` 이 없으면 도메인=나무 identity 로 동작하며 첫 grouping 후보만 제안한다.

판단 기준은 수치가 아니라 작업 맥락 효용이다. modularity·conductance 는 증거이고, 분화·병합·재배정 cut 은 사용자가 정한다. 빈/작은 vault (Phase 1) 에서는 도구가 분화 후보를 거의/전혀 잡지 않는 것이 정상이다.

## Report format

```markdown
# Care --check report — YYYY-MM-DD

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

## Trunk drift
- domain missing: ml has no `### ml` section under `## Knowledge domains`
- hub missing from trunk: [[generative-ai]] (inbound 6, top-10) but absent from `### ai-fluency` 주요
- chapter noise: [[course-ma101-ch01-00-index]] in trunk.md — should only be in course-ma101-00-index Chapters
- legacy: `## Domain:` prefix at line 12 — migrate to `## Knowledge domains` / `## Branches`

## Secrets (N) ⚠
- roots/conversations/2026-04-15-foo.md:23 — matched /sk-[A-Za-z0-9]+/
**BLOCKER** — halt commits until resolved.

## Binary creep
- roots/assets/big.png (2.3 MB) — consider resize or LFS
- roots/courses/ma101/ch01-lecture.pdf — git tracked PDF (gitignore violation)

## Post-grow residue (N)
- roots/conversations/2026-04-24-foo.md — rings shows grow 2026-04-24 but file still present. Cleanup (delete claim summary) never ran.

## Stale archive dirs (N)
- roots/conversations/_archive/ — not a legitimate archive location per docs/CONVENTIONS.md § Post-grow handling. Recommend removing (files inside may be cleanup residue).

## Branch archive coherence (N)
- roots/courses/_archive/aa101/ exists but no `branch-finish | course-aa101` entry in rings.md. Verify or log retroactively.
- stale source: course-ma101-ch02-* pages reference `roots/courses/ma101/ch02-*.pdf` but file is at `roots/courses/_archive/ma101/ch02-*.pdf`.

## Output quality guard (N)
- tree/course-ma101-ch02-03-foo.md:42 — `필기에는` before `## Source`; absorb the note insight into prose.
- tree/course-ma101-ch03-00-index.md:18 — generic English heading `Overview`; use a Korean heading unless course-native.

## Study-note quality (N issues)
- [[foo]] (`repair-candidate`, Markdown form): H2에서 H4로 건너뛰고 한 문장짜리 heading이 반복되어 논리 계층이 보이지 않는다.
- [[bar]] (`repair-candidate`, study effectiveness): 정의와 수식은 있으나 변수 해석, worked application, 성립 경계가 없어 다시 공부할 수 없다.

## Decision and insight quality (N issues)
- [[decision-2026-04-12-rag-reranker]] (`repair-candidate`): expected mechanism is present, but outcome is written as observed without evidence and no revisit signal is named.
- [[compounding-learning-context]] (`source-risk`): claim and implication are clear, but the evidence anchor and scope are not recoverable without the original conversation.

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
- recurring: `grow` on YouTube transcripts (5x) — propose `.agents/skills/naite/grow-transcript.md`

## Failure patterns (N)
- extraction (3x): PDF text extraction aborted on scanned docs → propose OCR pre-step in `grow.md`

## User model refresh
- (skipped / summary block)

## 우선 검토 후보 3개
- [repair-candidate] [[page-or-target]] - why this is worth reviewing first.
- [schema-pressure] <topic or workflow> - what repeated evidence suggests.
- [intentional-debt] <artifact> - why it is intentionally left alone.
```

## What this command never does

- Never modifies pages, `trunk.md`, or `seeds.md`.
- Never auto-resolves anything.
- Never commits.
- Never skips the secrets check — it runs every time, and any hit is a hard stop.
- Never writes to memory files without explicit user consent.
