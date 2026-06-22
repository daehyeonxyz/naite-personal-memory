# docs/CONVENTIONS.md — naite operating invariants

These rules apply to **every tree mutation** regardless of which workflow (`/naite grow`, `/naite ask`, `/naite fruit`, `/naite care`) is running. Workflow-specific procedures live in the naite workflow skill directory.

This file is shared by both tool surfaces. Keep it tool-neutral: workflow rules live here, while tool-specific paths and entrypoint wording live in `CLAUDE.md`, `AGENTS.md`, and the mirrored workflow skill directories.

For the *why* (rationale, theoretical basis, schema evolution playbook), see `docs/ARCHITECTURE.md`.
For the *data* (canonical vocabularies), see `.naite/ontology/subject-tree.md` and `.naite/ontology/topics.md`.

---

## Tree anatomy — 단일 매핑 기준

naite vault 하나 = 나무 한 그루. 부위 이름의 단일 기준은 이 표다. 다른 문서는 참조만 하고 재정의하지 않는다.

| 부위 | 자리 | 실체 |
|---|---|---|
| roots 뿌리 | 디렉터리 | `roots/` — 원천 자료 유입. content-immutable |
| tree 본체 | 디렉터리 | `tree/` — LLM 이 쓰는 페이지 전부. flat |
| trunk 줄기 | 특수 파일 | `tree/trunk.md` — 큐레이션 진입점 |
| rings 나이테 | 특수 파일 | `tree/rings.md` — append-only 성장 기록 |
| seeds 씨앗 | 특수 파일 | `tree/seeds.md` — 만들 페이지 후보 |
| leaf 잎 | kind | `kind=concept / entity / source-record / insight / comparison / project / essay / personal` 페이지 (전체 enum: § Ontology) |
| fruit 열매 | kind | `kind=decision` 페이지 — `/naite fruit` 가 맺는다 |
| branch 가지 | 군집 | `course-{slug}-*` 파일명 prefix 하나 = 가지 하나. grow 의 장기 모드 |
| vein 맥 | 링크 | 페이지 간 `[[wikilink]]`. 저장은 wikilink + `.naite/ontology/tree-dependencies.json` |
| forest 숲 | 군집 | 나무들의 집합. vault 가 커지면 독립 나무들의 숲으로 분화 (Phase 2). § Forest layer |

---

## Maintenance model

Tree maintenance has two user-facing modes, both under `/naite care`:

- `/naite care --check` is deterministic guardrail work: schema, broken links, domains cache, archive drift, output-quality regex checks, secrets, binaries, and other machine-checkable hygiene. Report-only.
- `/naite care` is qualitative judgement and repair: page/branch review, direct content cleanup, large-scope sweeps, and recurring-rule learning that should strengthen producer contracts or care-check checks.

---

## Naming

- Files: `lowercase-kebab-case.md`. No spaces, no capitals. One concept per file.
- Wikilinks: `[[page-slug]]` or `[[page-slug|Display Text]]`. Plain `[[...]]` only — no typed relations (relations live in prose; see § Soft ontology).
- Aliases: list at top of page under `## Also known as` heading. `trunk.md` lists only the canonical slug.
- **Migration 보존본 예외:** `/naite start` 가 가져온 메모리 export 의 영구 보존본은 `roots/conversations/_transcripts/migration-<service>.md` 로 **날짜 prefix 없이 서비스별 stable 이름**을 쓴다. 재import 시 같은 파일을 갱신하기 위한 의도된 예외다 (`<service>` = `chatgpt`/`gemini`/`claude`). 일반 transcript 의 `YYYY-MM-DD-<slug>.md` 규칙과 다르다.

---

## Personal tree scope — what belongs

This tree is about **what the user knows**, not a generic encyclopedia. Beyond plain study concepts, pages legitimately cover:

- **Projects** — products, repos, research efforts the user runs.
- **Decisions** — considered choices with tradeoffs, often tied to a project.
- **Insights** — realized connections or claims the user endorses.
- **Questions** — open threads the user is thinking about but hasn't closed.
- **People / orgs / tools** — `kind=entity`.

These map to the `kind` facet enum (§ Ontology). The `kind` facet is *page essence* (concept/entity/source-record/project/decision/insight/comparison/essay/personal); `form` is *presentation shape* (prose/index). `domains` is a derived cache, not a facet. Do not mint new `kind` / `form` / `source-types` values without care-check-surfaced pressure + user decision.

`comparison` pages (A-vs-B, e.g. `[[k-means-vs-dbscan]]`) → `kind=comparison`. Query-derived pages absorb provenance into prose, no separate facet.

---

## Ontology — quick reference

기계 가독 facet 정의는 `.naite/ontology/facets.json` 하나가 단일 소스다 (enum 값, 단일/복수, 검색 타입). lint 검증기와 naite-app 필터 UI 가 같은 파일을 읽는다. enum 변경은 여전히 C-level (사용자 결정) 이다.

Every page has these frontmatter facets:

```yaml
---
kind: concept | entity | source-record |          # page essence (immutable)
      project | decision | insight | comparison |
      essay | personal
form: prose | index                               # presentation shape
topics: [<canonical-topic>, ...]                  # folksonomy. 0-5 per page. Empty array OK.
subject: [<skos-path>]                            # SKOS-lite path. Multi-value for cross-domain.
source-types: [course | conversation | paper |    # 8-enum, always a list
               article | docs | book |
               essay | external]
domains: [<top-level>]                            # CACHED — care-check derives from subject top-level
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**Schema note** — an earlier `type` / `role` / `source-type` (singular) schema was replaced by `kind` / `form` / `source-types` (list). Legacy schema in new pages is an error (drift signal); historical references to old facet names in decision pages' "Before/As-Was" sections are preserved as documentation.

**Field rules:**

- `kind` enum (9 values): `concept` (reusable concept/method/technique/pattern), `entity` (person/org/tool/platform/model/product), `source-record` (single source unit recorded in the tree — course top/chapter/subchapter, paper note, book note, article note), `project` (user's project tracker), `decision` (synapse / decision record), `insight` (extracted/synthesized observation), `comparison` (A-vs-B page where the comparison itself is the subject), `essay` (사용자가 직접 작성한 에세이 또는 학문 도메인 밖 개인 글쓰기. `source-types: [essay]` 와 짝을 이루며 `subject: [personal]` 을 사용한다. `source-record` 는 외부 source 의 study note 이고, `essay` 는 사용자 본인이 직접 쓴 글이다), `personal` (사용자 본인의 신원, 학력, 산출물 목차, 진로 hub 등 self-reference 메타 페이지. `subject: [personal]` 과 짝을 이루며 source-types 는 보통 [conversation, external]. essay 가 본인이 쓴 학문 외 글이라면 personal 은 본인에 대한 메타-기록 페이지다. C-level 신설로 사용자 승인 후 추가된 enum 사례). `question` is **not** a kind — earlier `role=question` deprecated in 2026-05-18 (no corpus use case; future C-level decision if needed).
- `form` enum (2 values): `prose` (body is flowing text — explanation, decision record, insight, etc.), `index` (body is a list/navigation hub of wikilinks).
- `topics`: 0-5 per page. Canonical list (`.naite/ontology/topics.md`) preferred. Uncanonicalized topic → care-check warns (does not block — folksonomy philosophy). Empty array OK (e.g. `kind=entity`). Do not force topics. Topics are **re-usable concept/technique level** — not broad domain names.
- `subject`: SKOS-lite path notation (`parent/child[/grandchild]`, slash-separated). Single path is default; multi only for genuine cross-domain (`[a/x, b/y]`). Canonical tree: `.naite/ontology/subject-tree.md`. **Course / collection / institution / source names are NOT subjects** — `course`, `course-{slug}`, `anthropic-academy`, `ode`, `laplace-transform` are page slugs/entities, not subject paths. Course membership is carried by the `course-{slug}-*` filename prefix.
- `source-types` (always list, 8 values): `course` (academic/online courses), `paper` (peer-reviewed academic), `article` (informal: blog / news / X thread / Substack), `docs` (official docs: Anthropic / OpenAI / library docs), `book` (book), `conversation` (user dialogue capture), `essay` (self-authored essay/long-form), `external` (fallback). A page can be informed by multiple sources — `source-types: [course, paper]` is valid. `legacy` is **not** a value — it's an import channel; staged legacy notes ingest with the source-types matching their content nature. Detail: `docs/ARCHITECTURE.md § 7`.
- `domains` (CACHED, NOT a facet): top-level path component of `subject`. **care-check auto-derives** (`.naite/scripts/lint-ontology.py --refresh-domains`); never hand-write. Idempotent on schema change.

`trunk.md` and `rings.md` have no frontmatter (special files). Additional facet fields (`confidence`, `status`, `depends-on`, `contradicts`, `source-count`, `as-of`, etc.) are added only after care-check surfaces accumulated pressure → user decision. No arbitrary additions.

For the why behind each facet: `docs/ARCHITECTURE.md § 3`. Schema evolution: § Schema evolution below.

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

When reading these idioms during `/naite ask`, synthesize as if they were typed edges. When writing new pages, prefer these exact phrasings to keep the vocabulary compounding.

---

## Decision thread shape

A decision page has **`kind=decision`** (occasionally embedded as decision-shape content within `kind=concept`/`entity`/`source-record` pages — both are valid synapse forms). Its `subject` is the actual content path (canonical tree: `.naite/ontology/subject-tree.md`). Cross-domain decisions get multi-subject. **Do not invent meta subject paths** like `dmu/`, `failure-*/`, `synapse/` — categorizing a synapse defeats its purpose.

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

This is a **reference structure, not a strict template**. `/naite fruit` walks the user through it as dialogue, not a form.

A decision thread can also live as a short prose paragraph **embedded in another concept page** ("In my projects" or similar section). Both forms are equally valid synapses. A standalone page is just a paragraph that grew large enough to deserve its own slug.

When writing a synapse and a referenced concept is missing from the tree, propose a stub in `seeds.md`. The synapse layer creates pressure to fill graph gaps — that is one of its core values.

**Most-cross-linked concepts are emergent decision-critical neurons.** `/naite care --check` surfaces high-degree pages — they are the implicit anchors of the user's reasoning. No frontmatter tag needed; falls out of the link graph.

**Career framing is deliberately outside this schema.** When career-relevant evidence is needed, it is extracted on demand by `grep`-ing synapse prose across pages — not by a pre-built index.

---

## trunk.md discipline

`tree/trunk.md` is a **curated entrypoint and drill-down starting point**, not an enumerator of every page. It exposes domain hubs and branch meta pages; everything else is discovered by drill-down through those.

Structure (2 fixed top-level sections):

```
## Knowledge domains

### {domain-name}
한 줄 설명 (이 도메인이 무엇을 다루는지).
주요: [[hub-1]], [[hub-2]], [[hub-3]]   (4-7 pages, entry-point role only)

## Branches

### {institution / source}
- [[course-{slug}-00-index]] — 한 줄 설명
- ...
```

Rules:

- No `## Domain:` prefix. Two fixed top-level sections (`## Knowledge domains`, `## Branches`) with `### <name>` subsections only.
- **Not all pages get listed.** Domain section: 4-7 hub pages only (knowledge domain entry points). Branch chapter / subchapter meta pages **never appear in `trunk.md`** — they live in `course-{slug}-00-index.md § Chapters` and `course-{slug}-ch{NN}-00-index.md § Subchapters`.
- **No completion status markers.** No "(완료)", "(진행중)" in trunk. That info lives in the branch meta page body — more token-efficient.
- **Domain inclusion criteria**: subject-tree 의 top-level 중 **kind=concept + kind=entity 페이지 합 ≥ 10 AND 그 중 inbound 최고치 ≥ 10** 인 도메인만 `## Knowledge domains` 에 노출한다. 임계 미달 도메인 (예: 단발 코스 1개에만 콘텐츠가 묶이는 소수 도메인) 은 `## Branches` 의 drill-down 으로만 접근한다. 새 가지가 추가돼 임계를 통과하면 care-check § 5 가 그 사실을 surface 하고, 사용자가 confirm 한 뒤 도메인 섹션을 추가한다. 반대로 노출돼 있던 도메인이 약해져 임계에 못 미치면 care-check 가 약화 신호로 surface 한다 (유지할지 제거할지는 사용자가 결정한다). 임계의 정량 기준은 care-check § 5 와 동기화를 유지한다.
- **Hub selection criteria**: high inbound link count + answers the domain's starting question. care-check § high-degree neurons surfaces candidates.
- **Branches grouped by source/institution** (Anthropic Academy, your university department, single book, etc.). One branch added = one line added to trunk.
- Target after one quarter of operation: 25-40 lines (도메인 섹션 늘면 비례 증가, 도메인당 약 3 line). Explosion → care-check surfaces.
- Page body change → only update the trunk line if the page is a hub (most pages have no trunk line).

---

## rings.md discipline

`tree/rings.md` is **append-only, coarse-grained audit trail**. Per-page created/updated info is carried by frontmatter — rings captures "one work unit done", not every tree mutation.

When to write a rings entry:

| op | unit | note |
|---|---|---|
| `grow` | roots → tree page bundle | 1 grow = 1 entry |
| `ask-filed` | only when answer was filed as page | rumination-only ask: skip |
| `fruit` | 1 page written/updated | decision-shape page |
| `care-check` | 1 care-check run | findings summary |
| `care` | 1 qualitative maintenance run | review, repair, sweep, or system-learning summary (details go to `tmp/care-*` or `.naite/reports/*-care/`) |
| `branch-start` | new branch setup | branch meta created |
| `branch-chapter` | chapter completion | **N subchapters bundled into 1 entry** |
| `branch-finish` | branch end | includes archive move |
| `migration` | schema/structure change | non-content op |

Do **not** write rings entries for:
- `branch-note` (subchapter unit) — frontmatter `created`/`updated` carries this; bundled into `branch-chapter` at chapter end.

Format:

```
## [YYYY-MM-DD] <op> | <title>
- what changed (pages touched, domains added, seeds added)
```

Use the prefix exactly so `grep "^## \[" rings.md | tail -5` works.

**Aborted operations also get logged.** When a workflow stops mid-flow (secrets flagged, user cancels, extraction fails, schema conflict), append an entry with the same prefix but the change list reads:

```
- aborted: <one-line cause>
```

Preserves audit value; later care-check passes spot recurring failure modes.

**Format evolution**: `rings.md` stays markdown for Phase 1 (human-readable "work trajectory" priority — even when not viewed in Obsidian). If accumulated audit data balloons to MB scale, append-only data splits to `rings.json` / `rings.yaml` and `rings.md` becomes curated reflection only.

---

## Post-grow handling — per-subdir matrix

**Archive-as-copy is deliberately absent.** Raw files are source of truth; tree pages are the distillation. A third archive layer was tried earlier, found redundant, and removed. "Has this been grown into the tree?" is answered by `rings.md`, not file location.

Type-specific:

| Subdir | Post-grow behavior | Reason |
|---|---|---|
| `roots/articles/` | source stays in place | articles/papers stay forever |
| `roots/conversations/` | **delete** the claim summary `YYYY-MM-DD-<slug>.md` after successful grow | ephemeral staging artifact of the grow capture step. The verbatim transcript in `_transcripts/` is the permanent insurance copy and must be kept. |
| `roots/courses/{slug}/` | per-file: no action during subchapter ingests. Wholesale: at `branch-finish`, **move** the entire `roots/courses/{slug}/` directory to `roots/courses/_archive/{slug}/` | This is the **only `_archive/` in the project** — it exists because a finished branch is a large staging bundle that should visually clear out of the active workspace. |

If the tool environment blocks the required file op (delete for conversations, move for courses), log an `- aborted: <cause>` entry in `rings.md` and surface to user instead of claiming completion. `/naite care --check` flags residual staging state as drift.

---

## Output quality contract

Every producer workflow (`/naite grow`, `/naite grow` branch mode, `/naite grow backfill {slug}`, and any future page-writing workflow) writes **self-contained tree prose**, not a description of raw material.

The page body must carry the meaning directly. Raw files, PDFs, rendered PNGs, transcript chunks, handwriting scans, and working artifacts are evidence used during writing; they are not the reader-facing object.

This is a producer contract first and a validator rule second. Page-writing skills must prevent violations before `/naite care --check` or `/naite care` sees them.

Required:

- Body prose is Korean by default. English technical terms, formulas, model names, course-native headings, quoted titles, and established abbreviations are allowed when they carry precision.
- Generic headings are Korean unless the lecture/source itself uses the English phrase as the conceptual unit.
- Handwriting, slide emphasis, examples, diagrams, and source-specific structure are absorbed into explanatory prose. Do not say that the handwriting, PDF, page, note, or raw source "says" something.
- Raw paths appear only in the trailing `## Source` block. No `roots/` path should appear in the body before `## Source`.
- A page must make sense without opening the raw PDF, note, PNG, transcript, staging folder, or run log.
- Links are load-bearing: nearby prose explains why the linked page matters here.
- Source substance is preserved, but source anchors are not. Preserve the concept, mechanism, example, distinction, and reasoning; do not preserve "page 7", "the note", "this PDF", or production traces.
- Source-fidelity ceiling (`kind=source-record`): 공식, 정의, 정리, 성립 조건, 수치는 source 검토 없이 재서술하거나 단순화하지 않는다. 표현, 문단 흐름, H 계층, lead, 링크 설명은 개선하되 내용의 정확성은 보존한다. 재서술이 원자료의 주장과 어긋날 위험이 있으면 고치지 말고 `source-risk` 로 분류해 보류한다. fidelity 가 재서술보다 우선이다.

Forbidden in body prose before `## Source`:

- raw/process voice such as `raw`, `staging`, `source bundle`, `PDF page`, `page range`, `render`, `image-read`, `backfill`, `run-log`, `extraction`.
- Korean source-voice phrasing such as "필기에는", "필기에서", "강의 노트에는", "노트에서는", "원문에서는", "원자료", "자료에서는", "페이지에서는", "이 페이지에서는", "이 자료".
- generic course-page rubric headings such as `Core idea`, `Details`, `Overview`, `Related`, `Maps to`, `Source Staging`, `Practice & Assignments`, unless an explicit non-course template allows them.

**`kind=essay` / `kind=personal` 예외**: 사용자 본인이 직접 쓴 글 또는 자기-기록 메타 페이지다. 재서술 (source 흡수, 문체 교정, 서술 밀도 강제) 대상에서 제외하고 voice 를 보존한다. raw/process-voice 금지와 self-contained 원칙은 동일 적용하되, source 흡수와 prose 밀도 기준은 적용하지 않는다.

After writing or rewriting pages, run the content guard described in `/naite care` and fix touched pages immediately. `/naite care --check` can surface deterministic violations later, but producer skills should prevent them first.

Leaf-page depth rules (thin-leaf demotion, lint thresholds) live in `docs/QUALITY.md § Leaf-page depth rubric`.

---

## External skills — tree-relevant kinds

The user's environment may expose many external skills and agents. **Most are code/framework-specific and not relevant to this tree.** The table below lists *kinds* of external skills that pair well with tree work — actual names and availability vary per environment, so verify a skill actually exists in the current session before invoking it. Ignore the rest unless the user explicitly asks.

| External (kind) | When to use |
|---|---|
| Knowledge-management skill | General KM moves; complement `/naite` skills. Check before inventing a workflow. |
| Web deep-research skill | Fill identified tree gaps via web research. Result feeds `/naite grow` or `/naite ask --file`. |
| Search-first skill | Search existing pages and web prior art before writing a new tree page. |
| Official-docs lookup skill/agent | Consult official docs of a tool/library before summarizing. |
| Long-form writing/export skill | Export tree content as a blog post or long-form piece. |
| Planning agent | Non-trivial multi-step tree tasks (large legacy migration). |
| Conversation-analysis agent | During the grow capture step or grow conversation mode — improves claim extraction. |
| Quality-review agent | During `/naite care --check` — catches quality issues regex misses. |
| PDF/OCR extraction skill | OCR/extraction inside `/naite grow` file-mode pre-step or branch chapter-start fallback. |
| Paper-summarizer / transcript-translator skill | Paper PDF or lecture transcript → structured summary → grow. |

Ground rules:

- **Tree files are off-limits to external skills.** Only the naite workflow skills may edit `tree/*.md`, `tree/trunk.md`, `tree/rings.md`, `tree/seeds.md`, or move files under `roots/`. If an external skill would write there, stop and tell the user.
- **Chained, not parallel.** External skills *produce* artifacts that get fed into `/naite grow`. They don't run concurrently with a tree-writing skill.
- **Cite, don't absorb.** Research agents may fetch the web to fill gaps, but tree pages still need a `kind=source-record` page for citation — never a naked web claim.
- **Outputs go outside `tree/`** for export skills (article-writing, slides, docs). Only file the result back when the user explicitly asks.
- **Anything outside these kinds** should not be invoked for tree work without user's explicit request. TDD/frontend/backend/language agents are for code projects.

If an external skill conflicts with a naite workflow, the naite workflow wins — surface the conflict and ask how to reconcile.

---

## Schema evolution

Tree ontology evolves with content accumulation. Evolution autonomy is **graded by impact cardinality** — the wider the change reaches, the higher the bar for autonomous action.

| Level | Impact scope | LLM behavior |
|---|---|---|
| **A — autonomous** | Single page or 1-2 page additions; reversible by edit | LLM acts during grow, surfaces in summary. care-check validates post-hoc. |
| **B — propose** | Tree structure (narrower, rename, move); future pages affected; cheap to revert via SKOS altLabel | LLM appends candidate to ontology file + flags in grow summary. User confirms or reverts in next sweep. |
| **C — user decision** | Trunk schema (top-level domain, enum values, new facet field, deprecation) | LLM never adds. care-check surfaces pressure; user decides. |

**Why graded, not blanket-deny**: a 2026-05 review found that the previous "no speculative additions" rule (well-meant against folksonomy explosion) instead produced thinness — bulk course ingests left general concept pages uncreated, topic discovery skipped at warn-level, and post-hoc Codex remediation needed. The risk inverted. Autonomy A/B closes that gap; autonomy C still guards trunk schema.

Evolution channels:

| Scenario | Level | Action | Page change |
|---|---|---|---|
| New general concept page (e.g. `[[bayes-theorem]]` extracted from a course chapter) | **A** | LLM creates page during grow with proper frontmatter + wikilink from caller | None to existing |
| New canonical topic (e.g. `posterior-probability`) | **A** | LLM appends to `.naite/ontology/topics.md § canonical_topics` + uses on page | None |
| Topic alias addition | **A** | LLM appends to `.naite/ontology/topics.md § aliases` when synonymy is obvious (morphology / well-known abbreviation) | None — care-check resolves |
| Subject narrower added (e.g. `ml/inference-optimization`) | **B** | LLM appends to `.naite/ontology/subject-tree.md § narrower:` + flags in grow summary | None |
| Subject rename | **B** | LLM proposes canonical change + altLabel; user confirms in next sweep | None — care-check resolves alias |
| Subject move (reparent) | **B** | LLM proposes relocate + bidirectional altLabels | None — care-check resolves alias |
| New top-level domain | **C** | care-check surfaces pressure; user adds to tree | None |
| Subject deprecation | **C** | User decides; LLM-driven script for page rewrite | **Pages need rewrite** (only case requiring it) |
| New `kind` value | **C** | enum extension after care-check surfaces page-shape pain ≥5 pages | None for existing |
| New `form` value | **C** | enum extension after care-check surfaces presentation-shape pressure | None for existing |
| New `source-types` value | **C** | enum extension after surface pressure | None |
| New facet field | **C** | discussed in `docs/ARCHITECTURE.md § 7 future considerations` | None |

**Granularity guards on autonomy A** (gate before any autonomous addition):

- **General concept page**: must be reusable concept-level. NOT page-specific (`course-ma101-ch03-binomial`), NOT broad domain (`ml`, `statistics`). Same granularity rule as topics — see `.naite/ontology/topics.md § Topic granularity guidance`.
- **Canonical topic**: same granularity gate. LLM must check `.naite/ontology/topics.md § Topic granularity guidance` before appending. Reusable concept/technique/pattern level only.
- **Topic alias**: only when synonymy is obvious (`cot ↔ chain-of-thought`, `hitl ↔ human-in-the-loop`). Ambiguous synonyms surface to care-check cluster detection (Levenshtein + co-occurrence) for user confirmation, NOT autonomous addition.

**care-check as garbage collector** (post-hoc protection — `/naite care --check` § 3b / § 3c / § 14):

- Autonomously-added topics with <3 page usage after 30 days → surface for review (likely premature or garbage).
- Autonomously-added narrower used in only 1 page → surface as trivial split.
- Autonomously-created general concept pages with 0 inbound links after 30 days → orphan candidate.

care-check runs idempotent; it surfaces, the user decides.

Schema evolution history is distributed across 4 layers: git commit history + `tree/rings.md migration` entries + `docs/ARCHITECTURE.md` long-form rationale + `tree/decision-*` synapse pages. See `docs/ARCHITECTURE.md § 4.5`.

**External contributors — schema autonomy mapping.** 위 A/B/C 등급은 내부 LLM 동작 기준입니다. 외부 기여자(PR을 여는 사람)에게는 동일 등급이 아래와 같이 적용됩니다.

- **A (autonomous)**: 문서 오타 수정, 스크립트 버그 수정, 명백한 alias 추가 등 단일 파일 범위의 변경은 PR로 직접 제출합니다. 메인테이너가 리뷰 후 머지합니다.
- **B (propose)**: subject narrower 추가, subject rename/reparent 등 온톨로지 구조에 영향을 주는 변경은 PR에 포함하되, 해당 ontology 파일에 `# PROPOSED` 주석으로 후보를 표시합니다. 메인테이너가 confirm 또는 revert합니다.
- **C (user decision)**: 새 `kind`/`form`/`source-types` enum 값, 새 facet 필드, 새 top-level domain, subject deprecation은 **PR에서 직접 추가할 수 없습니다.** 내부 기준의 'user decision'에 해당하는 C 등급은, 외부 기여자에게는 메인테이너가 소유자 결정을 대신 내려 주는 절차로 바뀝니다. 그래서 외부 기여자는 PR로 `.naite/ontology/facets.json` 을 직접 편집하지 않습니다 (core enum 변경은 C-level 메인테이너 결정이고, user kind 선언은 vault 소유자의 행위라서 공유 하네스 repo의 PR 범위에 들어가지 않습니다). C-level 변경을 제안하려면 `.github/ISSUE_TEMPLATE/schema-change.md` 양식으로 issue를 여세요.

**Skill promotion.** When the same multi-step manual procedure executes ≥3 times across sessions (visible in `rings.md` or reported as recurring), propose formalizing it as a new naite workflow skill. `/naite care --check` flags candidates. Successful procedures deserve to be codified; one-offs stay one-offs.

**Out-of-tree failures.** `rings.md § aborted` covers tree operations. Failures *around* tree work — plugin install, git auth, path issues, Obsidian config, etc. — go to the project's auto-memory `gotchas.md` instead. Read at session start; after a non-trivial failure + fix, append an entry.

---

## Forest layer (vault → 숲)

한 vault 는 기본적으로 **한 그루 나무**다 (Phase 1). vault 가 커지면서 어떤 가지가 나머지와 **동일한 관계로 더는 정의되지 않을 때**, 그 vault 는 독립된 나무들의 **숲**으로 분화할 수 있다 (Phase 2). 설계 근거: `docs/ARCHITECTURE.md § 9`.

**어휘 (naming)**: 시스템·방법은 **naite**, 단위 (vault) 는 **나무 (tree)**, 전체 (나무들의 집합) 는 **숲 (forest)** 이다. 1차 이름은 이 세 단어로 통일한다.

**분화 기준은 크기가 아니라 의미다.** 페이지가 늘었다고 분화하는 것이 아니라, 한 군집이 나머지와 분리된 사상 공간을 이룰 때 분화한다. 이 신호는 군집 modularity·conductance 로 정량 보조 측정을 하되, 최종 cut 은 **"한 나무가 에이전트와 사용자에게 하나의 작업 맥락 (사상 공간) 으로 쓸모 있는가"** 라는 효용으로 정한다. 수치는 판관이 아니라 증거다.

**나무 소속은 과목·도메인 라벨이 아니라 개념 계보로 정한다.** 한 페이지는 자기 링크 이웃이 실제로 모이는 나무에 속한다. 한 과목에서 온 두 페이지라도 개념 계보가 다르면 다른 나무로 갈 수 있다 (예: 한쪽은 ai 계보, 다른 쪽은 statistics 계보). `forest-config.json` 이 도메인→나무 seed 를 주고, label propagation 이 최종 배정을 한다.

**걸침 개념 (boundary-straddling) 3 정책** — 한 페이지가 여러 나무에 걸칠 때:

- **flip (과목 오라벨)**: 개념 계보가 과목 라벨과 또렷이 다름 → 계보 나무로 재배정.
- **bridge (정당한 걸침, low margin)**: 두 계보에 정당하게 걸침 → **primary 나무에 거주, secondary 는 inter-tree wikilink 로 표현. 복제하지 않는다.**
- **scatter (계보 미성숙)**: 링크 이웃이 한 곳으로 안 모임 → 그 계보가 아직 콘텐츠로 안 자란 신호. 데이터 대신 **사용자의 개념 판단으로 나무를 미리 심는다** (창발 전 사상 공간).

**나무 사이 결합은 느슨하다.** `forest-manifest.json` 의 `inter_tree_edges` 가 메인 에이전트의 라우팅 표면이다. 시냅스 idiom (decided-over/trade-off 등) 은 대부분 나무 내부이므로, inter-tree 연결은 기존 링크에서 공짜로 창발하지 않고 **명시적으로** 관리한다.

**자율 등급: 분화·병합·재배정은 C급** (vault 구조 변경) 이다. LLM 은 `/naite care --check § Forest health` 로 압력만 surface 하고, 분할·병합·재배정은 사용자가 결정한다. 자동 분화 금지.

**산출물·도구** (모두 `.naite/`):

- `.naite/forest/forest-config.json` — vault-specific 도메인→나무 grouping (seed). 없으면 도메인=나무 identity 로 동작한다. 형식 예시는 `.naite/forest/forest-config.example.json`.
- `.naite/ontology/forest-manifest.json` — 개념 계보 배정 결과 (생성물, `forest-assign.py`).
- `.naite/forest/dashboard.md` — 나이테 forest 대시보드 (생성물, `forest-dashboard.py`).
- 도구: `forest-communities.py` (분화 신호 S1), `forest-assign.py` (계보 배정+걸침 개념), `forest-dashboard.py` (나이테), `forest-retrieval-experiment.py` (숲 vs vault 효용 측정). 의존성: `.naite/scripts/requirements.txt`.

**상태: 그림자 단계.** 물리 마이그레이션 전까지 forest 는 평평한 `tree/` 위에 manifest 를 투영해 운영한다 (파일 이동 0). 숲의 핵심 효용은 retrieval 정밀도가 아니라 **에이전트 맥락 범위 한정**이다. **Phase 1 (단일 나무) 에서는 이 layer 가 잠들어 있다.** 빈 vault 나 작은 vault 에서는 forest 도구가 분화 후보를 거의 또는 전혀 잡지 않는 것이 정상이다.

---

## Instruction surfaces

naite 의 지침은 안정도(변하는 빈도)가 다른 표면으로 나뉜다. 안정한 것일수록 위에, 휘발적인 것일수록 아래에 둔다 (안정 → 휘발 순서의 3단 조립이다).

| 표면 | 역할 | 누가 편집 | 추적 |
|---|---|---|---|
| `CLAUDE.md` / `AGENTS.md` | bootloader: 라우팅·안전·포인터 | LLM (정본 `CLAUDE.md`) | tracked, 미러됨 |
| `SOUL.md` | 에이전트 정체성·응답 스타일·일하는 자세 | LLM + 사용자 | tracked, shared (미러 안 함) |
| `USER.md` | 사용자 응답 선호 + `[[personal-profile]]` 포인터 | 사용자 주도, LLM 보조 | gitignore (양식 `.naite/templates/USER.md`) |
| `MEMORY.md` | 진행 중 작업·운영 사실 통합 인덱스 | LLM curate, 사용자 confirm | gitignore (양식 `.naite/templates/MEMORY.md`) |
| `tree/personal-profile.md` | 신원·이력 (PII), 그래프 참여 | LLM (tree 규약, `kind=personal`) | tree 콘텐츠 |

**USER.md vs personal-profile.md.** USER.md 는 "에이전트가 사용자를 어떻게 대할지 (선호·톤·작업 방식)" 를 담는 시스템 표면이다. personal-profile.md 는 "사용자가 누구인지 (신원·이력)" 를 담는 그래프 콘텐츠다. PII 는 USER.md 에 복제하지 않고 `[[personal-profile]]` 로 가리킨다.

**MEMORY.md 규율.** 메모리는 선언적 사실로 적고 출처·날짜를 단다. 낡으면 (일주일 기준) 지운다. 나무는 큐레이션된 장기 지식이고 MEMORY.md 는 휘발적 운영 기억이다. 오래 남길 지식은 `/naite grow` 로 나무에 새긴다.

**로딩.** claude / codex 는 이 표면들을 자동 로드하지 않는다. bootloader (`CLAUDE.md` § Instruction surfaces) 가 세션 시작 시 읽도록 지시한다. `SOUL.md` 는 항상, `USER.md` / `MEMORY.md` 는 있으면 읽는다.

**보이는 정체성 vs 런타임 정체성.** vault 안에서 실행되는 동안 사용자에게 보이는 정체성은 "사용자의 나이테를 관리하는 에이전트" 이고, 실제 실행 런타임 (Claude Code / Codex / 기타 모델) 은 구현 세부다. bootloader (`CLAUDE.md § 기본 정체성과 라우팅`) 가 모든 모델이 첫 응답부터 지킬 최소 default-voice 계약 (보이는 문장은 "저는 [호칭]님의 나이테를 관리하는 에이전트입니다", 호칭 모르면 "사용자님") 을 박고, 정본 persona 는 `SOUL.md § 보이는 정체성과 런타임` 에 둔다. 정체성·말투·선호·라우팅 질문은 `/naite ask` 로 보내지 않고 이 default voice 로 답하며, `/naite ask` 는 tree 내용의 조회나 추론이 필요할 때만 켠다.

**미러 정책.** SOUL / USER / MEMORY 는 shared 단일 파일이다 (docs/ 처럼 양 도구가 같은 파일을 읽는다). `CLAUDE.md`↔`AGENTS.md` 와 `.claude/skills`↔`.agents/skills` 만 `sync-agents` 로 미러한다. 새 표면 파일명에 도구 토큰 ("Claude" 등) 이 없어 sync 치환에 영향받지 않는다.

---

## Obsidian co-editing — operational gotcha

The user keeps Obsidian open on the repo root for graph view and reading. Editing is still the agent's job. Two failure modes to watch:

1. **Editor buffer race**: Obsidian holding a file open in its UI buffer can overwrite agent-committed working-tree changes via auto-save when its buffer is stale. HEAD is safe; only the working tree is affected.
   - **Defense**: `.git/hooks/post-commit` (per-clone, not tracked) auto-pushes `main` to origin immediately after every commit. Origin becomes the canonical recovery source. Reinstall by copying from another clone's `.git/hooks/post-commit`.
   - **Recovery**: `git checkout HEAD -- <file>` (commit not pushed) or `git checkout origin/main -- <file>` (pushed and Obsidian reverted afterward). Then re-apply pending working-tree changes.
   - **Agent rule**: before staging an edit, run `git diff HEAD -- <target>`. If unexpected modifications appear that you did not make, surface to the user and restore from HEAD before proceeding.
2. **Multi-file edit runs**: before `/naite grow` on a directory or a branch-mode chapter ingest, suggest the user pause Obsidian editing — not required, just reduces conflict risk.
