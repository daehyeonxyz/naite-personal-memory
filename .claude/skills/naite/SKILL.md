---
name: naite
description: Maintain a naite vault — a personal knowledge tree maintained by an LLM. Dispatcher for start, grow, ask, fruit, care, and upgrade. Invoke by typing /naite followed by one of the subcommand names.
---

# /naite — dispatcher

You maintain a **naite** vault: one vault = one tree. The user adds sources and asks questions; you read, write, and connect Markdown pages the user owns. This skill may be invoked from any working directory — always resolve paths against the locations below, never against the current CWD.

## Fixed paths

- **`NAITE_ROOT`**: the root of the naite vault — the directory containing `CLAUDE.md`, `tree/`, and `roots/`. All data paths resolve against this.
- **`SKILL_DIR`**: `<NAITE_ROOT>/.claude/skills/naite` — this skill and its sub-files. Optionally junction/symlink this into your user-level skills directory (e.g. `~/.claude/skills/naite`) so `/naite` resolves from any working directory.

**First action on every invocation**: read `<NAITE_ROOT>/CLAUDE.md` in full. For ask, care, grow, fruit, or any tree mutation, also read `<NAITE_ROOT>/docs/CONTEXT.md` before selecting evidence files.

If the current CWD is already `NAITE_ROOT` or a subdir of it, operating relative to CWD is fine; otherwise use absolute paths. When in doubt, use absolute.

## Dispatch

The user invokes `/naite <subcommand> [args]`. Parse the first token of `args` as the subcommand:

| Subcommand | When to use | Load |
|------------|-------------|------|
| `start` | 첫 세션 안내: 신규 사용자가 자기 메모리를 import 해 `/naite grow` 흐름으로 첫 나무를 짓고 그래프로 본다. 1회성 온보딩 진입점, 이후는 grow 로. | `<SKILL_DIR>/start.md` |
| `grow [args?]` | 나무를 키운다 — 학습·자료 반영의 단일 진입점. 대화 마무리, 파일/디렉터리 첨부, 장기 과정 (과목·책·시리즈 = branch), 소스만 던져진 경우 (받아두기) 를 자동 감지해 분기한다. | `<SKILL_DIR>/grow.md` |
| `ask <question>` | 나무에게 묻는다 — 쌓인 tree 에서 답을 합성하고, 가치 있으면 페이지로 남길지 제안한다. | `<SKILL_DIR>/ask.md` |
| `fruit [topic?]` | 열매를 맺는다 — 결정·trade-off·실패 분석을 `kind=decision` 페이지로 박는 dialogue scaffold. 대화 중 결정 패턴 감지 시 에이전트가 자동 제안. | `<SKILL_DIR>/fruit.md` |
| `care [scope?]` | 나무를 돌본다 — `--check` (점검: report-only, secrets 차단 게이트) 와 돌봄 (검토·수선·대규모 정리) 두 모드. | `<SKILL_DIR>/care.md` |
| `upgrade` | 하네스를 올린다 — 업스트림 최신 릴리스로 작업 틀만 갱신. 사용자 자료 (`roots/`, `tree/`, `.naite/ontology/`) 는 절대 건드리지 않고, 사용자 커스텀 파일은 3-way 제안으로 보존. | `<SKILL_DIR>/upgrade.md` |

`<SKILL_DIR>` = `<NAITE_ROOT>/.claude/skills/naite`. Substitute when reading.

Internal modules (not user-facing; loaded by grow/care as needed): `capture.md`, `ingest.md`, `grow-branch.md`, `grow-backfill.md`, `care-check.md`.

## How to run

1. Parse the subcommand from `args`. If missing or unrecognized, print the table above and ask the user which subcommand they meant.
2. Read `<NAITE_ROOT>/CLAUDE.md` if you haven't this session.
3. Read `<NAITE_ROOT>/docs/CONTEXT.md` when the subcommand needs tree context, generated maps, dependency review, or any mutation.
4. Read the matching sub-skill file with the Read tool (use the absolute path).
5. Follow its workflow exactly. Do not paraphrase or improvise steps — the sub-files are the contract.
6. Every successful subcommand (except `ask` without filing) appends a line to `<NAITE_ROOT>/tree/rings.md` with prefix `## [YYYY-MM-DD] <op> | <title>`.

## Shared rules (do not violate)

- **`roots/` is content-immutable.** Never change the *content* of files under `roots/`. There is **no generic `_archive/` layer** — see `docs/CONVENTIONS.md § Post-grow handling` for the per-subdir rule. Summary: `roots/articles/` files stay in place after grow; `roots/conversations/` claim summaries are deleted post-grow (transcripts in `_transcripts/` are preserved); `roots/courses/{slug}/` is wholesale-moved to `roots/courses/_archive/{slug}/` only at `branch-finish` (the only `_archive/` path in the vault). Content-writing exceptions: legacy import adds a translation comment to the staged copy; grow stages new files under `roots/`.
- **`tree/` is LLM-owned.** The user does not hand-edit pages; you do. But always surface material changes to the user before committing.
- **Read `.naite/ontology/tree-manifest.json` before searching for candidate pages**, then read `tree/trunk.md` before writing any page so you reuse existing curated domain entry points and page slugs.
- **Read `.naite/ontology/tree-dependencies.json` before changing an existing page** when semantic dependents (vein 으로 이어진 잎들) may need review.
- **Secrets policy from `CLAUDE.md` is absolute.** If care flags a secret, halt before any git operation and report.
- **Frontmatter contract**: `kind`, `form`, `topics`, `subject`, `source-types`, `domains` (cached), `created`, `updated`. Spec at `docs/CONVENTIONS.md § Ontology` + `.naite/ontology/subject-tree.md` + `.naite/ontology/topics.md` + `docs/ARCHITECTURE.md § 3`. Legacy `type` / `role` / `source-type` (singular) fields are an error — care 가 surface 하면 새 schema 로 고친다. No speculative fields without care-surfaced pressure + user decision.
- **Filename style**: `lowercase-kebab-case.md`. Wikilinks (vein): `[[page-slug]]` or `[[page-slug|Display]]`.
