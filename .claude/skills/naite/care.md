# /wiki curate

Qualitative maintenance for the wiki. This is the single user-facing skill for narrative quality review, direct cleanup, large-scope sweeps, and recurring-rule learning.

`/wiki lint` and `/wiki curate` are the two tracks:

- `/wiki lint` is deterministic guardrail work: schema, broken links, secrets, archive drift, obvious hygiene patterns.
- `/wiki curate` is contextual judgement: whether pages read like self-contained wiki pages, whether connections carry meaning, whether repeated defects should become producer rules or lint checks.

Old names are compatibility aliases only:

- `/wiki audit` → run `/wiki curate` in review mode.
- `/wiki consolidate` → run `/wiki curate` in sweep mode.
- `/wiki rewire` → run `/wiki curate` in system-learning mode.

Do not maintain separate standards in those legacy files. Prefer `/wiki curate` in new docs, prompts, and user-facing summaries.

## When to use

Use this when the user asks to:

- 검토 / 다시 훑기 / quality check / 내용 이상한 곳 찾기
- course 전체 또는 특정 course 내용을 다듬기
- lint 로는 잡기 어려운 prose quality, source voice, link usefulness 를 판단하기
- 반복 결함을 producer skill, lint rule, or `CONVENTIONS.md` 에 반영하기

## Scope

Supported scopes:

- `/wiki curate {slug}` — one page plus its immediate graph context.
- `/wiki curate course-{slug}` — course meta, chapter meta, and all subchapter pages for one course.
- `/wiki curate --courses` — all course pages.
- `/wiki curate --synapses` — decision-shape pages and their load-bearing links.
- `/wiki curate --all` — whole wiki qualitative sweep.
- `/wiki curate --system` — durable workflow learning: update producer contracts, lint criteria, or workflow docs from recurring failures.

- `/wiki curate --daily` - report-only daily triage after `/wiki lint --daily`. Review the lint handoff, read evidence for priority candidates, and write a short durable triage report without editing wiki content.

For large scopes, write working artifacts under `exports/{YYYY-MM-DD}-curate/` or `tmp/curate-{YYYY-MM-DD}/` as appropriate. `exports/` is for durable reports; `tmp/` is for disposable work logs.

Daily triage writes to `exports/daily/YYYY-MM-DD-curate.md` so the daily automation has a stable output location.

## Context maps

Before review or repair, read `CONTEXT.md` and load the generated operating maps:

- `ontology/wiki-manifest.json` for page coordinates and candidate narrowing.
- `ontology/wiki-dependencies.json` for inbound dependents, outbound links, soft relation idioms, high-degree pages, and orphan candidates.

If either map is missing or stale for the current task, run:

```powershell
python scripts/build-wiki-manifest.py
python scripts/build-wiki-dependencies.py
```

For one-page repair, inspect inbound entries for the touched slug before editing and again after rebuilding the map. Surface semantic dependent candidates; do not rewrite them unless the user asked for that repair scope.

## Modes

`curate` is one skill with four internal modes. Pick the mode from user intent; do not ask unless intent is genuinely ambiguous.

### Review

Read the requested pages, their frontmatter, and the directly relevant links. Produce a prose verdict with concrete page examples. Avoid scores, grades, thresholds, and rubric language.

Review answers should say:

- what is already usable,
- what is misleading or thin,
- which pages need edits,
- whether the issue is page-local, course-wide, or workflow-level.

### Daily Triage

Use this mode for `/wiki curate --daily`, usually immediately after `/wiki lint --daily`. It is a review mode, not repair.

Step A. Read the latest `exports/daily/YYYY-MM-DD-lint.md` if present; otherwise use the current lint report in the conversation. Also read `ontology/wiki-manifest.json` and `ontology/wiki-dependencies.json`.

Step B. Take the lint report's **우선 검토 후보 3개** as the starting queue. If that section is missing, derive a queue from Tier 1 findings in this order: missing targets/stubs, output quality guard, synapse coverage, autonomy garbage.

Step C. For each candidate, open the relevant source page or dependency-map source. Decide whether the finding is `false-positive`, `intentional-debt`, `repair-candidate`, or `schema-pressure`. Preserve the lint label if it still fits.

Step D. Write `exports/daily/YYYY-MM-DD-curate.md` with:

- what is actually worth reviewing next,
- what should be ignored as false positive or intentional debt,
- which candidate needs a user decision before repair,
- which candidate should be routed to a focused `/wiki curate {slug}` or `/wiki curate --synapses` pass.

Step E. Append a coarse `wiki/log.md` entry with `updated: 0 wiki content pages` unless the user explicitly asked for repair. Do not edit `wiki/*.md`, `wiki/index.md`, or `_stubs.md` in daily triage.

### Repair

When the user asks to fix, edit pages directly. Preserve source substance, existing good links, and frontmatter unless the defect is there. After editing, run the touched-page content guard and the relevant deterministic lint.

After editing pages, rebuild `ontology/wiki-manifest.json` when page coordinates changed and rebuild `ontology/wiki-dependencies.json` when body links or soft relation idioms changed. Include both generated maps in the change if they changed.

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

Use `ontology/wiki-dependencies.json` to choose inbound dependents and high-degree pages. Use `ontology/wiki-manifest.json` to avoid walking `wiki/index.md` as if it were exhaustive.

### System Learning

Use this when the same defect appears across pages or workflows. The order of preference is:

1. Strengthen producer contracts first (`course.md`, `course-backfill.md`, `ingest.md`, or another output-producing skill).
2. Add deterministic lint guard only when a pattern is reasonably machine-detectable.
3. Update `CONVENTIONS.md` when the rule applies across workflows.
4. Leave user-facing mental model simple: lint + curate.

Schema-level changes still follow `CONVENTIONS.md § Schema evolution`; do not introduce new facet fields, enum values, or top-level domains without user decision.

## Course Content Quality Criteria

Course pages must read as lecture-native, self-contained wiki pages. The body should carry the meaning directly; `## Source` is provenance, not a dependency.

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
- generic wiki-rubric headings such as `Core idea`, `Details`, `Overview`, `Related`, `Maps to`, `Source Staging`, `Practice & Assignments`, unless they are part of a non-course page template that explicitly allows them.

## Content Guard

For touched pages, inspect only the body before `## Source` unless a rule says otherwise.

Flag and fix:

- `raw/`, `` `raw` ``, `Staging`, `Source Staging`, `Archived source bundle`
- `PDF page`, `raw PDF`, `source PDF`, `source page`, `lecture notes`, `page range`, `render`, `image-read`, `backfill`, `run-log`, `extraction`
- `필기에는`, `필기에서`, `강의 노트`, `노트에서는`, `원문에서는`, `원자료`, `자료에서는`, `페이지에서는`, `이 페이지에서는`, `이 자료`
- mojibake markers: `???`, `�`, `Ã`, `Â`
- generic English headings on course pages: `Status`, `Scope`, `Chapters`, `Projects`, `Connections`, `Also known as`, `Overview`, `Related`, `Sequence Logic`, `Practice & Assignments`, `Course Bridges`, `Concept Extraction`, `Source Staging`, `Names`, `Maps to`

False positives are possible. Preserve legitimate technical English, formulas, commands, file paths inside `## Source`, and quoted titles that belong to the course.

## Log Format

Successful curate runs append one coarse entry:

```markdown
## [YYYY-MM-DD] curate | <scope>
- reviewed: <N pages>
- updated: <N pages or none>
- output: <report path if any>
- summary: <one-line finding or fix>
```

When `curate --system` changes workflow files, use `migration` if the change is structural, or `curate` if it is a maintenance-rule update. Keep `log.md` coarse; detailed page lists belong in reports.
