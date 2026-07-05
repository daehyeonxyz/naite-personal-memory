# /naite start

naite 를 처음 켠 사용자의 **첫 세션을 안내한다**. 빈 나무에는 보여줄 게 없으므로, 사용자가 이미 다른 AI(ChatGPT, Gemini, claude.ai) 에 쌓아둔 기록과(또는) 가지고 있는 원본 자료로 첫 나무를 짓고, 그 나무를 그래프로 보며 모델을 납득하게 한다.

모든 데이터 경로는 NAITE_ROOT 기준으로, 하위 스킬 참조는 SKILL_DIR (`<NAITE_ROOT>/.claude/skills/naite`) 기준으로 푼다. 맥락은 SKILL.md 를 본다. 사용자 대면 카피와 export 품질 기준은 `docs/QUALITY.md` 가 단일 진실원이다.

## When to use

- 설치 직후이고 vault 가 비어 있을 때 (`tree/` 에 `trunk.md`/`rings.md`/`seeds.md` 외 페이지가 없음).
- 사용자가 "어떻게 시작해?", "처음인데" 같은 신호를 줄 때.
- 사용자가 다른 AI 에서 기억을 뽑아 올 추출·이전 프롬프트를 요청할 때. 프롬프트를 즉석에서 새로 쓰지 않고 `docs/migrate-prompt.md` 정본을 서비스별 팁과 함께 그대로 전달한다 (즉석 프롬프트는 § 4 게이트와 어긋나는 export 를 만든다).
- 빈 vault 에 컨텍스트 덤프나 대화 export 가 명령 없이 먼저 도착했을 때 (붙여넣기 또는 `roots/` 아래 파일). 이때는 아래 § 0 fast path 로 들어간다.
- **1회성 온보딩 진입점이다.** 한 번 나무가 생긴 뒤의 일반 자료 반영은 `/naite grow` 로 간다. 메모리를 다시 가져오고 싶으면 `/naite start` 를 다시 불러도 되며, 이때는 서비스별 보존본을 갱신한다.

## Hard rules (inherited)

- `roots/` 는 source of truth. import 한 export 는 `roots/conversations/` 에만 쓴다. `tree/` 를 직접 편집하지 않는다.
- `roots/conversations/` 에 쓰기 전 `capture.md § 4` secrets pre-check 를 돌린다. 적중 시 쓰지 않고 사용자에게 알리고 redact 를 제안한다. 우회하지 않는다.
- **export 가 `docs/QUALITY.md § Import 검수 게이트` 를 통과하지 못하면 ingest 로 넘기지 않는다.** 얕은 입력을 그대로 빈약한 나무로 만들지 않는다.
- 새 rings op 를 만들지 않는다. rings 기록은 위임된 `ingest`/`grow` 가 한다.
- git commit 하지 않는다.

## Workflow

### 0. Export 가 이미 도착했는지 확인 (fast path)

§ 1 로 가기 전에 확인한다. 사용 가능한 export (메모리 이전 export, 컨텍스트 덤프, 대화 export) 가 이미 대화에 붙여넣어져 있거나 `roots/` 아래 파일로 놓여 있으면, § 1 모델 설명을 보여준 뒤 § 2 (경로 선택 + 프롬프트 전달) 와 § 3 (import 받기) 을 건너뛰고 바로 § 4 게이트로 간다.

- 이미 받은 자료에 대해 추출 프롬프트를 다시 제안하지 않고, "원본 자료를 가지고 계신가요?" 도 이 시점에 다시 묻지 않는다. 사용자에게 같은 일을 두 번 시키지 않는다.
- 원본 자료 보유 여부는 이 경로에서는 § 7 depth pass 에서 다룬다. export 에 주제별 `[있음]`/`[없음]` 마커가 있으면 그것을 우선 신호로 쓴다.
- export 가 임의 이름의 파일로 이미 `roots/` 에 놓여 있어도 § 5 를 건너뛰지 않는다. § 5 의 명명 규약 (claim summary + `_transcripts/` 보존본) 에 맞춰 정규화해 기록한다.

### 1. 모델 설명

아래 고정 문구를 **그대로** 보여준다. 매번 새로 쓰지 않는다. 기준은 `docs/QUALITY.md § Onboarding copy rubric` 이다.

````text
naite 는 한 사람의 모든 지식과 경험을 모아두는 저장소이자, 그 사람의 에이전트들이 함께 읽는 공통 맥락입니다.

데이터는 두 층입니다.
- roots: 원본 자료가 그대로 들어가는 곳입니다 (대화 export, 강의 노트, 논문, 아티클). 손대지 않은 출처입니다.
- tree: roots 를 소화해 만든 위키 형식의 페이지 공간입니다. 페이지끼리 wikilink 로 연결됩니다. 기록하는 내용의 종류에 따라 나무를 여러 개 만들 수 있습니다 (예: ai 나무, 통계 나무).

한 나무의 페이지 종류입니다.
- 줄기(trunk): 그 나무의 목차이자 뼈대가 되는 페이지입니다. 여기서 가지가 뻗어 나갑니다.
- 잎(leaf): 사용자 본인의 지식과 경험을 적은 페이지입니다. 위키백과처럼 잎끼리 서로 link 로 이어집니다.
- 열매(fruit): 사용자가 내린 결정과 그때 얻은 통찰을 적은 페이지입니다.
- 나이테(rings): 이 저장소가 시간에 따라 쌓이고 자라온 기록입니다.

파일을 모아두는 것과, 서로 링크되어 다시 꺼내 쓸 수 있게 되는 것은 다릅니다. naite 는 자료를 쌓아두는 폴더가 아니라, 나중에 사용자와 에이전트가 함께 읽고 연결을 따라갈 수 있는 살아 있는 위키입니다.
````

### 2. 깊이 경로 선택 + 이전 프롬프트 전달

먼저 한 줄로 묻는다: "원본 자료(강의 노트, 논문, 문서, 전체 대화 export)를 가지고 계신가요?"

- **A. 메모리로 골격 먼저:** 원본이 마땅치 않으면, 다른 AI 의 기억에서 골격을 먼저 깐다. 사용자가 ChatGPT / Gemini / claude.ai 중 어디서 가져올지 묻고, `docs/migrate-prompt.md` 의 프롬프트를 해당 서비스 팁과 함께 제시한다.
- **B. 원본 자료로 깊이 (권장):** 원본이 있으면, 메모리 골격과 함께 그 자료로 깊이를 채운다. 메모리 프롬프트로 골격을 깔되, 깊은 주제는 6~7단계에서 원본 파일을 직접 ingest 한다.

회상은 골격과 색인에 좋고, 위키 깊이는 원본 자료에서 나온다. 두 경로는 배타적이지 않다.

### 3. import 받기

사용자가 자기 AI 에 붙여넣고 받은 export(Markdown 한 덩어리) 를 가져온다.

### 4. import 검수 게이트

`docs/QUALITY.md § Import 검수 게이트` 의 기준으로 export 를 판정한다. 기준 목록의 단일 진실원은 QUALITY.md 다 (여기 다시 적지 않는다). 판정은 섹션 번호·제목 문자열이 아니라 내용으로 한다. 결과는 두 갈래다.

- **반려 기준 해당 (자기소개 부재, 깊이 부족, secrets/PII):** ingest 로 넘기지 않고 사용자에게 보완을 요청한다. 되돌릴 때의 한 줄 예: "자기소개를 채우고, 배운 것의 항목 몇 개를 문단으로 전개해 다시 생성하거나, 원본 자료를 첨부해 주세요." 통과할 때까지 다음 단계로 가지 않는다.
- **정규화 기준만 해당 (정본 아닌 프롬프트가 남긴 섹션·제목 잔재):** 반려하지 않는다. 통과로 보고 § 6 skeleton pass 에서 정규화한다.

### 5. roots 에 안전하게 기록

1. export 내용에 `capture.md § 4` secrets pre-check 를 돌린다. 적중하면 멈추고 사용자에게 알린 뒤 redact 를 제안한다.
2. 통과하면 두 곳에 쓴다 (서비스 식별자 `<service>` 는 `chatgpt` / `gemini` / `claude` 중 하나).
   - 임시 claim summary: `roots/conversations/YYYY-MM-DD-memory-migration-<service>.md` (grow 후 `ingest` 가 삭제하는 ephemeral 스테이징).
   - 영구 보존본: `roots/conversations/_transcripts/migration-<service>.md` (**서비스별 stable 이름**, 날짜 prefix 없음). import 를 다시 하면 이 파일을 갱신하고 새 날짜의 claim summary 를 만든다. 이 stable 이름은 "재import 시 갱신" 을 위한 의도된 컨벤션이다 (`CONVENTIONS.md § Naming` 참조).
3. `_transcripts/` 보존본은 사용자의 distilled 메모리 원본이자 재-grow 보험이다. 절대 삭제하지 않는다.

### 6. 골격 세우기 (skeleton pass)

`SKILL_DIR/ingest.md` 를 읽고 그 전체 워크플로를 `<path> = <NAITE_ROOT>/roots/conversations/YYYY-MM-DD-memory-migration-<service>.md` 로 실행한다. 이것은 grow 의 conversation 모드가 capture 직후 쓰는 것과 **같은 ingest 프리미티브**다. file 모드(article 이동 로직) 와 Branch pre-check 를 거치지 않으므로, 여러 주제가 섞인 export 가 branch 모드로 오탐될 일이 없다.

이 패스의 결과물은 **골격**이다. 자기소개 페이지, subject 경로, 그리고 각 주제의 잎이다. 원본 자료가 없어 `[없음]` 이거나 "(원본 자료 필요)" 로 표시된 주제는 얕은 stub 으로 정직하게 남기고, `seeds.md` 에 깊이 보강 후보로 적는다.

§ 4 에서 정규화 대상으로 판정된 옛 프롬프트 잔재는 이 패스에서 흡수한다. 결정·통찰에 해당하는 내용은 제목이 달라도 (예: "트레이드오프") 열매(`kind=decision`) 재료로 그대로 쓰고, "미해결 질문" 류 항목은 schema home 이 없으므로 `seeds.md` 후보로 옮기거나 버린다. 처리 내역은 사용자에게 한 줄로 알린다.

잎·맥(wikilink)·열매(`kind=decision`)·`subject`/facet 변환과 rings 기록은 전부 `ingest` 가 한다. start 는 스키마를 직접 손대지 않는다.

`ingest` 의 사후 삭제(§ 8)는 넘긴 경로, 즉 날짜가 붙은 claim summary(`YYYY-MM-DD-memory-migration-<service>.md`)만 지운다. 영구 보존본은 이름이 다른 stable 파일(`roots/conversations/_transcripts/migration-<service>.md`)이라 삭제 대상에 해당하지 않는다.

### 7. 깊이 채우기 (depth pass)

export 에서 `[있음]` 으로 표시된 주제는, 그 원본 자료로 골격 잎을 진짜 위키 페이지로 채운다. 사용자에게 해당 파일(강의 노트, 논문 PDF, 전체 대화 export 등)을 받아, `SKILL_DIR/grow.md` 의 **file 모드**로 ingest 한다. 한 과목·책·시리즈처럼 긴 호흡이면 grow 의 **branch 모드**가 적절하다 (이 경우 Branch pre-check 가 제대로 작동해야 하므로, 골격 패스와 달리 grow 를 정상 경로로 탄다).

원본 자료가 없는 주제는 stub 으로 둔다. 나중에 자료가 생기면 `/naite grow` 로 보강한다. 깊이는 원본에서 나온다는 점을 사용자에게 한 줄로 알린다. depth pass 로 넣는 원본 자료는 §4 게이트가 아니라 grow 자신의 `capture.md § 4` secrets pre-check 를 거친다. grow 가 그 검사를 전담한다.

### 8. reflect / 그래프 보기

`ingest`/`grow` 가 만든 페이지 요약(생성·갱신된 페이지, 다음 단계) 을 받은 뒤, 사용자에게 그래프 뷰를 열어보라고 안내한다: Obsidian 으로 vault 를 열거나 naite-app 의 Forest 뷰를 연다. 막 생긴 자기 나무가 링크된 네트워크로 보이는 것이 납득의 순간이다.

마지막으로 고정 문구로 닫는다 (그대로 보여준다).

````text
방금 본 이 그래프는 전부 당신이 직접 쌓은 것입니다. 이제 이 나무는 당신의 다른 AI 에이전트가 당신을 이해하는 공유 맥락이 됩니다. 새 작업을 시작할 때 /naite ask 로 "내가 X 에 대해 이미 아는 것" 을 먼저 꺼내 쓰세요.
````

이어서 다음 한두 수를 제안한다 (관심 주제로 `/naite ask`, 새 자료로 `/naite grow`).

### 9. 표면 준비 (선택, 동의 기반)

나무가 처음 생긴 뒤, 에이전트의 instruction surface 를 갖출지 **제안한다** (단정하지 않고 사용자 동의로 채운다).

- **USER.md**: 응답 선호를 한두 가지 묻고 (톤·길이·피할 것 등), 동의하면 `.naite/templates/USER.md` 를 vault 루트 `USER.md` 로 복사해 채운다. PII 는 적지 않고, 신원은 `[[personal-profile]]` 로 가리킨다. 루트 `USER.md` 는 `.gitignore` 되어 공개되지 않는다.
- **MEMORY.md**: 진행 중 작업·운영 사실을 모을 곳이 필요하면 `.naite/templates/MEMORY.md` 를 루트 `MEMORY.md` 로 복사한다. 비워 두고 시작해도 된다.
- **SOUL.md**: 에이전트의 기본 정체성·응답 스타일이 담긴 파일임을 한 줄로 안내한다. 톤을 바꾸고 싶으면 이 파일을 함께 다듬는다.

사용자가 원치 않으면 만들지 않는다. 표면이 없으면 bootloader 가 자동으로 건너뛴다. 이 단계는 `tree/` 를 건드리지 않는다.

## What this command never does

- `roots/` 의 import 기록과 (동의 시) 루트 instruction surface (`USER.md`/`MEMORY.md`) 외에는 직접 쓰지 않는다. `tree/` 변환은 `ingest`/`grow` 에 위임한다.
- secrets pre-check 를 건너뛰지 않는다.
- 게이트를 통과하지 못한 얕은 export 를 ingest 하지 않는다.
- 새 rings op 를 만들지 않는다.
- Never commits to git.
