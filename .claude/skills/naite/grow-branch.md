# /naite grow — branch 모드 (장기 과정)

branch 모드는 장기 과정의 학습 세션을 담당한다. 과목 하나와 책 한 권과 시리즈 하나가 각각 가지(branch) 하나다. 에이전트는 세션 시작부터 끝까지 상주하며 튜터·리마인드 모드로 진행하고, 서브챕터마다 tree 에 페이지를 grow 한다. grow 단발 모드가 단발성 학습 이벤트를 다룬다면, branch 모드는 구조화된 과목·책·시리즈 단위의 작업을 다룬다.

아래 모든 데이터 경로는 NAITE_ROOT(naite vault 의 루트) 기준으로, 하위 스킬 참조는 SKILL_DIR(`<NAITE_ROOT>/.claude/skills/naite`) 기준으로 해석한다. 맥락은 `SKILL.md` 가 담당한다.

## 컨텍스트 라우팅과 역할 분리

branch 를 바꾸기 전에 `docs/CONTEXT.md` 를 읽는다. branch 작업은 소스와 계약이 무거우므로, `subchapter-note` 와 `backfill` 은 활성 도구 표면이 지원하고 사용자가 위임을 허용했으면 `docs/CONTEXT.md` 의 Reader·Writer·Verifier 분리를 쓴다.

- Reader 는 강의 PDF 와 전사본과 노트와 렌더된 이미지와 현재 대화를 읽는다. 압축된 claim 과 개념과 예시와 수식과 손필기 통찰과 wikilink 후보를 돌려준다.
- Writer 는 이 워크플로와 `docs/CONVENTIONS.md` 와 생성 지도와 ontology 파일과 문체 참조와 Reader 덩어리를 읽는다. `course-*` 페이지와 자율 A 의 concept 페이지를 쓴다.
- Verifier 는 content guard 를 실행하고 `.naite/ontology/tree-manifest.json` 과 `.naite/ontology/tree-dependencies.json` 을 재생성하고 바뀐 페이지를 검사하고 inbound 의미 의존 페이지를 surface 한다.

별도 에이전트를 쓸 수 없으면 같은 세 단계를 한 세션에서 순차로 진행한다. 전체 소스 묶음이 이 워크플로의 출력 계약을 컨텍스트에서 밀어내게 두지 않는다.

## 사용 시점

사용자가 과목 단위의 학습을 시작하거나 진행하거나 마무리할 때 쓴다. 신호는 다음과 같다.

- "X 과목 공부할게 / 정리할게", "MA101 선형대수 학습 시작", "이번 학기 X 복습".
- 분류와 과목코드와 syllabus 와 목차 스크린샷과 강의자료 PDF 를 함께 공유하는 경우.
- 이미 시작된 과목의 다음 챕터 자료를 업로드하는 경우.
- "1.3 정리해줘", "Ch1 끝", "이 과목 다 끝났어".

### grow 단발 모드와의 구분

| | grow 단발 | grow branch |
|---|---|---|
| 단위 | 단발성 학습 이벤트 (논문 1편, 아티클 1편, 강의 1편) | 과목·책·시리즈 (10-20 챕터, 100+ 페이지) |
| 세션 | 마무리 시점의 capture 와 ingest 1회 | 세션 전체에 상주하고 서브챕터마다 개별 반영 |
| 출력 | 보통 1~3개 페이지 | 과목 메타와 챕터 메타와 서브챕터 노트 (수십 페이지 누적) |
| 스테이징 | `roots/articles/` | `roots/courses/{slug}/` |

단발성인지 과목 단위인지 불명확하면 사용자에게 묻는다.

## 강행 규칙

- staging: 강의자료 PDF 와 이미지는 `roots/courses/{slug}/` 아래에 정규화된 파일명으로 staging 한다. 구조는 flat 이다.
- tree 페이지의 파일명 규칙은 `docs/CONVENTIONS.md` 의 Naming 절(lowercase-kebab-case, 영문)을 지킨다.
  - 과목 메타: `course-{slug}-00-index.md` (`kind=source-record`, `form=index`).
  - 챕터 메타: `course-{slug}-ch{NN}-00-index.md` (`kind=source-record`, `form=index`).
  - 서브챕터 노트: `course-{slug}-ch{NN}-{SS}-{title-slug}.md` (`kind=source-record`, `form=prose`).
- 출력 품질 계약(`docs/CONVENTIONS.md` 의 출력 품질 계약과 학습 노트 품질 축과 kind 별 품질 계약)을 지킨다.
  - 본문은 페이지 자체로 의미를 가져야 하고, raw·PDF·필기·소스 공정의 설명과 em dash(`—`)를 `## Source` 앞 본문에 쓰지 않는다.
  - 필기와 슬라이드 강조와 worked example 은 본문의 설명과 학습 순서로 흡수한다.
  - H 계층은 강의의 논리적 구획을 드러내고, 수식은 조건과 기호와 해석을 갖춘다.
  - `kind=source-record` 는 소스의 질문과 메커니즘과 근거와 조건을 보존하고, 자율 생성하는 `kind=concept` 는 정의와 메커니즘과 경계와 해석과 무게 있는 링크를 갖춘다.
- slug 는 영소문자와 숫자의 단일 토큰이다 (하이픈 금지. 레벨 구분자 `-` 와 충돌한다).
  - 공식 과목코드가 있으면 소문자화한다 (`MA101` 은 `ma101` 이 된다). 없으면 prefix 와 NNN 으로 임의 부여한다 (`aa101`, `aa102`, ...).
  - slug 는 과목 내내 고정되고 이후 절대 바꾸지 않는다.
- subject: branch 페이지의 subject 는 그 과목·책·시리즈가 다루는 콘텐츠 경로 하나다 (예: `[statistics]` 나 더 좁은 `[engineering-math/ode]`).
  - 메타와 챕터와 서브챕터 모두 동일한 단일 경로나 narrower 를 쓴다. 정본 트리는 `.naite/ontology/subject-tree.md` 다.
  - `course` 나 `course-{slug}` 같은 컬렉션 태그는 subject 에 절대 넣지 않는다 (`docs/CONVENTIONS.md` Ontology 절 참조). branch 소속은 파일명 prefix `course-{slug}-*` 가 보장한다.
  - 새 페이지의 `domains` cache 는 선택한 `subject` 의 top-level 에서 기계적으로 도출한다.
- trunk 분리: trunk.md 에는 과목 메타 한 줄만 등재한다 (`## Branches` 의 institution 절).
  - 챕터와 서브챕터의 발견 경로는 `course-{slug}-00-index.md` 의 Chapters 절에서 `course-{slug}-ch{NN}-00-index.md` 의 Subchapters 절로 내려가는 drill-down 이다.
  - trunk.md 에 서브챕터와 챕터를 절대 나열하지 않는다.
- grow 단위: 서브챕터 단위로 즉시 페이지를 쓴다. 챕터 메타는 챕터 완료 시점에 일괄 작성한다.
  - 단 rings.md 에는 서브챕터마다 쓰지 않는다. frontmatter 의 `created`·`updated` 가 그 정보를 운반한다.
  - rings 항목은 `branch-chapter` 마무리 시점에 한 줄(서브챕터 수만 명시)이고, `branch-start` 와 `branch-finish` 도 한 줄씩이다.
- `ingest` 모듈의 직접 호출은 금지된다. `ingest.md` 는 "raw 파일 하나에서 여러 페이지로" 가는 워크플로이고, branch 모드는 "대화 맥락에서 페이지 하나로" 가는 구조라 맞지 않는다. 단 결과물의 규격(frontmatter, `trunk.md` 와 `rings.md` 의 갱신 형식)은 `ingest.md` 와 정합되게 맞춘다.
- raw 보존: `roots/courses/{slug}/*.pdf` 는 서브챕터 grow 시점에 `_archive/` 로 옮기지 않는다. 과목 완료(`branch-finish`) 시점에 일괄 이동한다. 여러 서브챕터가 같은 PDF 를 페이지 범위로 참조하므로 챕터 진행 중에는 원본이 남아 있어야 하기 때문이다.
- 유일한 archive: `roots/courses/_archive/` 는 이 프로젝트 전체에서 유일하게 존재하는 `_archive/` 디렉터리다. `roots/articles/` 와 `roots/conversations/` 에는 archive 층이 없다 (파일은 제자리에 남고, `conversations/` 의 claim 요약만 grow 후 삭제된다). `docs/CONVENTIONS.md` 의 grow 이후 처리 절을 참조한다.
- 학술 정보만 담는다: syllabus 와 about 에서 수업 시간과 교수명과 시험 일정과 평가 기준 같은 행정 정보는 tree 에 넣지 않는다. 내용과 범위와 선후수 관계만 넣는다.
- 그 밖의 `CLAUDE.md` 비밀과 프라이버시 절과 작업 트리 안전 절과 `docs/CONVENTIONS.md` 의 Obsidian 공동 편집 절과 Schema evolution 절이 전부 그대로 적용된다.

## Schema autonomy

이 스킬은 `docs/CONVENTIONS.md` Schema evolution 절의 등급 자율성을 따른다. 요약하면 다음과 같다.

- 자율 A (사용자 confirm 없이 작성):
  - 새 일반 개념 페이지 (`[[bayes-theorem]]` 같은 추출 페이지). 입자도 가드의 통과가 필수다. 기준은 `.naite/ontology/topics.md` 의 Topic granularity guidance 절이다 (넓은 도메인도 페이지 특정도 아닐 것).
  - 새 정본 topic: `.naite/ontology/topics.md` 의 canonical_topics 절에 직접 덧붙인다.
  - 명백한 topic 별칭 (`cot ↔ chain-of-thought` 처럼 형태 변형이나 잘 알려진 약어): `.naite/ontology/topics.md` 의 aliases 절에 직접 덧붙인다.
- 자율 B (후보 추가와 요약 surface. 사용자가 다음 검토 사이클에서 confirm 하거나 되돌린다):
  - 새 subject narrower: `.naite/ontology/subject-tree.md` 의 narrower: 에 후보를 덧붙인다.
  - subject 의 rename 과 이동(reparent): altLabel 과 함께 제안한다.
- 자율 C (LLM 의 추가가 절대 금지된다):
  - 새 top-level domain 과 새 enum 값(`kind`·`form`·`source-types`)과 새 facet 필드와 subject 폐기.

`subchapter-note` 와 `backfill` 두 모드에 동일하게 적용된다. 차이는 표면화 방식이다. active 는 takeaways 단계에서 surface 하고, backfill 은 chapter-finish 기록에서 surface 한다. 입자도 검사에 실패한 후보는 어느 모드에서도 자율 추가가 금지되고 기록의 surface 항목으로만 남는다.

## Sub-operations (자동 선택)

스킬이 호출되면 사용자 의도와 현재 tree 상태를 보고 아래 중 하나로 자동 분기한다. 분기 직전에 한 줄로 사용자에게 확인한다 ("지금 {op} 진행할까요?"). 혼동되면 선택지를 제시한다.

| Op | 트리거 | Tree 변경 |
|---|---|---|
| `start` | 신규 과목 시작. slug 가 `tree/trunk.md` Branches 절의 어느 institution 에도 없다 | 과목 메타 생성, trunk 와 rings 갱신 |
| `resume` | 기존 slug 가 이미 존재한다 | 없음 (진행 상태만 요약한다) |
| `chapter-start` | 새 챕터 PDF 업로드, 챕터 시작 선언 | 없음 (staging 과 맥락 세팅만 한다) |
| `subchapter-note` | "1.3 정리해줘", "이 서브챕터 반영" | 서브챕터 노트 1개 생성 (+선택적 일반 개념 페이지). rings.md 는 쓰지 않는다 |
| `chapter-finish` | "이 챕터 끝", 챕터 메타 요청 | 챕터 메타 생성, 과목 메타 갱신, rings 한 줄 |
| `branch-finish` | "과목 끝", "학기 종강" | 과목 메타 상태 변경, raw archive, rings 한 줄 |
| `stage-source` | start·chapter-start 밖에서 자료만 업로드됐다 | 없음 (roots 쪽만 staging 한다) |
| `backfill` | 학습 완료 과목의 대량 자동화. `/naite grow backfill {slug}` 명시 호출 | chapter loop sweep. `grow-backfill.md` 의 Workflow 절로 위임한다 |

## Workflow

### 0. 사전 점검 (모든 호출)

1. `<NAITE_ROOT>/CLAUDE.md` 를 읽는다.
2. `<NAITE_ROOT>/docs/CONTEXT.md` 를 읽는다.
3. `<NAITE_ROOT>/.naite/ontology/tree-manifest.json` 이 없거나 현재 작업 기준으로 낡았으면 `python .naite/scripts/build-tree-manifest.py` 를 실행한다.
4. 기존의 과목·개념·entity 페이지를 찾기 전에 `<NAITE_ROOT>/.naite/ontology/tree-manifest.json` 을 읽는다.
5. 기존 과목·개념 페이지를 바꾸기 전에, 의미 의존 페이지의 리뷰가 필요할 수 있으면 `<NAITE_ROOT>/.naite/ontology/tree-dependencies.json` 을 읽는다. 없으면 `python .naite/scripts/build-tree-dependencies.py` 를 실행한다.
6. `<NAITE_ROOT>/tree/trunk.md` 를 읽는다. 특히 `## Branches` 절(institution 별 과목 메타 목록)과 `## Knowledge domains` 의 hub 페이지들을 본다.
7. `<NAITE_ROOT>/tree/rings.md` 의 마지막 30줄 정도를 읽어 최근 `branch-*` 항목으로 진행 상태를 파악한다 (branch-note 는 더 이상 rings 에 없다. frontmatter 의 `updated` 나 `course-{slug}-*` 파일의 mtime 으로 파악한다).
8. op 를 결정하고 사용자에게 한 줄로 확인한다.

### A. `start` — 신규 과목

1. 사용자로부터 다음을 한 번에 또는 단계적으로 수집한다.
   - 분류 (예: "{대학·학과} 전공", "Anthropic Academy", "3Blue1Brown").
   - 과목코드 (있으면).
   - 과목명 (한글과 영어를 가능하면 둘 다).
   - 목차 (스크린샷이나 텍스트).
   - syllabus 나 about (PDF 나 텍스트, 또는 생략).
2. slug 를 결정한다.
   - 과목코드가 있으면 소문자화한다. `MA101` 은 `ma101` 이 된다.
   - 없으면 기관 prefix 와 NNN 을 제안한다. `tree/trunk.md` 의 Branches 절과 `roots/courses/` 디렉터리에서 기존 slug 를 확인한 뒤 다음 번호를 쓴다.
   - slug 는 반드시 단일 토큰이어야 한다 (영소문자와 숫자, 하이픈 없음).
3. staging: `roots/courses/{slug}/` 를 만들고 업로드 자료를 복사한다 (Staging rules 절 참조).
4. takeaways 를 3~8개의 bullet 로 논의한다.
   - 이 과목이 다루는 범위와 핵심 흐름.
   - subject 경로의 결정: `.naite/ontology/subject-tree.md` 의 경로 하나를 고른다 (예: `[statistics]` 나 `[engineering-math/ode]`). 어느 경로로도 분류가 곤란하면 사용자와 새 narrower 나 top-level 도입을 결정한 뒤 `.naite/ontology/subject-tree.md` 갱신부터 한다.
   - 기존 tree 개념 페이지와의 접점 (`[[probability]]` 가 있으면 메타 페이지에서 링크한다).
   - 유사 과목과 선후수 관계.
   - 사용자 확인 후 진행한다.
5. `tree/course-{slug}-00-index.md` 를 작성한다 (`kind=source-record`, `form=index`). template 은 Templates 절의 과목 메타를 쓴다. frontmatter 의 `subject` 는 단일 경로이고, `domains` 는 그 경로의 top-level 로 함께 작성한다.
6. `tree/trunk.md` 를 갱신한다.
   - `## Branches` 의 해당 institution 절에 한 줄을 넣는다: `- [[course-{slug}-00-index]] — {과목명, 짧은 설명}`. institution 절이 없으면 신설한다.
   - 챕터와 서브챕터는 절대 trunk 에 나열하지 않는다. drill-down 으로 발견된다.
7. `tree/rings.md` 에 덧붙인다.
   ```
   ## [YYYY-MM-DD] branch-start | course-{slug}
   - pages created: [[course-{slug}-00-index]]
   - subject: <path>  (.naite/ontology/subject-tree.md 참조)
   - staged: roots/courses/{slug}/<files>
   ```
8. checkpoint: "과목 셋업을 마쳤습니다. 첫 챕터 자료를 주시면 `chapter-start` 로 넘어갑니다."

### B. `resume` — 기존 과목 재개

1. `tree/course-{slug}-00-index.md` 를 읽는다.
2. `grep "^## \[" tree/rings.md | grep "course-{slug}"` 로 진행 이력을 파악한다 (branch-start 와 branch-chapter 와 branch-finish 만 보인다).
3. 진행 상태의 추론은 `course-{slug}-00-index.md` Chapters 절의 챕터 status 와 `course-{slug}-ch{NN}-00-index.md` 의 존재 여부와 서브챕터 페이지 glob 으로 한다.
4. 완료된 챕터와 진행 중인 챕터와 남은 챕터를 한 화면에 요약한다.
5. 사용자에게 다음 의도를 확인한다 ("새 챕터 시작? 특정 서브챕터 정리? 챕터 마무리?").
6. 파일은 쓰지 않는다. `rings.md` 에도 쓰지 않는다.

### C. `chapter-start` — 새 챕터 진입

1. 챕터 자료의 업로드를 확인한다. 기본 staging 이름은 `roots/courses/{slug}/ch{NN}-lecture.pdf` 다. 기존 파일이 있으면 덮어쓰기 전에 사용자에게 확인한다.
2. PDF 를 읽거나 텍스트를 추출한다. 추출 품질이 나쁘면(스캔본, OCR 필요 등) 중단하고 사용자에게 보고한다. `rings.md` 에 `aborted` 항목을 덧붙인다.
3. 목차와 서브챕터 목록을 파악한다. 사용자에게 "이 챕터 서브챕터는 {리스트} 가 맞나요?"라고 확인한다.
4. 파일은 쓰지 않는다. 이 단계는 맥락 세팅만 한다 (리마인드와 설명은 이제부터 진행한다). `rings.md` 에도 쓰지 않는다. 챕터 메타는 `chapter-finish` 에서만 작성된다.
5. 서브챕터 단위로 리마인드와 설명을 진행한다. 사용자가 "정리해줘" 류의 신호를 보내면 `subchapter-note` 로 전환한다.

### D. `subchapter-note` — 서브챕터 반영 (핵심 동작)

한 번에 서브챕터 하나만 처리한다.

작성 전의 필수 캘리브레이션은 절대 생략할 수 없다.

- a. 기존 서브챕터 노트 1개 읽기: 같은 과목(`course-{slug}-ch*-[^0]*.md`)의 기존 서브챕터 노트 중 가장 최근 것 하나를 읽는다. 없으면 같은 domain 의 다른 과목 서브챕터 노트를 읽는다. 이 페이지의 깊이와 서술 방식과 수식 형식이 현재 작성의 최저 기준이다. 기존 페이지보다 얕으면 안 된다.
- b. 해당 section 의 PNG 전체 읽기: `chapter-start` 에서 PDF 가 이미 staging 된 경우라도, 서브챕터 노트를 쓸 때는 해당 section 의 슬라이드를 PNG 로 render 해서 한 장씩 읽는다. 텍스트 추출만으로는 수식과 필기와 그래프가 누락된다. render 파이프라인은 PDF rendering pipeline 절에 있다. section 경계를 모를 때는 그 절의 지침대로 5~10장을 먼저 render 해서 header 를 확인한 뒤 범위를 확정한다.
- c. 학생 필기 통찰의 수집: PNG 를 읽으면서 학생 필기(형광펜 강조, 여백 메모, 수식 옆 주석, 한국어 해설)를 모두 기록한다. 이것이 이 학생이 중요하다고 판단한 부분이므로 페이지 본문에 반드시 반영한다. 단 본문에서 "필기에는"이나 "노트에서는"처럼 소스를 직접 말하지 말고, 강조점과 직관을 해당 개념의 설명으로 흡수한다.

1. 현재 대화에서 해당 서브챕터 관련 논의(질문과 설명과 예시와 유도와 사용자 반응)를 추출한다.
2. `tree/trunk.md` 를 재확인해서 관련된 기존 hub 개념 페이지가 있는지 본다 (`[[laplace-transform]]`, `[[generative-ai]]` 등). `[[...]]` 연결 후보를 수집한다.
3. 사용자에게 takeaways 를 3~8개 bullet 로 제시한다 (`ingest.md` 4절의 원칙 그대로).
   - 이 서브챕터에 담을 내용.
   - 일반 개념 페이지의 추출 후보: 강의에 등장한 개념 중 재사용 가능한 입자도에 부합하는 것을 LLM 이 식별해서 제시한다 (예: `Bayes' Theorem`, `chain-of-thought`). 기준은 `.naite/ontology/topics.md` 의 Topic granularity guidance 절이다 (넓은 도메인도 페이지 특정도 아닐 것). Schema autonomy 절의 자율 A 권한으로 5단계에서 자동 생성한다. 사용자가 명시적으로 빼라고 하지 않는 한 진행한다.
   - 기존 페이지의 갱신이 필요한 것 (예: 기존 `[[laplace-transform]]` 에 이번 강의의 formulation 을 추가).
   - 강의 내용에 trade-off 나 결정이나 실패 분석이 들어 있으면, 서브챕터 노트와 별도로 `/naite fruit` 페이지로 분리할지 (`docs/CONVENTIONS.md` Decision thread 형태 절 참조).
   - 사용자 확인 후 진행한다.
4. 서브챕터 노트 파일을 작성한다.
   - 경로: `tree/course-{slug}-ch{NN}-{SS}-{title-slug}.md`.
   - frontmatter: `kind=source-record`, `form=prose`, `domains: [<subject-top-level>]` (선택한 subject 에서 기계적으로 도출).
   - 본문: Templates 절의 서브챕터 노트를 참조한다.
5. 일반 개념 페이지를 자율 생성한다 (Schema autonomy 절의 자율 A).
   - 3단계에서 식별된 추출 후보 중 사용자가 명시적으로 뺀 것을 제외하고 이 시점에 별도로 쓴다. frontmatter 5 facet 은 `ingest.md` 5절의 규격이다.
   - 본문은 `docs/QUALITY.md` 4절의 LEAF-1~6 과 `docs/CONVENTIONS.md` 의 학습 노트 품질 축과 kind 별 품질 계약의 concept 계약으로 자기 점검한다. 소스가 메커니즘과 경계와 해석을 뒷받침하지 못하면 얇은 concept 를 만들지 말고 `seeds.md` 에 보강 후보로 남긴다.
   - `topics` 와 `subject` 는 `.naite/ontology/` 의 정본을 우선한다. 미등록 새 topic 이 입자도 가드를 통과하면 `.naite/ontology/topics.md` 의 canonical_topics 절에 직접 덧붙인다 (자율 A). 새 narrower 가 자연스러우면 `.naite/ontology/subject-tree.md` 의 narrower: 에 후보를 덧붙이고 chapter-finish rings 의 surface 항목으로 기록한다 (자율 B).
   - 새 일반 페이지가 hub 후보면(다른 페이지에서 링크를 자주 받을 만하면) `trunk.md` 의 해당 도메인 주요 줄 추가를 검토한다.
6. `tree/trunk.md` 를 갱신한다.
   - 서브챕터 노트는 trunk 에 등재하지 않는다.
   - 새 일반 개념 페이지가 hub 자격이 있으면 `## Knowledge domains` 의 해당 도메인 주요 목록에 한 줄을 넣는다 (4~7개 한도 안에서).
   - 기존 hub 페이지의 요약이 본질적으로 바뀌면 한 줄을 고친다.
7. `tree/rings.md` 는 쓰지 않는다. frontmatter 의 `created`·`updated` 가 정보를 운반한다.
8. content guard: 방금 쓰거나 고친 페이지의 `## Source` 앞 본문을 `/naite care` 의 Content Guard 기준으로 스캔하고, em dash 와 원자료·소스 화법과 불필요한 영어 범용 heading 과 mojibake 를 즉시 고친다.
9. 생성 지도를 재생성한다.
   ```powershell
   python .naite/scripts/build-tree-manifest.py
   python .naite/scripts/build-tree-dependencies.py
   ```
10. `.naite/ontology/tree-dependencies.json` 에서 바뀐 slug 로 들어오는 inbound 참조를 점검한다. 의미 의존 후보는 surface 만 하고, `subchapter-note` 중에는 자동으로 다시 쓰지 않는다.
11. checkpoint: "반영을 마쳤습니다. 다음 서브챕터로 갈까요?"

### E. `chapter-finish` — 챕터 마무리

1. 해당 챕터의 서브챕터 노트가 전부 존재하는지 확인한다 (glob `tree/course-{slug}-ch{NN}-*` 에서 `-00-index` 를 제외).
2. 누락이 있으면 사용자에게 확인한다. 의도적 스킵이면 진행하고, 실수면 해당 서브챕터를 먼저 `subchapter-note` 로 처리한다.
3. 챕터 메타 파일을 작성한다: `tree/course-{slug}-ch{NN}-00-index.md` (`kind=source-record`, `form=index`). template 은 Templates 절의 챕터 메타다. `domains` 는 선택한 `subject` 의 top-level 로 함께 작성한다.
4. `tree/course-{slug}-00-index.md` 의 Chapters 절을 갱신한다 (챕터 상태를 "완료"로 바꾸고 요약 줄을 새로 고친다).
5. trunk.md 는 갱신하지 않는다 (챕터 메타는 course 메타에서만 발견되고 trunk 에 직접 등재하지 않는다).
6. `tree/rings.md` 에 덧붙인다.
   ```
   ## [YYYY-MM-DD] branch-chapter | course-{slug} Ch{NN} — {Chapter Title}
   - subchapters: N — {slug list}
   - source: roots/courses/{slug}/ch{NN}-lecture.pdf
   - drafter: {cowork | code | codex}
   ```
7. git commit 을 한다 (chapter 가 원자 단위다. push 는 하지 않는다).
   ```
   git add tree/course-{slug}-ch{NN}-*.md \
           tree/course-{slug}-00-index.md \
           tree/rings.md \
           .naite/ontology/tree-manifest.json \
           .naite/ontology/tree-dependencies.json \
           [해당 챕터에서 만들어진 hub 페이지 slug] \
           [hub 승격으로 trunk.md 가 바뀐 경우 tree/trunk.md]
   git commit -m "course: {slug} ch{NN} — {Chapter Title} (drafter={cowork|code|codex})"
   ```
   - drafter 태그는 필수다. `cowork`(데스크톱 앱 Cowork 탭)와 `code`(CLI 나 데스크톱 앱 Code 탭)와 `codex`(OpenAI Codex CLI) 중 하나다. 사후의 품질 비교와 추적에 쓰인다 (`git log --grep "drafter=codex"` 같은 질의로 드러난다).
   - 한 commit 이 한 chapter 다 (서브챕터 페이지와 챕터 메타와 과목 메타 갱신과 rings 항목과 그 챕터에서 만들어진 일반 개념 페이지).
   - 스키마 파일과 settings 같은 무관한 변경은 staging 하지 않는다. 별도 commit 으로 한다.
   - push 는 하지 않는다. `branch-finish` 시점에 누적된 chapter commit 과 finish commit 이 한 번에 origin 으로 간다.
   - 첫 chapter commit 은 미추적 상태인 `course-{slug}-00-index.md`(branch-start 의 산출물)도 함께 staging 한다.

### F. `branch-finish` — 과목 종료

1. `tree/course-{slug}-00-index.md` 의 상태를 바꾼다 (frontmatter `updated` 와 본문의 `상태: 완료 (YYYY-MM-DD)`).
2. `roots/courses/{slug}/` 전체를 `roots/courses/_archive/{slug}/` 로 이동한다. `_archive/` 가 없으면 만든다.
3. `tree/rings.md` 에 덧붙인다.
   ```
   ## [YYYY-MM-DD] branch-finish | course-{slug}
   - chapters: N
   - subchapter pages: M
   - archived: roots/courses/_archive/{slug}/
   ```
4. git commit 과 push 를 한다 (과목의 원자적 종료와 원격 동기화).
   ```
   git add tree/course-{slug}-00-index.md tree/rings.md roots/courses/_archive/{slug}/
   git add .naite/ontology/tree-manifest.json .naite/ontology/tree-dependencies.json
   git commit -m "course: {slug} — finished ({N} chapters, {M} pages)"
   git push origin main
   ```
   - 이 op 가 자동 push 의 트리거다. chapter-finish 는 로컬 전용 commit 이었고, 누적된 chapter commit 과 이 finish commit 이 한 번에 원격으로 간다.
   - 현재 브랜치를 확인한다. `main` 이 아니면 사용자에게 확인한다. worktree 에서 진행 중이었으면 main 으로 merge 나 checkout 후 push 한다.
   - push 가 실패하면(네트워크, 인증, 충돌) 사용자에게 보고하고 commit 까지는 보존한다. 자동 force-push 는 금지된다.

### G. `stage-source` — 자료 단독 staging

이 op 는 `start` 와 `chapter-start` 흐름에 포함되지만, 중간에 보조자료(필기, 보충 슬라이드)만 들어올 때 단독으로 호출된다.

1. 업로드 경로를 확인한다 (`uploads/` 나 사용자 제시 경로).
2. 정규화된 파일명을 정한다 (Staging rules 절).
3. 복사한다 (bash `cp`. workspace 에서 불가능하면 정확한 경로와 이름을 제시하고 사용자에게 수동 복사를 요청한다).
4. `rings.md` 에는 쓰지 않는다. roots 층의 staging 만 했기 때문이다.

### H. `backfill` — Codex 자동화 모드

세부 워크플로는 `.claude/skills/naite/grow-backfill.md` 가 담당한다. 이 op 는 분기만 책임진다.

1. 트리거: 사용자가 `/naite grow backfill {slug}` 를 호출한다 (라우터에 정의된 유일한 진입형이다). 자동 추론은 하지 않는다. 0절 8단계의 op 결정에서 사용자 입력으로 명시된다.
2. A 절 start 의 1~3단계(slug 결정, staging)를 그대로 진행한다.
3. A 절 start 에서 건너뛰는 것은 대화 단계뿐이다. 4단계(takeaways 논의)와 8단계(대화형 checkpoint)가 그것이다.
   - 파일 생성 단계인 5단계(`tree/course-{slug}-00-index.md` 과목 메타)와 6단계(`tree/trunk.md` 갱신)와 7단계(`tree/rings.md` 의 `branch-start` 항목)는 A 절 그대로 수행한다.
   - 이 메타와 trunk 와 rings 산출물이 없으면, 이후 chapter loop 의 E 절 chapter-finish(챕터 메타가 과목 메타를 참조한다)와 branch-finish(F 절이 과목 메타의 status 를 바꾼다)가 존재하지 않는 파일을 참조해 실패한다.
   - backfill 은 사용자의 멘탈 모델이 이미 안정된 콘텐츠를 다루므로 큐레이션 대화만 생략하는 것이지, 파일과 연결의 생성을 생략하는 것이 아니다.
   - Schema autonomy 절의 자율 A 는 그대로 적용된다. 일반 개념 페이지의 추출과 정본 topic 의 추가와 명백한 별칭의 추가는 입자도 가드를 통과하면 전부 자율로 진행한다. 자율 B(narrower 제안)는 후보 덧붙이기와 chapter-finish rings 의 surface 항목으로 기록하고, 자율 C 는 발견 시 rings 에 명시한 뒤 사용자 결정을 기다린다.
   - 일반 개념 페이지의 추출이 빠지면 chapter 가 고립되어 그래프가 빈약해진다.
4. `grow-backfill.md` Workflow 절의 chapter loop 로 위임한다.
5. 모든 chapter 가 끝나면 branch-finish 는 이 파일의 F 절 그대로 사용자의 명시적 승인 후 수행한다 (자동 push 포함).

backfill 모드는 active 모드(A 절)와 동시에 사용하지 않는다. 학습 중인 콘텐츠에 backfill 을 쓰면 dialogue takeaway 가 사라져서 페이지의 가치가 떨어진다.

## Staging rules (`roots/courses/{slug}/`)

구조는 flat 이다. 한 챕터의 자료가 너무 많아지면(대략 3개 초과) 작성자가 nested 재구성을 검토한다 (이것은 작성 시점의 판단이지 `care --check` 의 자동 검사 항목이 아니다).

| 자료 종류 | 파일명 |
|---|---|
| Syllabus / about | `syllabus.pdf`, `syllabus.md` |
| 목차 스크린샷 | `toc.png` |
| 챕터 강의자료 | `ch{NN}-lecture.pdf` |
| 챕터 사용자 필기 | `ch{NN}-notes.pdf` |
| 챕터 교재 발췌 | `ch{NN}-textbook.pdf` |
| 챕터 슬라이드·보조자료 | `ch{NN}-slides.pdf`, `ch{NN}-handout.pdf` |

- 원본 업로드명의 자동 파싱: `Ch1 Probability Theory.pdf` 처럼 "Ch{N} {Title}" 구조면 `ch01-lecture.pdf` 로 자동 변환한다. 파싱에 실패하면 사용자에게 묻는다.
- 바이너리 복사: PDF 와 이미지는 `Write` 도구로 못 쓴다 (텍스트 전용이다). `bash cp <src> <dst>` 를 쓴다. workspace 에서 불가능하면 사용자에게 정확한 경로와 파일명을 제시하고 수동 복사를 요청한다.

## 외부 소스 폴더 접근 (선택)

강의자료가 클라우드 동기화 폴더(OneDrive, Google Drive, Dropbox 등)에 이미 정리되어 있으면, 사용자 업로드 없이 그 폴더에서 직접 staging 할 수 있다. 절차는 다음과 같다.

1. 사용자에게 원본 폴더의 경로와 구조를 확인한다.
2. 파일 복사로 staging 한다 (원본은 절대 수정하지 않는다).
```powershell
Copy-Item "{원본 폴더}\{원본파일명}.pdf" "<NAITE_ROOT>\roots\courses\{slug}\ch{NN}-lecture.pdf"
```
3. 복사가 끝나면 staging 경로(`roots/courses/{slug}/ch{NN}-lecture.pdf`)에서 render 한다. tree 페이지의 Source 절에는 staging 경로를 기록한다 (외부 원본 경로는 적지 않는다. 경로 누출을 막기 위해서다).

## PDF rendering pipeline (Read 도구가 PDF 를 직접 못 읽는 환경용)

환경에 따라 Read 도구가 PDF 를 직접 읽지 못할 수 있다 (`pdftoppm` 미설치 등). 그 경우 PyMuPDF 로 PNG render 한 뒤 Read 하는 방식을 쓴다.

전체 페이지 수의 확인과 render 는 NAITE_ROOT 에서 실행한다. PyMuPDF(`pip install pymupdf`, import 이름은 `fitz`)가 필요하다. PNG 는 `tmp/render/`(gitignore 대상)에 쓰므로 커밋에 새지 않는다. 경로는 forward slash 만 쓴다. backslash 는 POSIX 에서 파일명 문자로 남아 엉뚱한 파일을 만든다.

```python
import fitz, os
pdf = fitz.open('roots/courses/{slug}/ch{NN}-lecture.pdf')
print('Total pages:', len(pdf))
mat = fitz.Matrix(1.5, 1.5)   # 1.5x 배율 — 필기 판독 최적값
d = 'tmp/render'
os.makedirs(d, exist_ok=True)
for i in range(START, END):   # 0-indexed; 페이지 X → index X-1
    pdf[i].get_pixmap(matrix=mat).save(f'{d}/ch{NN}_p{i+1:02d}.png')
pdf.close()
print('done')
```

Read 후에는 즉시 삭제한다 (한 서브챕터 작업이 끝나면 그 챕터의 PNG 를 지운다). 파일명은 위 render 와 정확히 같은 `ch{NN}_p*.png` 패턴이다.

```python
import glob, os
for p in glob.glob('tmp/render/ch{NN}_p*.png'):
    os.remove(p)
```

운영 규칙:

- PNG 는 `tmp/render/` 에 임시로만 둔다. 서브챕터 노트 작성이 끝나는 즉시 삭제한다. `tmp/` 는 gitignore 대상이라 git 에 들어가지 않지만, 누적을 막기 위해 즉시 지운다.
- 한 번의 render 권장 범위는 5~15 페이지다. section 경계를 모를 때는 5~10장을 먼저 render 해서 header 를 확인한 뒤 범위를 정한다.
- 한 세션의 적정 분량은 챕터 1개(서브챕터 7~10개 기준)다. 컨텍스트 한계 때문에 챕터 단위로 세션을 나누는 것을 권장한다.

## Templates

### 과목 메타 (`course-{slug}-00-index.md`)

```markdown
---
kind: source-record
form: index
topics: []
subject: [<path-from-.naite/ontology/subject-tree.md>]
source-types: [course]
domains: [<subject-top-level>]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# {Course Title EN} ({과목코드 있으면})

## Also known as
- {한글 과목명}
- {영어 전체명}

## Overview

- **분류**: {예: {대학·학과} 전공, Anthropic Academy}
- **과목코드**: {MA101 또는 N/A}
- **상태**: 진행중 | 완료 (YYYY-MM-DD)
- **Staging**: `roots/courses/{slug}/`  (또는 완료 후 `roots/courses/_archive/{slug}/`)

## Scope

{이 과목이 다루는 범위·핵심 thread. prose 한두 단락, syllabus/about 기반. 학술 정보만.}

## Chapters

- [[course-{slug}-ch01-00-index|Ch1. {Title}]] — {one-line summary} (완료 | 진행중 | 예정)
- [[course-{slug}-ch02-00-index|Ch2. {Title}]] — ...
- ...

## Related

{prose로 인접 영역 연결. 예: "확률론 기초를 다루므로 [[probability]], [[conditional-probability]] 와 연결된다. [[statistical-inference]] 의 선수과목 역할."}
```

### 챕터 메타 (`course-{slug}-ch{NN}-00-index.md`)

```markdown
---
kind: source-record
form: index
topics: []
subject: [<과목과 동일 path 또는 narrower>]
source-types: [course]
domains: [<subject-top-level>]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# {과목코드} Ch{NN}. {Chapter Title}

## Subchapters

- [[course-{slug}-ch{NN}-01-{title}|{NN}.1 {Subchapter Title}]]
- [[course-{slug}-ch{NN}-02-{title}|{NN}.2 {Subchapter Title}]]
- ...

## Chapter summary

{챕터 전체 thread prose. 서브챕터 간 논리적 연결, 핵심 정리.}

## Maps to

- {위키 일반 개념 페이지 연결. 예: "이 챕터는 [[probability-theory]] 의 basics를 다룬다."}

## Source

- `roots/courses/{slug}/ch{NN}-lecture.pdf`  (과목 완료 후엔 `roots/courses/_archive/{slug}/ch{NN}-lecture.pdf`)
```

### 서브챕터 노트 (`course-{slug}-ch{NN}-{SS}-{title-slug}.md`)

페이지 골격의 강행 규칙이다. 이 파일이 authoritative 이고 다른 스킬들이 이 절을 참조한다.

서브챕터 페이지의 H-tag 매핑은 강의의 자연스러운 구획을 그대로 따른다. tree 는 subchapter 하나가 파일 하나라는 기준이라, chapter 하나가 파일 하나인 외부 노트의 H2 가 이 tree 에서는 페이지 자체(H1)에 해당한다.

- H1 은 subchapter 제목이다.
- H2 는 강의의 그 subchapter 안의 자연스러운 구획(큰 골자)이다.
- H3 는 그 골자 아래의 개념 묶음이다.
- H4 는 단일 개념·설명·공식·정리다. 본문은 길이 제한 없이 충분히 설명할 수 있다.
- H2 나 H3 아래에 H4 없이 산문만 두는 것도 필요하면 허용된다 (메타 설명과 연결 문장).
- `---` 는 H2 사이의 시각 구분선이다.
- 산문은 한국어가 기본이다. 강의 고유의 기술 단위인 영어 heading 과 용어는 허용되고, 범용 heading 은 한국어로 쓴다 (`docs/CONVENTIONS.md` 출력 품질 계약).
- frontmatter 5 facet 을 유지한다 (`docs/CONVENTIONS.md` Ontology 절).

`## Source` 는 H2 규칙의 예외이고 trailing provenance block 이다. 파일 경로만 적고 페이지 범위는 본문에 노출하지 않는다. 페이지 범위는 backfill 의 run-log 나 commit 메시지가 관리한다.

```md
## Source
- `roots/courses/_archive/{slug}/sessionNN-notes.pdf`
```

- 원본 소스 참조 금지: 본문 산문이 원본 PDF 의 특정 페이지·위치·다이어그램을 가리키는 anchor 를 포함하지 않는다. 페이지 자체와 tree 의 인접 페이지로 자립해야 한다. 원본은 검토·보강 용도이지 본문 이해의 의존물이 아니다.
- 원자료·필기·소스 공정 화법 금지: `## Source` 앞의 본문에 roots 경로와 PDF page 와 page range 와 staging 과 render 와 backfill 과 "필기에는"과 "강의 노트에는"과 "자료에서는"과 "이 페이지에서는" 같은 표현을 쓰지 않는다. 손필기와 시각 강조는 해당 개념 설명의 관점·직관·주의점으로 흡수한다.
- 이미지 임베드는 기본으로 하지 않는다. 무게 있는 diagram 일 때만 예외다.
- `## Core idea / ## Details / ## Also known as / ## Related` 같은 위키 rubric 절 heading 을 만들지 않는다. 그 정보는 H4 산문 안에 자연스럽게 흐른다.
- 문체 참조(read-only): voice anchor 는 `tmp/style-reference/` 아래의 manifest 가 관리한다. backfill 과 care 하위 스킬이 manifest 가 있으면 참조하고, 없으면 manifest 의 fallback 경로로 원본 노트를 read-only 로 참고한다. 어느 경우에도 tree 에 ingest 하지 않는다.

작성 품질 기준이다. 이 수준 미만은 반려된다.

- 공식의 나열은 금지된다. 공식이 등장할 때는 반드시 유도 근거나 메커니즘과, 각 항이 뜻하는 것과, 어떤 조건에서 성립하는지를 함께 쓴다. "E(X) = np" 한 줄만 쓰는 것은 품질 미달이다.
- 앞 서브챕터·챕터와의 논리적 흐름을 잇는다. 첫 H2 나 여는 산문에서 "이 개념이 왜 필요한가, 앞에서 무엇을 다뤘고 이것이 어디서 나오는가"가 산문 안에 자연스럽게 드러난다. 별도의 heading 은 만들지 않는다.
- 필기 통찰을 통합한다. 캘리브레이션 c 단계에서 수집한 학생 필기의 강조점을 해당 개념 H4 의 설명 산문 안에 자연스럽게 녹인다.
- 예시에는 숫자를 직접 계산한다. 슬라이드의 예시를 가져올 때 과정과 결과값을 실제로 쓴다.
- 유사·대비 개념을 명시한다. 이 개념과 혼동하기 쉬운 것이나 구조적으로 대응하는 것이 있으면 비교 산문을 더한다.
- 한국어 별칭은 인라인으로 쓴다. 단일 별칭은 H4 정의의 lead 안에 둔다 (`#### Bayes' theorem (베이즈 정리)`). 별도의 `## Also known as` 절을 만들지 않는다.

```markdown
---
kind: source-record
form: prose
topics: []
subject: [<과목과 동일 path 또는 narrower>]
source-types: [course]
domains: [<subject-top-level>]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# {NN}.{SS} {Subchapter Title}

{optional opening prose — 이 subchapter 의 위치·맥락·앞 흐름과의 연결.}

## {first sub-division from lecture}

{optional H2 prose — 메타 설명·연결 문장.}

### {concept group}

#### {concept name} ({Korean alias if relevant})
정의 lead.
prose narrative 충분히 — 위 퀄리티 기준 따름.

$$
P(A|B) = \frac{P(A \cap B)}{P(B)}
$$

분모 $P(B)$ 는 $B$ 가 주어진 축소된 sample space; 분자 $P(A \cap B)$ 는 그 안에서 $A$ 가 차지하는 비율. $B$ 가 전체 sample space 면 $P(A|B)=P(A)$ 와 같다.

#### {next concept}
...

### {next concept group}
...

## {next sub-division}
...

---

## Source

- `roots/courses/_archive/{slug}/sessionNN-notes.pdf`
```

## 이 명령이 절대 하지 않는 것

- 과목 시작 시점에 빈 챕터·서브챕터 stub 을 미리 만들지 않는다 (naite 전반의 "얕은 stub 을 미리 만들지 않는다" 원칙과 같은 취지다. 페이지는 실제 내용이 생길 때 만든다).
- 서브챕터 노트 없이 챕터 메타를 쓰지 않는다.
- slug 충돌을 허용하지 않는다 (`tree/trunk.md` 의 Branches 절과 `ls roots/courses/` 의 중복 확인이 필수다).
- 서브챕터 grow 시점에 원본 PDF 를 `_archive/` 로 옮기지 않는다 (챕터와 과목의 완료 시점까지 보존한다).
- `ingest` 나 `capture` 내부 모듈을 직접 호출하지 않는다 (구조가 맞지 않는다). 결과물의 규격만 정합되게 맞춘다.
- frontmatter 의 `domains` 에 `course` 나 `course-{slug}` 같은 컬렉션 태그를 절대 넣지 않는다 (2026-04-28 이후 스키마). 단일 콘텐츠 도메인만 넣는다.
- 서브챕터와 챕터 메타를 `trunk.md` 에 등재하지 않는다. drill-down 으로 발견된다.
- `subchapter-note` 시점에 `rings.md` 를 갱신하지 않는다. frontmatter 의 `created`·`updated` 가 정보를 운반하고, 챕터 마무리의 `branch-chapter` 한 줄로 묶인다.
- tree 를 건드리지 않는 op(`resume`, `chapter-start`, `stage-source`)에는 `rings.md` 항목을 남기지 않는다.
- 수업 시간과 교수명과 시험과 평가 기준 같은 행정 정보를 tree 에 쓰지 않는다.
- `chapter-finish` 와 `branch-finish` 외의 op 에서는 git commit 을 하지 않는다 (E 절 7단계와 F 절 4단계 참조). `branch-finish` 외의 op 에서는 git push 도 하지 않는다.
