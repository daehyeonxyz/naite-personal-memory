# /naite fruit

결정 thread 를 나무의 **열매** 로 맺는 dialogue scaffold. tree 의 노드(concept/entity/source) 들이 뉴런이라면, 시냅스 layer 는 그 위를 가로지르며 의사결정 흐름을 형성하는 별도 차원의 결합이다. 별도 decision page와 다른 concept 페이지에 박힌 짧은 decision prose는 둘 다 정당하다. 품질은 섹션 수가 아니라 선택, 제약, 작동 가설, 검증 상태, 재검토 조건이 얼마나 정직하게 보존됐는지로 판단한다.

All data paths below resolve against **NAITE_ROOT** (the root of the naite repo). Sub-skill references resolve against **SKILL_DIR** (`<NAITE_ROOT>\.agents\skills\naite`). See `SKILL.md` for context.

## When to use — 3 triggers

1. **명시 슬래시**: `/naite fruit [topic?]`. 사용자가 "이 결정 정리해두자" 라고 의식적으로 부를 때.
2. **자연 감지**: 대화 중 "선택했다 / 고민했다 / 보류했다 / 실패했다 / 결정했다 / 비교했다" 신호 + trade-off 정황이 감지되면 Codex 가 한 줄로 제안 — "이거 열매로 정리해둘까요?" 사용자 확인 후에만 실행. grow.md § Branch pre-check 와 같은 cadence.
3. **작업 종료 트리거**: 사용자가 "끝났어 / 마무리 / 완료 / 다 됐어" 신호 + 그 작업이 의사결정·trade-off 를 포함한 흐름이면 wrap-up 제안. 단순 task 종료엔 발동 안 함.

세 trigger 모두 동일 워크플로로 진입. 차이는 모드 판별 단계에서 사용자 확인 한 줄 추가될 뿐.

## Hard rules

- **출력은 `kind: decision` 페이지** (적합 시 `kind: concept`/`entity`/`source-record` 페이지에 decision-shape content 인라인 embed 도 가능). `form: prose`. `subject` 는 `.naite/ontology/subject-tree.md` 의 path 1개; 진짜 cross-domain 일 때만 multi (`[a/x, b/y]`). `dmu/`, `failure-*/`, `career-*/`, `synapse/` 같은 메타 subject path 또는 별도 kind enum 추가는 **금지** — 시냅스의 본질은 카테고리화 거부 (`docs/CONVENTIONS.md § Decision thread shape` 참조). Decision-shape thread 자체는 page-level enum 으로 좁히지 않고 cross-page 시냅스 layer 로 흐른다.
- **파일명**: `decision-YYYY-MM-DD-<slug>.md` 형식. `YYYY-MM-DD` 는 페이지 `created` 날짜 (frontmatter 와 일치). `<slug>` 부분은 `lowercase-kebab-case`. `DMU-` prefix 금지. 예: `decision-2026-01-15-vector-db-selection`, `decision-2026-02-03-retrieval-strategy`.
- **본문은 decision kernel을 보존**한다 (`docs/CONVENTIONS.md § Decision thread shape`, `§ Page-kind quality contracts`). 선택과 현재 상태, 맥락과 binding constraint, 실제 대안, 예상 메커니즘, 검증 상태, 실패·재검토 조건이 핵심이다. 고정 헤더나 섹션 수를 강제하지 않고 빈 헤더를 쓰지 않는다.
- **관찰·해석·기대 결과를 분리**한다. 아직 검증하지 않은 기대는 outcome으로 쓰지 않고, 무엇을 보면 검증되는지 적는다. 대안이 없었다면 가상의 대안을 만들지 않는다.
- **링크 수를 품질 목표로 쓰지 않는다.** 프로젝트, 제약, 메커니즘, 영향을 받는 개념처럼 실제 reasoning을 지탱하는 wikilink만 산문으로 연결한다. 장식용 `Related` 목록으로 개수를 채우지 않는다.
- **누락 개념 발견 시** `tree/seeds.md` 에 stub 제안한다. 없는 페이지를 대신해 decorative link를 만들지 않는다.
- **Soft ontology idiom은 의미가 맞을 때 사용**한다. `decided ... over`, `failed when`, `trade-off:`, `validates`, `falsifies`를 문장에 억지로 넣지 않는다. 자연스러운 한국어 산문이 같은 관계를 더 정확히 표현하면 그 산문을 우선한다.
- 기타 `AGENTS.md § Secrets & privacy`, `docs/CONVENTIONS.md § Schema evolution` 전부 그대로 적용.

## Dialogue scaffold (template filler 가 아니라 사고 캐묻기)

skill 의 핵심 가치는 빈 헤더를 채우게 하는 게 아니라 **누락된 thinking 을 끌어내는 것**.

- 이미 확보된 decision kernel은 다시 묻지 않고 **빠진 증거만** 질문한다. 한 번에 1~2개씩 묻는다.
- **표면 답변은 binding constraint로 구체화**한다. "좋아 보여서 / 유명해서"라고 답하면 "다른 선택을 탈락시킨 실제 제약이 비용, 시간, 유지보수, 데이터 품질, 되돌리기 가능성 중 무엇이었나요?"처럼 좁혀 묻는다.
- **검증 상태를 먼저 분리**한다. 실제 관찰, 그 관찰에 대한 해석, 아직 확인하지 않은 기대를 한 문장에 섞지 않는다.
- **실패·재검토 조건은 관찰 가능한 신호로 묻는다.** "잘 안 됐다"가 아니라 어떤 입력, 사용자 행동, 비용, 품질 저하 또는 맥락 변화가 결정을 다시 열게 하는지 묻는다.
- **Invariant와 재사용 규칙은 선택 사항**이다. 한 사례에서 일반 규칙을 억지로 만들지 않고, 반복 관찰이나 충분한 메커니즘 근거가 있을 때만 끌어낸다.
- **Cross-link는 후보를 제시하되 padding하지 않는다.** 기존 tree에서 프로젝트, 제약, 메커니즘 페이지를 찾고, 관계를 설명할 수 있는 것만 연결한다.

## Workflow

### 0. Pre-flight (every invocation)

1. Read `<NAITE_ROOT>/AGENTS.md § Decision threads — synapse layer`, 그리고 `docs/CONVENTIONS.md § Soft ontology` / `§ Personal tree scope` / `§ Ontology`. 그리고 `.naite/ontology/subject-tree.md` (canonical paths) + `.naite/ontology/topics.md` (canonical vocabulary).
2. Read `<NAITE_ROOT>/tree/trunk.md` 전체 — 도메인·기존 hub 페이지 candidate 수집.
3. Last ~20 lines of `<NAITE_ROOT>/tree/rings.md` — 최근 맥락.
4. Trigger 모드 판별. 자연 감지·작업 종료 모드면 사용자에게 한 줄 확인 후 진행.

### 1. Decision-kernel pass

대화와 기존 페이지에서 이미 확인된 내용을 먼저 채운 뒤, 빠진 항목만 질문한다.

1. **Choice and state** — 무엇을 선택·기각·보류·되돌렸으며, 지금도 유효한가?
2. **Context and binding constraint** — 어떤 문제와 제약이 결정을 필요하게 했고, 실제로 어느 제약이 선택을 갈랐는가?
3. **Alternatives** — 현실적으로 고려한 대안과 기각 이유는 무엇인가? 실제 대안이 없었다면 그 사실과 이유를 적는다.
4. **Expected mechanism** — 이 선택이 입력, 처리, 병목, 결과를 어떻게 바꿀 것으로 보았는가?
5. **Validation state** — 무엇을 실제로 관찰했고, 무엇은 해석이며, 무엇은 아직 검증하지 않은 기대인가? 미검증이면 필요한 관찰이나 실험을 적는다.
6. **Failure and revisit condition** — 어떤 신호, 맥락 변화, 비용 또는 결과가 이 결정을 무효화하거나 다시 열게 하는가?

Outcome, iteration, rollback cost, reuse condition, invariant, related pages, next action은 실제 근거가 있을 때만 더한다. 빈 섹션은 쓰지 않는다.

### 2. Cross-link 검수

본문의 wikilink마다 주변 산문이 실제 관계를 설명하는지 확인한다.

- 프로젝트, binding constraint, 작동 메커니즘, 대안, 영향을 받는 개념 중 tree에 존재하는 페이지를 후보로 제시한다.
- 관계를 설명할 수 없는 링크는 추가하지 않는다. 이미 있는 decorative link는 수선 범위에서 제거하거나 관계를 설명한다.
- 필요한 개념이 tree에 없으면 § 3의 stub 제안으로 넘긴다.

### 3. 누락 개념 → stub 제안

대화 중 "이 개념은 tree 에 아직 없네" 가 발견되면:
- `tree/seeds.md` 에 한 줄 추가 제안: `- [[missing-slug]] — first seen in [[this-decision-slug]], context: ...`
- 사용자 승인 후 추가. 강요는 안 함.

### 4. 페이지 작성

`<NAITE_ROOT>/tree/<slug>.md` 작성. 템플릿 § Templates 참조.

Frontmatter:
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

본문을 `docs/CONVENTIONS.md § Study-note quality dimensions`와 `§ Page-kind quality contracts`의 decision 계약으로 self-check한다. H 계층은 실제 결정 흐름을 드러내고, 짧은 decision에 빈 형식용 heading을 만들지 않으며, `## Source` 앞 본문에는 em dash (`—`)를 쓰지 않는다. 특히 다음을 확인한다.

- 선택의 현재 상태와 binding constraint가 드러나는가?
- 실제 대안과 예상 메커니즘이 있는가, 또는 없는 이유를 정직하게 적었는가?
- 관찰한 결과, 해석, 미검증 기대를 구분했는가?
- 실패·rollback·재검토 조건 중 해당하는 신호가 있는가?
- wikilink가 개수 채우기가 아니라 reasoning을 지탱하는가?

### 5. `tree/trunk.md` 업데이트 (hub 자격 있을 때만)

이 열매 페이지가 **hub 후보** 면 (즉 다른 페이지에서 자주 link 받을 가능성이 높으면) `## Knowledge domains § <domain>` 의 "주요" 라인에 한 줄 추가. 한도 (4-7개) 도달 시 사용자에게 어느 줄을 빼고 추가할지 물음.

대부분의 열매 페이지는 작은 결정 한 건이라 **hub 후보가 아님** — 이때는 trunk 미등재, 본문 wikilink 와 prose idiom 으로만 발견되게 둠. care --check 의 high-degree neurons 가 자동으로 promotion candidate 를 surface.

`docs/CONVENTIONS.md § trunk.md discipline` 참조.

### 6. `tree/rings.md` append

```
## [YYYY-MM-DD] fruit | <slug>
- pages created: [[<slug>]]
- pages updated (back-prose 박은 경우): [[...]]
- domain: <subject-tree 의 top-level, 예: ml | statistics | personal>
- stubs added: N
```

### 7. Bidirectional prose 제안

이 결정이 닿는 기존 concept 페이지가 있으면, 그 페이지에도 한 줄 박을지 사용자 확인:
> "`[[other-page]]` 에 'used in [[this-decision-slug]]' / '`[[this-decision-slug]]` 의 trade-off 분석 참조' 같은 prose 한 줄 추가할까요?"

승인 시 그 페이지 Edit. 시냅스가 양방향으로 자라남.

### 8. Post-write duties (tree mutation 공통)

열매 페이지 작성도 tree mutation 이므로 grow/ingest 와 같은 사후 의무를 진다 (`docs/CONVENTIONS.md § Output quality contract`, `docs/CONTEXT.md § Verification`): 새 페이지 본문에 content guard 를 돌리고 (raw/source-process voice 없음, self-contained), 생성 맵을 재빌드한다 — `python .naite/scripts/build-tree-manifest.py` (새 페이지·좌표), 그리고 이 열매가 다른 페이지와 링크로 이어졌으면 `python .naite/scripts/build-tree-dependencies.py` (§ 7 의 bidirectional prose 를 반영하려면 특히 필요). 이 재빌드를 빼면 맵이 stale 해져 다음 orphan/inbound 계산이 어긋난다.

### 9. Checkpoint

사용자에게 한 단락 요약:
- 작성된 페이지 경로
- 추가된 stub 목록
- bi-directional prose 박은 페이지 목록
- decision kernel에서 확인된 것 / 아직 미검증인 것
- 다음 행동 (있으면)

## Templates

### Standalone decision page (adaptive composition example)

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

{결정이 필요했던 문제와 실제 binding constraint를 설명한다. 현실적으로 검토한 대안은 같은 비교 축으로 서술한다. 대안이 없었다면 만들지 말고, 비교하지 못한 이유를 남긴다.}

## 이 선택이 작동할 것으로 본 이유

{입력, 처리, 병목, 결과가 어떻게 달라질 것으로 보았는지 설명한다. 관련 메커니즘이나 프로젝트는 관계가 드러나는 문장으로 연결한다.}

## 현재 확인한 것과 아직 모르는 것

{실제로 관찰한 결과와 그 해석을 분리한다. 기대에 머무는 결과는 아직 확인하지 않았다고 밝히고, 어떤 관찰이나 실험이 필요한지 적는다.}

## 다시 결정을 열 조건

{어떤 신호, 비용, 품질 저하, 사용자 행동 또는 맥락 변화가 결정을 무효화하거나 재검토하게 하는지 적는다. 되돌리기 비용이 중요하면 함께 적는다.}

{결정 변경 이력, 다음 증거, 다른 페이지와의 연결은 실제 내용이 있을 때만 자연스러운 heading 또는 마무리 문단으로 더한다. 단순 링크 목록은 쓰지 않는다.}
```

이 예시는 decision kernel의 배열 한 가지일 뿐이다. 실제 페이지의 H2 이름과 개수는 결정의 논리 흐름에 맞춰 바꾸며, 짧은 결정은 두세 절이나 몇 문단만으로도 충분할 수 있다. 위 heading을 고정 양식처럼 복사하지 않는다.

### Synapse 짧은 형태 (다른 concept 페이지에 박는 prose)

별도 페이지가 필요할 만큼 무겁지 않으면, 기존 concept 페이지의 본문에 decision kernel을 짧은 단락으로 남긴다.

```markdown
## 프로젝트에서의 판단

2026-04 [[project-portfolio-site]]에서 retrieval precision을 높이기 위해 [[2-stage-reranking]]을 검토했지만, [[interactive-latency-budget]]을 넘을 가능성 때문에 보류했다. 현재 관찰한 것은 latency 예산뿐이며 precision 개선 효과는 아직 검증하지 않았다. 캐시를 적용한 실험에서 예산 안에 들어오면 결정을 다시 연다.
```

이런 prose 가 여러 페이지에 박혀 있으면 grep 으로 의사결정 thread 가 즉시 surface.

## What this command never does

- 새 type / 새 frontmatter 필드 / 새 메타 도메인 태그 신설 안 함.
- Decision-shape 페이지를 별도 메타 인덱스로 분리하지 않음.
- Career 관련 frontmatter / `[[fde-skill-*]]` 페이지 사전 생성 안 함 (docs/CONVENTIONS.md § Decision thread shape 의 grep-on-demand 원칙 준수).
- 파일명 `DMU-YYYYMMDD-...` prefix 안 씀.
- 고정 섹션을 강제로 채우지 않음. 미검증과 누락을 추측으로 메우지 않음.
- outbound wikilink 개수를 맞추려고 decorative link를 추가하지 않음.
- frontmatter `domains` 는 선택한 `subject` path 의 top-level 에서 기계적으로 도출해 함께 쓴다. 임의 값을 선택하지 않는다. `care --check` 는 stale cache 를 보고만 한다. hub 후보면 별도로 `trunk.md` 의 `## Knowledge domains § <domain>` 주요 라인에 한 줄 더한다.
- 모든 열매 페이지를 자동으로 trunk.md 에 등재 안 함 — hub 후보일 때만.
- `git commit` 안 함.
