# /naite grow

grow 는 나무를 키우는 단일 진입점이다. 대화와 파일과 장기 과정(branch)과 받아두기(stage-only)를 자동 감지해서 tree 에 반영한다. 저수준 절차의 계약은 내부 모듈(`capture.md`, `ingest.md`, `grow-branch.md`, `grow-backfill.md`)이 소유하고, grow 는 그 위의 라우터다. grow 는 모듈에 없는 동작을 새로 발명하지 않는다.

아래 모든 데이터 경로(`roots/articles/`, `roots/conversations/` 등)는 naite vault 의 루트인 NAITE_ROOT 기준으로 해석한다. 하위 스킬 참조는 SKILL_DIR(`<NAITE_ROOT>/.agents/skills/naite`) 기준으로 해석한다. 맥락은 `SKILL.md` 가 담당한다.

## 사용 시점

사용자가 학습 세션을 방금 마쳤거나 마치는 중일 때 켜진다. 트리거는 다음과 같다.

- 학습 대화 직후의 "tree에 반영해줘"나 "update the tree".
- 경로가 첨부된 "이 PDF·강의록 공부했어".
- 전사본이 붙거나 staged 파일이 있는 "이 유튜브 강의 봤어, 정리 부탁".
- 소스만 던져지고 의도가 없는 경우. grow 가 받아두기(stage-only)까지 담당한다.

소스만 있고 새 대화 맥락이 없으면 file 모드가 ingest 내부 모듈을 호출해서 처리한다.

## 모드 감지

`args` 와 대화 맥락을 파싱한다.

| 신호 | 모드 | 실행 |
|---|---|---|
| args 없음 + 직전에 학습 대화 | conversation | 2절 |
| args 가 존재하는 파일·디렉터리 경로 + 반영 의도 | file | 3절 |
| 첫 토큰이 `backfill {slug}` | backfill | `grow-backfill.md` 의 Workflow 절로 위임한다 |
| 장기 과정 신호 (Branch pre-check 절) | branch | `grow-branch.md` 로 위임한다 |
| 소스만 던져지고 반영 의도 불명 | stage-only | 4절 |
| 경로가 존재하지 않음 | 질문 | topic slug 인지 오타인지 사용자에게 확인한다. 짐작하지 않는다 |

## Branch pre-check (장기 과정 감지)

conversation 이나 file 모드로 가기 전에, 이 학습이 하나의 큰 줄기 아래 이어지는 과정(과목, 책 한 권, 강의 시리즈)인지 신호를 확인한다.

- syllabus 나 목차 스크린샷이나 여러 강의 파일의 업로드.
- 한 프레임 아래 네 개 이상의 구분되는 개념 ("X 프레임워크의 4 역량", "Ch1~Ch3 정리").
- "이번 학기"나 "Ch{N}"이나 과목코드나 책 제목과 챕터의 언급.
- 연속물임이 명백한 파일명 (`Ch1 ...`, `Lecture 02 ...`).

신호가 잡히면 멈추고 한 줄로 확인한다: "단발 학습이 아니라 긴 호흡(branch) 같은데, branch 모드로 갈까요? (y → branch, n → 단발로 계속)"

무응답은 동의가 아니다. 답이 없으면 보수적으로 단발 모드로 진행하되, branch 메타데이터가 빠지므로 나중에 branch 모드로 보강이 필요하다고 경고한다.

## 강행 규칙 (상속)

- `roots/` 는 아래에 기술된 보관·staging 이동을 제외하면 불변이다 (`ingest`·`capture` 와 같은 규칙이다).
- `tree/` 는 LLM 이 소유한다. 모든 실질 변경은 쓰기 전에 사용자의 확인을 받는다.
- `roots/conversations/` 에 무엇이든 쓰기 전에 `capture.md` 4절의 비밀 사전 검사를 실행한다.
- 이 스킬은 자기 몫의 rings 항목을 쓰지 않는다. 하부의 `capture` 와 `ingest` 실행이 기록의 주체다 (`capture` 는 기록하지 않고 `ingest` 가 기록한다).
- Writer 불변식: ingest 가 원천 메커니즘을 보존하고, "원본 필요"는 정말 없는 자료에만 쓴다.
  - 각 `form=prose` 잎은 작성 시점에 `docs/QUALITY.md` 4절(LEAF-1~6)과 `docs/CONVENTIONS.md` 의 학습 노트 품질 축과 kind 별 품질 계약으로 gating 된다.
  - `## Source` 앞의 본문에는 em dash(`—`)를 쓰지 않는다 (`ingest.md` 5절 참조).

## Workflow

### 1. 모드 확정

- 빈 vault 선검사: `tree/` 에 `trunk.md` 와 `rings.md` 와 `seeds.md` 외의 페이지가 없으면(빈 vault) 한 줄로 제안한다: "vault 가 비어 있습니다. 처음이시면 `/naite start` 로 안내형 첫 세션을 권합니다 (y → `/naite start` 로 전환, n → grow 계속)." 거절이면 grow 를 정상 진행한다. 이미 자란 vault 면 이 선검사는 조용히 통과한다.
- `args` 가 비어 있으면 conversation 모드로 간다. 단 Branch pre-check 신호가 잡히면 branch 모드다.
- 첫 토큰이 `backfill {slug}` 면 backfill 모드로 가고 `grow-backfill.md` 의 Workflow 절로 위임한다.
- 장기 과정 신호가 잡히면 branch 모드로 가고 `grow-branch.md` 로 위임한다.
- `args` 에 경로 토큰이 있으면 경로를 해석한다.
  - 절대 경로는 그대로 쓴다.
  - 상대 경로는 vault 루트 기준으로 해석한다.
  - 존재하고 반영 의도가 명확하면 file 모드다.
  - 존재하지만 반영 의도가 불명확하면 stage-only 모드다 (4절).
  - 존재하지 않으면 conversation 모드용 topic slug 인지 오타인지 사용자에게 묻는다. 짐작하지 않는다.

### 2. Conversation 모드

1. `<SKILL_DIR>/capture.md` 를 읽고 그 1~4단계(topic slug → claim 요약 → 원문 전사 → 비밀 사전 검사)를 실행한다. 경로는 `<NAITE_ROOT>/roots/conversations/YYYY-MM-DD-<topic-kebab>.md` 와 `_transcripts/` 쌍둥이다.
2. capture 가 끝나면 쓴 내용을 요약하고 한 가지를 묻는다.
   > "바로 tree 에 반영할까요? (y / later / cancel)"
3. `y` 면 `<SKILL_DIR>/ingest.md` 를 읽고 `<path> = <NAITE_ROOT>/roots/conversations/YYYY-MM-DD-<topic>.md` 로 전체 워크플로를 실행한다. ingest 8단계의 grow 이후 처리가 이 claim 요약을 삭제하고, `roots/conversations/_transcripts/` 의 원문 쌍둥이는 영구 보험으로 남는다.
4. `later` 나 `cancel` 이면 `<SKILL_DIR>/capture.md` 5절의 마무리 문장으로 끝낸다. tree 변경은 없다.

### 3. File 모드

확장자와 위치에서 소스 종류를 판별하고, `ingest` 에 위임하기 전에 사전 단계를 실행한다.

비밀과 PII 사전 검사 (file 모드의 모든 소스): 파일을 이동하거나 ingest 하기 전에 그 내용을 `capture.md` 4절의 비밀·PII 목록으로 검사한다. guard 훅은 커밋 시점에만, 그것도 토큰 패턴에만 발동하므로, 아티클이나 PDF 안의 비밀·PII 가 `tree/` 에 닿기 전에 잡는 층은 file 모드다. 걸리면 멈추고 삭제 처리를 제안한다. ingest 로 진행하지 않는다.

경로 인식 라우팅 (이미 관리되는 roots 하위 폴더에 있는 파일은 이동하지 않는다): 아래의 "`roots/articles/` 로 이동" 규칙은 사용자가 vault 루트나 Downloads 나 비슷한 임시 위치에 떨어뜨린 파일에만 적용된다.

- `roots/conversations/` 아래의 경로는 캡처된 대화이지 아티클이 아니다. 대화 ingest 경로(2절이 쓰는 것과 같은 primitive)로 라우팅한다. 그래야 `ingest` 8절이 일시적 claim 요약을 삭제하고 `_transcripts/` 쌍둥이를 지킬 수 있다. `roots/articles/` 로 옮기면 grow 이후 삭제 계약과 쌍둥이 짝이 깨지므로 절대 옮기지 않는다.
- `roots/legacy/` 아래의 경로는 legacy import 다. `ingest --legacy <path>`(wikilink 번역 pass)로 라우팅한다. 이 pass 는 파일이 `roots/legacy/` 에 남아 있기를 전제한다. `roots/articles/` 로 옮기지 않는다.
- 이미 `roots/articles/` 나 `roots/courses/` 아래에 있는 경로는 제자리에 둔다.

#### 3a. `.md` 또는 `.txt`

- 이미 `roots/articles/` 나 `roots/conversations/` 나 `roots/legacy/` 나 `roots/courses/` 아래에 있으면 이동 없이 위의 경로 인식 규칙대로 라우팅한다.
- 그 밖의 위치(예: vault 루트나 Downloads 에 떨어뜨린 파일)면 basename 을 kebab-case 로 바꿔 `roots/articles/<slug>.md` 로 옮긴다. 원본 내용은 바이트 단위로 보존한다. 그 다음 `ingest roots/articles/<slug>.md` 로 위임한다.

#### 3b. `.pdf`

1. `roots/articles/_source/` 가 없으면 만든다. 원본 PDF 를 `roots/articles/_source/<name>.pdf` 로 옮긴다. 원본이 vault 밖에 있으면 복사만 하고, 외부 파일은 절대 수정하지 않는다.
2. 텍스트를 `roots/articles/<slug>.md` 로 추출한다. 세션에서 쓸 수 있는 도구(PDF 에 대한 Read, 로드된 PDF 스킬)를 쓴다. 쓸모 있는 곳에서는 `## p.<n>` heading 으로 페이지 경계를 보존한다. 추출 품질이 나쁘면(OCR 없는 스캔 PDF, 깨진 글자) 무엇이든 쓰기 전에 멈추고 사용자에게 알린다. 얻은 것으로 계속할지 미룰지 묻는다.
3. 추출된 md 의 맨 위에 한 줄 포인터를 더한다.
   ```
   > Source PDF: `roots/articles/_source/<name>.pdf`
   ```
4. `ingest roots/articles/<slug>.md` 로 위임한다. 현행 규칙(`docs/CONVENTIONS.md` 의 grow 이후 처리 절)대로 추출 md 는 grow 후에도 `roots/articles/` 에 남는다. 아티클은 보관 이동되지 않는다. 원본 PDF 는 `roots/articles/_source/<name>.pdf` 에 위치한다.

#### 3c. YouTube · 영상

URL 만 있는 입력은 소스가 아니다. 전사본 md 파일을 먼저 요구한다.

- 사용자가 전사본을 인라인으로 붙이면 `roots/articles/<slug>.md` 에 쓰고, 맨 위에 `source-url:` 과 `date-watched:` 를 자유 형식으로 적는다 (tree frontmatter 가 아니다. 이 파일은 raw 파일이지 tree 페이지가 아니다).
- 전사본이 아직 없으면 멈추고 사용자에게 안내한다. Obsidian Web Clipper 나 YouTube 자체의 전사 내보내기나 사용 가능한 MCP 도구를 가리킨다. URL 만으로는 진행하지 않는다.
- 전사본 md 가 생기면 `ingest roots/articles/<slug>.md` 로 위임한다.

#### 3d. 그 밖의 확장자

표시하고 묻는다. 조용히 변환하지 않는다. Office 형식(`.docx`, `.pptx`)과 스프레드시트와 압축 형식은 각각 자기 사전 단계나 다른 스킬이 필요하다.

### 4. Stage-only 모드 (받아두기)

소스는 던져졌는데 "반영해줘" 의도가 없거나 불명확할 때 쓴다. 물만 주고 심지는 않는 단계다.

1. 소스 종류를 판별해서 3절 file 모드의 사전 단계까지만 수행한다 (정규화된 이름으로 `roots/` 아래 저장. md·txt 는 `roots/articles/<slug>.md` 로, pdf 는 `roots/articles/_source/` 와 추출 md 로, 대화는 capture 절차로).
2. `tree/` 는 건드리지 않고 `tree/rings.md` 에도 쓰지 않는다 (roots 층만 만진다).
3. 한 줄로 확인한다: "`roots/` 에 받아뒀습니다. 지금 심을까요? (y → 이어서 반영 / later → 여기까지)"
4. `y` 면 3절의 본 절차로 이어서 진행한다. `later` 면 받아둔 경로만 알려 주고 끝낸다.

### 5. Mixed 모드 (파일 + 새 대화 맥락)

사용자가 같은 주제의 실질적인 Q&A 직후에 `grow <path>` 를 실행했으면, 대화 자체가 raw 파일에 없는 takeaway 를 담고 있다. 별도의 `capture` 파일을 쓰지 않는다 (내용이 이중으로 계산된다). 대신 다음처럼 한다.

- 대화의 takeaway 를 `ingest` 의 4단계("Discuss takeaways")에 전달한다. 사용자 맥락으로 풀어 전해서, 어떤 페이지가 만들어지고 요약이 어떤 모양이 될지에 반영되게 한다.
- 대화에 소스가 뒷받침하지 않는 claim 이 있었으면 tree 페이지 본문에 `_YYYY-MM-DD conversation note (not in source): …_` 로 표시한다. 출처의 정직함을 지킨다.

### 6. Checkpoint

하부의 `ingest` 실행이 끝나면(또는 conversation 모드가 ingest 없이 끝나면) 사용자에게 한 문단 요약을 준다.

- capture 파일 경로 (만들었으면).
- 만들거나 갱신한 페이지 (ingest 실행 결과).
- 다음 단계 (예: "몇 번 더 grow 한 뒤 `/naite care --check` 실행").

반영한 자료에 명확한 결정·trade-off·실패 분석이 있으면(신호: "선택했다·보류했다·비교했다·실패했다"와 근거) 다음도 제안한다: "이거 `/naite fruit` 로 의사결정 thread 까지 박아둘까요?" 상세는 `docs/CONVENTIONS.md` 의 Decision thread 형태 절이 담당한다.

## 이 명령이 절대 하지 않는 것

- `capture` 와 `ingest` 의 단계별 사용자 확인을 우회하지 않는다.
- 자기 몫의 기록을 하지 않는다 (`rings.md` 항목은 하위 스킬이 쓴다).
- PDF 와 office 바이너리를 `tree/` 에 쓰지 않는다.
- grow 의 단발 경로(conversation·file·stage-only)는 git commit 을 하지 않는다. branch 모드의 커밋과 push 는 `grow-branch.md` 의 E·F 절이 담당한다.
