# capture — grow 내부 모듈

이 파일은 사용자 노출 명령이 아니다. `/naite grow` 가 위임하는 내부 모듈이다.

capture 는 현재 대화의 지식을 `roots/conversations/` 로 스냅샷한다. `tree/` 는 건드리지 않는다. 나무로 접는 병합은 사용자가 시작하는 별도의 grow ingest 단계가 담당한다.

## 사용 시점

사용자가 에이전트와 학습 대화(데스크톱 채팅, cowork, 코드 표면)를 하다가 "tree 업데이트해줘"나 "capture this"나 "방금 다룬 것 저장해줘"라고 말하면 이 모듈이 켜진다.

## 강행 규칙

- 쓰기는 `roots/conversations/` 아래에만 한다.
  - `tree/` 아래의 페이지를 만들거나 고치지 않는다. `trunk.md` 와 `rings.md` 와 `seeds.md` 를 편집하지 않는다.
- capture 하나는 수명이 다른 두 파일을 만든다.
  - claim 요약: `roots/conversations/YYYY-MM-DD-<slug>.md`. 일시적 staging 파일이다. grow ingest 단계가 grow 성공 후 이 파일을 삭제한다 (`ingest.md` 8절). 이 파일은 ingester 에게 넘기는 전달 봉투이지 장기 보존물이 아니다.
  - 원문 전사 쌍둥이: `roots/conversations/_transcripts/YYYY-MM-DD-<slug>.md`. 영구 보험 사본이다. 어느 스킬도 삭제하지 않는다. claim 요약의 추출이 손실됐으면 이 전사본이 재캡처를 가능하게 한다.
  - 두 파일 모두 필수다. 전사본 하나만으로는 capture 가 아니다.
- 파일명 slug 는 `YYYY-MM-DD-<topic-kebab>.md` 다. 오늘 날짜에 같은 slug 가 이미 있으면 `-2`, `-3` 을 붙인다.
- 끝에는 후속 단계를 사용자에게 알린다: "run `/naite grow roots/conversations/<file>` to fold this in."

## Workflow

> [!IMPORTANT]
> 2절과 3절에서 무엇이든 쓰기 전에, 대화 내용에 4절(비밀과 PII 사전 검사)을 먼저 실행해야 한다. 절 번호는 쓰기 순서이지만 검사는 두 쓰기 모두에 앞서는 관문이다. 텍스트가 한번 디스크에 오르면(특히 영구 보존되는 `_transcripts/` 쌍둥이) 비밀은 이미 유출된 것이다. slug 를 정하고(1절), 검사하고(4절), 그 다음에 쓴다(2절, 3절).

### 1. 주제 slug 결정

사용자가 주제를 지정했으면(`/naite grow transformer-attention`) kebab-case 로 바꿔 그대로 쓴다. 지정하지 않았으면 대화의 초점에서 slug 를 제안하고, 쓰기 전에 한 줄로 사용자의 확인을 받는다.

### 2. claim 수준 요약 작성

경로: `roots/conversations/YYYY-MM-DD-<topic-kebab>.md`

frontmatter:

```yaml
---
source: <the assistant/service this came from, e.g. claude-desktop, chatgpt, gemini, codex>
surface: chat | cowork | code
date: YYYY-MM-DD
topic: <natural language topic>
---
```

본문 구조:

```markdown
# <Topic>

## Context
One or two sentences on what the user was doing or thinking about.

## Claims
- <Claim 1, self-contained. One concept per bullet.>
- <Claim 2>
- ...

## Open threads
- <Things the user wanted to look into later, unresolved questions.>

## Proposed tree touchpoints
- new: `[[proposed-slug]]` (type) — one-line rationale
- update: `[[existing-slug]]` — what changes
```

claim 은 원자적이고 출처를 붙일 수 있게 유지한다. claim 하나는 tree 페이지에서 홀로 살 수 있는 내용이어야 한다. 잡담과 도구 호출 로그와 나중에 인용할 수 없는 내용은 건너뛴다.

### 3. 원문 전사 쌍둥이 작성

경로: `roots/conversations/_transcripts/YYYY-MM-DD-<topic-kebab>.md` (2절과 같은 slug).

이 파일이 보험이다. claim 추출이 손실됐거나 틀렸어도 전체 전사본이 보존되어 있으면 나중에 재캡처할 수 있다.

내용은 대화를 raw 산문으로 담고 `**User:**` 와 `**Claude:**` 턴 라벨을 붙인다. 도구 호출 출력은 사용자가 중요하게 여긴 실질 신호가 아니면 접는다. 수천 단어 분량의 붙여넣기도 괜찮고, 자르지 않는다.

### 4. 비밀과 PII 사전 검사

이 검사는 두 파일 중 어느 것이든 쓰기 전에 실행한다 (claim 요약과 원문 전사 쌍둥이 모두. 쌍둥이는 영구 보존이라 검사 없이 들어간 비밀도 영구가 된다). 내용에서 다음을 찾는다.

- API 키·토큰·개인 키: guard 훅이 차단하는 것과 같은 계열이다 (`.naite/hooks/pre-commit` part 2 가 단일 소스이고 이 목록은 그것과 동기화를 유지한다).
  - `sk-...`(Anthropic `sk-ant-...`, OpenAI `sk-proj-...`), GitHub `ghp_`·`gho_`·`ghs_`·`github_pat_`, GitLab `glpat-`, Slack `xox[baprs]-`, AWS `AKIA...`, Google `AIza...`, JWT(`eyJ....eyJ...`), PEM `-----BEGIN ... PRIVATE KEY-----`.
  - Stripe `sk_live_` 와 HuggingFace `hf_` 와 npm `npm_` 와 SendGrid `SG.` 와 Slack webhook URL 도 발견되면 포함한다.
- 자격 증명 줄: `password:` 나 `api_key:` 나 `token:` 이나 `Authorization: Bearer ...` 뒤에 실제처럼 보이는 값이 붙은 경우 (`xxx` 나 `<redacted>` 나 `your-key-here` 는 제외).
- URL 이나 해시처럼 보이지 않는 40자 이상의 고엔트로피 문자열.
- PII(개인 식별 정보): 한국 주민등록번호(`######-#######`), 전화번호, 신용카드 모양의 16자리 연속 숫자, 전체 도로명 주소, 국가 신분증 번호.
  - 결정론 guard 훅은 PII 를 잡지 못하므로 이 LLM 판단 검사가 1차 PII 관문이다. 하류 층이 잡아 줄 것이라고 가정하지 않는다.

무엇이든 걸리면 쓰지 않는다. 사용자에게 보고하고 삭제 처리를 제안한다. 비밀이 이미 이전 커밋에 들어갔으면(이 관문을 지나쳤거나 `--no-verify` 로 커밋된 경우), 지금 파일을 고쳐도 git 이력과 영구 `_transcripts/` 쌍둥이에서는 제거되지 않는다는 사실을 알리고, 안전한 대응은 노출된 자격 증명의 rotate·revoke 와 필요하면 공유 원격에 push 하기 전의 이력 재작성(`git filter-repo`)이라고 안내한다.

### 5. 후속 안내

정확히 한 문장으로 끝낸다.

> roots/conversations/YYYY-MM-DD-<topic>.md 에 기록해 두었습니다. 나무에 심으려면 /naite grow roots/conversations/YYYY-MM-DD-<topic>.md 를 실행해 주세요 (전부 심으려면 /naite grow roots/conversations/).

### 6. rings 기록 없음

capture 단계는 `tree/rings.md` 에 쓰지 않는다. rings 기록은 tree 층 변경의 몫이다. 뒤따르는 grow ingest 단계가 기록된다.

## 이 모듈이 절대 하지 않는 것

- `tree/` 아래에 쓰지 않는다.
- git 커밋을 하지 않는다.
- 스스로 grow 를 결정하지 않는다. capture 만 한다.
- 같은 slug 의 기존 파일을 덮어쓰지 않는다. `-2`, `-3` 을 붙여 구분한다.
