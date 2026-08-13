# /naite care --check

이 파일은 점검 모드의 계약이다. `care.md` 가 `--check` 나 "점검만"이나 "상태 봐줘" 의도를 감지하면 이 파일을 읽고 그대로 따른다. 점검은 나무의 건강을 확인하고 보고만 하며 절대 자동 수정하지 않는다.

선택 플래그:

- `/naite care --check --daily`: 일일 자동화 프로파일이다. 같은 검사를 실행하되, 사용자 결정을 바꿀 가능성이 큰 발견에 추가 읽기 예산을 쓴다. 지속 보고도 `.naite/reports/daily/YYYY-MM-DD-care-check.md` 에 쓴다.

기본 출력은 대화에 인쇄되는 markdown 보고 하나다 (파일로 쓰지 않는다). `--daily` 에서는 보고를 인쇄하고 `.naite/reports/daily/YYYY-MM-DD-care-check.md` 에도 쓴다. 사용자가 발견에 대해 조치하고 싶으면 이후 명령으로 수리를 지시한다. care --check 는 `tree/rings.md` 에 항목 하나를 덧붙인다.

```
## [YYYY-MM-DD] care-check | <N> findings
- orphans: N
- stubs: N
- ontology — frontmatter incomplete: N
- ontology — subject tree drift: N
- ontology — topic uncanonicalized: N (P promotion candidates)
- ontology — domain cache stale: N
- ontology — BOM-prefixed: N
- ontology — legacy collection drift: N
- slug collisions: N
- trunk drift: N
- secrets: N
- binary creep: N
- skill candidates: N
- failure patterns: N
- user model refresh: yes | skipped
- post-grow residue: N
- stale archive dirs: N
- branch archive coherence: N
- output quality guard: N
- body em dash: N
- study-note quality issues: N (markdown form: a, study effectiveness: b, content composition: c, writing manner: d)
- decision/insight quality issues: N (decision: a, insight: b)
- high-degree neurons: top-N listed
- autonomy garbage: N (low-use canonical: a, trivial narrower: b, orphan spawn: c)
- context maps: refreshed | stale | missing
- daily report: .naite/reports/daily/YYYY-MM-DD-care-check.md | n/a
```

## 토큰 예산의 계층

care --check 는 이미 넓은 기계 검사를 갖고 있다. 품질은 검사를 더하는 데서가 아니라, 기계적 카운트에 판단이 필요한 곳에 읽기 토큰을 쓰는 데서 나온다.

### Tier 1 — 깊은 증거 검토

발견이 있으면 다음 네 영역에는 항상 추가 읽기 예산을 쓴다.

1. 누락 target 과 stub: 의미 있는 누락 target 마다 그 target 을 링크하는 소스 페이지를 최소 하나 연다. 그 링크가 `rings.md` 의 과거 이력인지, placeholder·template 산출물인지, 의도된 평문·외부 참조 후보인지, 실제로 깨진 wikilink 인지, 새 개념 페이지의 후보인지 분류한다.
2. 출력과 학습 노트의 품질: 결정론 검출마다 걸린 구절만이 아니라 그 줄의 앞뒤 맥락을 읽는다. 그 다음 Markdown form 과 study effectiveness 와 content composition 과 writing manner 를 독립적으로 판단한다. guard 가 깨끗하다는 결과는 그 페이지가 잘 가르친다는 증거가 아니다.
3. decision 과 insight 의 품질: 독립된 `kind=decision`·`kind=insight` 페이지와 다른 kind 안에 파묻힌 추론을 구분한다. 증거의 부재와 약한 template 을 구분할 만큼 본문 맥락을 읽는다. 명시된 unknown 과 미검증 상태는 유효하고, 짐작으로 채운 완전성이 결함이다.
4. 자율성 쓰레기: 정리 후보를 surface 하기 전에 30일 윈도와 사용 카운트와 inbound 카운트를 검증한다. 카운트만 보고 topic 이나 narrower 나 생성된 concept 를 쓰레기로 보고하지 않는다.

### Tier 2 — 조건부 깊은 검토

1차 통과에서 반복 신호가 보일 때만 더 깊이 읽는다.

1. 스킬 후보: 최근 50개 정도의 기록 항목에서 반복되는 수동 절차가 보이면, 반복된 op 이름만이 아니라 실제 절차를 식별할 만큼 인접 항목을 읽는다.
2. 실패 패턴: aborted 나 실패성 항목이 뭉치면, 근본 원인과 예방 지점을 식별할 만큼 주변 기록을 읽는다.

### 카운트 전용 신호

13절의 고연결 페이지는 카운트 전용으로 유지된다. 그 절에 정성 해석을 더하지 않는다. 고연결 카운트는 다른 발견의 우선순위 신호로만 쓴다. 예를 들어 출력 품질 문제가 주요 hub 에 영향을 줄 때다.

## 발견의 분류

0이 아닌 각 발견은 구분이 사용자 행동에 영향을 줄 때 다음 라벨 중 하나를 단다.

- `blocker`: 사용자가 조치할 때까지 커밋이나 수리 흐름을 멈춰야 한다. 대개 비밀이나 데이터 안전이다.
- `false-positive`: 기계적으로 걸렸지만 맥락 검토 후 나무의 결함이 아니다.
- `intentional-debt`: 알려졌거나 의도된 잔재다. 감사 가치를 위해 보존한 `rings.md` 의 과거 링크가 그 예다.
- `repair-candidate`: 이후의 사용자 지시 pass 에서 고칠 수 있는 구체적인 페이지·링크·소스 화법·워크플로 문제다.
- `source-risk`: 잘 읽히지만 소스 검토 없이 다시 쓰면 안 되는 fidelity 민감 페이지다 (공식, 정의, 정리, 조건, 수치). 수리를 미룬다 (`docs/CONVENTIONS.md` 출력 품질 계약의 source-fidelity 상한).
- `schema-pressure`: 온톨로지나 워크플로나 검사 규칙의 진화를 정당화할 수 있는 반복 증거다. 스키마 진화 규칙을 따른다.

`--daily` 에서는 보고가 우선 검토 후보 3개로 끝나야 한다. 이 후보는 자동 수정이 아니다. 사람이나 이후의 `/naite care --daily` 검토에 가장 유용한 세 항목이다.

## 검토 증거와 재검증 규율

요청된 scope 의 첫 care-check 가 필요한 전체 검사 집합을 한 번 수집한다. 이후의 수리가 모든 lane 의 반복을 정당화하지 않는다. `docs/CONTEXT.md` 의 검증 무효화와 완료 규율 절을 따라, 소유 파일이나 의존물이 바뀐 검사만 다시 실행한다.

- 모든 PASS 를 검토한 스냅샷과 scope 에 결부시킨다. 영향을 주는 파일이 바뀌기 전까지 유효하다.
- FAIL 에는 재현 가능한 명령이나 확인 방법과, 해당할 때의 정확한 파일과 줄과, 기대 상태와 실제 상태와, 최소 수리 경계가 포함되어야 한다. 선호와 개선 가능성과 미검증 의심은 blocker 가 아니다.
- 새 증거 없이 `false-positive` 와 `intentional-debt` 와 `repair-candidate` 와 `source-risk` 와 공개된 범위 밖 잔재를 `blocker` 로 승격하지 않는다. 요청된 결과를 막거나 안전 위험을 만든다는 증거가 있어야 한다.
- 읽기 전용 검토자는 파일을 편집하지 않고, 지도를 재생성하지 않고, lock 을 갱신하지 않고, 미러를 sync 하지 않고, 저장소 상태를 바꾸는 명령을 실행하지 않는다. 스크립트가 dry-run 이나 check 모드를 문서화하지 않았으면 호출 전에 인터페이스나 소스를 확인한다. `--check` 나 `--dry-run` 이나 `--help` 가 부작용 없다고 가정하지 않는다.
- 안정된 스냅샷에서 무효화된 lane 마다 최대 한 번의 검토 pass 를 실행한다. 사용자가 요청하거나 변경이 안전에 결정적이거나 첫 pass 가 자기 lane 안에서 해소할 수 없는 증거를 보고할 때만 독립 pass 를 추가한다.
- 요청된 산출물과 정확한 범위 산정과 관련 결정론 검사와 diff 검사와 허가 경계와 blocker 종결이 전부 통과하면 완료를 보고하고 멈춘다. 완료 계약이 충족된 뒤에 새 감사 범위를 열지 않는다.

## Checks

전부 한 pass 에서 실행한다. 실패에서 short-circuit 하지 말고 모든 것을 수집한다.

### 0. 컨텍스트 지도

`docs/CONTEXT.md` 를 읽는다. 그 다음 생성된 운영 지도를 갱신하고 읽는다.

```powershell
python .naite/scripts/build-tree-manifest.py
python .naite/scripts/build-tree-dependencies.py
```

페이지 좌표에는 `.naite/ontology/tree-manifest.json` 을, inbound·outbound 링크 데이터에는 `.naite/ontology/tree-dependencies.json` 을 쓴다. 두 지도는 추적되는 생성 파일이지 손으로 편집하는 정본 어휘가 아니다.

care-check 보고에 생성 지도의 상태를 적는다.

- `manifest pages: N`
- `dependency edges: N`
- `dependency missing targets: N`
- `dependency orphans: N`

`--daily` 에서는 짧은 delta 노트를 포함한다.

- 자동화가 last-run 시각을 주면 `git log --since <last-run>`.
- 생성 지도의 diff 가 timestamp 만인지 그래프 카운트 변화인지.
- 가능하면 이전 daily 기억·보고 대비 hard blocker 카운트가 바뀌었는지.

참고로 `--daily` 에서는 짝인 `/naite care --daily` 분류가 `.naite/reports/daily/YYYY-MM-DD-care-check.md` 를 읽고 자기 `.naite/reports/daily/YYYY-MM-DD-care.md` 를 쓴다.

### 1. Orphans

`tree/` 의 페이지(`trunk.md` 와 `rings.md` 와 `seeds.md` 제외) 중 다른 `tree/` 페이지에서 들어오는 wikilink 가 0 인 것을 찾는다.

1차 소스는 `.naite/ontology/tree-dependencies.json` 이다. 지도를 쓸 수 없으면 `tree/*.md` 전체에 `\[\[<slug>` 와 `\[\[<slug>\|` 를 Grep 하는 폴백을 쓴다. 페이지 자신과 `trunk.md`·`rings.md`·`seeds.md` 밖에서 일치가 없으면 orphan 이다.

보고: orphan slug 와 그 domain 을 나열한다. 어떤 것이 링크나 삭제의 후보인지 제안한다. branch 메타 페이지(`course-{slug}-00-index.md`)는 보통 `trunk.md` Branches 절에서만 링크되므로, 내용 페이지에서의 inbound 가 낮아도 orphan 이 아니다.

### 2. Stubs

- `tree/seeds.md` 를 읽고 아직 해소되지 않은 항목을 나열한다.
- 모든 페이지에서 개념 언급을 스캔한다. 어떤 명사구가 굵은 글씨로 나오거나, 존재하지 않는 wikilink target 이거나, 두 페이지 이상에서 세 번 이상 평문으로 나오는데 대응하는 `tree/<slug>.md` 가 없으면 새 stub 으로 제안한다.

`.naite/ontology/tree-dependencies.json` 의 누락 target 에는 stub 을 제안하기 전에 Tier 1 검토를 적용한다. `rings.md` 의 과거 항목과 placeholder 와 의도적으로 안 만든 외부 조직 이름을 페이지 증거 없이 stub 으로 승격하지 않는다.

보고: 미해소 stub 과 새로 제안하는 stub.

### 3. Ontology 검증

매 페이지의 frontmatter 5 facet(`kind`, `form`, `topics`, `subject`, `source-types`)과 cache 인 `domains` 와 날짜를 ontology spec(`docs/CONVENTIONS.md` Ontology 절, `.naite/ontology/subject-tree.md`, `.naite/ontology/topics.md`)과 비교한다. 자세한 능력 spec 은 `docs/ARCHITECTURE.md` 4.2절과 5.2절이 담당한다.

스키마 규칙:

- 유효 스키마는 `kind`·`form`·`source-types` 다.
- legacy 스키마(`type`·`role`·단수 `source-type`)는 오류다. legacy 가 surface 되면 드리프트 신호이고, 해당 페이지를 새 스키마로 수동 전환한다.
- mixed 스키마(한 페이지 안에 kind 와 role, 또는 type 과 form 의 혼재)는 드리프트이자 오류다. 수동 수정이 필요하다.
- 새 페이지를 쓸 때는 항상 새 스키마만 쓴다.

도우미: `.naite/scripts/lint-ontology.py` 는 결정론 Python 검증기로 3a~3k 의 기계 검사(3k 는 form=prose 잎 깊이 경고)와 7절의 비 tree 오염 검사를 수행한다. 군집 탐지(Louvain)와 topic 별칭 군집 같은 무거운 작업은 LLM 주도로 별도로 한다.

```
python .naite/scripts/lint-ontology.py                # report only
```

`--strip-bom` 과 `--refresh-domains` 는 파일을 쓰는 수선 플래그라 care-check 에서 실행하거나 안내하지 않는다. 발견 건수와 대상만 보고하고, 사용자가 수선을 승인하면 `/naite care` Repair 모드로 넘긴다.

#### 3a. Frontmatter 완결성

모든 내용 페이지(`trunk.md`·`rings.md`·`seeds.md` 제외)가 다음 필수 facet 을 유효한 enum 값으로 가져야 한다.

- `kind`: enum `concept | entity | source-record | project | decision | insight | comparison | essay | personal`
- `form`: enum `prose | index`
- `topics`: 리스트 (페이지당 0~5개, 빈 배열 허용)
- `subject`: 리스트 (SKOS-lite 경로 1개 이상)
- `source-types`: enum 값의 리스트 `course | conversation | paper | article | docs | book | essay | external` (원소 하나짜리 리스트 허용, 항상 리스트)
- `domains`: 리스트 (cache. `subject` 의 top-level 에서 기계적으로 도출되고, care-check 는 낡음 여부만 보고한다)
- `created`, `updated`: `YYYY-MM-DD`

미보유와 잘못된 enum 과 빈 subject 가 발견되면 incomplete 로 surface 한다.

legacy 스키마는 오류다. 다음이 발견되면 incomplete 로 surface 하고 새 스키마로 수동 전환한다.

- `type` 이나 `role` 이나 단수 `source-type` 이 있는데 `kind` 가 없으면 legacy 스키마다 (incomplete).
- `kind` 와 `role` 이 함께 있거나 `type` 과 `form` 이 함께 있으면 mixed 스키마다 (incomplete, 드리프트 신호).

`.naite/scripts/lint-ontology.py` 의 `detect_schema()` 가 자동으로 감지한다.

#### 3b. Subject tree 검증

각 페이지의 `subject` 필드의 모든 경로가 `.naite/ontology/subject-tree.md` 의 정본 트리에 존재해야 한다.

- top-level 이 `subjects:` 의 key 이거나 어느 도메인의 `altLabels` 안에 있어야 한다.
- 경로가 narrower(`parent/narrower`)면 그 `narrower` 가 부모의 `narrower:` 목록에 있어야 한다.

미등록 경로는 드리프트다. altLabel 로 해석되면 alias hit 으로 분류한다 (정본으로의 점진적 갱신을 권장하되 강제하지 않는다).

승격 후보: 어떤 narrower 후보가 다섯 페이지 이상에 등장하는데 정본에 없으면 surface 한다 (사용자 결정 후 `.naite/ontology/subject-tree.md` 에 추가한다). wikilink 그래프의 군집 탐지(Louvain modularity) 결과와 교차 참조한다.

#### 3c. Topic 정본 검증

각 페이지의 `topics` 의 모든 항목이 `.naite/ontology/topics.md` 의 `canonical_topics` 에 있거나 `aliases` 지도의 key 여야 한다.

- 미등록 topic 은 경고다 (차단이 아니다). folksonomy 철학이다 (`docs/CONVENTIONS.md` Ontology 절).
- 세 페이지 이상에 등장하면 승격 후보다 (사용자 confirm 후 정본에 추가한다).
- Levenshtein 거리 2 이하의 쌍(topic 끼리나 topic 대 정본)은 별칭 후보로 surface 한다.
- topic 이 넓은 도메인 이름(`ml`, `statistics` 등)이거나 페이지 특정(`course-ma101-ch03-binomial`)이면 오용으로 surface 한다. `topics` 는 재사용 가능한 개념 수준이어야 한다.

#### 3d. Domain cache 의 신선도

각 페이지의 `domains` cache 가 `subject` 에서 정확히 도출됐는지 확인한다.

- 기댓값은 `domains == derive_domains(subject)` 다 (첫 등장 순서, 중복 제거).
- 불일치하면 cache 갱신이 필요한 repair candidate 로 surface 한다. care-check 에서는 쓰지 않고, 사용자 승인 후 `/naite care` Repair 모드에서 갱신한다.

#### 3e. Kind·form·source-types 의 분포

매 care-check 가 enum 별 카운트 표를 surface 해서 새 enum 도입의 압력을 감지한다.

- `kind` 분포: `concept` / `entity` / `source-record` / `project` / `decision` / `insight` / `comparison` / `essay` / `personal` 별 카운트.
- `form` 분포: `prose` / `index` 별 카운트.
- `source-types` 분포: `course` / `conversation` / `paper` / `article` / `docs` / `book` / `essay` / `external` 별 카운트 (한 페이지가 복수 값을 가질 수 있어 합계가 페이지 수와 다를 수 있다).

승격 후보: 본문 분석에서 자주 등장하는 페이지 형태 패턴이 기존 enum 에 맞지 않으면 surface 한다 (예: tutorial 형태, literature-review 형태, video 소스 등). 다섯 페이지 이상 누적되면 사용자 결정 후 `docs/CONVENTIONS.md` Ontology 절의 enum 에 추가한다.

#### 3i. 스키마 무결성 (드리프트 감지기)

alias 단계가 끝났고 tree 는 전부 새 스키마다. 다음 지표는 0 이어야 정상이다.

- `legacy_schema_count`: type·role·단수 source-type 만 있는 페이지다. 0 보다 크면 신규 페이지가 옛 스키마로 작성된 것이고 해당 페이지를 새 스키마로 수동 전환한다.
- `mixed_schema_count`: kind 와 role 또는 type 과 form 의 혼재다. 0 보다 크면 수동으로 고친다.
- `unknown_count`: 어느 스키마 필드도 없다. 0 보다 크면 frontmatter 파싱 오류거나 incomplete 페이지다.

#### 3j. 출력 품질 계약의 guard

`docs/CONVENTIONS.md` 출력 품질 계약의 결정론 부분집합을 surface 한다. 품질 평가가 아니라 본문 위생의 guard 다. false positive 는 가능하지만, 새 생산자 출력과 손댄 course 페이지에서는 발견 즉시 고친다.

스캔 대상:

- 모든 내용 페이지와 `tree/trunk.md` 와 `tree/seeds.md` 의 trailing `## Source` 앞 본문: em dash(`—`, U+2014).
- append-only 인 `tree/rings.md`: 기존 이력의 em dash 는 소급 수정하지 않고 별도의 intentional debt 로 계수한다. 새로 쓰는 항목은 em dash 0건이어야 한다.
- 모든 `tree/course-*.md` 의 trailing `## Source` 앞 본문: 기존의 원자료·소스 공정 화법과 mojibake 와 범용 영어 course heading 규칙.
- 워크플로가 방금 쓴 최근 변경된 일반 tree 페이지: 기존 출력 품질 패턴도 함께 확인한다.

표시할 것:

- em dash(`—`, U+2014): 모든 페이지 kind 의 본문과 수정 가능한 특수 페이지에서 금지된다. 쉼표와 마침표와 콜론과 괄호와 줄바꿈 중 논리 관계에 맞는 표현으로 고치고, 하이픈 일괄 치환은 금지된다.
- `## Source` 앞의 roots·소스 경로 누출: `roots/`, `` `raw` ``, `Staging`, `Source Staging`, `Archived source bundle`.
- 소스·공정 화법: `PDF page`, `raw PDF`, `source PDF`, `source page`, `lecture notes`, `page range`, `render`, `image-read`, `backfill`, `run-log`, `extraction`.
- 한국어 소스 화법: `필기에는`, `필기에서`, `강의 노트`, `노트에서는`, `원문에서는`, `원자료`, `자료에서는`, `페이지에서는`, `이 페이지에서는`, `이 자료`.
- mojibake 표식: `???`, `�`, `Ã`, `Â`.
- 범용 영어 course heading: `Status`, `Scope`, `Chapters`, `Projects`, `Connections`, `Also known as`, `Overview`, `Related`, `Sequence Logic`, `Practice & Assignments`, `Course Bridges`, `Concept Extraction`, `Source Staging`, `Names`, `Maps to`.

표시하지 않을 것:

- `course-*-00-index.md` 메타 페이지 (mojibake 는 예외 없이 검사한다). 그 template(`grow-branch.md` Templates 절)이 범용 heading(`Also known as` / `Overview` / `Scope` / `Chapters` / `Related` / `Subchapters` / `Chapter summary` / `Maps to`)과 `Staging: roots/...` 포인터를 요구하므로, heading·누출 규칙이 그 페이지들에는 적용되지 않는다.
- trailing `## Source` 블록 안의 경로.
- 수식과 코드펜스와 명령과 모델 이름과 방법 이름과 기술 영어 용어와 course 고유의 영어 제목.
- 출처·공정 화법이 아니라 기술 개념인 `source` 단어 (예: source node, source distribution, source coding).

파일과 줄과 걸린 구절과 그것이 `## Source` 앞인지를 보고한다. 손댄 생산자 출력에서는 완료 전 필수 수정으로 취급한다. em dash 발견은 blocking 이다. 규칙이 보편적이고 결정론적이기 때문이다. 나머지 발견은 전체 care-check 실행에서는 report-only 로 남되, 활성 워크플로가 이미 그것을 수리 중이면 예외다.

`--daily` 에서는 서로 다른 출력 품질 군집마다 `false-positive` 나 `intentional-debt` 나 `repair-candidate` 분류를 포함한다.

#### 3k. 잎 깊이 guard

warn-only 의 근사 검사다. `form=prose` 잎 페이지에 대해 두 가지를 감지한다.

- 본문(frontmatter 제외, `## Source` 이전)에 `[[wikilink]]` 가 0개인 경우.
- 본문 산문의 글자 수가 대략 400자 미만인 경우 (얇은 본문).

두 항목 모두 정밀 판정이 아니라 굵은 근사다. 실제 깊이 판정의 기준은 작성 시점의 자기 점검(`docs/QUALITY.md` 4절 LEAF-1~6)이고, care-check 는 report-only 로만 surface 한다. blocker 가 아니고 자동 수정도 없다.

#### 3f. BOM 검출

UTF-8 BOM(`EF BB BF`) prefix 를 검출한다.

- `tree/*.md` 의 어느 페이지든 BOM 을 가지면 surface 한다.
- 발견된 파일을 제자리 정규화가 필요한 repair candidate 로 surface 한다. care-check 에서는 쓰지 않고, 사용자 승인 후 `/naite care` Repair 모드에서 정규화한다.
- 정상 운영 상태에서는 0 이어야 한다 (migration 때 제거된다).

#### 3g. 과목·컬렉션·소스 이름의 frontmatter 사용 (legacy 드리프트)

`course` 와 `course-{slug}` 와 `anthropic-academy` 와 `ode` 와 `laplace-transform` 같은 컬렉션·entity·하위 주제 이름이 `domains` 나 `subject` 에 들어간 사례다. 항상 0 이어야 하고 발견 즉시 surface 한다.

#### 3h. 언어 형태의 검토 후보

`docs/CONVENTIONS.md` Naming 절의 "한국어 산문과 영어 heading·용어" 정책에서 벗어난 후보를 surface 한다. 품질 평가가 아니라 정책 준수의 후보 검토 단계다. 비율과 등급과 임계와 점수는 없다.

surface 규칙 (단순 존재 확인이고 false positive 가 예상된다):

- 산문 맥락의 줄(heading 이 아니고 코드블록·수식블록 밖이며 알파벳이나 한글이 있는 줄)에 한글이 없으면 후보다.
- heading 맥락의 줄(`^#+ ` 로 시작)에 라틴 문자가 없으면 후보다.

수식 줄과 영어 인용 줄과 영어 정의 줄과 외국어 hub entity 등은 false positive 일 수 있다. 사람이 직접 검토한 뒤 정책 위반인 경우만 고친다. care-check 자체는 줄의 위치만 surface 한다.

blocker 가 아니다 (blocker 는 비밀뿐이다). 보고는 후보 줄의 위치만 출력한다.

#### 3 종합 보고 형식

```
## Ontology validation
| Sub-check | Count | Action |
|---|---|---|
| 3a frontmatter incomplete | N | fix per page |
| 3b subject tree drift | N | resolve via altLabel or migrate |
| 3c topic uncanonicalized | N | surface promotion / alias candidates |
| 3d domain cache stale | N | route to care Repair |
| 3e kind/form/source-types distribution | (table) | surface enum-add candidates |
| 3f BOM-prefixed files | N | route to care Repair |
| 3g legacy collection/entity drift | N | manual migration |
| 3h language-shape review candidates | N lines | manual review (false positive expected) |
| 3i schema integrity (drift detector) | legacy N / mixed M | both must be 0; if > 0 fix pages to the new schema |
| 3j output quality contract guard | N lines | fix source/process voice and raw leakage |
| 3k leaf-depth guard | N findings | warn-only; thin/unlinked prose leaves (real bar: write-time self-check) |
```

3i 의 legacy·mixed 카운트가 0 인 것이 정상 상태다. 0 보다 크면 새 페이지가 옛 스키마로 작성됐다는 드리프트 신호다.

### 4. Slug 충돌

- 대소문자 무시 충돌: `Attention.md` 대 `attention.md`. 프로젝트 규약이 lowercase-kebab-case 이므로 규약에 맞지 않는 파일 자체도 위반이다.
- 근사 중복: Levenshtein 거리 2 이하의 slug 쌍 (예: `attention.md` 대 `attentions.md`)이나 한쪽이 다른 쪽의 엄밀한 suffix·prefix 인 쌍 (`attention.md` 대 `attention-mechanism.md`). 서로 다른 챕터에서 같은 짧은 제목을 가진 course 페이지 (예: `course-ma101-ch02-01-basic-concepts` 와 `course-ma101-ch03-01-basic-concepts`)는 의도된 관례라 표시하지 않는다.

보고: 표시된 쌍이다. 자동으로 합치지 않는다. 어느 것이 정본인지 사용자에게 묻는다.

### 5. Trunk 드리프트

`trunk.md` 는 큐레이션된 대문 페이지다. 모든 페이지를 열거하지 않는다 (`docs/CONVENTIONS.md` trunk.md 규율 절 참조). 따라서 care --check 의 "missing/ghost" 의 의미도 그에 맞춰 바뀌었다.

큐레이션 커버리지 검사:

- 도메인 노출 임계 (`docs/CONVENTIONS.md` trunk.md 규율 절의 도메인 노출 기준과 동기화): subject-tree 의 top-level 중 kind=concept 와 kind=entity 페이지 합이 10장 이상이면서 그중 inbound 최고치가 10 이상인 도메인은 `## Knowledge domains` 아래에 `### <domain>` 절을 가져야 한다.
  - 임계를 통과하는데 미노출이면 드리프트다 (도메인 절 추가 후보).
  - 임계에 못 미치는데 노출되어 있으면 약화 신호다 (페이지 삭제나 rename 으로 도메인이 얇아진 경우이고, 유지·제거 결정을 사용자에게 요청한다).
  - 임계 미달 도메인은 branch drill-down 으로만 접근한다 (예: 단일 branch 하나에만 콘텐츠가 묶인 도메인). 새 branch 추가로 임계를 통과하면 이 surface 가 트리거된다.
- hub 누락: 각 노출 도메인의 inbound 링크 상위 5 페이지 중 `### <domain>` 의 주요 줄에 없는 페이지가 있으면 후보로 surface 한다 (자동 추가는 금지된다. hub 인지 아닌지는 사용자가 결정한다).
- branch 누락: 모든 `course-{slug}-00-index.md` 는 `## Branches` 의 institution 절에 나와야 한다. 누락되면 어느 institution 절에 들어갈지 사용자에게 묻는다.

노이즈 검사 (이전 스키마의 잔재):

- 챕터·서브챕터의 등재: `course-{slug}-ch{NN}-*` 페이지가 trunk.md 에 나오면 노이즈이고 제거를 권장한다. branch 메타 페이지의 Chapters 절이 단일 소스다.
- `## Domain:` prefix: trunk.md 에 `## Domain:` heading 이 남아 있으면 스키마 migration 이 미완료다. `## Knowledge domains` 의 도메인 절이나 `## Branches` 의 institution 절로 교체한다.
- `## Domain: course-{slug}` 절: 2026-04-28 이후 스키마에서 폐기됐다. 발견되면 제거를 권장한다.

trunk 안의 ghost: `trunk.md` 가 참조하는 모든 slug 는 대응하는 `tree/<slug>.md` 를 가져야 한다. ghost 항목을 나열한다 (단 페이지 시작부의 형식 예시 블록에 있는 `[[page-slug]]` placeholder 는 false positive 다. 첫 코드블록 밖의 등장만 센다).

요약 드리프트: hub 페이지의 첫 문단이 `trunk.md` 의 한 줄 요약과 본질적으로 어긋나면 surface 한다 (경험 규칙: frontmatter 의 `updated:` 이후 trunk 요약이 갱신되지 않은 경우다).

### 6. 비밀과 PII 스캔

이 검사는 LLM 이 수행하는 pass 이지 결정론 관문이 아니다. 결정론 관문은 `.naite/hooks` 의 pre-commit·pre-push 가드이고, 공유 스캔 로직은 `.naite/hooks/_naite_guard.sh` 에 있다. `roots/` 와 `tree/` 아래의 모든 것을, 최소한 가드가 차단하는 것과 같은 토큰 계열로 regex 스캔한다 (이 목록은 단일 소스인 `.naite/hooks/_naite_guard.sh` 와 동기화를 유지한다).

- `sk-[A-Za-z0-9_-]{20,}` (OpenAI/Anthropic `sk-`, `sk-ant-`, `sk-proj-`, `sk-svcacct-`), Stripe `(sk|pk|rk)_(live|test)_...`
- GitHub `ghp_`/`gho_`/`ghs_`/`ghr_`/`ghu_` classic 과 `github_pat_...` fine-grained, GitLab `glpat-...`
- Slack `xox[baprs]-...` / `xapp-...` 와 Slack webhook URL (`hooks.slack.com/services/...`)
- AWS `AKIA[0-9A-Z]{16}`, Google `AIza[0-9A-Za-z_-]{35}` / `GOCSPX-...`
- HuggingFace `hf_...`, Databricks `dapi...`, SendGrid `SG....`, DigitalOcean `dop_v1_...`, Linear `lin_api_...`
- npm `npm_...`, PyPI `pypi-...`
- JWT `eyJ...\.eyJ...\....`, PEM `-----BEGIN ... PRIVATE KEY-----`
- `(?i)(password|passwd|secret|api[_-]?key|access[_-]?token|authorization)[:=]\s*\S{8,}` 에 걸리는 줄 중 값이 명백한 placeholder(`xxx`, `<redacted>`, `your-key-here`, `changeme`, `example`)가 아닌 것.
- URL 이나 해시로 보이지 않는 길이 40 이상의 고엔트로피 base64 류 문자열.
- PII: 한국 주민등록번호(`\d{6}-\d{7}`)와 전화번호와 카드 모양의 16자리 연속 숫자와 전체 주소와 국가 신분증 번호. 결정론 층은 PII 를 잡지 못하므로 이 스캔이 지속적인 PII 검사다.

커버리지 노트: 이 regex 스캔은 `roots/` 와 `tree/` 아래의 텍스트(`.md`)를 읽는다. 바이너리 내부는 볼 수 없다. force-track 된 PDF(`.gitignore` 는 작은 완성 PDF 의 `git add -f` 를 허용한다)의 텍스트 레이어에 비밀·PII 가 있어도 여기서는 보이지 않는다. 추적된 PDF 는 7절에서 surface 하고 깨끗한지 사용자에게 확인을 받는다.

무엇이든 일치하면 blocker 가 된다. 진행 중인 git 작업을 멈추고 파일과 줄을 보고하고, 진행 전에 삭제 처리를 사용자에게 요청한다. 일치가 `roots/conversations/_transcripts/`(영구 보존)나 이미 이전 커밋 안에 있으면 작업 사본의 수정만으로는 부족하다. 노출된 자격 증명의 rotate 를 권하고, 이미 커밋됐으면 push 전에 이력 재작성을 권한다.

### 7. Binary creep 과 비 tree 오염

Binary creep:

- `roots/assets/` 아래에서 1MB 를 넘는 파일을 나열한다. Git LFS 도입(Phase 2 결정)이나 변환·리사이즈 여부를 묻는다.
- `tree/` 아래의 markdown 이 아닌 파일을 표시한다 (0 이어야 한다).
- PDF 가 git 에 추적되는지 확인한다. `*.pdf` 는 기본적으로 `.gitignore` 가 차단하지만, `.gitignore` 는 작은 완성 PDF 의 `git add -f` 를 명시적으로 허용한다 (`CLAUDE.md` 바이너리 파일 절). 따라서 추적된 PDF 는 위반이 아니라 확인 대상으로 surface 한다. 의도된 force-track 인지, 그리고 6절이 들여다볼 수 없는 텍스트 레이어에 비밀·PII 가 없는지 사용자에게 확인한다.

비 tree 의 scratch 오염 (에이전트·IDE·패키지 매니저의 scratch 가 tree repo 에 쌓이는 패턴):

- 다음이 git 에 추적되면 surface 한다.
  - `.codex-cache/`: codex CLI 의 cache 다.
  - `.aider/` 와 `.cursor/` 와 `.windsurfai/`: 다른 에이전트·IDE 의 로컬 상태다.
  - 어느 깊이에서든 `node_modules/`: 가장 강한 오염 신호이고 의도적으로 유지하는 사례가 거의 없다.
  - 프로젝트 루트의 `gpt-*.md` 와 `claude-*.md` 같은 임시 scratch markdown.
- `.codex-work/` 는 의도적으로 목록에서 제외된다. 사용자가 codex 하위 프로젝트의 workspace 로 의도적으로 쓸 수 있어 일괄 표시하면 false positive 가 된다. 그 안에 `node_modules/` 가 들어 있으면 그 경로만 표시된다.
- 발견 시 권장 조치: 해당 경로를 `.gitignore` 에 추가하고 추적 항목을 `git rm --cached` 한 뒤 commit 한다. blocker 가 아니라 경고다.
- `grow-backfill.md` Contamination guards 절의 Codex scratch 격리와 연계된다.

### 8. 스킬 승격 후보

`tree/rings.md` 의 최근 50개 정도 항목을 읽는다. `op | title` 형태로 항목을 묶고 반복되는 수동 절차를 찾는다. 같은 연쇄의 작업이 `.claude/skills/naite/` 아래 전용 스킬 파일 없이 세 번 이상 실행된 경우다.

경험 규칙:

- 같은 종류의 소스(예: YouTube 전사본)를 항상 다루면서 사용자가 계속 반복하는 공통 사전 단계가 있는 `grow` 실행의 반복.
- 특정 주제에 대한 `ask` 와 파일 기록 패턴의 반복 (도메인 특화 ask 스킬을 시사한다).
- 최근 캡처에서 사용자가 "나 계속 X 하고 있어"라고 보고한 경우.

보고: 후보 절차와 반복 횟수와 제안하는 스킬 파일 이름. 스킬을 직접 쓰지 않는다. 사용자가 승인하도록 제안만 한다. 스키마에 닿는 것은 `CLAUDE.md` 의 스키마 규율 절을 따르고, 하네스 기여는 `CONTRIBUTING.md` 를 거친다.

### 9. 실패 패턴

`tree/rings.md` 의 최근 50개 정도 항목에서 `- aborted:` 줄을 grep 한다. 근본 원인 키워드(예: "secrets", "extraction", "schema conflict")로 묶는다. 어느 군집이든 세 건 이상이면 구조적 실패 패턴으로 surface 한다.

보고: 군집과 건수와 항목. 예방 변경(사전 단계, 스킬 갱신, CLAUDE.md 규칙)을 제안한다. 자동 수정은 하지 않는다.

### 10. 사용자 모델 갱신 (선택)

나무에 페이지가 10장 이상 있고 `rings.md` 에 grow 항목이 5개 이상일 때만 실행한다. 가장 최근의 `care-check | user model refresh: yes` 항목이 3주 이내면 건너뛴다 (대략의 주기다).

건너뛰지 않을 때:

- 최근 20개 정도의 rings 항목과 최근 페이지의 frontmatter 를 훑는다.
- 사용자를 위해 다음을 요약한다.
  - 어느 도메인을 가장 많이 나무로 끌어오고 있는지.
  - grow 됐지만 한 번도 교차 참조되지 않은 개념 (얕은 관심일 수 있다).
  - 캡처 파일에서 보이는 반복적인 판단 기준 (예: "사용자가 일관되게 X 추론을 Y 보다 선호한다").
  - 공백: 자주 묻지만 한 번도 기록되지 않은 주제.
- 요약을 vault 의 운영 기억 표면인 `MEMORY.md`(`docs/CONVENTIONS.md` Instruction surfaces 절이 정의하는 표면, 양식은 `.naite/templates/MEMORY.md`)에 날짜 블록으로 덧붙일지 제안한다.
  - 기존 내용을 덮어쓰지 않는다. `## [YYYY-MM-DD] refresh` header 로 덧붙이기만 한다.
  - 사용자에게 `MEMORY.md` 가 없으면 template 에서 먼저 만들지 제안한다.
  - 이 검사 중에는 `tree/` 와 `roots/` 를 절대 건드리지 않는다.

사용자가 기억 덧붙이기를 거절해도 요약은 care --check 보고에 남긴다.

### 11. grow 이후 잔재와 낡은 archive 디렉터리

이 나무에는 범용 `_archive/` 층이 없다 (`docs/CONVENTIONS.md` grow 이후 처리 절). 유일하게 정당한 archive 경로는 `branch-finish` 가 채우는 `roots/courses/_archive/{slug}/` 다. 그 밖의 모든 것은 드리프트다.

다음을 확인한다.

- 11a. 낡은 archive 디렉터리: `roots/articles/` 나 `roots/conversations/` 아래의 어떤 `_archive/` 든 옛 관례의 잔재이거나 cowork 실수다. 스키마 드리프트로 표시한다.
- 11b. 정리되지 않은 대화 claim 요약: `roots/conversations/`(최상위, `_transcripts/` 제외)의 모든 `YYYY-MM-DD-<slug>.md` 에 대해, 그 slug 나 파생 tree 페이지를 다룬 `grow` 항목이 `rings.md` 에 있는지 교차 확인한다. grow 됐는데 삭제되지 않았으면 "grow 이후 잔재"로 표시한다. grow 8단계의 정리가 끝까지 돌지 않은 것이다.
- 11c. branch archive 의 정합: 각 `roots/courses/_archive/{slug}/` 에 대응하는 `branch-finish` 항목이 `rings.md` 에 있는지 검증한다. archive 디렉터리는 있는데 `branch-finish` 항목이 없거나 그 반대면 표시한다.
- 11d. 낡은 source 경로: branch 의 chapter·subchapter 페이지의 `## Source` 절이 `roots/courses/{slug}/...` 를 가리키는데 실제 파일이 `roots/courses/_archive/{slug}/...` 에 있으면 낡은 것이다. branch-finish 후 source 경로의 일괄 갱신이 누락된 신호다.

보고: 표시된 경로와 이유를 나열한다. 낡은 디렉터리의 제거나 정리의 완료나 op 의 재실행을 권한다. 자동으로 해소하지 않는다. 사용자가 고른다. "범용 archive 없음" 결정 이전의 잔재에는 1회성 migration 정리가 정당할 수 있고, 그것은 `migration` 후보로 기록한다.

### 12. 학습 노트와 decision 과 insight 의 품질

요청된 검토 scope 의 모든 페이지에 `docs/CONVENTIONS.md` 의 학습 노트 품질 축을 적용한다. 나무 전체 검토에서 표본이나 얇은 본문의 근사로 페이지별 판단을 대체하지 않는다. 페이지의 평가와 실패한 축을 기록해서, 이후의 Writer 가 결함이 구조인지 교육인지 실질인지 문체인지 알 수 있게 한다.

- Markdown form: H1 은 하나이고, H2·H3·H4 가 단계를 건너뛰지 않고 자연스럽게 중첩되고, heading 이 범용 rubric 이 아니라 내용의 이름을 갖고, 비었거나 한 줄짜리 장식 절이 없고, 부모 heading 이 의미 있는 자식 heading 을 직접 묶을 수 있고, `## Source` 는 끝에 있다. 표는 같은 축을 비교하고, bullet 은 조각난 논증이 아니라 병렬 항목을 담고, 코드펜스는 코드나 literal 구조를 보존하며 언어가 있으면 태그를 달고, blockquote 는 실제 인용을 보존하고, GFM alert 는 참고와 경고를 담고, 수식과 강조는 의미의 일을 한다.
- Study effectiveness: 독자가 소스를 다시 열지 않고 정의와 문제와 메커니즘과 형식 용어와 worked 해석·적용과 한계와 흔한 혼동과 개념 연결을 복원할 수 있다. 모든 항목이 자기 heading 을 요구하지는 않지만, 추론의 부재는 결함이다.
- Content composition: 정의와 직관과 형식화와 예시와 경계가 각각 구분되는 단위를 더하고, 전제는 링크로 잇되 페이지 자신의 메커니즘은 그 자리에서 설명되고, source claim 과 관찰과 해석과 가설이 구분 가능하게 남는다.
- Writing manner: 한국어 강의 필기의 산문이 무엇만이 아니라 왜와 그래서를 설명하고, 전환이 인과와 조건과 비교와 확장 관계를 드러내고, 사전식 stub 과 마케팅 화법과 중요성 주장의 반복과 번역투와 rubric 모양의 bullet 덤프를 피한다.

`docs/CONVENTIONS.md` 의 쓸모 있는 정리의 조직 방식 절도 적용한다.

- 정리 질문: 시작이 이 페이지가 어떤 질문에 답하고 독자가 왜 다시 찾을지를 분명히 한다.
- 추론 순서: 절이 반복되는 범용 template 이 아니라 소스와 kind 가 뒷받침하는 이해 경로를 따른다.
- 절의 책임: 각 절이 같은 주장을 반복하지 않고 구분되는 정의·메커니즘·형식화·예시·비교·경계·귀결을 기여한다.
- 의미에 맞는 Markdown: 산문과 표와 목록과 수식과 코드블록과 인용과 콜아웃이 실제 정보 관계대로 쓰인다.
- 복원 가능한 압축: 반복과 공정 서술은 제거하되 증거와 조건과 불확실성과 실패 신호와 사용자가 직접 쓴 긴장은 지워지지 않는다.
- 쓸모 있는 끝: 마지막 움직임이 장식성 요약이 아니라 적용 경계와 귀결과 개념 연결과 재검토 조건을 드러낸다.

concept 페이지는 학습 순서를 같은 나무에서 가장 강한 course 노트 페이지와 비교한다. 최소 허용 잎과 비교하지 않는다. 목표는 재구성 가능한 이해이지 균일한 길이나 복사된 heading template 이 아니다.

추가로 frontmatter 의 `kind` 를 decision·insight 페이지의 1차 선택자로 쓴다. 다른 kind 안에 파묻힌 결정 꼴·통찰 꼴 산문도 고가치 프로젝트나 hub 에 영향을 줄 때는 검토할 수 있지만, 독립 페이지를 큐에서 밀어내면 안 된다. `docs/CONVENTIONS.md` 의 kind 별 품질 계약을 적용하고, 절 수나 단어 수나 요구된 영어 관용구에서 품질을 추론하지 않는다.

각 `kind=decision` 페이지에서는 decision kernel 을 검증한다.

- 선택과 현재 상태가 명시적이다: 선택·기각·보류·번복·잠정.
- 맥락과 구속 조건이 무엇이 결정을 필요하게 했고 무엇이 선택지를 실제로 갈랐는지 설명한다.
- 신빙성 있는 대안이 기록되어 있거나, 의미 있는 대안을 검토하지 않은 이유를 페이지가 명시한다. 지어낸 대안을 요구하지 않는다.
- 기대 메커니즘이 그 선택이 왜 의도한 효과를 낼지 설명한다.
- 검증 상태가 관찰된 결과와 해석과 미검증 기대를 구분한다.
- 실패·롤백·재검토 조건이 결정을 다시 열게 할 관찰 가능한 신호나 맥락 변화를 준다.
- 링크가 무게를 싣는다: 실제 프로젝트와 제약과 메커니즘과 선택지와 영향받는 개념을 연결한다. outbound 링크 수의 임계는 없다.

각 `kind=insight` 페이지에서는 다음을 검증한다.

- 주장: 구호가 아니라 검토할 수 있는 명료한 진술 하나.
- 증거 앵커: 주장을 낳은 관찰이나 소스나 반복 사례나 결정.
- 메커니즘이나 해석: 그 패턴이 성립할 수 있는 이유.
- 범위와 불확실성: 경계와 반례와 대안 설명과 명시적 가설 상태.
- 귀결: 이 통찰이 미래 행동이나 해석이나 관련 프로젝트를 어떻게 바꾸는지.
- 링크가 무게를 싣는다: 증거와 메커니즘과 적용과 수정되는 개념을 연결한다.

페이지별로 누락된 정보 단위의 목록을 보고하고 각각을 `repair-candidate` 나 `source-risk` 나 `intentional-debt` 로 분류한다. 자동으로 고치지 않는다. decision 의 공백은 `/naite fruit <slug>` 로, 더 넓은 산문 수리는 `/naite care <slug>` 로 라우팅한다.

`--daily` 에서는 누락된 검증이나 범위가 활성 결정을 바꿀 수 있는 페이지를 우선한다. 성기지만 정직한 잠정 기록은, 추론을 관찰된 사실처럼 제시하는 매끈한 페이지보다 우선순위가 낮다.

### 13. 고연결 페이지 (창발적 우선순위)

`tree/` 의 모든 concept 페이지에 대해 inbound `[[wikilink]]` 카운트를 계산한다. inbound 카운트의 1차 소스는 `.naite/ontology/tree-dependencies.json` 이다.

- 최다 참조 상위 10: 사용자의 결정에 결정적인 페이지이자 추론의 암묵적 기준점이다. 조치는 필요 없다. 자기 지식의 표면이다. `trunk.md` 해당 도메인 주요 목록의 hub 후보이기도 하다.
- 하위 분포: inbound 0 페이지(1절 Orphans 가 이미 다룬다)와 1~2 페이지(약하게 연결됨). synapse 층에 아직 짜여 들지 않은 개념을 발견하는 데 유용하다.

보고 형식은 단순한 순위 목록이다. inbound 카운트가 유일한 신호이고 논평을 더하지 않는다.

이 검사에는 자동 행동이 없다. 링크 그래프의 창발 구조를 보이게 하는 것이 목적이다. 12절과 짝지어 어느 개념이 결정과 통찰을 지지하는지 본 뒤, 원시 카운트가 아니라 산문의 관계를 판단한다.

### 14. 자율 추가물의 garbage collector

`docs/CONVENTIONS.md` Schema evolution 절의 자율 A·B 추가물에 대한 사후 품질 검증이다. 자율 추가는 일관된 속도를 만드는 대신 성급한 추가의 위험을 안고, care --check 가 30일 윈도로 쓰레기 후보를 surface 한다. 모든 항목은 경고이지 blocker 가 아니다.

추가 시점은 파일 생성이 아니라 그 topic·narrower 줄이 들어온 커밋으로 본다: `git log -1 --format=%cs -S'<정확한 topic 또는 narrower 문자열>' -- .naite/ontology/topics.md .naite/ontology/subject-tree.md` (해당 문자열이 도입된 마지막 커밋의 날짜). tree 페이지의 나이는 그 페이지의 `git log -1 --format=%cs -- tree/<slug>.md` 로 본다. `--diff-filter=A` 는 파일이 처음 추가된 커밋만 잡아 개별 append 시점을 놓치므로 쓰지 않는다.

#### 14a. 정본 topic 의 저사용 (자율 A 쓰레기)

`.naite/ontology/topics.md` 의 canonical_topics 의 각 topic 에 대해 다음을 확인한다.

- `git log` 로 추가 시점을 확인해서 30일 이상 지났고,
- `tree/*.md` 의 `topics:` 필드 사용 카운트가 3 미만이면,
- "low-usage canonical" 후보로 surface 한다. 사용자가 결정한다: 별칭으로 redirect, 다른 정본으로 통합, 또는 유지 (도메인이 작아서 정상). LLM 의 입자도 판단 실수의 신호일 수 있다.

#### 14b. 자율 추가된 narrower 의 사소한 분할 (자율 B 쓰레기)

`.naite/ontology/subject-tree.md` 의 각 `narrower:` 항목에 대해 다음을 확인한다.

- `git log` 로 추가 시점을 확인해서 30일 이상 지났고,
- 그 경로를 `subject:` 로 쓰는 페이지가 1장 이하면,
- "trivial narrower" 후보로 surface 한다. 사용자가 결정한다: 트리에서 제거, 부모로 흡수, 또는 유지 (의도된 좁은 분류).

#### 14c. 자율 생성된 일반 개념 페이지의 orphan (자율 A 쓰레기)

1절 Orphans 와 교차 참조한다. 자율 A 로 생성된 일반 개념 페이지(branch 스킬의 subchapter-note 5단계, `ingest.md` 5절)가 다음이면,

- `git log` 로 생성 시점을 확인해서 30일 이상 지났고,
- inbound `[[wikilink]]` 카운트가 0(`trunk.md`·`seeds.md`·`rings.md` 밖)이면,
- "orphan spawn" 후보로 surface 한다. 입자도 실수나 너무 좁은 추출의 신호다. 사용자가 결정한다: 페이지 삭제, 본문을 흡수해 다른 페이지로 병합, 또는 다른 페이지에서의 명시적 교차 링크 추가.

철학: 자율 A·B 의 선택 가치(빠른 스키마 진화)를 보존하면서 누적되는 무질서를 막는다. 자율 추가가 잘못되어도 care --check 가 30일 후에 잡고 사용자가 정리한다. grow 시점의 "확실하지 않으면 추가하지 마"보다 "추가하고 care --check 가 청소"가 노드 연결을 촘촘하게 유지하는 데 유리하다. `docs/ARCHITECTURE.md` 2.3절의 folksonomy 철학과 일치한다.

### 15. Forest health (선택, report-only)

vault 가 숲으로 분화 중이거나 분화 압력을 점검할 때 실행한다. report-only 이고 자동 분할과 병합과 재배정은 없다 (C급, 사용자 결정). 근거는 `docs/CONVENTIONS.md` Forest layer 절과 `docs/ARCHITECTURE.md` 9절이다.

실행 도구는 전부 `tree/` 에 대해 read-only 다.

- `python .naite/scripts/forest-communities.py`: S1 구조 신호다. 군집별 conductance 와 지배 도메인과 hub 를 본다. 새로 나타난 낮은 conductance 군집은 분화 후보이고, conductance 가 높은 줄기는 아직 미성숙하다.
- `python .naite/scripts/forest-assign.py --write`: 개념 계보 배정이다 (`forest-config.json` seed 와 label propagation). `forest-manifest.json` 을 갱신한다.
- `python .naite/scripts/forest-dashboard.py`: 나이테 대시보드(`.naite/forest/dashboard.md`)를 갱신한다.

의존성은 `.naite/scripts/requirements.txt`(`networkx>=3.0`, `numpy`, `scikit-learn`)에 정의되어 있다.

surface 할 압력:

- 분화 압력: 한 나무 안에 size 가 floor 이상이면서 conductance 가 임계 이하인 군집이 새로 자랐는가.
- 병합 압력: 두 나무가 두꺼운 `inter_tree_edges` 로 붙었는가.
- 재배정 압력: flip 페이지. 과목 라벨과 링크 계보가 어긋난 페이지다 (걸침 개념 메커니즘의 flip 부류).
- `forest-config.json` 이 없으면 도메인=나무 identity 로 동작하고 첫 grouping 후보만 제안한다.

판단 기준은 수치가 아니라 작업 맥락의 효용이다. modularity 와 conductance 는 증거이고 분화·병합·재배정의 결정은 사용자가 한다. 비어 있거나 작은 vault(Phase 1)에서는 도구가 분화 후보를 거의 또는 전혀 잡지 않는 것이 정상이다.

## 보고 형식

```markdown
# Care --check report — YYYY-MM-DD

## Daily delta
- last run: YYYY-MM-DDTHH:MM:SSZ | unknown | n/a
- commits since last run: N
- map diff: timestamp-only | graph-count changed | not compared
- hard blocker delta: unchanged | changed | not compared

## Context maps
- manifest pages: N
- dependency edges: N
- dependency missing targets: N
- dependency orphans: N

## Orphans (N)
- [[slug-a]] (domain: x) — no inbound links
- ...

## Stubs (N unresolved, M proposed)
- unresolved: [[missing-slug]] — from [[source-page]]
- proposed: [[attention-heads]] — mentioned 4x across [[transformer]], [[multi-head]]

## Domain drift
| domain | count | known? | notes |
|---|---|---|---|
| ai-fluency | 42 | ✓ | ok |
| ml | 15 | ✓ | ok |
| engineering-math | 37 | ✓ | ok |
| course-ma101 | 42 | ✗ | unknown — collection tag, migrate out |
| ...

## Slug collisions (N)
- attention.md ⇔ Attention.md (case violation)
- k-means.md ⇔ kmeans.md (distance 1)

## Trunk drift
- domain missing: ml has no `### ml` section under `## Knowledge domains`
- hub missing from trunk: [[generative-ai]] (inbound 6, top-10) but absent from `### ai-fluency` 주요
- chapter noise: [[course-ma101-ch01-00-index]] in trunk.md — should only be in course-ma101-00-index Chapters
- legacy: `## Domain:` prefix at line 12 — migrate to `## Knowledge domains` / `## Branches`

## Secrets (N) ⚠
- roots/conversations/2026-04-15-foo.md:23 — matched /sk-[A-Za-z0-9]+/
**BLOCKER** — halt commits until resolved.

## Binary creep
- roots/assets/big.png (2.3 MB) — consider resize or LFS
- roots/courses/ma101/ch01-lecture.pdf — git tracked PDF (gitignore violation)

## Post-grow residue (N)
- roots/conversations/2026-04-24-foo.md — rings shows grow 2026-04-24 but file still present. Cleanup (delete claim summary) never ran.

## Stale archive dirs (N)
- roots/conversations/_archive/ — not a legitimate archive location per docs/CONVENTIONS.md § Post-grow handling. Recommend removing (files inside may be cleanup residue).

## Branch archive coherence (N)
- roots/courses/_archive/aa101/ exists but no `branch-finish | course-aa101` entry in rings.md. Verify or log retroactively.
- stale source: course-ma101-ch02-* pages reference `roots/courses/ma101/ch02-*.pdf` but file is at `roots/courses/_archive/ma101/ch02-*.pdf`.

## Output quality guard (N)
- tree/course-ma101-ch02-03-foo.md:42 — `필기에는` before `## Source`; absorb the note insight into prose.
- tree/course-ma101-ch03-00-index.md:18 — generic English heading `Overview`; use a Korean heading unless course-native.

## Study-note quality (N issues)
- [[foo]] (`repair-candidate`, Markdown form): H2에서 H4로 건너뛰고 한 문장짜리 heading이 반복되어 논리 계층이 보이지 않는다.
- [[bar]] (`repair-candidate`, study effectiveness): 정의와 수식은 있으나 변수 해석, worked application, 성립 경계가 없어 다시 공부할 수 없다.

## Decision and insight quality (N issues)
- [[decision-2026-04-12-rag-reranker]] (`repair-candidate`): expected mechanism is present, but outcome is written as observed without evidence and no revisit signal is named.
- [[compounding-learning-context]] (`source-risk`): claim and implication are clear, but the evidence anchor and scope are not recoverable without the original conversation.

## High-degree neurons (top 10)
| rank | page | inbound count |
|---|---|---|
| 1 | [[ai-fluency-framework]] | 24 |
| 2 | [[ai-fluency-description]] | 12 |
| ... | | |

Weakly connected (inbound 1~2): N pages.

## Autonomy garbage (N)
- low-use canonical: `posterior-probability` added 2026-04-01, used by 1 page after 33 days. Recommend: keep | redirect-to-`bayes-theorem` | remove.
- trivial narrower: `ml/agents/orchestrator-pattern` added 2026-04-05, used by 1 subject. Recommend: absorb into `ml/agents` or keep.
- orphan spawn: [[posterior-probability]] created 2026-04-01 (autonomy A), 0 inbound after 33 days. Recommend: cross-link from [[bayes-theorem]] | merge into [[bayes-theorem]] body | delete.

## Skill candidates (N)
- recurring: `grow` on YouTube transcripts (5x) — propose `.claude/skills/naite/grow-transcript.md`

## Failure patterns (N)
- extraction (3x): PDF text extraction aborted on scanned docs → propose OCR pre-step in `grow.md`

## User model refresh
- (skipped / summary block)

## 우선 검토 후보 3개
- [repair-candidate] [[page-or-target]] - why this is worth reviewing first.
- [schema-pressure] <topic or workflow> - what repeated evidence suggests.
- [intentional-debt] <artifact> - why it is intentionally left alone.
```

## 이 명령이 절대 하지 않는 것

- 페이지와 `trunk.md` 와 `seeds.md` 를 수정하지 않는다.
- 무엇이든 자동으로 해소하지 않는다.
- 커밋하지 않는다.
- 비밀 검사를 건너뛰지 않는다. 매번 실행하고 어떤 검출이든 즉시 멈춘다.
- 사용자의 명시적 동의 없이 기억 파일에 쓰지 않는다.
