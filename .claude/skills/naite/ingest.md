# ingest — grow internal module

사용자 노출 명령이 아니다. /naite grow 가 위임하는 내부 모듈이다.

Pull a raw source into the tree. Two modes share one workflow shape.

## Modes

- **Default** `<path>` — `<path>` is a file or a directory under `roots/` (delegated by grow).
- **Legacy** `--legacy <path>` — `<path>` is an Obsidian Vault note (in `roots/legacy/` or an absolute Vault path). Adds wikilink translation before the default flow.

If `<path>` is a directory, process each file inside **one at a time** with the full workflow below (not batched silently). Between files, give the user a chance to stop.

## Context routing and role split

Before reading a source, load `CONTEXT.md` and follow its context admission order. Use `ontology/tree-manifest.json` as the agent fast path for page lookup, while still reading `tree/trunk.md` for curated human entry points.

For long sources, multi-file sources, directories, or any source likely to push the workflow contract out of attention, split the work into three roles:

1. **Reader**: reads the raw source and produces a compact extraction chunk. The Reader does not edit `tree/`, `ontology/`, or `roots/`.
2. **Writer**: reads `CONVENTIONS.md`, this workflow, generated maps, ontology files, and the Reader chunk. The Writer creates or updates tree pages.
3. **Verifier**: checks touched pages, rebuilds generated maps, and surfaces inbound semantic dependents from `ontology/tree-dependencies.json`.

Use physical subagents when the active tool surface supports them and the user has authorized delegation. Otherwise keep the same roles as explicit sequential phases in one session.

## Workflow (every file)

### 1. Pre-flight

- Read `CONTEXT.md`.
- If `ontology/tree-manifest.json` is missing or stale for the current task, run `python scripts/build-tree-manifest.py`.
- Read `ontology/tree-manifest.json` and use it to narrow candidate existing pages before loading full page bodies.
- Read `ontology/tree-dependencies.json` before editing an existing page when the change could affect pages that depend on it. If the file is missing, run `python scripts/build-tree-dependencies.py`.
- Read `tree/trunk.md` in full so you know which **knowledge domains** exist (`## Knowledge domains` section) and which **course meta pages** exist (`## Courses`). Note: trunk is curated, not exhaustive — `tree/*.md` glob is the truth for slugs.
- Read `tree/seeds.md` — a matching stub means a page is expected and this source may fulfill it.
- Read the last ~20 lines of `tree/rings.md` for recent context (what was grown, any pending threads).

### 2. Read the source

- Read the file. If it's longer than ~2,000 lines, read in slices.
- For images referenced in the source (markdown image syntax), Read them with the Read tool when their content matters for extraction.

### 3. (Legacy mode only) Wikilink translation

Before writing anything, do the link pass:

1. Find every `[[target]]` and `[[target|display]]` in the source.
2. For each target, resolve by **basename or display text**, not the embedded path. Rationale: the Obsidian Vault has pre-existing link rot (e.g. `K-Means.md` encodes `1_Knowledge/Machine Learning/...` but the folder is `1_Knowledge/AI-ML/...`). Trusting the path will silently drop references.
3. Classify each link:
   - **resolved** — target exists as a `tree/` page or matches an existing slug when kebab-cased.
   - **ambiguous** — multiple candidate pages (e.g. two pages named `attention` and `attention-mechanism`).
   - **missing** — no page exists under any name.
4. Present the classified list to the user as a **translation report** before proceeding. Example format:

   ```
   Translation report for sigmoid.md:
   resolved  : softmax          → tree/softmax.md
   resolved  : activation       → tree/activation-function.md (slug differs)
   ambiguous : attention        → attention | attention-mechanism (which?)
   missing   : universal-approximation-theorem
   ```
5. On user confirmation:
   - Resolved links: rewrite to the canonical slug (e.g. `[[activation-function|activation]]`).
   - Ambiguous: ask the user to pick.
   - Missing: keep the link with the kebab-cased target, and append an entry to `tree/seeds.md` (`- [[missing-slug]] — first seen in [[new-page-slug]], context: ...`).
6. In the `roots/legacy/` copy of the source (never the original Vault file), preserve the pre-translation wikilinks as HTML comments above the translated form, e.g. `<!-- original: [[1_Knowledge/Machine Learning/Softmax|Softmax]] -->`.

### 4. Discuss takeaways

Before writing any page, tell the user in 3–8 bullets what you extracted. Ask which pages they want created/updated and in what shape. This step is non-optional — the user is the curator.

### 5. Write/update pages

For each affected page:

Follow `CONVENTIONS.md § Output quality contract`. The body is a self-contained tree page, not a processing note. Absorb source substance into prose; keep raw paths and source provenance in `## Source` or source-record links only. Do not leave raw/source-processing voice (`raw`, staging, extraction, PDF page, "원문에서는", "자료에서는", "이 페이지에서는") in the body before `## Source`.

- If the page does **not** exist: create `tree/<slug>.md` with full ontology frontmatter:
  ```yaml
  ---
  kind: concept | entity | source-record | project | decision | insight | comparison
  form: prose | index              # grow 산물은 보통 prose
  topics: []                       # canonical from `ontology/topics.md`. 0-5개. 빈 배열 OK.
  subject: [<path>]                # SKOS-lite path from `ontology/subject-tree.md`
  source-types: [course | conversation | paper | article | docs | book | essay | external]   # 8-enum list (single-item OK)
  domains: []                      # CACHED — care --check 가 채움 (subject 의 top-level)
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  ---
  ```
  - **`kind` 선택 기준**:
    - `concept` — 재사용 가능한 일반 개념·방법·이론 (permanent note)
    - `entity` — 구체적 도구/사람/조직/제품 (Claude Code, Karpathy, OpenAI 등)
    - `source-record` — 특정 source unit 을 tree 안에 정리한 기록 (course subchapter note, chapter index, paper note, book note, essay 등 = literature note)
    - `project` — 본인 프로젝트의 추적
    - `decision` — 결정/선택/실패 기록 (synapse). 파일명: `decision-YYYY-MM-DD-<slug>.md`
    - `insight` — 작업·학습에서 압축된 통찰
    - `comparison` — A vs B 비교가 페이지 본질
  - **`form` 선택 기준**: 본문이 산문 흐름이면 `prose`, 다른 페이지 link list/navigation 허브면 `index`.
  - `subject` 는 `ontology/subject-tree.md` 의 path 1개. Cross-domain 진짜일 때만 multi (`[a/x, b/y]`).
  - `topics` 는 `ontology/topics.md` 의 canonical 우선. **미등록 topic 후보가 입자도 가드 (`ontology/topics.md § Topic granularity guidance` — 재사용 가능한 concept-level, broad domain 도 page-specific 도 아닐 것) 통과하면 LLM 이 직접 `ontology/topics.md § canonical_topics` 에 append 하고 페이지에 사용** (`CONVENTIONS.md § Schema evolution` autonomy A). 가드 실패면 페이지에서 빼고 grow summary 에 "topic skipped (granularity): X" 로 surface 만. 명백한 alias (`cot ↔ chain-of-thought` 처럼 morphology 또는 well-known abbrev) 도 LLM 이 `ontology/topics.md § aliases` 에 직접 append (autonomy A); 동의어 의심이지만 모호하면 care --check cluster surface 로 미룸.
  - `source-types` 는 8-enum list (`CONVENTIONS.md § Ontology` 참조). 한 페이지가 여러 source 에서 강화될 수 있으니 list — `source-types: [course, paper]` 같이 multi 가능. `legacy` 는 source-types 값 아님 — `--legacy` mode 의 import provenance 는 본문 또는 log entry 로 남김, source-types 은 콘텐츠 본질 (보통 `[article]` 또는 `[conversation]`).
  - **새 subject narrower** 가 자연스러우면 LLM 이 `ontology/subject-tree.md § narrower:` 에 candidate append + grow summary 에 "narrower proposed: X" 로 surface (autonomy B). 사용자가 다음 검토 사이클에 confirm 또는 revert. **새 top-level domain / 새 enum 값 (`kind` / `form` / `source-types`) / 새 facet field / subject deprecation** 은 autonomy C — LLM 절대 추가 금지, grow summary 에 pressure 로 surface 만.
  - Body: summary first, then detail. Cite the source with `[[source-page-slug]]` (creating a `kind=source-record` page if the source merits one, e.g. a specific paper/article).
- If the page **exists**: Edit it. Update `updated:` in frontmatter. Preserve existing structure; add or revise prose surgically. Flag contradictions explicitly in the text (e.g. "_2026-04-15 source [[foo]] disagrees: ..._").

After writing or editing affected pages, run the `/naite care § Content Guard` on the touched bodies before `## Source` and fix violations immediately. This is part of production, not a later audit cleanup.

After content guard, run:

```powershell
python scripts/build-tree-manifest.py
python scripts/build-tree-dependencies.py
```

Then inspect `ontology/tree-dependencies.json` for inbound references to every touched slug. Surface semantic dependent candidates in the grow summary. Do not rewrite dependent pages automatically unless the user explicitly asked for repair.

**Subject path drift 와 가드-실패 topic 누적은 care --check 의 주 surface 대상.** Autonomy A 추가물 (canonical topic, alias, 일반 개념 페이지) 의 사후 품질은 care --check 의 garbage collector (`.claude/skills/naite/care-check.md § 14`) 가 검증.

### 6. Update `trunk.md` (curated, not exhaustive)

`trunk.md` 는 큐레이션된 진입점이라 **모든 새 페이지를 등록하지 않는다.** 다음 경우에만 갱신:

- **새 hub 페이지** (즉 다른 페이지에서 자주 link 받을 가능성이 높은 일반 개념 페이지): `## Knowledge domains § <domain>` 의 "주요" 라인에 한 줄 추가 (4-7개 한도 — 한도 도달 시 사용자에게 어느 줄을 빼고 추가할지 물음).
- **새 source/entity 페이지가 hub 역할** (예: 메이저 paper · 책 · 플랫폼 메타): 동일하게 hub 라인에 등재.
- **새 known domain 채택** (사용자 결정 후): `## Knowledge domains` 아래 `### <new-domain>` 섹션 신설.

다음 경우는 갱신 안 함:
- 일반 컨셉 페이지가 **hub 후보가 아닐 때** (한 페이지에서만 link 받을 짧은 개념). care --check 의 high-degree neurons 가 후 surface.
- Course 챕터·서브챕터 (course meta 의 Chapters 섹션이 진실 단일 소스).

기존 hub 페이지의 콘텐츠가 본질적으로 바뀌면 한 줄 요약 revise.

### 7. Append to `rings.md`

Add one entry:

```
## [YYYY-MM-DD] grow | <source title or slug>
- pages created: [[...]]
- pages updated: [[...]]
- subject: <path>  (cross-domain 일 때만 복수, ontology/subject-tree.md 참조)
- stubs added: N
```

### 8. Post-grow handling (type-specific)

This tree has no generic `_archive/` layer — raw files are the source of truth, tree pages are the distillation, duplicating raw into an archive was redundant and removed (see `CONVENTIONS.md § Post-grow handling`).

Do exactly one of these based on the source location:

- **Source under `roots/articles/`** → no action. The file stays in place. `rings.md` records the grow.
- **Source under `roots/legacy/`** → no action. Same as articles; file stays.
- **Source under `roots/conversations/`** (`YYYY-MM-DD-<slug>.md` claim summary from the capture step) → **delete the claim summary**. It was ephemeral staging. The verbatim transcript at `roots/conversations/_transcripts/<same-slug>.md` stays untouched — that's the insurance copy, permanent.
- **Source under `roots/courses/{slug}/`** → no action at subchapter-grow time. grow branch 모드의 `branch-finish` op handles wholesale archival (`roots/courses/{slug}/` → `roots/courses/_archive/{slug}/`). Do not attempt per-file moves.
- **Source elsewhere** (e.g. user dropped a file outside `roots/` and pointed at it directly) → flag it, ask whether to stage under one of the above first. Do not grow from a non-`roots/` location.

If the required file operation fails (e.g. tool environment blocks `rm` on the conversations claim summary), **do not claim completion**. Append an entry to `rings.md` with the same prefix but a body of `- aborted: could not clean up <path> after grow` and surface the residual state to the user. `/naite care --check` will flag it too.

For `--legacy` mode with an absolute Vault path outside `roots/legacy/`: first copy into `roots/legacy/<slug>.md` (with the translation comments from step 3.6). Then apply the `roots/legacy/` rule above — file stays. Do not modify the original Vault file itself.

### 9. Checkpoint with user

Summarize what landed. Ask if anything should be revised. Only after confirmation should you move on to the next file (if processing a directory).

## What this command never does

- Never mutates the *content* of files under `roots/`. Per-type cleanup (delete claim summary under `roots/conversations/`, legacy-copy creation) is the only allowed move.
- Never creates an `_archive/` directory under `roots/articles/`, `roots/conversations/`, or `roots/legacy/`. The only archive path in the project is `roots/courses/_archive/` and it is grow branch 모드 `branch-finish`'s concern, not this module's.
- **Autonomy A 외 schema 변경 금지.** Canonical topic / alias / 일반 개념 페이지는 입자도 가드 통과 시 자율 추가 (autonomy A). Subject narrower 는 candidate append + summary surface (autonomy B). **새 top-level domain, 새 enum 값 (`type` / `role` / `source-type`), 새 facet field, subject deprecation 은 LLM 이 절대 추가 안 한다 (autonomy C — 사용자 결정).** `domains` cache 는 care --check 가 자동 도출하므로 grow 시점에 직접 작성 금지.
- **Never registers chapter/subchapter pages in `trunk.md`.** course meta 의 Chapters 섹션이 진실 단일 소스.
- Never commits to git. The user commits on their own cadence.
- Never "batch-grows" a directory without per-file user confirmation.
