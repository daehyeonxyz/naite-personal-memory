---
name: wiki
description: Maintain a naite wiki — a personal, cross-domain knowledge wiki maintained by an LLM. Dispatcher skill for ingest, capture, query, lint, study, course, synapse, and curate subcommands. Invoke by typing /wiki followed by one of the subcommand names.
---

# /wiki — dispatcher

You maintain the **naite** personal knowledge base, following Karpathy's llm-wiki pattern. This skill may be invoked from any working directory — always resolve paths against the locations below, never against the current CWD.

## Fixed paths

- **`WIKI_ROOT`**: the root of your naite repo — the directory containing `CLAUDE.md`, `wiki/`, and `raw/`. All data paths (`wiki/`, `raw/`, `CLAUDE.md`, `CONTEXT.md`, `index.md`, `log.md`) resolve against this.
- **`SKILL_DIR`**: `<WIKI_ROOT>/.claude/skills/wiki` — this skill and its sub-files. Optionally junction/symlink this into your user-level skills directory (e.g. `~/.claude/skills/wiki`) so `/wiki` resolves from any working directory.

**First action on every invocation**: read `<WIKI_ROOT>/CLAUDE.md` in full. It defines the bootloader rules you must respect. Do not skip this read. For query, lint, curate, ingest, course, synapse, or any wiki mutation, also read `<WIKI_ROOT>/CONTEXT.md` before selecting evidence files.

If the current CWD is already `WIKI_ROOT` or a subdir of it, operate relative to CWD is fine; otherwise use absolute paths. When in doubt, use absolute.

## Dispatch

The user invokes `/wiki <subcommand> [args]`. Parse the first token of `args` as the subcommand:

| Subcommand | When to use | Load |
|------------|-------------|------|
| `ingest <path>` | A raw source exists at `<path>` and should be integrated into `wiki/`. `<path>` can be a file or a directory. | `<SKILL_DIR>/ingest.md` |
| `ingest --legacy <path>` | Source is a legacy Obsidian Vault note — requires wikilink translation before integration. | `<SKILL_DIR>/ingest.md` |
| `capture [topic?]` | Extract knowledge from the *current conversation* into a timestamped file under `<WIKI_ROOT>/raw/conversations/`. Does **not** touch `wiki/`. | `<SKILL_DIR>/capture.md` |
| `query <question>` | Answer a question from the wiki; optionally file the answer as a new page. | `<SKILL_DIR>/query.md` |
| `lint` | Health-check the wiki: orphans, stubs, domain drift, slug collisions, index drift, output quality guard, secrets scan, binary creep, skill candidates, failure patterns, user model refresh. | `<SKILL_DIR>/lint.md` |
| `study [path?]` | "Just studied something, put it in the wiki." Convenience wrapper over `capture` + `ingest`; auto-detects conversation / file / mixed mode. Handles PDF and YouTube-transcript pre-staging. | `<SKILL_DIR>/study.md` |
| `course [args?]` | 과목 단위 학습 모드. 세션 전체에 상주하며 서브챕터마다 ingest, 과목/챕터 메타 관리. `study`가 단발성 학습이면 `course`는 다챕터·다페이지 구조. Sub-ops (`start`, `resume`, `chapter-start`, `subchapter-note`, `chapter-finish`, `course-finish`, `stage-source`)은 대화 맥락 기반 자동 분기. | `<SKILL_DIR>/course.md` |
| `synapse [topic?]` | 의사결정 thread (DMU) 를 wiki 의 시냅스 layer 로 박는 dialogue scaffold. 14 섹션을 차례 질문으로 끌어내고 trade-off / failure / invariant / cross-link 을 강제. 명시 슬래시 외에도 대화 중 결정 패턴 또는 작업 종료 시그널 감지 시 Claude 가 자동 제안. CONVENTIONS.md § Decision thread shape 참조. | `<SKILL_DIR>/synapse.md` |
| `curate [scope?]` | Qualitative maintenance: page/course review, direct repair, large-scope content sweep, and recurring-rule learning. This is the single user-facing partner to `lint`; score·grade·threshold 없음. scope: `{slug}` / `course-{slug}` / `--courses` / `--synapses` / `--all` / `--system`. | `<SKILL_DIR>/curate.md` |

Compatibility aliases:

| Legacy subcommand | Behavior | Load |
|------------|-------------|------|
| `audit [scope?]` | Alias for `/wiki curate` review mode. Prefer `curate` in new prompts and docs. | `<SKILL_DIR>/audit.md` |
| `consolidate [scope?]` | Alias for `/wiki curate` sweep mode. Prefer `curate` in new prompts and docs. | `<SKILL_DIR>/consolidate.md` |
| `rewire [scope?]` | Alias for `/wiki curate --system`. Prefer `curate` in new prompts and docs. | `<SKILL_DIR>/rewire.md` |

`<SKILL_DIR>` = `<WIKI_ROOT>/.claude/skills/wiki`. Substitute when reading.

## How to run

1. Parse the subcommand from `args`. If missing or unrecognized, print the table above and ask the user which subcommand they meant.
2. Read `<WIKI_ROOT>/CLAUDE.md` if you haven't this session.
3. Read `<WIKI_ROOT>/CONTEXT.md` when the subcommand needs wiki context, generated maps, dependency review, or any mutation.
4. Read the matching sub-skill file with the Read tool (use the absolute path).
5. Follow its workflow exactly. Do not paraphrase or improvise steps — the sub-files are the contract.
6. Every successful subcommand (except `query` without filing) appends a line to `<WIKI_ROOT>/wiki/log.md` with prefix `## [YYYY-MM-DD] <op> | <title>`.

## Shared rules (do not violate)

- **`raw/` is content-immutable.** Never change the *content* of files under `raw/`. There is **no generic `_archive/` layer** — see `CONVENTIONS.md § Post-ingest handling` for the per-subdir rule. Summary: `raw/articles/` files stay in place after ingest; `raw/conversations/` claim summaries are deleted post-ingest (transcripts in `_transcripts/` are preserved); `raw/courses/{slug}/` is wholesale-moved to `raw/courses/_archive/{slug}/` only at `course-finish` (the only `_archive/` path in the project). Content-writing exceptions: `ingest --legacy` adds a translation comment to the staged legacy copy; `capture` writes new files under `raw/conversations/`; `course` stages sources under `raw/courses/{slug}/`.
- **`wiki/` is LLM-owned.** The user does not hand-edit pages; you do. But always surface material changes to the user before committing.
- **Read `ontology/wiki-manifest.json` before searching for candidate pages**, then read `wiki/index.md` before writing any wiki page so you reuse existing curated domain entry points and page slugs.
- **Read `ontology/wiki-dependencies.json` before changing an existing page** when semantic dependents may need review.
- **Secrets policy from `CLAUDE.md` is absolute.** If lint flags a secret, halt before any git operation and report.
- **Frontmatter contract**: `kind`, `form`, `topics`, `subject`, `source-types`, `domains` (cached), `created`, `updated`. Spec at `CONVENTIONS.md § Ontology` + `ontology/subject-tree.md` + `ontology/topics.md` + `ARCHITECTURE.md § 3`. Legacy `type` / `role` / `source-type` (singular) fields are an error — 새 페이지가 legacy schema 로 작성되면 lint 가 surface 하고 새 schema 로 고친다. No speculative fields without lint-surfaced pressure + user decision.
- **Filename style**: `lowercase-kebab-case.md`. Wikilinks: `[[page-slug]]` or `[[page-slug|Display]]`.
