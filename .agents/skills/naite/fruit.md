# /naite fruit

fruit 는 결정 thread 를 나무의 열매로 맺는 dialogue scaffold 다. tree 의 노드(concept·entity·source)가 뉴런이라면, synapse 층은 그 위를 가로지르며 의사결정 흐름을 형성하는 별도 차원의 결합이다. 독립 decision 페이지와 다른 concept 페이지에 담긴 짧은 decision 산문은 둘 다 정당하다. 품질은 절의 개수가 아니라 선택과 제약과 작동 가설과 검증 상태와 재검토 조건이 얼마나 정직하게 보존됐는지로 판단한다.

아래 모든 데이터 경로는 NAITE_ROOT(naite vault 의 루트) 기준으로, 하위 스킬 참조는 SKILL_DIR(`<NAITE_ROOT>/.agents/skills/naite`) 기준으로 해석한다. 맥락은 `SKILL.md` 가 담당한다.

## 사용 시점 — 세 가지 트리거

1. 명시적 슬래시: `/naite fruit [topic?]`. 사용자가 "이 결정 정리해두자"라고 의식적으로 부를 때다.
2. 자연 감지: 대화 중 "선택했다·고민했다·보류했다·실패했다·결정했다·비교했다" 신호와 trade-off 정황이 감지되면 에이전트가 한 줄로 제안한다: "이거 열매로 정리해둘까요?" 실행은 사용자 확인 후에만 한다. `grow.md` 의 Branch pre-check 와 같은 리듬이다.
3. 작업 종료 트리거: 사용자가 "끝났어·마무리·완료·다 됐어" 신호를 주고 그 작업이 의사결정이나 trade-off 를 포함한 흐름이면 wrap-up 을 제안한다. 단순 task 의 종료에는 발동하지 않는다.

세 트리거 모두 같은 워크플로로 진입한다. 차이는 모드 판별 단계에서 사용자 확인 한 줄이 추가되는 것뿐이다.

## 강행 규칙

- 출력은 `kind: decision` 페이지다. 적합하면 `kind: concept`·`entity`·`source-record` 페이지에 결정 꼴 내용을 인라인으로 넣는 것도 가능하다. `form` 은 `prose` 다.
  - `subject` 는 `.naite/ontology/subject-tree.md` 의 경로 하나를 쓰고, 진짜 cross-domain 일 때만 복수로 둔다 (`[a/x, b/y]`).
  - `dmu/` 나 `failure-*/` 나 `career-*/` 나 `synapse/` 같은 메타 subject 경로와 별도 kind enum 의 추가는 금지된다. synapse 의 본질이 카테고리화의 거부다 (`docs/CONVENTIONS.md` 의 Decision thread 형태 절 참조). 결정 꼴 thread 는 페이지 수준 enum 으로 좁히지 않고 페이지를 가로지르는 synapse 층으로 흐른다.
- 파일명은 `decision-YYYY-MM-DD-<slug>.md` 형식이다. `YYYY-MM-DD` 는 페이지의 `created` 날짜와 일치해야 한다. `<slug>` 는 `lowercase-kebab-case` 다. `DMU-` prefix 는 금지된다. 예: `decision-2026-01-15-vector-db-selection`, `decision-2026-02-03-retrieval-strategy`.
- 본문은 decision kernel 을 보존한다 (`docs/CONVENTIONS.md` 의 Decision thread 형태 절과 kind 별 품질 계약).
  - 핵심은 선택과 현재 상태, 맥락과 구속 조건, 실제 대안, 예상 메커니즘, 검증 상태, 실패와 재검토 조건이다.
  - 고정 header 나 절의 개수를 강제하지 않고 빈 header 를 만들지 않는다.
- 관찰과 해석과 기대 결과를 분리한다. 아직 검증하지 않은 기대는 결과로 쓰지 않고, 무엇을 보면 검증되는지를 적는다. 대안이 없었다면 가상의 대안을 만들지 않는다.
- 링크 수를 품질 목표로 쓰지 않는다. 프로젝트와 제약과 메커니즘과 영향받는 개념처럼 실제 추론을 지탱하는 wikilink 만 산문으로 연결한다. 장식용 `Related` 목록으로 개수를 채우지 않는다.
- 누락 개념을 발견하면 `tree/seeds.md` 에 stub 을 제안한다. 없는 페이지를 대신해 장식성 링크를 만들지 않는다.
- soft ontology 관용구는 의미가 맞을 때만 쓴다. `decided ... over` 와 `failed when` 과 `trade-off:` 와 `validates` 와 `falsifies` 를 문장에 억지로 넣지 않는다. 자연스러운 한국어 산문이 같은 관계를 더 정확히 표현하면 그 산문을 우선한다.
- 그 밖의 `AGENTS.md` 비밀과 프라이버시 절과 `docs/CONVENTIONS.md` 의 Schema evolution 절이 전부 그대로 적용된다.

## Dialogue scaffold — template 채우기가 아니라 사고 캐묻기

이 스킬의 핵심 가치는 빈 header 를 채우게 하는 것이 아니라 누락된 생각을 끌어내는 것이다.

- 이미 확보된 decision kernel 은 다시 묻지 않고 빠진 증거만 질문한다. 한 번에 한두 개씩 묻는다.
- 표면적인 답변은 구속 조건으로 구체화한다. 사용자가 "좋아 보여서"나 "유명해서"라고 답하면 "다른 선택을 탈락시킨 실제 제약이 비용, 시간, 유지보수, 데이터 품질, 되돌리기 가능성 중 무엇이었나요?"처럼 좁혀 묻는다.
- 검증 상태를 먼저 분리한다. 실제 관찰과 그 관찰의 해석과 아직 확인하지 않은 기대를 한 문장에 섞지 않는다.
- 실패와 재검토 조건은 관찰 가능한 신호로 묻는다. "잘 안 됐다"가 아니라 어떤 입력이나 사용자 행동이나 비용이나 품질 저하나 맥락 변화가 결정을 다시 열게 하는지를 묻는다.
- invariant 와 재사용 규칙은 선택 사항이다. 한 사례에서 일반 규칙을 억지로 만들지 않고, 반복 관찰이나 충분한 메커니즘 근거가 있을 때만 끌어낸다.
- cross-link 는 후보를 제시하되 개수 채우기를 하지 않는다. 기존 tree 에서 프로젝트와 제약과 메커니즘 페이지를 찾고, 관계를 설명할 수 있는 것만 연결한다.

## Workflow

### 0. 사전 점검 (모든 호출)

1. `<NAITE_ROOT>/AGENTS.md` 의 결정 스레드 절과 `docs/CONVENTIONS.md` 의 Soft ontology 절과 개인 나무의 범위 절과 Ontology 절을 읽는다. `.naite/ontology/subject-tree.md`(정본 경로)와 `.naite/ontology/topics.md`(정본 어휘)도 읽는다.
2. `<NAITE_ROOT>/tree/trunk.md` 를 전문으로 읽어 도메인과 기존 hub 페이지 후보를 수집한다.
3. `<NAITE_ROOT>/tree/rings.md` 의 마지막 20줄 정도를 읽어 최근 맥락을 파악한다.
4. 트리거 모드를 판별한다. 자연 감지나 작업 종료 모드면 사용자에게 한 줄 확인을 받은 뒤 진행한다.

### 1. Decision-kernel pass

대화와 기존 페이지에서 이미 확인된 내용을 먼저 채운 뒤, 빠진 항목만 질문한다.

1. 선택과 상태: 무엇을 선택·기각·보류·번복했으며 지금도 유효한가?
2. 맥락과 구속 조건: 어떤 문제와 제약이 결정을 필요하게 했고, 실제로 어느 제약이 선택을 갈랐는가?
3. 대안: 현실적으로 고려한 대안과 기각 이유는 무엇인가? 실제 대안이 없었다면 그 사실과 이유를 적는다.
4. 예상 메커니즘: 이 선택이 입력과 처리와 병목과 결과를 어떻게 바꿀 것으로 보았는가?
5. 검증 상태: 무엇을 실제로 관찰했고, 무엇이 해석이며, 무엇이 아직 검증하지 않은 기대인가? 미검증이면 필요한 관찰이나 실험을 적는다.
6. 실패와 재검토 조건: 어떤 신호나 맥락 변화나 비용이나 결과가 이 결정을 무효화하거나 다시 열게 하는가?

결과와 반복과 롤백 비용과 재사용 조건과 invariant 와 관련 페이지와 다음 행동은 실제 근거가 있을 때만 더한다. 빈 절은 쓰지 않는다.

### 2. Cross-link 검수

본문의 wikilink 마다 주변 산문이 실제 관계를 설명하는지 확인한다.

- 프로젝트와 구속 조건과 작동 메커니즘과 대안과 영향받는 개념 중 tree 에 존재하는 페이지를 후보로 제시한다.
- 관계를 설명할 수 없는 링크는 추가하지 않는다. 이미 있는 장식성 링크는 수선 범위에서 제거하거나 관계를 설명해 준다.
- 필요한 개념이 tree 에 없으면 3단계의 stub 제안으로 넘긴다.

### 3. 누락 개념의 stub 제안

대화 중 "이 개념은 tree 에 아직 없다"가 발견되면 다음처럼 처리한다.

- `tree/seeds.md` 에 한 줄 추가를 제안한다: `- [[missing-slug]] — first seen in [[this-decision-slug]], context: ...`
- 사용자가 승인하면 추가한다. 강요하지 않는다.

### 4. 페이지 작성

`<NAITE_ROOT>/tree/<slug>.md` 를 작성한다. 형태는 아래 Templates 절을 참조한다.

frontmatter:

```yaml
---
kind: decision   # standalone 열매 페이지. 다른 kind 안에 embed 도 가능 (concept/entity/source-record)
form: prose
topics: [...]
subject: [<path>]
source-types: [conversation]   # fruit 는 대부분 conversation 산출물
domains: [<subject-top-level>]   # CACHED — 위 subject path 에서 기계적으로 도출
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

본문을 `docs/CONVENTIONS.md` 의 학습 노트 품질 축과 kind 별 품질 계약의 decision 계약으로 자기 점검한다. H 계층이 실제 결정 흐름을 드러내게 하고, 짧은 결정에 빈 형식용 heading 을 만들지 않고, `## Source` 앞의 본문에는 em dash(`—`)를 쓰지 않는다. 특히 다음을 확인한다.

- 선택의 현재 상태와 구속 조건이 드러나는가?
- 실제 대안과 예상 메커니즘이 있는가, 또는 없는 이유를 정직하게 적었는가?
- 관찰한 결과와 해석과 미검증 기대를 구분했는가?
- 실패·롤백·재검토 조건 중 해당하는 신호가 있는가?
- wikilink 가 개수 채우기가 아니라 추론을 지탱하는가?

### 5. `tree/trunk.md` 갱신 (hub 자격이 있을 때만)

이 열매 페이지가 hub 후보면(다른 페이지에서 링크를 자주 받을 가능성이 높으면) `## Knowledge domains` 의 해당 도메인 "주요" 줄에 한 줄을 추가한다. 한도(4~7개)에 닿으면 어느 줄을 빼고 넣을지 사용자에게 묻는다.

대부분의 열매 페이지는 작은 결정 한 건이라 hub 후보가 아니다. 이때는 trunk 에 올리지 않고 본문 wikilink 와 산문 관용구로만 발견되게 둔다. care --check 의 고연결 페이지 검사가 승격 후보를 자동으로 surface 한다.

상세는 `docs/CONVENTIONS.md` 의 trunk.md 규율 절이 담당한다.

### 6. `tree/rings.md` 에 덧붙이기

```
## [YYYY-MM-DD] fruit | <slug>
- pages created: [[<slug>]]
- pages updated (back-prose 박은 경우): [[...]]
- domain: <subject-tree 의 top-level, 예: ml | statistics | personal>
- stubs added: N
```

### 7. 양방향 산문 제안

이 결정이 닿는 기존 concept 페이지가 있으면, 그 페이지에도 한 줄을 넣을지 사용자에게 확인한다.

> "`[[other-page]]` 에 'used in [[this-decision-slug]]' 나 '`[[this-decision-slug]]` 의 trade-off 분석 참조' 같은 산문 한 줄을 추가할까요?"

승인되면 그 페이지를 편집한다. synapse 가 양방향으로 자라게 된다.

### 8. 쓰기 이후의 의무 (tree 변경 공통)

열매 페이지 작성도 tree 변경이므로 grow·ingest 와 같은 사후 의무가 적용된다 (`docs/CONVENTIONS.md` 의 출력 품질 계약과 `docs/CONTEXT.md` 의 검증 절).

- 새 페이지 본문에 content guard 를 실행한다 (원자료·공정 화법 없음, 자립 산문).
- 생성 지도를 재생성한다. `python .naite/scripts/build-tree-manifest.py`(새 페이지와 좌표)를 실행하고, 이 열매가 다른 페이지와 링크로 이어졌으면 `python .naite/scripts/build-tree-dependencies.py` 도 실행한다 (7단계의 양방향 산문을 반영하려면 특히 필요하다).
- 이 재생성을 빼먹으면 지도가 낡아서 다음 orphan·inbound 계산이 어긋난다.

### 9. Checkpoint

사용자에게 한 문단으로 요약한다.

- 작성된 페이지 경로.
- 추가된 stub 목록.
- 양방향 산문을 넣은 페이지 목록.
- decision kernel 에서 확인된 것과 아직 미검증인 것.
- 다음 행동 (있으면).

## Templates

### 독립 decision 페이지 (적응형 구성 예시)

```markdown
---
kind: decision
form: prose
topics: [<canonical-topics>]
subject: [<path>]
source-types: [conversation]
domains: [<subject-top-level>]   # CACHED — 위 subject path 에서 기계적으로 도출
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# {무엇을 어떻게 결정했는지 드러나는 제목}

{YYYY-MM-DD 현재 무엇을 선택·기각·보류했는지, 그리고 결정이 잠정적인지 확정적인지를 첫 문단에서 바로 적는다.}

## 무엇이 선택을 갈랐나

{결정이 필요했던 문제와 실제 구속 조건을 설명한다. 현실적으로 검토한 대안은 같은 비교 축으로 서술한다. 대안이 없었다면 만들지 말고, 비교하지 못한 이유를 남긴다.}

## 이 선택이 작동할 것으로 본 이유

{입력, 처리, 병목, 결과가 어떻게 달라질 것으로 보았는지 설명한다. 관련 메커니즘이나 프로젝트는 관계가 드러나는 문장으로 연결한다.}

## 현재 확인한 것과 아직 모르는 것

{실제로 관찰한 결과와 그 해석을 분리한다. 기대에 머무는 결과는 아직 확인하지 않았다고 밝히고, 어떤 관찰이나 실험이 필요한지 적는다.}

## 다시 결정을 열 조건

{어떤 신호, 비용, 품질 저하, 사용자 행동 또는 맥락 변화가 결정을 무효화하거나 재검토하게 하는지 적는다. 되돌리기 비용이 중요하면 함께 적는다.}

{결정 변경 이력, 다음 증거, 다른 페이지와의 연결은 실제 내용이 있을 때만 자연스러운 heading 이나 마무리 문단으로 더한다. 단순 링크 목록은 쓰지 않는다.}
```

이 예시는 decision kernel 의 배열 한 가지일 뿐이다. 실제 페이지의 H2 이름과 개수는 결정의 논리 흐름에 맞춰 바꾸고, 짧은 결정은 두세 절이나 몇 문단만으로도 충분할 수 있다. 위 heading 을 고정 양식처럼 복사하지 않는다.

### synapse 짧은 형태 (다른 concept 페이지에 넣는 산문)

별도 페이지가 필요할 만큼 무겁지 않으면, 기존 concept 페이지의 본문에 decision kernel 을 짧은 단락으로 남긴다.

```markdown
## 프로젝트에서의 판단

2026-04 [[project-portfolio-site]]에서 retrieval precision을 높이기 위해 [[2-stage-reranking]]을 검토했지만, [[interactive-latency-budget]]을 넘을 가능성 때문에 보류했다. 현재 관찰한 것은 latency 예산뿐이며 precision 개선 효과는 아직 검증하지 않았다. 캐시를 적용한 실험에서 예산 안에 들어오면 결정을 다시 연다.
```

이런 산문이 여러 페이지에 흩어져 있으면 grep 으로 의사결정 thread 가 즉시 드러난다.

## 이 명령이 절대 하지 않는 것

- 새 type 과 새 frontmatter 필드와 새 메타 도메인 태그를 신설하지 않는다.
- 결정 꼴 페이지를 별도의 메타 색인으로 분리하지 않는다.
- 진로 관련 frontmatter 와 `[[fde-skill-*]]` 페이지를 미리 만들지 않는다 (`docs/CONVENTIONS.md` Decision thread 형태 절의 grep-on-demand 원칙을 지킨다).
- 파일명에 `DMU-YYYYMMDD-...` prefix 를 쓰지 않는다.
- 고정 절을 강제로 채우지 않는다. 미검증과 누락을 추측으로 메우지 않는다.
- outbound wikilink 의 개수를 맞추려고 장식성 링크를 추가하지 않는다.
- frontmatter 의 `domains` 는 선택한 `subject` 경로의 top-level 에서 기계적으로 도출해 함께 쓴다. 임의 값을 선택하지 않는다. `care --check` 는 낡은 cache 를 보고만 한다. hub 후보면 별도로 `trunk.md` 의 해당 도메인 주요 줄에 한 줄을 더한다.
- 모든 열매 페이지를 자동으로 `trunk.md` 에 등재하지 않는다. hub 후보일 때만 등재한다.
- git 커밋을 하지 않는다.
