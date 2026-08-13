# /naite care

care 는 나무를 돌본다. 하나의 명령 아래 두 모드가 있다.

- 점검 모드 (`/naite care --check`): 결정론 건강 점검이다. report-only 로 동작하고 절대 고치지 않는다. 비밀이 발견되면 차단 게이트가 작동한다. 절차의 계약은 `care-check.md` 가 소유한다. `--check` 플래그나 "점검만"이나 "상태 봐줘" 류의 의도가 감지되면 `care-check.md` 를 읽고 그대로 따른다.
- 돌봄 모드 (기본): 정성 검토와 직접 수선과 대규모 정리와 반복 결함의 규칙화를 담당한다. 이 파일이 계약이다.

모드 판별: `--check` 플래그가 있으면 점검이다. "고쳐줘"나 "다듬어줘"나 "검토하고 수선까지"면 돌봄이다. 애매하면 한 줄로 묻는다.

## 사용 시점

사용자가 다음을 요청할 때 쓴다.

- 검토와 다시 훑기와 quality check 와 내용이 이상한 곳 찾기.
- branch 전체나 특정 branch 내용의 다듬기.
- care --check 로는 잡기 어려운 산문 품질과 소스 화법과 링크 유용성의 판단.
- 반복 결함을 생산자 스킬이나 care --check 규칙이나 `docs/CONVENTIONS.md` 에 반영하기.

## Scope

지원되는 scope 는 다음과 같다.

- `/naite care {slug}`: 페이지 하나와 그 직접 그래프 맥락.
- `/naite care branch-{slug}`: 한 branch 의 branch 메타와 chapter 메타와 모든 subchapter 페이지 (페이지 이름은 course-{slug}-* 다).
- `/naite care --branches`: 모든 branch 페이지.
- `/naite care --fruits`: 결정 꼴 페이지와 그 무게 있는 링크.
- `/naite care --all`: 나무 전체의 정성 정리.
- `/naite care --system`: 지속되는 워크플로 학습이다. 반복 실패에서 생산자 계약이나 care --check 기준이나 워크플로 문서를 갱신한다.
- `/naite care --daily`: `/naite care --check --daily` 다음에 실행하는 report-only 일일 분류다. care --check 의 인계를 검토하고, 우선 후보의 증거를 읽고, tree 내용을 편집하지 않은 채 짧은 분류 보고를 남긴다.

큰 scope 에서는 작업 산출물을 `.naite/reports/{YYYY-MM-DD}-care/` 나 `tmp/care-{YYYY-MM-DD}/` 에 적절히 쓴다. `.naite/reports/` 는 지속 보고용이고 `tmp/` 는 폐기 가능한 작업 로그용이다.

일일 분류는 `.naite/reports/daily/YYYY-MM-DD-care.md` 에 쓴다. 일일 자동화가 안정된 출력 위치를 갖게 하기 위해서다.

## 컨텍스트 지도

검토나 수선 전에 `docs/CONTEXT.md` 를 읽고 생성된 운영 지도를 로드한다.

- `.naite/ontology/tree-manifest.json`: 페이지 좌표와 후보 좁히기에 쓴다.
- `.naite/ontology/tree-dependencies.json`: inbound 의존 페이지와 outbound 링크와 soft relation 관용구와 고연결 페이지와 orphan 후보에 쓴다.

둘 중 하나라도 없거나 현재 작업 기준으로 낡았으면 다음을 실행한다.

```powershell
python .naite/scripts/build-tree-manifest.py
python .naite/scripts/build-tree-dependencies.py
```

페이지 하나의 수선에서는 편집 전에 그 slug 의 inbound 항목을 점검하고, 지도 재생성 후에 다시 점검한다. 의미 의존 후보는 surface 하되, 사용자가 그 수선 범위를 요청하지 않았으면 다시 쓰지 않는다.

## Modes

care 는 내부 모드 다섯을 가진 한 스킬이다. 모드는 사용자 의도에서 고르고, 의도가 정말 모호할 때만 묻는다.

### Review

요청된 페이지와 frontmatter 와 직접 관련된 링크를 읽는다. 구체적인 페이지 예시가 든 산문 평가를 만든다. 점수와 등급과 임계와 rubric 언어를 피한다.

의미적 완결성은 `docs/CONVENTIONS.md` 의 kind 별 품질 계약과 대조해 판단하고, 학습 노트 품질 축 절의 네 축(Markdown form, study effectiveness, content composition, writing manner)을 별도로 점검한다. 길이 자체에 보상을 주지 않는다. 페이지가 건강하다는 것은 kind 별 claim spine 이 쓸모 있고 소스에 근거하며, H 계층이 추론 구조를 드러내고, 나중의 독자가 소스를 다시 열지 않고 주제를 재구성할 수 있다는 뜻이다. 증거의 부재와 약한 글쓰기를 구분한다. 전자는 `source-risk` 나 명시적 공백이지, 내용을 지어낼 허가가 아니다.

평가는 점수가 아니라 평이한 라벨을 쓴다: `healthy` / `thin-but-acceptable` / `repair-candidate` / `source-risk` / `system-rule-candidate`. `source-risk` 는 페이지가 잘 읽히지만 공식과 정의와 정리와 조건과 수치를 소스 검토 없이 다시 쓰면 안 된다는 뜻이다 (`docs/CONVENTIONS.md` 출력 품질 계약의 source-fidelity 상한). 소스를 왜곡할 위험을 지느니 수선을 미룬다.

Review 의 답은 다음을 말해야 한다.

- 이미 쓸모 있는 것.
- 오해를 부르거나 얇은 것.
- 편집이 필요한 페이지.
- 문제가 페이지 국소인지 과목 전체인지 워크플로 수준인지.

### Daily Triage

`/naite care --daily` 에 이 모드를 쓴다. 보통 `/naite care --check --daily` 직후다. 이 모드는 검토이지 수선이 아니다.

- A 단계: 최신 `.naite/reports/daily/YYYY-MM-DD-care-check.md` 가 있으면 읽고, 없으면 대화에 있는 현재 care --check 보고를 쓴다. `.naite/ontology/tree-manifest.json` 과 `.naite/ontology/tree-dependencies.json` 도 읽는다.
- B 단계: care --check 보고의 우선 검토 후보 3개를 시작 큐로 삼는다. 그 절이 없으면 Tier 1 발견에서 다음 순서로 큐를 만든다: 누락 target·stub, 출력 품질 guard, decision·insight 품질, 자율성 쓰레기.
- C 단계: 각 후보에 대해 관련 소스 페이지나 의존성 지도의 출처를 연다. 그 발견이 `false-positive` 인지 `intentional-debt` 인지 `repair-candidate` 인지 `schema-pressure` 인지 판정한다. care --check 의 라벨이 여전히 맞으면 보존한다.
- D 단계: `.naite/reports/daily/YYYY-MM-DD-care.md` 에 다음을 쓴다.
  - 다음에 실제로 검토할 가치가 있는 것.
  - false positive 나 의도된 부채로 무시할 것.
  - 수선 전에 사용자 결정이 필요한 후보.
  - 집중 `/naite care {slug}` 나 `/naite care --fruits` 로 라우팅할 후보.
- E 단계: 사용자가 명시적으로 수선을 요청하지 않았으면 `tree/rings.md` 에 `updated: 0 tree content pages` 로 굵은 항목 하나를 덧붙인다.
  - 일일 분류에서는 어떤 tree 내용 페이지(`tree/*.md` 의 잎·색인)도 편집하지 않고, `tree/trunk.md` 와 `tree/seeds.md` 도 편집하지 않는다.
  - `tree/rings.md` 에 덧붙이는 것이 여기서 허용되는 유일한 쓰기다. 기록은 내용 페이지가 아니다.

### Repair

사용자가 고치기를 요청하면 페이지를 직접 편집한다. 소스의 실질과 기존의 좋은 링크와 frontmatter 는 결함이 거기 있지 않은 한 보존한다. 편집 후에는 바뀐 페이지의 content guard 와 관련 결정론 검사(care --check)를 실행한다.

care-check 가 낡은 `domains` cache 나 BOM 이 붙은 파일을 보고했고 사용자가 수선을 승인하면, 이 모드에서 대응하는 결정론 쓰기 명령을 쓴다.

```powershell
python .naite/scripts/lint-ontology.py --refresh-domains
python .naite/scripts/lint-ontology.py --strip-bom
```

승인된 발견에 필요한 명령만 실행하고, 직후에 `git diff HEAD -- tree/` 를 확인하고, staging 전에 정확히 어떤 페이지가 바뀌었는지 보고한다.

- 최소 침습이 먼저다. 가장 작은 수정으로 결함을 고친다. 확실한 버그라도 이번 turn 의 scope 밖이면 고치지 말고 defer 로 표기한다 (scope 규율이 완벽주의보다 우선한다). 구조 수술(파일 재구성, 대량 재작성)은 최소 침습으로 해결이 안 되는 것이 확실할 때만, 그리고 Sweep 의 무손실 증명을 동반할 때만 한다.
- 변경은 소스에 비례해야 한다. 원본 소스의 변경이 작으면 tree 반영도 작게 유지한다. 다섯 파일 미만이 바뀐 소스 갱신은 위키 페이지도 한두 장만 손대는 것이 정상이고, 작은 원본 변경이 전면 재검토로 번지지 않게 한다. 검토 결과 실제로 고칠 것이 없으면 변경 없음(no-op)도 정당한 결과다. 손댈 이유가 없는 페이지를 완결성만을 위해 억지로 바꾸지 않는다. (계보: openwiki, langchain-ai/openwiki MIT @559788fe. 개념만 증류했고 코드는 복사하지 않았다.)

페이지를 편집한 뒤에는 페이지 좌표가 바뀌었으면 `.naite/ontology/tree-manifest.json` 을, 본문 링크나 soft relation 관용구가 바뀌었으면 `.naite/ontology/tree-dependencies.json` 을 재생성한다. 생성 지도가 바뀌었으면 변경에 함께 포함한다.

#### Organizing pass

사용자가 정리나 재구성이나 다듬기나 학습하기 좋게 만들기를 요청하면, 문장을 다듬기 전에 `docs/CONVENTIONS.md` 의 쓸모 있는 정리의 조직 방식 절을 적용한다.

1. 페이지의 정리 질문과 `kind` 와 `form` 과 source-fidelity 상한을 식별한다.
2. 가장 강한 기존 추론과 사용자가 직접 쓴 voice 를 보존한다. 새 구조를 더하기 전에 반복과 공정 서술을 먼저 제거한다.
3. 본문을 독자의 추론 경로대로 배열한다. 문제나 맥락, 주장, 메커니즘, 필요할 때의 형식화나 절차, 작동하는 예시, 경계, 귀결이나 연결의 순서다. 소스와 페이지 kind 가 뒷받침하는 단위만 쓴다.
4. Markdown 은 의미의 일에 따라 고른다. 인과는 산문으로, 같은 축의 비교는 표로, 병렬 항목과 순서는 목록으로, 형식 관계는 수식으로, 실행 가능하거나 원형 보존이 필요한 재료만 코드블록으로 쓴다.
5. 나중의 독자가 소스를 다시 열지 않고 주제를 재구성할 수 있는지 확인하며 끝낸다. 표준 heading template 과 목표 단어 수와 장식성 요약 절을 강제하지 않는다.

눈에 보이는 결과는 그저 청소된 것이 아니라 의도적으로 조직된 것으로 읽혀야 한다. 더 짧은 페이지는 claim spine 과 메커니즘과 증거와 불확실성과 적용 경계를 보존할 때만 더 낫다.

#### 완료와 재검증 규율

큰 수선 전에는 작업 보고나 대장에 구체적인 완료 집합을 명시한다. 나무 전체 정리에서는 범위 안의 모든 페이지가 정확히 한 번씩 나타나야 하고 누락과 중복과 잘못된 소유자가 없어야 한다. 집중 수선에서는 완료 집합이 지목된 페이지와 워크플로가 명시적으로 허용한 의존 항목뿐이다.

편집 후에는 `docs/CONTEXT.md` 의 검증 무효화와 완료 규율 절을 따른다.

- 통과한 검사는 나중의 편집이 그 검사가 소유한 파일이나 의존물을 건드리기 전까지 같은 스냅샷에서 유효하다.
- 나중의 편집이 무효화한 검사만 다시 실행한다. 통과한 내용·코드·보안·보고 리뷰를 처음부터 다시 시작하지 않는다.
- 보고 전용 편집은 보고 무결성과 diff 검사만 다시 열지, tree 내용이나 생성 지도 검사를 다시 열지 않는다.
- 본문이나 Source 경로의 편집은 바뀐 페이지의 guard 와 해당할 때의 경로 존재 확인과 ontology lint 를 다시 열고, wikilink 나 의미 관계가 바뀌었을 때만 의존성 생성을 다시 연다.
- frontmatter 와 제목과 별칭과 wikilink 와 워크플로와 검증기와 테스트의 편집은 무효화 표의 해당 행을 따른다.
- 발견은 재현 가능하고 활성 완료 계약 안에 있을 때만 blocking 으로 취급한다. 개선 아이디어와 공개된 잔여 부채는 non-blocking 으로 남는다.

완료의 조건: 요청된 산출물이 존재하고, 해당할 때 범위 산정이 정확하고, 관련 결정론 검사가 통과하고, `git diff --check` 가 통과하고, staging 과 외부 행동이 사용자 허가와 일치하고, 무관한 작업이 보존되고, 미해결의 재현 가능한 blocker 가 없어야 한다. 조건이 성립하면 결과를 보고하고 멈춘다. 같은 실행에서 또 다른 감사나 정리나 리팩터링이나 선택적 개선을 추가하지 않는다.

### Sweep

큰 scope 에서는 먼저 반복 가능한 신호를 모은다.

- 본문의 소스·공정 화법.
- 불필요한 영어 문장 골격.
- 범용 rubric heading.
- 무효하거나 장식성인 H 계층: 복수의 H1, 건너뛴 단계, 비었거나 빈약한 잎 heading, 반복된 heading, 끝이 아닌 곳의 `## Source`. 의미 있는 자식 heading 이 뒤따르는 부모 heading 은 유효하다.
- `## Source` 앞의 raw 경로 누출.
- mojibake.
- 관계를 설명하지 않는 얕은 링크 목록.
- raw 노트나 PDF 없이는 이해되지 않는 본문의 페이지.
- kind 별 claim spine 의 누락: 메커니즘이나 경계가 없는 concept, 검증·재검토 상태가 없는 decision, 증거나 범위가 없는 insight, 날짜 있는 증거가 없는 project.
- 조건과 변수 의미와 해석이 없는 수식. 메커니즘을 재생하지 않는 이름뿐인 예시.
- bullet 로 조각난 인과 산문, 입자도가 섞인 목록, 언어가 있는데 태그가 없는 코드펜스, 코드로 감싼 산문이나 수식, 장식성 blockquote, GFM 이 아닌 콜아웃.
- 사전식 정의와 rubric 모양의 bullet 덤프와 왜 중요한지 설명 없이 중요하다고만 하는 문단.
- 관찰과 source claim 과 해석과 가설이 같은 확실성인 것처럼 섞인 글.
- `## Source` 앞 본문의 em dash(`—`). 무조건 하이픈으로 치환하지 말고 한국어 문장부호와 문장 구조로 관계를 다시 쓴다.

그 다음 원인별로 묶고, 사용자가 수선을 요청했을 때만 배치로 고친다. 정리 결과가 이번 turn 을 넘어 중요하면 지속 보고를 남긴다.

inbound 의존 페이지와 고연결 페이지의 선정에는 `.naite/ontology/tree-dependencies.json` 을 쓴다. `tree/trunk.md` 를 전수인 것처럼 걷지 않기 위해 `.naite/ontology/tree-manifest.json` 을 쓴다.

무손실 대량 정리: 대량 삭제와 압축(큰 삭제, 공백 접기, boilerplate 제거)은 두 층으로 분리한다. 기계적 정규화(중복 빈 줄과 후행 공백과 반복 boilerplate 의 제거)와 의미 편집(문장과 내용의 변경)을 섞어서 한 번에 하지 않는다. 대량 정리를 무손실로 주장하려면 증명을 붙인다. 빈 줄을 제외한 diff(`diff <(grep -v '^[[:space:]]*$' old) <(grep -v '^[[:space:]]*$' new)`)로 실질 내용 줄이 보존됐음을 보이고 그 결과를 보고에 남긴다. 증명 없는 대량 삭제는 커밋하지 않는다.

### System Learning

같은 결함이 여러 페이지나 워크플로에 걸쳐 나타날 때 이 모드를 쓴다. 우선순위는 다음 순서다.

1. 생산자 계약을 먼저 강화한다 (`grow.md` 나 `grow-backfill.md` 나 다른 출력 생산 스킬).
2. 패턴이 기계로 검출될 만할 때만 결정론 care --check 가드를 추가한다.
3. 규칙이 워크플로를 가로질러 적용되면 `docs/CONVENTIONS.md` 를 갱신한다.
4. 사용자 대면 멘탈 모델은 단순하게 유지한다: care --check 와 care 둘뿐이다.

스키마 수준의 변경은 여전히 `docs/CONVENTIONS.md` 의 Schema evolution 절을 따른다. 사용자 결정 없이 새 facet 필드와 enum 값과 top-level domain 을 도입하지 않는다.

enum·스키마 불일치를 고칠 때는 전체 불일치(모든 페이지가 spec 과 어긋난 상태로, 수선 대상이다)와 의도된 subset(일부만 다른 것이 설계상 정당한 상태로, 유지한다)을 구별한다. 전자만 수선하고 후자는 건드리지 않는다. 판별이 애매하면 수정하지 말고 surface 한다.

## Branch 내용의 품질 기준

branch 페이지는 강의 원어에 가까운 자립 tree 페이지로 읽혀야 한다. 본문이 의미를 직접 담아야 하고, `## Source` 는 출처이지 의존물이 아니다.

요구 사항:

- 본문 산문은 한국어가 기본이다. 정밀성을 실어 나르는 영어 기술 용어와 수식과 모델 이름과 강의 고유 heading 과 정착된 약어는 허용된다.
- `## Source` 앞의 본문에는 em dash(`—`)가 없어야 한다. 관계에 따라 쉼표와 마침표와 콜론과 괄호와 줄바꿈을 쓴다.
- 범용 heading 은 한국어를 쓴다. 강의 자체가 영어 용어를 개념 단위로 쓸 때만 예외다.
- 손필기와 슬라이드 강조와 예시와 도식은 설명 산문으로 흡수한다. "노트가 말한다"나 "PDF 가 보여 준다"로 서술하지 않는다.
- raw 경로는 끝의 `## Source` 블록에만 나타난다.
- 페이지는 원본 PDF 나 raw 노트나 PNG 나 staging 산출물을 열지 않아도 이해되어야 한다.
- 링크는 무게를 실어야 한다. 링크된 페이지가 여기서 왜 중요한지를 산문이 말한다.

`## Source` 앞의 본문에서 금지되는 것:

- 원자료·공정 화법: "raw", "staging", "source bundle", "PDF page", "page range", "필기에는", "강의 노트에는", "원문에서는", "자료에서는", "이 페이지에서는".
- 페이지가 만들어진 방법의 설명: extraction, backfill, render, image-read, note mapping, run-log.
- `Core idea`, `Details`, `Overview`, `Related`, `Maps to`, `Source Staging`, `Practice & Assignments` 같은 범용 위키 rubric heading. 그 heading 을 명시적으로 허용하는 페이지 template 의 일부일 때만 예외다.
  - `grow-branch.md` Templates 절의 course·chapter 메타 index template 은 `course-*-00-index.md` 페이지에 `Also known as` / `Overview` / `Scope` / `Chapters` / `Related` / `Subchapters` / `Chapter summary` / `Maps to` 를 요구한다. 그 페이지들에서는 이 heading 이 올바른 것이지 드리프트가 아니다.

## Content Guard

바뀐 페이지에서는 규칙이 달리 말하지 않는 한 `## Source` 앞의 본문만 검사한다.

다음을 표시하고 고친다.

- `## Source` 앞 본문 어디에서든 em dash(`—`, U+2014).
- `roots/`, `` `raw` ``, `Staging`, `Source Staging`, `Archived source bundle`.
- `PDF page`, `raw PDF`, `source PDF`, `source page`, `lecture notes`, `page range`, `render`, `image-read`, `backfill`, `run-log`, `extraction`.
- `필기에는`, `필기에서`, `강의 노트`, `노트에서는`, `원문에서는`, `원자료`, `자료에서는`, `페이지에서는`, `이 페이지에서는`, `이 자료`.
- mojibake 표식: `???`, `�`, `Ã`, `Â`.
- branch 페이지의 범용 영어 heading: `Status`, `Scope`, `Chapters`, `Projects`, `Connections`, `Also known as`, `Overview`, `Related`, `Sequence Logic`, `Practice & Assignments`, `Course Bridges`, `Concept Extraction`, `Source Staging`, `Names`, `Maps to`.
  - `course-*-00-index.md` 메타 페이지는 면제된다 (mojibake 검사는 그대로 적용된다). 그 template(`grow-branch.md` Templates 절)이 이 heading 과 `Staging: roots/...` 포인터를 요구하므로, 표시는 subchapter 노트 페이지와 일반 잎에서만 한다.

false positive 가 가능하다. 정당한 기술 영어와 수식과 명령과 `## Source` 안의 파일 경로와 branch 에 속한 인용 제목은 보존한다.

## 기록 형식

성공한 care 실행은 굵은 항목 하나를 덧붙인다.

```markdown
## [YYYY-MM-DD] care | <scope>
- reviewed: <N pages>
- updated: <N pages or none>
- output: <report path if any>
- summary: <one-line finding or fix>
```

`care --system` 이 워크플로 파일을 바꿨으면, 변경이 구조적이면 `migration` 을, 유지보수 규칙의 갱신이면 `care` 를 쓴다. `rings.md` 는 굵게 유지하고 상세한 페이지 목록은 보고에 둔다.
