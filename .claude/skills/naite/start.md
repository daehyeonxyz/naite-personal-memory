# /naite start

naite 를 처음 켠 사용자의 **첫 세션을 안내한다**. 빈 나무에는 보여줄 게 없으므로, 사용자가 이미 다른 AI(ChatGPT, Gemini, claude.ai) 에 쌓아둔 기록을 가져와(import) 첫 나무를 짓고, 그 나무를 그래프로 보며 모델을 납득하게 한다.

모든 데이터 경로는 NAITE_ROOT 기준으로, 하위 스킬 참조는 SKILL_DIR (`<NAITE_ROOT>/.claude/skills/naite`) 기준으로 푼다. 맥락은 SKILL.md 를 본다.

## When to use

- 설치 직후이고 vault 가 비어 있을 때 (`tree/` 에 `trunk.md`/`rings.md`/`seeds.md` 외 페이지가 없음).
- 사용자가 "어떻게 시작해?", "처음인데" 같은 신호를 줄 때.
- **1회성 온보딩 진입점이다.** 한 번 나무가 생긴 뒤의 일반 자료 반영은 `/naite grow` 로 간다. 메모리를 다시 가져오고 싶으면 `/naite start` 를 다시 불러도 되며, 이때는 서비스별 보존본을 갱신한다.

## Hard rules (inherited)

- `roots/` 는 source of truth. import 한 export 는 `roots/conversations/` 에만 쓴다. `tree/` 를 직접 편집하지 않는다.
- `roots/conversations/` 에 쓰기 전 `capture.md § 4` secrets pre-check 를 돌린다. 적중 시 쓰지 않고 사용자에게 알리고 redact 를 제안한다. 우회하지 않는다.
- 새 rings op 를 만들지 않는다. rings 기록은 위임된 `ingest` 가 한다.
- git commit 하지 않는다.

## Workflow

### 1. 모델 설명

나무 모델을 30초로 설명한다: `roots`(자료가 들어옴) → 잎·맥(이해가 링크됨) → 열매(결정) → 나이테(성장 기록). "저장 ≠ 축적" 을 한 줄로 짚는다.

### 2. 이전 프롬프트 전달

사용자가 ChatGPT / Gemini / claude.ai 중 어디서 기록을 가져올지 묻는다. `docs/migrate-prompt.md` 의 프롬프트를 해당 서비스 팁과 함께 제시한다.

### 3. import 받기

사용자가 자기 AI 에 붙여넣고 받은 export(Markdown 한 덩어리) 를 가져온다.

### 4. roots 에 안전하게 기록

1. export 내용에 `capture.md § 4` secrets pre-check 를 먼저 돌린다. 적중하면 멈추고 사용자에게 알린 뒤 redact 를 제안한다.
2. 통과하면 두 곳에 쓴다 (서비스 식별자 `<service>` 는 `chatgpt` / `gemini` / `claude` 중 하나):
   - 임시 claim summary: `roots/conversations/YYYY-MM-DD-memory-migration-<service>.md` — grow 후 `ingest` 가 삭제하는 ephemeral 스테이징.
   - 영구 보존본: `roots/conversations/_transcripts/migration-<service>.md` — **서비스별 stable 이름** (날짜 prefix 없음). import 를 다시 하면 이 파일을 갱신(덮어쓰기)하고, 새 날짜의 claim summary 를 만든다. 이 stable 이름은 "재import 시 갱신" 을 위한 의도된 컨벤션 (CONVENTIONS.md § Naming 참조).
3. `_transcripts/` 보존본은 사용자의 distilled 메모리 원본이자 재-grow 보험이다. 절대 삭제하지 않는다.

### 5. ingest 로 위임 (스키마는 여기서 적용)

`SKILL_DIR/ingest.md` 를 읽고 그 전체 워크플로를 `<path> = <NAITE_ROOT>/roots/conversations/YYYY-MM-DD-memory-migration-<service>.md` 로 실행한다. 이것은 grow 의 conversation 모드가 capture 직후 쓰는 것과 **같은 ingest 프리미티브**다. file 모드(article 이동 로직) 와 Branch pre-check 를 거치지 않으므로, 여러 주제가 섞인 export 가 branch 모드로 오탐될 일이 없다.

잎·맥(wikilink)·열매(`kind=decision`)·`subject`/facet 변환과 rings 기록은 전부 `ingest` 가 한다. start 는 스키마를 직접 손대지 않는다.

`ingest` 의 사후 삭제(§ 8)는 넘긴 경로, 즉 날짜가 붙은 claim summary(`YYYY-MM-DD-memory-migration-<service>.md`)만 지웁니다. 영구 보존본은 이름이 다른 stable 파일(`roots/conversations/_transcripts/migration-<service>.md`)이라 삭제 대상에 해당하지 않습니다.

### 6. reflect / 그래프 보기

`ingest` 가 만든 페이지 요약(생성·갱신된 페이지, 다음 단계) 을 받은 뒤, 사용자에게 그래프 뷰를 열어보라고 안내한다: Obsidian 으로 vault 를 열거나 naite-app 의 Forest 뷰를 연다. 막 생긴 자기 나무가 링크된 네트워크로 보이는 것이 납득의 순간이다. 다음 한두 수를 제안한다 (관심 주제로 `/naite ask`, 새 자료로 `/naite grow`).

## What this command never does

- `roots/` 의 import 기록 외에는 직접 쓰지 않는다 (`tree/` 변환은 `ingest` 위임).
- secrets pre-check 를 건너뛰지 않는다.
- 새 rings op 를 만들지 않는다.
- Never commits to git.
