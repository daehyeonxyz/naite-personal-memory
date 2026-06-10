# /wiki study

Convenience wrapper for the "I just studied something, put it in the wiki" flow. Chains `capture` and `ingest` as needed. The low-level skills remain the contract — `study` never invents behavior they don't already have.

All data paths below (`raw/articles/`, `raw/conversations/`, etc.) resolve against **WIKI_ROOT** (the root of the naite repo). Sub-skill references resolve against **SKILL_DIR** (`<WIKI_ROOT>\.claude\skills\wiki`). See `SKILL.md` for context.

## When to use

The user just finished (or is finishing) a study session. Triggers include:
- "wiki에 업데이트해줘" / "update the wiki" right after a learning conversation.
- "이 PDF/강의록 공부했어" with a path attached.
- "이 유튜브 강의 봤어, 정리 부탁" with a pasted transcript or staged file.

If the user has only a file and no fresh context, `/wiki ingest` is enough — point them there instead of running `study`.

## Mode detection

Parse `args` as zero-or-one path token.

| args | Mode | What runs |
|------|------|-----------|
| *(empty)* | **Conversation** | `capture` → offer `ingest` of the capture file |
| `<path>` where path exists | **File** | source-type pre-step → `ingest <path>` (optionally merged with conversation takeaways) |
| `<path>` where path does not exist | Ask user: did they mean a new topic slug (conversation mode) or mistype a path? |

## Course-vs-study pre-check

Before committing to conversation or file mode, scan for signals that this learning spans **multiple related concepts forming a course, not a single-source event**:

- Uploaded syllabus, table-of-contents screenshot, or multiple lecture files
- Conversation covers ≥ 4 distinct concepts under one framing (e.g. "4 competencies of X framework", "Ch1~Ch3 summaries")
- User mentions "이번 학기", "Ch{N}", "과목", a course code, or Anthropic-Academy-style phased content
- Source file is part of an obvious series (filename like `Ch1 ...`, `Lecture 02 ...`)

If any signal triggers, **pause and ask** before executing: "이거 단발 학습 아니고 과목 단위 학습 같은데 `/wiki course` 로 전환할까요? (y → course, n → study 계속)"

Silence is not consent — if the user doesn't answer, default to the more conservative option (study) but warn that course metadata will be missing and will need retrofitting via `/wiki course start` later.

## Hard rules (inherited)

- `raw/` is immutable except for the archival/staging moves described below (same rule as `ingest`/`capture`).
- `wiki/` is LLM-owned; every material change is confirmed with the user before writing.
- Secrets pre-check from `capture.md` § 4 runs before any write to `raw/conversations/`.
- This skill writes **no** log entry of its own. The underlying `capture` and `ingest` runs are what get logged (`capture` does not log; `ingest` does).

## Workflow

### 1. Resolve mode

- If `args` is empty → conversation mode.
- If `args` has a token, resolve the path:
  - Absolute → use as-is.
  - Relative → relative to the repo root.
  - Does not exist → ask whether they meant a topic slug for conversation mode or there's a typo. Do not guess.

### 2. Conversation mode

1. Read `<SKILL_DIR>/capture.md` and execute its steps 1–4 (topic slug → claim summary → verbatim transcript → secrets pre-check). Path: `<WIKI_ROOT>/raw/conversations/YYYY-MM-DD-<topic-kebab>.md` (+ `_transcripts/` twin).
2. After `capture` finishes, summarize what was written and ask one question:
   > "바로 `/wiki ingest raw/conversations/<file>` 로 위키에 반영할까요? (y / later / cancel)"
3. On `y`: read `<SKILL_DIR>/ingest.md` and run its full workflow with `<path> = <WIKI_ROOT>/raw/conversations/YYYY-MM-DD-<topic>.md`. Post-ingest handling (step 8 of ingest) deletes this claim summary; the verbatim twin under `raw/conversations/_transcripts/` stays as permanent insurance.
4. On `later` or `cancel`: finish with capture's closing sentence from `<SKILL_DIR>/capture.md` § 5. No wiki mutation.

### 3. File mode

Determine source type from the extension and location, then run a pre-step before delegating to `ingest`.

#### 3a. `.md` or `.txt`
- If already under `raw/articles/` → no move. Delegate to `ingest`.
- Elsewhere (e.g. the user dropped it at repo root or in Downloads) → move to `raw/articles/<slug>.md` using kebab-cased basename. Preserve original content byte-for-byte. Then delegate to `ingest raw/articles/<slug>.md`.

#### 3b. `.pdf`
1. Create `raw/articles/_source/` if missing. Move the original PDF into `raw/articles/_source/<name>.pdf` (or copy, if the original lives outside the repo — in that case only copy, never modify external files).
2. Extract text to `raw/articles/<slug>.md`. Use the tool available to you in the session (Read on the PDF, or a PDF skill if one is loaded). Preserve page boundaries with `## p.<n>` headings where useful. If extraction quality is poor (scanned PDF without OCR, garbled characters), stop and tell the user before writing anything — ask whether to continue with what you got or defer.
3. Add a one-line pointer at the top of the extracted md:
   ```
   > Source PDF: `raw/articles/_source/<name>.pdf`
   ```
4. Delegate to `ingest raw/articles/<slug>.md`. Per current rule (`CONVENTIONS.md § Post-ingest handling`), the extracted md stays in `raw/articles/` after ingest — articles are not archived. The original PDF lives at `raw/articles/_source/<name>.pdf`.

#### 3c. YouTube / video
URL-only inputs are not sources. Require a transcript md file first:
- If the user pastes the transcript inline: write it to `raw/articles/<slug>.md` with frontmatter-style front block noting `source-url:` and `date-watched:` as free-form top matter (no wiki frontmatter — this is a raw file, not a wiki page).
- If no transcript yet: stop and tell the user — point them at Obsidian Web Clipper, YouTube's own transcript export, or an MCP tool if one is available. Do not proceed with URL alone.
- Once the transcript md exists, delegate to `ingest raw/articles/<slug>.md`.

#### 3d. Other extensions
Flag and ask. Do not silently convert. Office formats (`.docx`, `.pptx`), spreadsheets, and archive formats each need their own pre-step or a different skill.

### 4. Mixed mode (file + fresh conversation context)

If the user ran `study <path>` right after a substantive Q&A about the same topic, the conversation itself carries takeaways the raw file doesn't. Do not write a separate `capture` file (that would double-count the content). Instead:

- Surface the conversation takeaways to `ingest` during its step 4 ("Discuss takeaways"). Paraphrase them as user context so they influence which pages get created and how the summary is shaped.
- If the conversation contained a claim that the source does **not** support, tag it in the wiki page body as `_YYYY-MM-DD conversation note (not in source): …_`. Provenance stays honest.

### 5. Checkpoint

After the underlying `ingest` run completes (or conversation mode ends without ingest), give the user a one-paragraph summary:
- capture file path (if created)
- pages created / updated (from the ingest run)
- next steps (e.g. "run `/wiki lint` after a few more ingests").

If the ingested material includes a clear decision / trade-off / failure analysis (signals: "선택했다 / 보류했다 / 비교했다 / 실패했다" + reasoning), also offer: "이거 `/wiki synapse` 로 의사결정 thread 까지 박아둘까요?" — see CONVENTIONS.md § Decision thread shape.

## What this command never does

- Never bypasses per-step user confirmation from `capture`/`ingest`.
- Never logs on its own (`log.md` entries come from the sub-skills).
- Never writes PDF/office binaries into `wiki/`.
- Never processes a directory argument — pass directories to `/wiki ingest` directly; batching is that skill's concern.
- Never commits to git.
