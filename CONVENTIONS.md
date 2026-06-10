# CONVENTIONS.md — naite operating invariants

These rules apply to **every wiki mutation** regardless of which workflow (`/wiki ingest`, `/wiki study`, `/wiki course`, `/wiki synapse`, `/wiki query`, `/wiki lint`, `/wiki curate`, `/wiki capture`) is running. Workflow-specific procedures live in the wiki workflow skill directory.

This file is shared by both tool surfaces. Keep it tool-neutral: workflow rules live here, while tool-specific paths and entrypoint wording live in `CLAUDE.md`, `AGENTS.md`, and the mirrored workflow skill directories.

For the *why* (rationale, theoretical basis, schema evolution playbook), see `ARCHITECTURE.md`.
For the *data* (canonical vocabularies), see `ontology/subject-tree.md` and `ontology/topics.md`.

---

## Maintenance model

Wiki maintenance has two user-facing tracks:

- `/wiki lint` is deterministic guardrail work: schema, broken links, domains cache, archive drift, output-quality regex checks, secrets, binaries, and other machine-checkable hygiene.
- `/wiki curate` is qualitative judgement and repair: page/course review, direct content cleanup, large-scope sweeps, and recurring-rule learning that should strengthen producer contracts or lint checks.

`/wiki audit`, `/wiki consolidate`, and `/wiki rewire` are compatibility aliases only. New docs, prompts, and user-facing summaries should say `curate` unless they are explaining older history.

---

## Naming

- Files: `lowercase-kebab-case.md`. No spaces, no capitals. One concept per file.
- Wikilinks: `[[page-slug]]` or `[[page-slug|Display Text]]`. Plain `[[...]]` only — no typed relations (relations live in prose; see § Soft ontology).
- Aliases: list at top of page under `## Also known as` heading. `index.md` lists only the canonical slug.

---

## Personal wiki scope — what belongs

This wiki is about **what the user knows**, not a generic encyclopedia. Beyond plain study concepts, pages legitimately cover:

- **Projects** — products, repos, research efforts the user runs.
- **Decisions** — considered choices with tradeoffs, often tied to a project.
- **Insights** — realized connections or claims the user endorses.
- **Questions** — open threads the user is thinking about but hasn't closed.
- **People / orgs / tools** — `kind=entity`.

These map to the `kind` facet enum (§ Ontology). The `kind` facet is *page essence* (concept/entity/source-record/project/decision/insight/comparison); `form` is *presentation shape* (prose/index). `domains` is a derived cache, not a facet. Do not mint new `kind` / `form` / `source-types` values without lint-surfaced pressure + user decision.

`comparison` pages (A-vs-B, e.g. `[[k-means-vs-dbscan]]`) → `kind=comparison`. Query-derived pages absorb provenance into prose, no separate facet.

---

## Ontology — quick reference

Every page has these frontmatter facets:

```yaml
---
kind: concept | entity | source-record |          # page essence (immutable)
      project | decision | insight | comparison
form: prose | index                               # presentation shape
topics: [<canonical-topic>, ...]                  # folksonomy. 0-5 per page. Empty array OK.
subject: [<skos-path>]                            # SKOS-lite path. Multi-value for cross-domain.
source-types: [course | conversation | paper |    # 8-enum, always a list
               article | docs | book |
               essay | external]
domains: [<top-level>]                            # CACHED — lint derives from subject top-level
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**Schema note** — an earlier `type` / `role` / `source-type` (singular) schema was replaced by `kind` / `form` / `source-types` (list). Legacy schema in new pages is an error (drift signal); historical references to old facet names in decision pages' "Before/As-Was" sections are preserved as documentation.

**Field rules:**

- `kind` enum (9 values): `concept` (reusable concept/method/technique/pattern), `entity` (person/org/tool/platform/model/product), `source-record` (single source unit recorded in wiki — course top/chapter/subchapter, paper note, book note, article note), `project` (user's project tracker), `decision` (synapse / decision record), `insight` (extracted/synthesized observation), `comparison` (A-vs-B page where the comparison itself is the subject), `essay` (사용자가 직접 작성한 에세이 또는 학문 도메인 밖 개인 글쓰기. `source-types: [essay]` 와 짝을 이루며 `subject: [personal]` 을 사용한다. `source-record` 는 외부 source 의 study note 이고, `essay` 는 사용자 본인이 직접 쓴 글이다), `personal` (사용자 본인의 신원, 학력, 산출물 목차, 진로 hub 등 self-reference 메타 페이지. `subject: [personal]` 과 짝을 이루며 source-types 는 보통 [conversation, external]. essay 가 본인이 쓴 학문 외 글이라면 personal 은 본인에 대한 메타-기록 페이지다. C-level 신설로 사용자 승인 후 추가된 enum 사례). `question` is **not** a kind — earlier `role=question` deprecated in 2026-05-18 (no corpus use case; future C-level decision if needed).
- `form` enum (2 values): `prose` (body is flowing text — explanation, decision record, insight, etc.), `index` (body is a list/navigation hub of wikilinks).
- `topics`: 0-5 per page. Canonical list (`ontology/topics.md`) preferred. Uncanonicalized topic → lint warns (does not block — folksonomy philosophy). Empty array OK (e.g. `kind=entity`). Do not force topics. Topics are **re-usable concept/technique level** — not broad domain names.
- `subject`: SKOS-lite path notation (`parent/child[/grandchild]`, slash-separated). Single path is default; multi only for genuine cross-domain (`[a/x, b/y]`). Canonical tree: `ontology/subject-tree.md`. **Course / collection / institution / source names are NOT subjects** — `course`, `course-{slug}`, `anthropic-academy`, `ode`, `laplace-transform` are page slugs/entities, not subject paths. Course membership is carried by the `course-{slug}-*` filename prefix.
- `source-types` (always list, 8 values): `course` (academic/online courses), `paper` (peer-reviewed academic), `article` (informal: blog / news / X thread / Substack), `docs` (official docs: Anthropic / OpenAI / library docs), `book` (book), `conversation` (user dialogue capture), `essay` (self-authored essay/long-form), `external` (fallback). A page can be informed by multiple sources — `source-types: [course, paper]` is valid. `legacy` is **not** a value — it's an import channel; staged legacy notes ingest with the source-types matching their content nature. Detail: `ARCHITECTURE.md § 7`.
- `domains` (CACHED, NOT a facet): top-level path component of `subject`. **Lint auto-derives** (`lint --refresh-domains`); never hand-write. Idempotent on schema change.

`index.md` and `log.md` have no frontmatter (special files). Additional facet fields (`confidence`, `status`, `depends-on`, `contradicts`, `source-count`, `as-of`, etc.) are added only after lint surfaces accumulated pressure → user decision. No arbitrary additions.

For the why behind each facet: `ARCHITECTURE.md § 3`. Schema evolution: § Schema evolution below.

---

## Soft ontology — relations live in prose

No typed relations in frontmatter. Relations are expressed with conventional idioms inline in page body. **Reuse the exact phrasings** so `grep` surfaces them later:

- `builds on [[x]]` / `extends [[x]]` — depends on or refines another idea.
- `contradicts [[y]]` / `YYYY-MM-DD source [[z]] disagrees:` — flagged conflict.
- `instance of [[category]]` — concrete example of a more general concept.
- `applies to [[project-slug]]` / `used in [[project-slug]]` — how a concept shows up in user's work.
- `see also [[x]]` — related, direction not load-bearing.
- `decided [[x]] over [[y]] when [[constraint]]` — selection + rejection + binding constraint. Used in decision threads.
- `failed when [[condition]]` — failure condition. Condition can be prose or a concept link.
- `trade-off: [[a]] vs [[b]]` — weighed-decision trace.
- `validates [[hypothesis]]` / `falsifies [[hypothesis]]` — experimental result tied to hypothesis.

Why prose, not frontmatter:
1. Pages stay readable; Obsidian renders cleanly.
2. No premature commitment to a relation taxonomy — the set of idioms people actually reach for becomes the input to any future typed-relation extension.
3. LLM reasons about relations at query time without formal ontology layer.

When reading these idioms during `/wiki query`, synthesize as if they were typed edges. When writing new pages, prefer these exact phrasings to keep the vocabulary compounding.

---

## Decision thread shape

A decision page has **`kind=decision`** (occasionally embedded as decision-shape content within `kind=concept`/`entity`/`source-record` pages — both are valid synapse forms). Its `subject` is the actual content path (canonical tree: `ontology/subject-tree.md`). Cross-domain decisions get multi-subject. **Do not invent meta subject paths** like `dmu/`, `failure-*/`, `synapse/` — categorizing a synapse defeats its purpose.

**File naming**: standalone decision pages use `decision-YYYY-MM-DD-<slug>.md` format, where `YYYY-MM-DD` matches frontmatter `created`. This prevents slug collision as decisions accumulate and provides session-cluster grouping in file listings.

Body shape — used as needed, empty sections dropped:

- **Context** — what circumstance forced the choice
- **Problem** — what was at stake
- **Decision** — what was chosen
- **Alternatives** — what was considered but rejected
- **Rationale** — *why* (the binding constraint)
- **Mechanism** — how the decision plays out
- **Outcome** — what happened (after-the-fact)
- **Failure mode** — when it would break
- **Iteration** — what changed since
- **Invariant** — what must remain true
- **Reusability** — does this recur?
- **Related** — `[[wikilinks]]`
- **Next action** — open thread (if any)

This is a **reference structure, not a strict template**. `/wiki synapse` walks the user through it as dialogue, not a form.

A decision thread can also live as a short prose paragraph **embedded in another concept page** ("In my projects" or similar section). Both forms are equally valid synapses. A standalone page is just a paragraph that grew large enough to deserve its own slug.

When writing a synapse and a referenced concept is missing from the wiki, propose a stub in `_stubs.md`. The synapse layer creates pressure to fill graph gaps — that is one of its core values.

**Most-cross-linked concepts are emergent decision-critical neurons.** `/wiki lint` surfaces high-degree pages — they are the implicit anchors of the user's reasoning. No frontmatter tag needed; falls out of the link graph.

**Career framing is deliberately outside this schema.** When career-relevant evidence is needed, it is extracted on demand by `grep`-ing synapse prose across pages — not by a pre-built index.

---

## index.md discipline

`wiki/index.md` is a **curated entrypoint and drill-down starting point**, not an enumerator of every page. It exposes domain hubs and course meta pages; everything else is discovered by drill-down through those.

Structure (2 fixed top-level sections):

```
## Knowledge domains

### {domain-name}
한 줄 설명 (이 도메인이 무엇을 다루는지).
주요: [[hub-1]], [[hub-2]], [[hub-3]]   (4-7 pages, entry-point role only)

## Courses

### {institution / source}
- [[course-{slug}-00-index]] — 한 줄 설명
- ...
```

Rules:

- No `## Domain:` prefix. Two fixed top-level sections (`## Knowledge domains`, `## Courses`) with `### <name>` subsections only.
- **Not all pages get listed.** Domain section: 4-7 hub pages only (knowledge domain entry points). Course chapter / subchapter meta pages **never appear in `index.md`** — they live in `course-{slug}-00-index.md § Chapters` and `course-{slug}-ch{NN}-00-index.md § Subchapters`.
- **No completion status markers.** No "(완료)", "(진행중)" in index. That info lives in the course meta page body — more token-efficient.
- **Domain inclusion criteria**: subject-tree 의 top-level 중 **kind=concept + kind=entity 페이지 합 ≥ 10 AND 그 중 inbound 최고치 ≥ 10** 인 도메인만 `## Knowledge domains` 에 노출한다. 임계 미달 도메인 (예: 단발 코스 1개에 콘텐츠가 묶이는 domain-b · domain-a · domain-c) 은 `## Courses` 의 drill-down 으로만 접근. 새 코스가 추가돼 임계를 통과하면 lint § 5 가 surface, 사용자 confirm 후 도메인 섹션 추가. 노출돼 있던 도메인이 약화돼 임계 미달이 되면 lint 가 약화 신호로 surface (유지·제거는 사용자 결정). 임계의 정량 기준은 lint § 5 와 동기화 유지.
- **Hub selection criteria**: high inbound link count + answers the domain's starting question. Lint § high-degree neurons surfaces candidates.
- **Courses grouped by source/institution** (Anthropic Academy, your university department, single book, etc.). One course added = one line added to index.
- Target after one quarter of operation: 25-40 lines (도메인 섹션 늘면 비례 증가, 도메인당 약 3 line). Explosion → lint surfaces.
- Page body change → only update the index line if the page is a hub (most pages have no index line).

---

## log.md discipline

`wiki/log.md` is **append-only, coarse-grained audit trail**. Per-page created/updated info is carried by frontmatter — log captures "one work unit done", not every wiki mutation.

When to write a log entry:

| op | unit | note |
|---|---|---|
| `ingest` | raw → wiki page bundle | 1 ingest = 1 entry |
| `capture` | conversation → claim summary | 1 entry |
| `query` | only when answer was filed as page | rumination-only query: skip |
| `lint` | 1 lint run | findings summary |
| `synapse` | 1 page written/updated | decision-shape page |
| `course-start` | new course setup | course meta created |
| `course-chapter` | chapter completion | **N subchapters bundled into 1 entry** |
| `course-finish` | course end | includes archive move |
| `migration` | schema/structure change | non-content op |
| `curate` | 1 qualitative maintenance run | review, repair, sweep, or system-learning summary (details go to `tmp/curate-*` or `exports/*-curate/`) |

Do **not** write log entries for:
- `course-note` (subchapter unit) — frontmatter `created`/`updated` carries this; bundled into `course-chapter` at chapter end.

Format:

```
## [YYYY-MM-DD] <op> | <title>
- what changed (pages touched, domains added, stubs added)
```

Use the prefix exactly so `grep "^## \[" log.md | tail -5` works.

**Aborted operations also get logged.** When a workflow stops mid-flow (secrets flagged, user cancels, extraction fails, schema conflict), append an entry with the same prefix but the change list reads:

```
- aborted: <one-line cause>
```

Preserves audit value; later lint passes spot recurring failure modes.

**Format evolution**: `log.md` stays markdown for Phase 1 (human-readable "work trajectory" priority — even when not viewed in Obsidian). If accumulated audit data balloons to MB scale, append-only data splits to `log.json` / `log.yaml` and `log.md` becomes curated reflection only.

---

## Post-ingest handling — per-subdir matrix

**Archive-as-copy is deliberately absent.** Raw files are source of truth; wiki pages are the distillation. A third archive layer was tried earlier, found redundant, and removed. "Has this been ingested?" is answered by `log.md`, not file location.

Type-specific:

| Subdir | Post-ingest behavior | Reason |
|---|---|---|
| `raw/articles/` | source stays in place | articles/papers stay forever |
| `raw/conversations/` | **delete** the claim summary `YYYY-MM-DD-<slug>.md` after successful ingest | ephemeral staging artifact of `/wiki capture`. The verbatim transcript in `_transcripts/` is the permanent insurance copy and must be kept. |
| `raw/courses/{slug}/` | per-file: no action during subchapter ingests. Wholesale: at `course-finish`, **move** the entire `raw/courses/{slug}/` directory to `raw/courses/_archive/{slug}/` | This is the **only `_archive/` in the project** — it exists because a finished course is a large staging bundle that should visually clear out of the active workspace. |

If the tool environment blocks the required file op (delete for conversations, move for courses), log an `- aborted: <cause>` entry in `log.md` and surface to user instead of claiming completion. `/wiki lint` flags residual staging state as drift.

---

## Output quality contract

Every producer skill (`/wiki ingest`, `/wiki study`, `/wiki course`, `/wiki course backfill`, and any future page-writing workflow) writes **self-contained wiki prose**, not a description of raw material.

The page body must carry the meaning directly. Raw files, PDFs, rendered PNGs, transcript chunks, handwriting scans, and working artifacts are evidence used during writing; they are not the reader-facing object.

This is a producer contract first and a validator rule second. Page-writing skills must prevent violations before `/wiki lint` or `/wiki curate` sees them.

Required:

- Body prose is Korean by default. English technical terms, formulas, model names, course-native headings, quoted titles, and established abbreviations are allowed when they carry precision.
- Generic headings are Korean unless the lecture/source itself uses the English phrase as the conceptual unit.
- Handwriting, slide emphasis, examples, diagrams, and source-specific structure are absorbed into explanatory prose. Do not say that the handwriting, PDF, page, note, or raw source "says" something.
- Raw paths appear only in the trailing `## Source` block. No `raw/` path should appear in the body before `## Source`.
- A page must make sense without opening the raw PDF, note, PNG, transcript, staging folder, or run log.
- Links are load-bearing: nearby prose explains why the linked page matters here.
- Source substance is preserved, but source anchors are not. Preserve the concept, mechanism, example, distinction, and reasoning; do not preserve "page 7", "the note", "this PDF", or production traces.

Forbidden in body prose before `## Source`:

- raw/process voice such as `raw`, `staging`, `source bundle`, `PDF page`, `page range`, `render`, `image-read`, `backfill`, `run-log`, `extraction`.
- Korean source-voice phrasing such as "필기에는", "필기에서", "강의 노트에는", "노트에서는", "원문에서는", "원자료", "자료에서는", "페이지에서는", "이 페이지에서는", "이 자료".
- generic course-page rubric headings such as `Core idea`, `Details`, `Overview`, `Related`, `Maps to`, `Source Staging`, `Practice & Assignments`, unless an explicit non-course template allows them.

After writing or rewriting pages, run the content guard described in `/wiki curate` and fix touched pages immediately. `/wiki lint` can surface deterministic violations later, but producer skills should prevent them first.

---

## External skills — wiki-relevant shortlist

The user's environment may expose many external skills and agents. **Most are code/framework-specific and not relevant to this wiki.** Wiki-relevant shortlist (invoke proactively when situation fits; ignore the rest unless user explicitly asks):

| External | When to use |
|---|---|
| `knowledge-ops` (skill) | General KM moves; complement `/wiki` skills. Check before inventing a workflow. |
| `deep-research` (skill) | Fill identified wiki gaps via web research. Result feeds `/wiki ingest` or `/wiki query --file`. |
| `search-first` (skill) | Search existing pages and web prior art before writing a new wiki page. |
| `documentation-lookup` (skill) | Consult official docs of a tool/library before summarizing. |
| `article-writing` (skill) | Export wiki content as a blog post or long-form piece. |
| `context-budget` (skill) | When the wiki grows past ~50 pages and sessions hit context limits. |
| `planner` (agent) | Non-trivial multi-step wiki tasks (large legacy migration). |
| `conversation-analyzer` (agent) | During `/wiki capture` or `/wiki study` conversation mode — improves claim extraction. |
| `docs-lookup` (agent) | Parallel to `documentation-lookup` skill at agent granularity. |
| `silent-failure-hunter` (agent) | During `/wiki lint` — catches quality issues regex misses. |
| `anthropic-skills:paper-summarizer` | PDF paper → structured summary → ingest. |
| `anthropic-skills:lecture-translator` | YouTube transcript → Korean narrative → ingest. |
| `anthropic-skills:pdf` | OCR/extraction inside `/wiki study` file-mode pre-step or `/wiki course` chapter-start fallback. |

Ground rules:

- **Wiki files are off-limits to external skills.** Only the wiki workflow skills may edit `wiki/*.md`, `wiki/index.md`, `wiki/log.md`, `wiki/_stubs.md`, or move files under `raw/`. If an external skill would write there, stop and tell the user.
- **Chained, not parallel.** External skills *produce* artifacts that get fed into `/wiki study` or `/wiki ingest`. They don't run concurrently with a wiki-writing skill.
- **Cite, don't absorb.** Research agents may fetch the web to fill gaps, but wiki pages still need a `kind=source-record` page for citation — never a naked web claim.
- **Outputs go outside `wiki/`** for export skills (article-writing, slides, docs). Only file the result back when the user explicitly asks.
- **Anything outside this shortlist** should not be invoked for wiki work without user's explicit request. The plugin has TDD/frontend/backend/language agents — those are for code projects.

If a shortlisted skill conflicts with a wiki workflow, the wiki workflow wins — surface the conflict and ask how to reconcile.

---

## Schema evolution

Wiki ontology evolves with content accumulation. Evolution autonomy is **graded by impact cardinality** — the wider the change reaches, the higher the bar for autonomous action.

| Level | Impact scope | LLM behavior |
|---|---|---|
| **A — autonomous** | Single page or 1-2 page additions; reversible by edit | LLM acts during ingest, surfaces in summary. Lint validates post-hoc. |
| **B — propose** | Tree structure (narrower, rename, move); future pages affected; cheap to revert via SKOS altLabel | LLM appends candidate to ontology file + flags in ingest summary. User confirms or reverts in next sweep. |
| **C — user decision** | Trunk schema (top-level domain, enum values, new facet field, deprecation) | LLM never adds. Lint surfaces pressure; user decides. |

**Why graded, not blanket-deny**: a 2026-05 review found that the previous "no speculative additions" rule (well-meant against folksonomy explosion) instead produced thinness — bulk course ingests left general concept pages uncreated, topic discovery skipped at warn-level, and post-hoc Codex remediation needed. The risk inverted. Autonomy A/B closes that gap; autonomy C still guards trunk schema.

Evolution channels:

| Scenario | Level | Action | Page change |
|---|---|---|---|
| New general concept page (e.g. `[[bayes-theorem]]` extracted from a course chapter) | **A** | LLM creates page during ingest with proper frontmatter + wikilink from caller | None to existing |
| New canonical topic (e.g. `posterior-probability`) | **A** | LLM appends to `ontology/topics.md § canonical_topics` + uses on page | None |
| Topic alias addition | **A** | LLM appends to `ontology/topics.md § aliases` when synonymy is obvious (morphology / well-known abbreviation) | None — lint resolves |
| Subject narrower added (e.g. `ml/inference-optimization`) | **B** | LLM appends to `ontology/subject-tree.md § narrower:` + flags in ingest summary | None |
| Subject rename | **B** | LLM proposes canonical change + altLabel; user confirms in next sweep | None — lint resolves alias |
| Subject move (reparent) | **B** | LLM proposes relocate + bidirectional altLabels | None — lint resolves alias |
| New top-level domain | **C** | Lint surfaces pressure; user adds to tree | None |
| Subject deprecation | **C** | User decides; LLM-driven script for page rewrite | **Pages need rewrite** (only case requiring it) |
| New `kind` value | **C** | enum extension after lint surfaces page-shape pain ≥5 pages | None for existing |
| New `form` value | **C** | enum extension after lint surfaces presentation-shape pressure | None for existing |
| New `source-types` value | **C** | enum extension after surface pressure | None |
| New facet field | **C** | discussed in `ARCHITECTURE.md § 7 future considerations` | None |

**Granularity guards on autonomy A** (gate before any autonomous addition):

- **General concept page**: must be reusable concept-level. NOT page-specific (`course-ma101-ch03-binomial`), NOT broad domain (`ml`, `statistics`). Same granularity rule as topics — see `ontology/topics.md § Topic granularity guidance`.
- **Canonical topic**: same granularity gate. LLM must check `ontology/topics.md § Topic granularity guidance` before appending. Reusable concept/technique/pattern level only.
- **Topic alias**: only when synonymy is obvious (`cot ↔ chain-of-thought`, `hitl ↔ human-in-the-loop`). Ambiguous synonyms surface to lint cluster detection (Levenshtein + co-occurrence) for user confirmation, NOT autonomous addition.

**Lint as garbage collector** (post-hoc protection — `/wiki lint` § 3b / § 3c / § 14):

- Autonomously-added topics with <3 page usage after 30 days → surface for review (likely premature or garbage).
- Autonomously-added narrower used in only 1 page → surface as trivial split.
- Autonomously-created general concept pages with 0 inbound links after 30 days → orphan candidate.

Lint runs idempotent; it surfaces, the user decides.

Schema evolution history is distributed across 4 layers: git commit history + `wiki/log.md migration` entries + `ARCHITECTURE.md` long-form rationale + `wiki/decision-*` synapse pages. See `ARCHITECTURE.md § 4.5`.

**Skill promotion.** When the same multi-step manual procedure executes ≥3 times across sessions (visible in `log.md` or reported as recurring), propose formalizing it as a new wiki workflow skill. `/wiki lint` flags candidates. Successful procedures deserve to be codified; one-offs stay one-offs.

**Out-of-wiki failures.** `log.md § aborted` covers wiki operations. Failures *around* wiki work — plugin install, git auth, path issues, Obsidian config, etc. — go to the project's auto-memory `gotchas.md` instead. Read at session start; after a non-trivial failure + fix, append an entry.
