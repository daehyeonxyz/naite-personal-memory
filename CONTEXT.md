# CONTEXT.md - naite context routing

This file defines what an agent should load first, what it should load only on demand, and when source-heavy work should be split into separate Reader / Writer / Verifier roles.

It is an operating contract. It is not schema rationale (`ARCHITECTURE.md`), mutation policy (`CONVENTIONS.md`), or workflow procedure (`.claude/skills/naite/*.md` and `.agents/skills/naite/*.md`).

---

## Purpose

The tree is now large enough that "read all important files" is a failure mode. Context must be admitted by role:

1. **Authority**: rules that decide what is allowed.
2. **Procedure**: the active workflow contract.
3. **Map**: compact generated indexes that find relevant pages fast.
4. **Evidence**: the specific source files and tree pages needed for this task.
5. **Verification**: deterministic checks and dependency review after edits.

Agents should load the smallest set that can safely decide the task, then expand only when the active workflow or evidence requires it.

---

## Foundation documents

| Role | File |
|---|---|
| Claude bootloader | `CLAUDE.md` |
| Codex bootloader | `AGENTS.md` |
| Context routing | `CONTEXT.md` |
| Mutation invariants | `CONVENTIONS.md` |
| Architecture rationale | `ARCHITECTURE.md` |
| Subject taxonomy | `ontology/subject-tree.md` |
| Topic vocabulary | `ontology/topics.md` |
| Agent page map | `ontology/tree-manifest.json` |
| Agent dependency map | `ontology/tree-dependencies.json` |
| Claude workflow contracts | `.claude/skills/naite/*.md` |
| Codex workflow contracts | `.agents/skills/naite/*.md` |
| Human landing page | `tree/trunk.md` |
| Audit trail | `tree/rings.md` |
| Missing page register | `tree/seeds.md` |

`ontology/tree-manifest.json` and `ontology/tree-dependencies.json` are compact generated operating maps. They are tracked because agents need them as fast-path context, but they are never hand-edited. Regenerate them with the scripts in `scripts/`.

---

## Default loading order

1. **Bootloader**: read `CLAUDE.md` or `AGENTS.md` for the active surface.
2. **Route intent**: classify the user request into a workflow or a non-mutating answer.
3. **Context contract**: read this file when the task involves tree mutation, tree query, context selection, routing, dependency propagation, care, or care-check.
4. **Mutation authority**: for any tree mutation, read `CONVENTIONS.md`.
5. **Workflow procedure**: read the exact workflow file under the active surface, such as `.claude/skills/naite/grow-branch.md` or `.agents/skills/naite/care.md`.
6. **Generated maps**: read `ontology/tree-manifest.json` before searching for target pages; read `ontology/tree-dependencies.json` before changing an existing page or reviewing semantic dependents.
7. **Local evidence**: read only the source files, tree pages, ontology sections, and recent rings entries required by the task.
8. **Verification**: after edits, run the relevant deterministic scripts and rebuild generated maps when page coordinates or links changed.

Do not use `tree/trunk.md` as an exhaustive search index. It is a curated human landing page. Use `ontology/tree-manifest.json` as the agent fast path, then read the specific tree pages it identifies.

---

## Workflow context matrix

| Workflow | Always load | Load when needed |
|---|---|---|
| `/naite ask` | bootloader, `CONTEXT.md`, `ontology/tree-manifest.json` | `ontology/tree-dependencies.json`, target pages, `tree/rings.md` for timeline questions |
| `/naite grow` (단발: conversation/file/stage-only) | bootloader, `CONTEXT.md`, `CONVENTIONS.md`, active `grow.md` (+ internal `ingest.md`/`capture.md` as needed), `ontology/tree-manifest.json`, `tree/trunk.md`, `tree/seeds.md`, recent `tree/rings.md` | `ontology/subject-tree.md`, `ontology/topics.md`, `ontology/tree-dependencies.json`, source files |
| `/naite grow` (branch 모드) | bootloader, `CONTEXT.md`, `CONVENTIONS.md`, active `grow-branch.md`, `ontology/tree-manifest.json`, `tree/trunk.md`, recent `tree/rings.md` | `ontology/subject-tree.md`, `ontology/topics.md`, `ontology/tree-dependencies.json`, course source files, prior course pages |
| `/naite fruit` | bootloader, `CONTEXT.md`, `CONVENTIONS.md`, active `fruit.md`, `ontology/tree-manifest.json`, `ontology/tree-dependencies.json` | target decision pages, related concept pages, `ARCHITECTURE.md` only for schema rationale |
| `/naite care` / `care --check` | bootloader, `CONTEXT.md`, `CONVENTIONS.md`, active `care.md` / `care-check.md`, generated maps | scripts, ontology files, target pages, inbound dependents, `tree/rings.md`, `tree/seeds.md`, producer workflow files when defects repeat |
| Schema or workflow redesign | bootloader, `CONTEXT.md`, `CONVENTIONS.md`, `ARCHITECTURE.md`, relevant workflow files | decision pages, validator scripts, mirror sync script |

---

## Reader / Writer / Verifier split

Use separate physical agents when the tool surface supports them and the user has authorized agent delegation. If physical subagents are unavailable, keep the same roles as explicit sequential phases in one session.

### Use the split when any condition is true

- The source is long, dense, or multi-file.
- A PDF, transcript, lecture bundle, or directory ingest is involved.
- The workflow has a strict output contract, especially `/naite grow` branch mode, `/naite grow` file ingest, and `/naite fruit`.
- Five or more tree pages may be touched.
- Ontology selection is ambiguous.
- Existing pages with inbound dependents may be changed.

### Reader role

The Reader receives the source material and minimal task framing. It extracts claims, concepts, examples, equations, diagrams, terms, possible wikilinks, and uncertainty. It does not write `tree/*.md`, does not choose final frontmatter, and does not mutate `ontology/`.

Reader output should be a compact raw chunk with:

- source unit identity,
- key claims,
- reusable concept candidates,
- examples and formulas,
- terms and aliases,
- questions or ambiguities,
- suggested existing tree links if obvious.

### Writer role

The Writer receives the Reader chunk, `CONVENTIONS.md`, the active workflow file, generated maps, and relevant ontology files. It writes or updates tree pages according to the workflow contract.

The Writer should avoid loading the full source again unless the Reader chunk is insufficient or the workflow requires exact verification.

### Verifier role

The Verifier checks touched pages against:

- frontmatter contract,
- output quality contract,
- link usefulness,
- source block placement,
- `tree/rings.md` rules,
- generated manifest freshness,
- dependency map inbound candidates.

The Verifier surfaces semantic dependents for review. It does not automatically rewrite dependent pages unless the active workflow and user request authorize repair.

---

## Generated map policy

### `ontology/tree-manifest.json`

Build command:

```powershell
python scripts/build-tree-manifest.py
```

Purpose:

- direct slug lookup,
- page coordinate lookup by `kind`, `form`, `topics`, `subject`, `source-types`, and `domains`,
- fast candidate narrowing before reading full tree pages,
- trunk drift and hub candidate support.

This map is intentionally compact. It stores page coordinates, titles, and aliases, not page bodies.

Regenerate when:

- a tree page is created, deleted, or renamed,
- frontmatter changes,
- a title or alias section changes,
- a workflow needs a fresh search map.

### `ontology/tree-dependencies.json`

Build command:

```powershell
python scripts/build-tree-dependencies.py
```

Purpose:

- inbound wikilink lookup,
- outbound dependency lookup,
- soft relation idiom lookup,
- semantic dependent candidate surfacing after edits,
- high-degree neuron and orphan support.

This map is intentionally slug-level. It stores which pages point to which slugs and which soft relation idioms appear, not full line text.

Regenerate when:

- a tree page body changes,
- wikilinks change,
- soft ontology idioms change,
- a workflow needs dependency propagation review.

---

## Dependency propagation policy

Not every dependency should trigger automatic edits. Use three levels:

| Level | Examples | Action |
|---|---|---|
| Hard dependency | `CLAUDE.md` to `AGENTS.md`, `.claude/skills/naite/*` to `.agents/skills/naite/*` | sync with `scripts/sync-agents.ps1` |
| Contract dependency | `CONVENTIONS.md` change affecting workflow files or validator scripts | update the affected contracts and validators in the same change |
| Semantic dependency | concept, decision, or source-record content change affecting linked pages | surface candidates from `ontology/tree-dependencies.json`, then repair through `/naite care` only when requested |

Python finds candidates. The LLM judges meaning. Do not auto-propagate semantic edits just because an inbound edge exists.

---

## Verification checklist

For changes to operating docs or workflow files:

1. Update canonical `.claude/` and root shared files first.
2. Run `scripts/sync-agents.ps1` after `.claude/` or `CLAUDE.md` changes.
3. Rebuild generated maps if tree page coordinates or links changed.
4. Run the relevant deterministic scripts.
5. Review `git diff` before staging.

For changes to tree pages:

1. Run content guard from `/naite care`.
2. Run `python scripts/build-tree-manifest.py` if page coordinates changed.
3. Run `python scripts/build-tree-dependencies.py` if wikilinks or body relations changed.
4. Inspect inbound dependents for touched slugs.
5. Run the relevant care-check before claiming completion.
