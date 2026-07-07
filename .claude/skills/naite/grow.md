# /naite grow

나무를 키우는 단일 진입점. 대화, 파일, 장기 과정 (branch), 받아두기 (stage-only) 를 자동 감지해 tree 에 반영한다. 저수준 절차는 내부 모듈 (`capture.md`, `ingest.md`, `grow-branch.md`, `grow-backfill.md`) 이 계약이며, grow 는 그 위의 라우터다 — grow never invents behavior the modules don't already have.

All data paths below (`roots/articles/`, `roots/conversations/`, etc.) resolve against **NAITE_ROOT** (the root of the naite vault). Sub-skill references resolve against **SKILL_DIR** (`<NAITE_ROOT>/.claude/skills/naite`). See `SKILL.md` for context.

## When to use

The user just finished (or is finishing) a study session. Triggers include:
- "tree에 반영해줘" / "update the tree" right after a learning conversation.
- "이 PDF/강의록 공부했어" with a path attached.
- "이 유튜브 강의 봤어, 정리 부탁" with a pasted transcript or staged file.
- 소스만 던져지고 의도가 없을 때 — grow 가 받아두기 (stage-only) 까지 담당한다.

소스만 있고 fresh context 가 없으면 file 모드가 ingest 내부 모듈을 호출해 처리한다.

## Mode detection

Parse `args` and conversation context:

| 신호 | 모드 | 실행 |
|---|---|---|
| args 없음 + 직전에 학습 대화 | conversation | § 2 |
| args = 존재하는 파일/디렉터리 경로 + 반영 의도 | file | § 3 |
| 첫 토큰이 `backfill {slug}` | backfill | `grow-backfill.md § Workflow` 로 위임 |
| 장기 과정 신호 (§ Branch pre-check) | branch | `grow-branch.md` 로 위임 |
| 소스만 던져지고 반영 의도 불명 | stage-only | § 4 |
| 경로가 존재하지 않음 | 질문 | topic slug 인지 오타인지 사용자에게 확인. Do not guess. |

## Branch pre-check (장기 과정 감지)

conversation / file 모드로 가기 전에, 이 학습이 **하나의 큰 줄기 아래 이어지는 과정** (과목, 책 한 권, 강의 시리즈) 인지 신호를 본다:

- syllabus, 목차 스크린샷, 여러 강의 파일 업로드
- 한 프레임 아래 ≥ 4 개의 구분되는 개념 ("X 프레임워크의 4 역량", "Ch1~Ch3 정리")
- "이번 학기", "Ch{N}", 과목코드, 책 제목 + 챕터 언급
- 연속물임이 명백한 파일명 (`Ch1 ...`, `Lecture 02 ...`)

신호가 잡히면 **멈추고 한 줄로 확인한다**: "단발 학습이 아니라 긴 호흡 (branch) 같은데, branch 모드로 갈까요? (y → branch, n → 단발로 계속)"

무응답은 동의가 아니다 — 답이 없으면 보수적으로 단발 모드로 진행하되, branch 메타데이터가 빠지므로 나중에 branch 모드로 보강이 필요하다고 경고한다.

## Hard rules (inherited)

- `roots/` is immutable except for the archival/staging moves described below (same rule as `ingest`/`capture`).
- `tree/` is LLM-owned; every material change is confirmed with the user before writing.
- Secrets pre-check from `capture.md` § 4 runs before any write to `roots/conversations/`.
- This skill writes **no** rings entry of its own. The underlying `capture` and `ingest` runs are what get logged (`capture` does not log; `ingest` does).
- Writer invariant: ingest 가 원천 메커니즘을 보존하고 "원본 필요" 는 진짜 없는 자료에만 쓴다. 각 `form=prose` leaf 깊이는 작성 시점에 `docs/QUALITY.md § 4` (LEAF-1~4) 로 gating 된다 (`ingest.md § 5` 참조).

## Workflow

### 1. Resolve mode

- **빈 vault 선검사:** `tree/` 에 `trunk.md`/`rings.md`/`seeds.md` 외 페이지가 없으면(빈 vault), 한 줄로 제안한다: "vault 가 비어 있습니다. 처음이시면 `/naite start` 로 안내형 첫 세션을 권합니다 (y → `/naite start` 로 전환, n → grow 계속)." n 또는 거절이면 grow 를 정상 진행한다. 이미 자란 vault 면 이 선검사는 조용히 통과한다.
- If `args` is empty → conversation mode (단, § Branch pre-check 신호가 잡히면 branch 모드).
- 첫 토큰이 `backfill {slug}` → backfill 모드, `grow-backfill.md § Workflow` 로 위임.
- 장기 과정 신호가 잡히면 → branch 모드, `grow-branch.md` 로 위임.
- If `args` has a path token, resolve the path:
  - Absolute → use as-is.
  - Relative → relative to the vault root.
  - Exists + 반영 의도 명확 → file mode.
  - Exists + 반영 의도 불명 → stage-only mode (§ 4).
  - Does not exist → ask whether they meant a topic slug for conversation mode or there's a typo. Do not guess.

### 2. Conversation mode

1. Read `<SKILL_DIR>/capture.md` and execute its steps 1–4 (topic slug → claim summary → verbatim transcript → secrets pre-check). Path: `<NAITE_ROOT>/roots/conversations/YYYY-MM-DD-<topic-kebab>.md` (+ `_transcripts/` twin).
2. After `capture` finishes, summarize what was written and ask one question:
   > "바로 tree 에 반영할까요? (y / later / cancel)"
3. On `y`: read `<SKILL_DIR>/ingest.md` and run its full workflow with `<path> = <NAITE_ROOT>/roots/conversations/YYYY-MM-DD-<topic>.md`. Post-grow handling (step 8 of ingest) deletes this claim summary; the verbatim twin under `roots/conversations/_transcripts/` stays as permanent insurance.
4. On `later` or `cancel`: finish with capture's closing sentence from `<SKILL_DIR>/capture.md` § 5. No tree mutation.

### 3. File mode

Determine source type from the extension and location, then run a pre-step before delegating to `ingest`.

**Secrets + PII pre-check (all file-mode sources).** Before moving or ingesting any file, scan its content with the `capture.md § 4` secrets + PII checklist. The guard hook only fires at commit time and only on token patterns, so file mode is the layer that catches a secret/PII in an article or PDF before it reaches `tree/`. On a hit, stop and offer to redact — do not proceed to ingest.

**Path-aware routing (do not move files that already live in a managed roots subdir).** The "move to `roots/articles/`" rule below applies only to files a user dropped at the vault root, in Downloads, or a similar loose location:

- A path already under `roots/conversations/` is a captured conversation, not an article. Route it to the conversation ingest path (the same primitive `§ 2` uses), which lets `ingest § 8` delete the ephemeral claim summary and keep the `_transcripts/` twin. Never move it to `roots/articles/` (that breaks the post-grow deletion contract and the twin pairing).
- A path under `roots/legacy/` is a legacy import. Route it to `ingest --legacy <path>` (the wikilink-translation pass), which expects the file to stay in `roots/legacy/`. Never move it to `roots/articles/`.
- A path already under `roots/articles/` or `roots/courses/` stays in place.

#### 3a. `.md` or `.txt`
- If already under `roots/articles/`, `roots/conversations/`, `roots/legacy/`, or `roots/courses/` → **no move**; route per the path-aware rule above.
- Elsewhere (e.g. the user dropped it at vault root or in Downloads) → move to `roots/articles/<slug>.md` using kebab-cased basename. Preserve original content byte-for-byte. Then delegate to `ingest roots/articles/<slug>.md`.

#### 3b. `.pdf`
1. Create `roots/articles/_source/` if missing. Move the original PDF into `roots/articles/_source/<name>.pdf` (or copy, if the original lives outside the vault — in that case only copy, never modify external files).
2. Extract text to `roots/articles/<slug>.md`. Use the tool available to you in the session (Read on the PDF, or a PDF skill if one is loaded). Preserve page boundaries with `## p.<n>` headings where useful. If extraction quality is poor (scanned PDF without OCR, garbled characters), stop and tell the user before writing anything — ask whether to continue with what you got or defer.
3. Add a one-line pointer at the top of the extracted md:
   ```
   > Source PDF: `roots/articles/_source/<name>.pdf`
   ```
4. Delegate to `ingest roots/articles/<slug>.md`. Per current rule (`docs/CONVENTIONS.md § Post-grow handling`), the extracted md stays in `roots/articles/` after grow — articles are not archived. The original PDF lives at `roots/articles/_source/<name>.pdf`.

#### 3c. YouTube / video
URL-only inputs are not sources. Require a transcript md file first:
- If the user pastes the transcript inline: write it to `roots/articles/<slug>.md` with frontmatter-style front block noting `source-url:` and `date-watched:` as free-form top matter (no tree frontmatter — this is a raw file, not a tree page).
- If no transcript yet: stop and tell the user — point them at Obsidian Web Clipper, YouTube's own transcript export, or an MCP tool if one is available. Do not proceed with URL alone.
- Once the transcript md exists, delegate to `ingest roots/articles/<slug>.md`.

#### 3d. Other extensions
Flag and ask. Do not silently convert. Office formats (`.docx`, `.pptx`), spreadsheets, and archive formats each need their own pre-step or a different skill.

### 4. Stage-only mode (받아두기)

소스는 던져졌는데 "반영해줘" 의도가 없거나 불명확할 때. 물만 주고 심지는 않는 단계다.

1. 소스 종류를 판별해 § 3 file 모드의 **pre-step 까지만** 수행한다 (정규화 이름으로 `roots/` 아래 저장. md/txt → `roots/articles/<slug>.md`, pdf → `roots/articles/_source/` + 추출 md, 대화 → capture 절차).
2. `tree/` 는 건드리지 않고 `tree/rings.md` 에도 쓰지 않는다 (roots 레이어만).
3. 한 줄로 확인한다: "`roots/` 에 받아뒀습니다. 지금 심을까요? (y → 이어서 반영 / later → 여기까지)"
4. `y` 면 § 3 의 본 절차로 이어서 진행한다. `later` 면 받아둔 경로만 알려주고 끝낸다.

### 5. Mixed mode (file + fresh conversation context)

If the user ran `grow <path>` right after a substantive Q&A about the same topic, the conversation itself carries takeaways the raw file doesn't. Do not write a separate `capture` file (that would double-count the content). Instead:

- Surface the conversation takeaways to `ingest` during its step 4 ("Discuss takeaways"). Paraphrase them as user context so they influence which pages get created and how the summary is shaped.
- If the conversation contained a claim that the source does **not** support, tag it in the tree page body as `_YYYY-MM-DD conversation note (not in source): …_`. Provenance stays honest.

### 6. Checkpoint

After the underlying `ingest` run completes (or conversation mode ends without ingest), give the user a one-paragraph summary:
- capture file path (if created)
- pages created / updated (from the ingest run)
- next steps (e.g. "run `/naite care --check` after a few more grows").

If the ingested material includes a clear decision / trade-off / failure analysis (signals: "선택했다 / 보류했다 / 비교했다 / 실패했다" + reasoning), also offer: "이거 `/naite fruit` 로 의사결정 thread 까지 박아둘까요?" — see docs/CONVENTIONS.md § Decision thread shape.

## What this command never does

- Never bypasses per-step user confirmation from `capture`/`ingest`.
- Never logs on its own (`rings.md` entries come from the sub-skills).
- Never writes PDF/office binaries into `tree/`.
- grow 단발 경로(conversation/file/stage-only)는 git commit 하지 않는다. branch 모드의 커밋·push 는 `grow-branch.md § E/§ F` 가 한다.
