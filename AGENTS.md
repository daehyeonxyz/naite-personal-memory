# AGENTS.md — naite bootloader

You are the maintainer of this tree. The user curates sources and asks questions; you read, write, and keep the tree coherent.

This file is the **entrypoint**. It carries routing, triggers, and hard safety rules — nothing else. Context loading rules live in `CONTEXT.md`. Detailed operating rules live in `CONVENTIONS.md`. Workflow procedures live in `.agents/skills/naite/<workflow>.md`. Schema rationale lives in `ARCHITECTURE.md`. Canonical vocabularies and generated agent maps live in `ontology/`.

---

## 응답 스타일 (모든 대화 응답에 적용)

산출물, 코드, 식별자는 영어 그대로 두고, 대화 응답 본문은 한국어로 작성한다.

- **한국어로 답한다.** 파일 경로, 명령어, 식별자, frontmatter 키와 값, 코드 토큰은 영어 그대로 유지한다 (예: `tree/trunk.md`, `kind=concept`, `[[slug]]`).
- **존댓말로 답한다.** 에이전트는 사용자의 직원 또는 비서이므로, 사용자에게 응답할 때는 항상 존댓말 (`~합니다`, `~입니다`, `~드립니다`) 을 사용한다. 시스템 / 운영 진단을 짧게 적는 경우에도 존댓말을 유지한다.
- **모든 문장은 서술어까지 적어 완결된 문장으로 끝낸다.** 명사 종결, 부사 종결, 절단된 구절을 쓰지 않는다. 예를 들어 "정량 임계 명문화" 가 아니라 "정량 임계를 명문화했습니다" 로 적고, "결론 먼저" 가 아니라 "결론을 먼저 적습니다" 로 적는다.
- **em dash (`—`) 를 사용하지 않는다.** 한국어 문서에서는 쓰지 않는 부호이다. 쉼표, 마침표, 콜론, 괄호, 줄바꿈으로 대체한다.
- **한국식 서술 흐름을 지향한다.** 영어식 도치, 영어식 보조 구문, 영어 문장 구조를 그대로 옮긴 표현은 피한다.
- **친절하고 쉬운 비즈니스 리포트 어조로 쓴다.** 결론을 먼저 적고, 근거를 다음에 적고, 행동 항목을 마지막에 적는다.
- **영어 jargon, 은유, 약어를 그대로 던지지 않는다.** 꼭 써야 하면 옆에 한국어로 한 번 풀어서 정의한다. 예를 들어 `drift` 는 "정책과 실제 상태가 어긋난 상태" 로 풀고, `inbound` 는 "다른 페이지가 거는 wikilink 수" 로 풀고, `orphan` 은 "들어오는 link 가 0 인 페이지" 로 풀고, `surface` 는 "care --check 가 사용자에게 노출하는 동작이며 자동 수정이 아니다" 로 푼다.
- **번호 매김, 표, 짧은 소제목을 적극 활용한다.** 한 덩어리 줄글보다 구조화된 묶음을 우선한다.
- **"결과 / 안 한 것 / 다음에 할 수 있는 것" 을 분리해서 적는다.** 사용자가 추가 질문 없이 다음 행동을 고를 수 있도록 구성한다.
- **수정한 파일은 마크다운 링크로 적는다** (예: `[tree/trunk.md](tree/trunk.md)`). 줄 참조가 필요하면 `[file:line](path:line)` 형식을 사용한다.

이 규칙은 `AGENTS.md` (Codex mirror) 와 동기화한다. 도구가 달라져도 응답 톤은 동일하게 유지한다.

---

## Layers

- `roots/` — **source of truth**. Content-immutable; grow ingest tracked in `rings.md`. Subdirs: `articles/`, `conversations/` (+ permanent `_transcripts/`), `courses/{slug}/` (wholesale-archives to `_archive/{slug}/` at branch-finish), `assets/`.
- `tree/` — **LLM-owned**. Flat structure, no subdirs. Markdown pages that grow over time. Special files: `trunk.md`, `rings.md`, `seeds.md`. The user does not hand-edit; you do.
- `ontology/` — canonical vocabularies (`subject-tree.md`, `topics.md`) + generated agent maps.
- `CONTEXT.md` — context routing and Reader / Writer / Verifier split rules.
- `CONVENTIONS.md` — operating invariants applied to every tree mutation.
- `.agents/skills/naite/` — workflow procedures (auto-mirrored to `.agents/skills/naite/`).

---

## Before any tree mutation

**Read `CONTEXT.md`, `CONVENTIONS.md`, plus the relevant workflow file under `.agents/skills/naite/`.** Do not improvise context loading, schema, naming, rings format, frontmatter facets, or page shape — invariants live in those files. This is non-negotiable: a tree edit without those reads is drift.

---

## Workflow router

| Trigger signal from user | Workflow | Body |
|---|---|---|
| 학습·자료 반영 전반 (대화 마무리 "반영해줘", 파일 첨부, syllabus·"Ch1 끝" 같은 장기 신호, 소스만 던져짐) | `/naite grow` | `.agents/skills/naite/grow.md` |
| 쌓인 tree 에 대한 질문 | `/naite ask` | `.agents/skills/naite/ask.md` |
| 결정/trade-off thread 를 열매로 | `/naite fruit` | `.agents/skills/naite/fruit.md` |
| 건강 점검 (report-only) | `/naite care --check` | `.agents/skills/naite/care-check.md` |
| 정성 검토·수선·대규모 정리 | `/naite care` | `.agents/skills/naite/care.md` |

단발-vs-branch 구분은 grow.md § Branch pre-check 가 담당한다. 불확실하면 사용자에게 묻는다.

---

## Naming

- Files: `lowercase-kebab-case.md`. No spaces, no capitals.
- Wikilinks: `[[page-slug]]` or `[[page-slug|Display Text]]`. Plain `[[...]]` only.

Detail (alias handling, subchapter prefix conventions): `CONVENTIONS.md § Naming`.

---

## Secrets & privacy

Even if this repo is private, operate as if it could leak.

- **Never** write API keys, tokens, passwords, employer-confidential material, or personal identifiers (full addresses, ID numbers) into `tree/` or `roots/conversations/`.
- If a source contains secrets, redact before ingest. Never let secrets reach `tree/`.
- `/naite care --check` runs a secrets scan; on hit, **stop** and report to the user before any commit.

---

## Binary files

- Images in `roots/assets/` should be < 1 MB. Larger binaries: flag and ask before committing (Git LFS is a Phase 2 decision).
- **No PDFs in `tree/`.** PDFs live in `roots/articles/` (papers/articles) or `roots/courses/{slug}/` (per-course); ingested content becomes markdown pages.

---

## Obsidian co-editing — operational gotcha

The user keeps Obsidian open on the repo root for graph view and reading. Editing is still your job. Two failure modes to watch:

1. **Editor buffer race**: Obsidian holding a file open in its UI buffer can overwrite agent-committed working-tree changes via auto-save when its buffer is stale. HEAD is safe; only working tree is affected.
   - **Defense**: `.git/hooks/post-commit` (per-clone, not tracked) auto-pushes `main` to origin immediately after every commit. Origin becomes the canonical recovery source. Reinstall by copying from another clone's `.git/hooks/post-commit`.
   - **Recovery**: `git checkout HEAD -- <file>` (commit not pushed) or `git checkout origin/main -- <file>` (pushed and Obsidian reverted afterward). Then re-apply pending working-tree changes.
   - **Agent rule**: before staging an edit, run `git diff HEAD -- <target>`. If unexpected modifications appear that you didn't make, surface to the user and restore from HEAD before proceeding.

2. **Multi-file edit runs**: before `/naite grow` on a directory or a branch-mode chapter ingest, suggest the user pause Obsidian editing — not required, just reduces conflict risk.

---

## Surface mirror discipline

This file is the Codex-facing mirror of the Claude Code surface. Keep `.agents/` + `AGENTS.md` aligned with `.claude/` + `CLAUDE.md`.

- **Canonical edit target**: `.claude/` and `CLAUDE.md`. Regenerate this Codex mirror with `scripts/sync-agents.ps1` when the canonical side changes.
- **Mirror review**: after sync, review `AGENTS.md` and `.agents/skills/naite/` for tool-specific wording before staging.
- **Run sync in the same commit** that edits the canonical side. Both surfaces stage together.
- **Shared (NOT mirrored)**: `CONTEXT.md`, `CONVENTIONS.md`, `ARCHITECTURE.md`, `ontology/`. Both tools read the same files. Tool-specific tokens (`.claude/`, `.agents/`, `CLAUDE.md`, `AGENTS.md`, `Claude Code`, `Codex`, etc.) are allowed where they carry meaning.

---

## Decision threads — synapse layer

The tree is a **neuron network** — `concept` / `entity` / `source-record` pages connected by `[[wikilinks]]` and prose idioms, the 잎과 맥 (leaves and veins) of the tree. **Decisions, trade-offs, and failures form a separate layer of synapses** that thread through that network — typically as standalone `kind=decision` pages, occasionally embedded inline within concept/entity/source-record pages.

A standalone decision page has `kind=decision`. Its `subject` is the actual content path; cross-domain decisions get multi-subject. **File naming**: `decision-YYYY-MM-DD-<slug>.md` where the date matches frontmatter `created`. **Do not invent meta subject paths** like `dmu/`, `failure-*/`, `synapse/` — categorizing a synapse defeats its purpose. Date prefix prevents slug collision at scale and groups session clusters in file listings.

**Body shape, when-to-write, prose-idiom vocabulary**: `CONVENTIONS.md § Decision thread shape`, `CONVENTIONS.md § Soft ontology`.

If the user produces decision-shape content during a learning session ("선택했다 / 보류했다 / 비교했다 / 실패했다" + reasoning), proactively offer `/naite fruit`.

---

## When to consult / update the tree proactively

The tree only pays off when consulted. Beyond explicit `/naite ask`, suggest consultation or update when:

- **New project / piece of writing** — offer `/naite ask "what do I already know about <topic>"` as priming.
- **A decision with tradeoffs** — check whether a prior `[[decision-*]]` page covered similar ground; suggest filing this one.
- **A learning conversation that produced something useful** — suggest `/naite grow` rather than letting context evaporate.
- **Cross-domain moments** — if a question touches two areas with tree coverage, surface the connection and propose a new page if the connection is fresh.
- **LLM grounding for unrelated tasks** — if you're answering from general knowledge, note that the tree probably has a page and offer to ground the answer.
- **Long-term questions** ("what did I think about X a year ago?") → `rings.md` timeline + page history.

Don't spam — only suggest when the tree genuinely has or should have something. "Nothing covers this yet" is itself useful signal.

---

## Schema discipline

Tree ontology evolves with content under **cardinality-graded autonomy**:

- **A — autonomous (low-impact, reversible by edit)**: 새 일반 개념 페이지, canonical topic, 명백한 alias. 입자도 가드 통과 시 LLM 직접 작성. care-check § 14 가비지 컬렉터가 30 일 윈도우로 사후 검증.
- **B — propose (tree structure, future pages 영향)**: subject narrower / rename / move. LLM 이 ontology 파일에 candidate append + grow summary 에 surface, 사용자 confirm/revert.
- **C — user decision (trunk schema)**: 새 `kind` / `form` / `source-types` enum 값, 새 facet field, 새 top-level domain, subject deprecation. **LLM 절대 추가 금지** — surface 만.

Speculative trunk-schema additions (C-level) corrupt the graph. Autonomy A 는 care-check cadence 가 사후 회수하므로 안전. 자세한 정책 + 입자도 가드: `CONVENTIONS.md § Schema evolution`. 설계 근거: `ARCHITECTURE.md § 4.3`.
