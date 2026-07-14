# /naite care

나무를 돌본다. 하나의 명령 아래 두 모드가 있다:

- **점검 모드 (`/naite care --check`)** — deterministic 건강 점검. report-only, 절대 고치지 않는다. secrets 발견 시 차단 게이트. 절차는 `care-check.md` 가 계약이다 — `--check` 또는 "점검만 / 상태 봐줘" 류 의도가 감지되면 `care-check.md` 를 읽고 그대로 따른다.
- **돌봄 모드 (기본)** — 정성 검토, 직접 수선, 대규모 정리, 반복 결함의 규칙화. 본 파일이 계약이다.

모드 판별: `--check` 플래그가 있으면 점검. "고쳐줘 / 다듬어줘 / 검토하고 수선까지" 면 돌봄. 애매하면 한 줄로 묻는다.

## When to use

Use this when the user asks to:

- 검토 / 다시 훑기 / quality check / 내용 이상한 곳 찾기
- branch 전체 또는 특정 branch 내용을 다듬기
- care --check 로는 잡기 어려운 prose quality, source voice, link usefulness 를 판단하기
- 반복 결함을 producer skill, care --check rule, or `docs/CONVENTIONS.md` 에 반영하기

## Scope

Supported scopes:

- `/naite care {slug}` — one page plus its immediate graph context.
- `/naite care branch-{slug}` — branch meta, chapter meta, and all subchapter pages for one branch (pages are named course-{slug}-*).
- `/naite care --branches` — all branch pages.
- `/naite care --fruits` — decision-shape pages and their load-bearing links.
- `/naite care --all` — whole tree qualitative sweep.
- `/naite care --system` — durable workflow learning: update producer contracts, care --check criteria, or workflow docs from recurring failures.

- `/naite care --daily` - report-only daily triage after `/naite care --check --daily`. Review the care --check handoff, read evidence for priority candidates, and write a short durable triage report without editing tree content.

For large scopes, write working artifacts under `.naite/reports/{YYYY-MM-DD}-care/` or `tmp/care-{YYYY-MM-DD}/` as appropriate. `.naite/reports/` is for durable reports; `tmp/` is for disposable work logs.

Daily triage writes to `.naite/reports/daily/YYYY-MM-DD-care.md` so the daily automation has a stable output location.

## Context maps

Before review or repair, read `docs/CONTEXT.md` and load the generated operating maps:

- `.naite/ontology/tree-manifest.json` for page coordinates and candidate narrowing.
- `.naite/ontology/tree-dependencies.json` for inbound dependents, outbound links, soft relation idioms, high-degree pages, and orphan candidates.

If either map is missing or stale for the current task, run:

```powershell
python .naite/scripts/build-tree-manifest.py
python .naite/scripts/build-tree-dependencies.py
```

For one-page repair, inspect inbound entries for the touched slug before editing and again after rebuilding the map. Surface semantic dependent candidates; do not rewrite them unless the user asked for that repair scope.

## Modes

`care` is one skill with five internal modes. Pick the mode from user intent; do not ask unless intent is genuinely ambiguous.

### Review

Read the requested pages, their frontmatter, and the directly relevant links. Produce a prose verdict with concrete page examples. Avoid scores, grades, thresholds, and rubric language.

Verdicts use plain labels, not scores: `healthy` / `thin-but-acceptable` / `repair-candidate` / `source-risk` / `system-rule-candidate`. `source-risk` means the page reads well but its formulas, definitions, theorems, conditions, or numbers must not be rewritten without source review (`docs/CONVENTIONS.md § Output quality contract`, source-fidelity ceiling); defer the repair rather than risk distorting the source.

Review answers should say:

- what is already usable,
- what is misleading or thin,
- which pages need edits,
- whether the issue is page-local, course-wide, or workflow-level.

### Daily Triage

Use this mode for `/naite care --daily`, usually immediately after `/naite care --check --daily`. It is a review mode, not repair.

Step A. Read the latest `.naite/reports/daily/YYYY-MM-DD-care-check.md` if present; otherwise use the current care --check report in the conversation. Also read `.naite/ontology/tree-manifest.json` and `.naite/ontology/tree-dependencies.json`.

Step B. Take the care --check report's **우선 검토 후보 3개** as the starting queue. If that section is missing, derive a queue from Tier 1 findings in this order: missing targets/stubs, output quality guard, fruit coverage, autonomy garbage.

Step C. For each candidate, open the relevant source page or dependency-map source. Decide whether the finding is `false-positive`, `intentional-debt`, `repair-candidate`, or `schema-pressure`. Preserve the care --check label if it still fits.

Step D. Write `.naite/reports/daily/YYYY-MM-DD-care.md` with:

- what is actually worth reviewing next,
- what should be ignored as false positive or intentional debt,
- which candidate needs a user decision before repair,
- which candidate should be routed to a focused `/naite care {slug}` or `/naite care --fruits` pass.

Step E. Append a coarse `tree/rings.md` entry with `updated: 0 tree content pages` unless the user explicitly asked for repair. Do not edit any **tree content page** (a `tree/*.md` leaf/index), nor `tree/trunk.md` or `tree/seeds.md`, in daily triage. (Appending to `tree/rings.md` is the one allowed write here — the log is not a content page.)

### Repair

When the user asks to fix, edit pages directly. Preserve source substance, existing good links, and frontmatter unless the defect is there. After editing, run the touched-page content guard and the relevant deterministic checks (care --check).

When care-check reports stale `domains` caches or BOM-prefixed files and the user approves repair, use the matching deterministic write command in this mode:

```powershell
python .naite/scripts/lint-ontology.py --refresh-domains
python .naite/scripts/lint-ontology.py --strip-bom
```

Run only the command needed for the approved finding, inspect `git diff HEAD -- tree/` immediately afterward, and report the exact pages changed before staging.

**Minimal-intrusion first.** 가장 작은 수정으로 결함을 고친다. 확실한 버그라도 이번 turn 의 scope 밖이면 고치지 말고 defer 로 표기한다 (scope 규율 > 완벽주의). 구조 수술(파일 재구성, 대량 재작성)은 최소침습으로 해결이 안 되는 게 확실할 때만, 그리고 Sweep 의 무손실 증명을 동반할 때만 한다.

After editing pages, rebuild `.naite/ontology/tree-manifest.json` when page coordinates changed and rebuild `.naite/ontology/tree-dependencies.json` when body links or soft relation idioms changed. Include both generated maps in the change if they changed.

### Sweep

For large scopes, first gather repeatable signals:

- source/process voice in body,
- unnecessary English sentence spine,
- generic rubric headings,
- raw path leaks before `## Source`,
- mojibake,
- shallow link lists that do not explain the relation,
- pages whose body depends on raw notes or PDFs to be understood.

Then cluster by cause and fix in batches only when the user asked for repairs. Store a durable report if the sweep result matters beyond the current turn.

Use `.naite/ontology/tree-dependencies.json` to choose inbound dependents and high-degree pages. Use `.naite/ontology/tree-manifest.json` to avoid walking `tree/trunk.md` as if it were exhaustive.

**Lossless bulk cleanup.** 대량 삭제·압축(large deletions, whitespace collapse, boilerplate 제거)은 두 층으로 분리한다: 기계적 정규화(중복 빈 줄·후행 공백·반복 boilerplate 제거)와 의미 편집(문장·내용 변경). 섞어서 한 번에 하지 않는다. 대량 정리를 무손실로 주장하려면 증명을 붙인다 — 비-빈 줄만 비교하는 diff(`diff <(grep -v '^[[:space:]]*$' old) <(grep -v '^[[:space:]]*$' new)`)로 실질 내용 라인이 보존됐음을 보이고 그 결과를 리포트에 남긴다. 증명 없는 대량 삭제는 커밋하지 않는다.

### System Learning

Use this when the same defect appears across pages or workflows. The order of preference is:

1. Strengthen producer contracts first (`grow.md`, `grow-backfill.md`, or another output-producing skill).
2. Add deterministic care --check guard only when a pattern is reasonably machine-detectable.
3. Update `docs/CONVENTIONS.md` when the rule applies across workflows.
4. Leave user-facing mental model simple: care --check + care.

Schema-level changes still follow `docs/CONVENTIONS.md § Schema evolution`; do not introduce new facet fields, enum values, or top-level domains without user decision.

enum/schema 불일치를 고칠 때는 **전체 불일치(모든 페이지가 spec 과 어긋남 = 수선 대상)와 의도된 subset(일부만 다른 것이 설계상 정당 = 유지)을 구별**한다. 전자만 수선하고 후자는 건드리지 않는다. 판별이 애매하면 수정하지 말고 surface 한다.

## Branch Content Quality Criteria

Branch pages must read as lecture-native, self-contained tree pages. The body should carry the meaning directly; `## Source` is provenance, not a dependency.

Required:

- Body prose is Korean by default. English technical terms, formulas, model names, course-native headings, and established abbreviations are allowed when they carry precision.
- Generic headings use Korean unless the lecture itself uses the English term as the conceptual unit.
- Handwriting, slide emphasis, examples, and diagrams are absorbed into explanatory prose. Do not describe them as "the note says" or "the PDF shows".
- Raw paths appear only in trailing `## Source` blocks.
- A page must make sense without opening the raw PDF, raw note, PNG, or staging artifact.
- Links are load-bearing: prose says why the linked page matters here.

Forbidden in the body before `## Source`:

- raw/source-process voice: "raw", "staging", "source bundle", "PDF page", "page range", "필기에는", "강의 노트에는", "원문에서는", "자료에서는", "이 페이지에서는".
- explanations of how the page was produced: extraction, backfill, render, image-read, note mapping, run-log.
- generic wiki-rubric headings such as `Core idea`, `Details`, `Overview`, `Related`, `Maps to`, `Source Staging`, `Practice & Assignments`, unless they are part of a page template that explicitly allows them (the course/chapter meta index templates in `grow-branch.md § Templates` mandate `Also known as` / `Overview` / `Scope` / `Chapters` / `Related` / `Subchapters` / `Chapter summary` / `Maps to` on `course-*-00-index.md` pages — those are correct, not drift).

## Content Guard

For touched pages, inspect only the body before `## Source` unless a rule says otherwise.

Flag and fix:

- `roots/`, `` `raw` ``, `Staging`, `Source Staging`, `Archived source bundle`
- `PDF page`, `raw PDF`, `source PDF`, `source page`, `lecture notes`, `page range`, `render`, `image-read`, `backfill`, `run-log`, `extraction`
- `필기에는`, `필기에서`, `강의 노트`, `노트에서는`, `원문에서는`, `원자료`, `자료에서는`, `페이지에서는`, `이 페이지에서는`, `이 자료`
- mojibake markers: `???`, `�`, `Ã`, `Â`
- generic English headings on branch pages: `Status`, `Scope`, `Chapters`, `Projects`, `Connections`, `Also known as`, `Overview`, `Related`, `Sequence Logic`, `Practice & Assignments`, `Course Bridges`, `Concept Extraction`, `Source Staging`, `Names`, `Maps to`. **Exempt `course-*-00-index.md` meta pages (mojibake check still applies)** — their templates (`grow-branch.md § Templates`) mandate these headings and a `Staging: roots/...` pointer; flag them only on subchapter note pages and general leaves.

False positives are possible. Preserve legitimate technical English, formulas, commands, file paths inside `## Source`, and quoted titles that belong to the branch.

## Log Format

Successful care runs append one coarse entry:

```markdown
## [YYYY-MM-DD] care | <scope>
- reviewed: <N pages>
- updated: <N pages or none>
- output: <report path if any>
- summary: <one-line finding or fix>
```

When `care --system` changes workflow files, use `migration` if the change is structural, or `care` if it is a maintenance-rule update. Keep `rings.md` coarse; detailed page lists belong in reports.
