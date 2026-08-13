# docs/ARCHITECTURE.md — naite 스키마 설계 근거

## 개요

- 상태: 5-facet 스키마(`kind`·`form`·`topics`·`subject`·`source-types` 와 cache 인 `domains`)는 안정 상태이고, 운영 중 정량 검증을 거친 설계다.
- 대체 이력: 이 스키마는 이전의 `type`·`role`·`source-type` 스키마를 facet 재설계로 교체한 결과다. 그 이전에는 hardcoded 단일 enum `domains` 를 썼다.
- 기원: LLM 과의 ontology 설계 대화와 사용자의 명시적 결정과 후속 care 검토 결과와 zero-base facet 재설계 세션이 이 설계를 만들었다.

- 역할 분담: 이 문서는 naite 스키마와 운영 모델의 장문 근거를 담당한다.
  - 운영 불변식은 [`docs/CONVENTIONS.md`](../docs/CONVENTIONS.md) 가, 정본 데이터는 [`.naite/ontology/`](../.naite/ontology/) 가, 워크플로 절차는 `.claude/skills/naite/*` 가 담당한다.
  - 이 문서는 왜 그렇게 설계했는지와 어떤 대안을 기각했는지와 언제 깨지는지를 담는다.

## 0. 요약

- 이 설계는 다축 분류(faceted)와 SKOS-lite 계층과 curated folksonomy 와 cached materialized view 네 가지를 결합한다. 정보과학 표준 세 가지(Ranganathan 1933, W3C SKOS 2009, 현대 PKM folksonomy)와 DB 패턴 하나 위에 LLM 주도 큐레이션을 얹은 구조다.
- 페이지 frontmatter 는 5 facet(`kind`, `form`, `topics`, `subject`, `source-types`)과 cache 하나(`domains`)로 구성된다. 각 facet 은 직교한다 (Ranganathan). 이전 `type`·`role`·`source-type` 스키마를 교체한 결과다.
- 스키마 진화는 영향 범위로 등급이 갈리는 자율성 A·B·C 를 따른다. A 는 LLM 자율(개념 페이지, 정본 topic, 명백한 별칭)이고, B 는 후보 제안(subject 트리 변경)이고, C 는 사용자 결정(trunk 스키마)이다.

## 1. 동기 — 왜 평평한 enum 을 버렸나

이 tree 는 평평한 단일 도메인 enum(`domains: [ml]`)으로 시작했다. 페이지가 빠르게 누적되면 두 종류의 통증이 다가온다.

| 문제 | 증상 | 해결 |
|---|---|---|
| 스키마 분리 비용 | `ml` 을 `ml-llm` 과 `ml-agents` 로 가를 때마다 페이지 N 장의 frontmatter 를 LLM 이 재분류해야 한다. 분리할 때마다 반복된다 | SKOS-lite 와 cached domain (1차 재설계) |
| 단일 도메인 강제 | cross-domain 페이지를 multi-value 로 억지 표현하게 된다. 실제로는 다축 분류 문제다 | 다축 분류. 5 facet 이 직교한다 |
| 페이지 역할의 부재 | decision·project·insight·question 같은 페이지 성격이 산문 관례로만 존재해서 grep 으로만 추적된다 | `role` facet 을 거쳐 `kind` facet 으로 본질 표현을 강화했다 |
| 출처 유형의 부재 | course·paper·docs·conversation 출처 정보가 본문 산문이나 파일명 prefix 로만 존재한다 | 단수 `source-type` 을 리스트 `source-types` 로 바꿔 다중 출처를 반영했다 |
| 자기 지식과 학습 지식의 혼재 | "내가 결정한 것"과 "내가 학습한 것"이 그래프에서 구분되지 않는다 | `kind=source-record` 를 도입해서 literature note 와 permanent note 를 명시적으로 분리했다 (Zettelkasten 정통) |

마지막 항목이 가장 결정적이다. 이 tree 의 본질은 사용자가 무엇을 알고 있는지이고, 그 앎은 compiled self-knowledge 와 study knowledge 두 갈래의 결합이다. 초기에는 `role` facet 이 그 구분을 명시했고, 재설계에서 `kind` facet 이 더 정확히 표현하게 됐다. `kind=source-record`(study knowledge)와 `kind=decision`·`insight`·`project`(compiled self-knowledge)가 그 결과다.

## 2. 이론 토대 — 여섯 기반

각 토대의 전체 설명은 tree 의 concept 페이지로 grow 한다. 이 절은 왜 그 토대를 채택했는지만 한 단락씩 적는다.

### 2.1 Faceted classification (Ranganathan 1933)

한 자료를 여러 직교 차원으로 분류하는 방법이다. PMEST(Personality, Matter, Energy, Space, Time)는 도서관 도메인의 사례이고, 핵심은 facet 의 직교성이다. 한 facet 의 변경이 다른 facet 에 영향을 주지 않는다는 성질이 스키마 변경의 영향을 격리해 준다. 이 tree 의 5 facet 이 이 원리를 직접 적용한다. 전체 설명은 tree 의 `faceted-classification` 개념 페이지가 담당한다.

### 2.2 SKOS-lite (W3C 2009)

W3C 의 Simple Knowledge Organization System 표준에서 부분집합을 채택했다. `narrower` 는 경로 표기(`ml/agents`)로 암묵적으로 두고 `altLabel` 은 명시한다. altLabel 이 rename 비용을 0 으로 만드는 핵심 메커니즘이다. 표준 자체의 상세는 tree 의 `skos` 개념 페이지에 둔다.

### 2.3 Folksonomy 와 curated taxonomy 의 결합

순수 taxonomy(하향식 경직)는 진화 비용이 크고, 순수 folksonomy(상향식 자유)는 무질서로 흐른다. 그래서 두 층을 결합한다. `topics` 는 folksonomy 방식으로 떠오르고 `subject` 는 큐레이션된다. 미등록 topic 은 입자도 가드를 통과하면 LLM 이 자율 추가하고(자율 A), 가드에 실패하면 surface 만 한다. 입자도 가드는 `.naite/ontology/topics.md` 의 Topic granularity guidance 절에 정의되어 있다. 두 층 결합의 배경은 tree 의 `folksonomy` 개념 페이지가 더 다룬다.

### 2.4 Cached materialized view

DB 의 materialized view 패턴이다. 매 질의 재계산(computed)과 박제(cached)는 각각 trade-off 를 갖는다. 이 tree 의 `domains` 필드는 생산자가 도출하는 cache 에 승인된 수리를 더한 형태다. 새 페이지 워크플로가 `subject` 와 함께 값을 계산하고, care-check 는 드리프트를 보고만 하고, 사용자 승인 후 Repair 가 기존 cache 를 갱신한다. Obsidian graph view 호환성이 결정 변수였다. 패턴의 전체 맥락은 tree 의 `materialized-view` 개념 페이지가 담당한다.

### 2.5 LLM-as-curator

전통 온톨로지에서는 사람이 schema steward 를 맡는다. 1인 운영 tree 에서는 LLM 이 그 기계적 부분(facet 선택, 별칭 군집 감지, 모호 사례 결정, narrower 후보 발견)을 수행한다. 비용 가정은 Codex Pro 와 Claude Pro 의 토큰이 풍부하다는 것이다. 이 역할 모델의 자세한 논의는 tree 의 `llm-as-curator` 개념 페이지에 모은다.

### 2.6 Graph-derived structure (Louvain, Blondel 2008)

페이지 간 wikilink 그래프는 의미 그래프의 근사다. modularity 최적화(Louvain)가 narrower 후보를 추출한다. 하향식 강제가 아니라 데이터 주도 진화다. care-check 의 고연결 페이지 검사는 단순 centrality 를 쓴다. 이 방법론의 자세한 설명은 tree 의 `louvain-modularity` 개념 페이지에 따로 적는다.

## 3. Architecture

### 3.1 Frontmatter 스키마

```yaml
---
kind: concept | entity | source-record |          # 페이지 본질 (불변)
      project | decision | insight | comparison |
      essay | personal
form: prose | index                               # 본문 제시 방식
topics: [<canonical-topic>, ...]                  # folksonomy. 0-5. 빈 배열 OK.
subject: [<skos-path>]                            # SKOS-lite path. 다축 가능 (cross-domain).
source-types: [course | conversation | paper |    # 출처 (8-enum, 항상 list)
               article | docs | book |
               essay | external]
domains: [<top-level>]                            # CACHED — page workflow 가 subject 에서 derive.
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

운영 규칙(필드별 enum, 입자도 관문, 별칭 처리)은 [`docs/CONVENTIONS.md`](../docs/CONVENTIONS.md) 의 Ontology 절이 단일 소스다. 이 절은 왜 이 5 facet 인지의 근거만 다룬다.

facet 재설계의 핵심 변화는 세 가지다.

1. `kind=source-record` 의 부활로 literature note(source-bound)와 permanent note(재사용 개념)가 분리됐다.
2. `role` 이 폐지되고 `form` 이 도입됐다. 페이지는 정보 산출물이라 role 개념이 맞지 않았다.
3. `source-types` 가 복수가 됐다 (다중 출처 반영).

### 3.2 필드의 책임 분리

| 필드 | 본질 | 진화 방식 |
|---|---|---|
| `kind` | 페이지의 referent, 즉 무엇을 가리키는가 (9-enum) | enum 확장이 가능하다 (care-check surface 후 사용자 결정, C-level) |
| `form` | 페이지의 모양, 즉 본문이 어떻게 제시되는가 (2-enum) | enum 이 거의 불변이다 (prose·index 외에 거의 없음) |
| `topics` | 재사용 가능한 키워드 | folksonomy 로 떠오르고 주기적으로 정본화된다 |
| `subject` | SKOS-lite 트리 위치 | narrower 추가가 자유롭고 페이지 변경이 없다 |
| `source-types` | 출처 종류 (리스트, 8-enum) | 안정적이고 새 값 추가는 C-level 이다 |
| `domains` | cache (facet 아님). subject 의 top-level | 새 페이지 워크플로가 도출하고, care-check 가 낡음을 보고하고, 승인된 Repair 만 갱신한다 |

핵심 불변식: `kind` 는 페이지가 가리키는 referent 의 본질이고, `form` 은 그 본문이 어떻게 제시되는가다. 두 차원은 독립적이라 같은 kind 가 다른 form 으로도 존재할 수 있다. 예를 들어 `kind=source-record, form=prose` 는 subchapter 노트이고 `kind=source-record, form=index` 는 chapter index hub 다. 미래 확장 시나리오로는 `kind=concept, form=index`(개념 hub)와 `kind=entity, form=index`(도구 카테고리 hub) 등이 가능하다.

### 3.3 스펙의 저장 위치

- `docs/ARCHITECTURE.md` (이 파일): Why. 철학과 이론 기반과 근거를 담는다.
- [`.naite/ontology/`](../.naite/ontology/): What (정본 데이터). `subject-tree.md` 와 `topics.md` 가 SKOS-lite 와 folksonomy 를 담는다.
- [`docs/CONVENTIONS.md`](../docs/CONVENTIONS.md): What (운영 불변식). Ontology 와 Schema evolution 과 Soft ontology 와 Decision shape 절을 두 도구(Claude Code, Codex CLI)가 공유한다.
- [`CLAUDE.md`](../CLAUDE.md) 와 자동 미러 `AGENTS.md`: bootloader. 라우팅과 트리거와 안전 규칙을 담는다.
- `.claude/skills/naite/*.md`: How. 워크플로 절차를 담는다.

`.naite/ontology/` 디렉터리는 스펙 데이터라서 양 표면이 동일하게 참조한다. 미러하지 않으므로 `sync-agents` 갱신이 필요 없다.

### 3.4 Topic 거버넌스 — 등급 자율성

- 정본 목록은 `.naite/ontology/topics.md` 가 유지한다.
- 신규 topic 도입(자율 A): 입자도 가드를 통과하면 LLM 이 canonical_topics 에 직접 덧붙이고 페이지에 사용한다. 가드에 실패하면 surface 만 한다.
- 별칭 정리: 명백한 형태 변형과 약어는 LLM 이 자율로 처리하고(자율 A), 동의어로 의심되지만 모호하면 care-check 의 군집 surface 로 넘겨 사용자가 결정한다.
- topic 없는 페이지는 허용된다 (예: `entity` 페이지). topics 의 빈 배열은 정상이다.

자세한 정책과 등급 매핑은 [`docs/CONVENTIONS.md`](../docs/CONVENTIONS.md) 의 Schema evolution 절이 담당한다.

## 4. 운영 모델의 근거

이 절은 왜 이렇게 운영하는지를 다룬다. 절차 자체는 `.claude/skills/naite/{grow,grow-branch,care-check,care,...}.md` 가 단일 소스다.

### 4.1 grow 시점의 facet 결정 — 왜 LLM 자율인가

새 페이지를 쓸 때 LLM 이 5 facet 을 결정한다 (입자도 가드와 정본 목록 참조). 사람 큐레이터와 비교하면 같은 규칙을 모든 페이지에 동일하게 적용하는 일관성이 강점이다. 이 가정의 비용 기반은 2.5절의 LLM-as-curator 다.

### 4.2 care 의 두 모드 — 분리된 책임

- `care --check`: `.naite/scripts/lint-ontology.py` 의 결정론 검사와 `.claude/skills/naite/care-check.md` 의 LLM 주도 검사가 스키마·정책 준수를 report-only 로 점검한다.
  - 검사 항목은 3a frontmatter 완결성, 3b subject tree, 3c topic 정본, 3d domain cache, 3e kind·form·source-types 분포, 3f BOM, 3g legacy 드리프트, 3h 언어 형태, 3i 스키마 무결성, 3j 출력 품질, 3k 잎 깊이, 7절 비 tree 오염, 14절 자율성 garbage collector(LLM 주도, 30일 윈도)다.
- `care`(돌봄 모드): 정성 리뷰와 수리를 담당한다. 서사형 산문 평가도 이 모드에 흡수되어 있다 (점수 없음, 임계 없음). 페이지·가지 리뷰와 직접 내용 수선과 대규모 정리와 반복 규칙 학습을 수행하고 사용자가 수동으로 호출한다.

분리한 이유: `care --check` 의 기계 검사와 `care` 의 맥락 판단은 서로 다른 성격의 작업이다. 상세는 `.claude/skills/naite/{care-check,care}.md` 가 담당한다.

### 4.2.1 워크플로 명령의 지형

사용자에게 보이는 `/naite` 명령과 내부 워크플로 파일은 일부러 분리되어 있다.

| 사용자 진입 | 로드하는 것 | 비고 |
|---|---|---|
| `/naite start` | `start.md` 와 `ingest.md` | 신규 사용자의 첫 세션이다. migration 내보내기를 통과시키면 ingest primitive 로 첫 나무를 만든다 |
| `/naite grow` | `grow.md` 와 필요 시 `capture.md`·`ingest.md`·`grow-branch.md` | 학습·자료 반영의 단일 진입점이다. capture 와 ingest 는 직접 명령이 아니다 |
| `/naite grow backfill <slug>` | `grow.md` 와 `grow-backfill.md` | 이미 학습을 마친 course·archive 를 dialogue 없이 보강하는 grow 하위 모드다 |
| `/naite ask` | `ask.md` | tree 기반 질의응답이다 |
| `/naite fruit` | `fruit.md` | 결정·trade-off thread 를 `kind=decision` 으로 남긴다 |
| `/naite care --check` | `care.md` 와 `care-check.md` | report-only 점검이다 |
| `/naite care` | `care.md` | 실제 수선과 정성 검토다 |
| `/naite upgrade` | `upgrade.md` | 사용자 자료를 보존하며 하네스를 갱신하고, 필요한 vault schema migration 은 preview 와 승인 뒤에 적용한다 |

`capture.md` 는 대화 내용을 `roots/conversations/` 에 staging 하는 단계이고, `ingest.md` 는 승인된 원천을 `tree/` 로 접는 단계다. 둘 다 `/naite capture` 나 `/naite ingest` 로 직접 노출하지 않는다. 명령 수를 줄이고, 원천 보존과 사용자 승인의 순서를 `grow` 안에서 강제하기 위해서다.

### 4.3 스키마 진화 — 등급 자율성

| 등급 | 영향 범위 | LLM 동작 |
|---|---|---|
| A (자율) | 페이지 한두 장의 추가·변경. 편집으로 되돌릴 수 있다 | LLM 이 직접 작성하고 요약에서 surface 한다. care-check 가 사후 검증한다 |
| B (제안) | 트리 구조(narrower·rename·move). 미래 페이지에 영향을 주고 altLabel 로 싸게 되돌린다 | 후보를 덧붙이고 요약에 표시한다. 사용자가 확인한다 |
| C (사용자 결정) | trunk 스키마(top-level domain, enum 값, facet 필드, 폐기) | LLM 의 추가가 절대 금지된다 |

이 정책의 동기는 위험 반전 분석이다. 보수적 정책이 folksonomy 폭발을 막는 동안 빈약함(개념 페이지 미생성, 연결 부족)이라는 다른 위험을 만들었다는 정량 발견이 있었다. 정책을 완화한 뒤 그래프 활성화 지표(chapter 의 outbound 링크 수, 링크 0 페이지 수)로 순이익을 검증했다.

자세한 등급 매핑과 입자도 가드는 [`docs/CONVENTIONS.md`](../docs/CONVENTIONS.md) 의 Schema evolution 절이 담당한다.

### 4.4 나무 발전 궤적 — 네 층의 분산 기록

- 전술 타임라인: `tree/rings.md` 가 작업 단위를 한 줄씩 기록한다.
- 행동 델타: git 커밋 이력이 원자 변경을 기록한다.
- 구조 근거: `docs/ARCHITECTURE.md`(이 파일)가 담는다.
- 지적 추론: `tree/` 의 fruit(decision) 페이지가 담는다.

### 4.5 다중 패스 오케스트레이션 — 대규모 작업의 기본값

100 페이지 이상에 영향을 주는 작업은 3 패스 순환(draft → review → refine, review 관문이 정책을 조정)을 기본값으로 한다. 대규모 concept 층 작업에서 적용과 검증을 거친 패턴이다.

## 5. Tooling

### 5.1 활성 스크립트

- `.naite/scripts/lint-ontology.py`: 3절의 결정론 하위 검사(3a~3k)와 7절의 비 tree 오염 탐지를 담당한다. 매 care --check 실행에서 호출된다.
- `.naite/scripts/sync-agents.ps1`: `.claude/skills/naite/*` 를 `.agents/skills/naite/*` 로 자동 미러한다 (`Claude Code` 를 `Codex` 로 치환). `CLAUDE.md` 에서 `AGENTS.md` 로의 변환도 함께 처리한다.
- `.naite/scripts/sync-agents.py`: sync-agents.ps1 의 크로스플랫폼 포팅이다 (PowerShell 없는 환경용). 치환 규칙이 동일하고 LF 로 출력한다 (CI 미러 게이트가 LF 를 전제한다).
- `.naite/scripts/build-harness-lock.py`: release 와 upgrade 가 의존하는 하네스 파일의 hash lock 을 생성한다. 하네스 파일을 고친 뒤 재생성하고 `--check` 로 드리프트를 검증한다.
- `.naite/scripts/build-tree-manifest.py`: `tree/*.md` 의 frontmatter 와 heading 과 별칭을 모아 에이전트 fast-path 지도를 만든다. ingest 와 care 가 페이지 후보를 찾기 전에 낡았으면 실행한다.
- `.naite/scripts/build-tree-dependencies.py`: wikilink 와 soft relation 관용구를 스캔해서 inbound·outbound 의존성 지도를 만든다. 기존 페이지의 의미가 바뀌거나 링크 구조가 바뀐 뒤에 실행한다.
- `.naite/scripts/gen-subagents.py`: `.naite/ontology/forest-manifest.json` 이 있을 때 나무별 subagent 정의를 `.naite/agents/` 아래에 생성한다. 보통 `forest-assign.py --write` 이후에 선택적으로 실행한다.
- `.naite/scripts/forest-*.py`: forest 층의 진단 도구다 (9절, 보고서와 manifest 생성만 하고 tree 내용은 수정하지 않는다). `forest-communities.py`(분화 신호)와 `forest-assign.py`(개념 계보 배정)와 `forest-dashboard.py`(나이테 대시보드)와 `forest-retrieval-experiment.py`(숲 대 vault 효용 측정)로 구성된다. 의존성은 `.naite/scripts/requirements.txt`(`networkx>=3.0`, `numpy`, `scikit-learn`)에 정의되어 있다.

### 5.2 lint-ontology.py 의 보조 플래그

이 절의 플래그는 `/naite care --check` 자체의 플래그가 아니라 `lint-ontology.py` 의 쓰기 플래그다 (`lint-ontology.py` 의 argparse 절). care-check 는 불일치를 보고만 하고, 사용자가 수선을 승인하면 `/naite care` Repair 모드가 필요한 플래그만 실행한다.

- `--strip-bom`: UTF-8 BOM 을 제자리에서 정규화한다.
- `--refresh-domains`: 낡은 `domains` cache 를 `tree/*.md` frontmatter 에 제자리에서 다시 쓴다 (idempotent). 보고 전용이 아니라 쓰기 플래그다 (`lint-ontology.py:857-866`).
- 14절 자율성 garbage collector: 30일 윈도로 저사용 정본과 사소한 narrower 와 orphan 생성물을 회수한다. 현재는 LLM 주도로 동작하고 결정론 스크립트는 미구현이다 (7절 future considerations).

## 6. 예시 — 현재 frontmatter 형태

### 6.1 일반 개념 페이지 (permanent note)

```yaml
---
kind: concept
form: prose
topics: [normal-distribution, central-limit-theorem]
subject: [statistics/distribution]
source-types: [course]
domains: [statistics]
created: 2026-04-29
updated: 2026-05-04
---
```

재사용 가능한 일반 개념이다. 같은 topic 의 source-bound 기록은 별도의 `kind=source-record` 페이지로 분리된다.

### 6.2 Course 서브챕터 페이지 (literature note)

```yaml
---
kind: source-record
form: prose
topics: [normal-approximation, central-limit-theorem]
subject: [statistics/distribution]
source-types: [course]
domains: [statistics]
created: 2026-04-29
updated: 2026-04-29
---
```

특정 강의 unit(`course-XXX-chYY-ZZ-*`)의 기록이고 source-bound 다. 본문이 산문이라 `form=prose` 이고, 챕터 index hub 면 `form=index` 가 된다. Zettelkasten 의 literature·permanent 구분이 스키마에 명시된 형태다.

### 6.3 Decision 페이지

```yaml
---
kind: decision
form: prose
topics: [llm-curator, agentic-workflow]
subject: [ml/agents]
source-types: [conversation]
domains: [ml]
created: 2026-05-04
updated: 2026-05-04
---
```

파일명은 `decision-YYYY-MM-DD-<slug>.md` 다 (날짜 prefix 규칙).

### 6.4 Cross-domain 페이지

```yaml
---
kind: concept
form: prose
topics: [oversight, agentic-workflow]
subject: [statistics/estimation, ml/agents]
source-types: [conversation]
domains: [statistics, ml]
created: 2026-04-29
updated: 2026-04-29
---
```

cross-domain 은 kind 와 무관하게 `subject` 의 multi-value 로 표현된다. domains cache 도 복수가 된다.

`source-types=[legacy]` 는 사용하지 않는다. Obsidian vault 에서 import 한 페이지도 콘텐츠 본질이 conversation 이었으면 `[conversation]`, article 이었으면 `[article]` 을 쓴다.

### 6.5 Source-record 페이지 — 단일 docs 정리

```yaml
---
kind: source-record
form: prose
topics: [claude-api, prompt-caching]
subject: [ml/agents]
source-types: [docs]
domains: [ml]
created: 2026-04-29
updated: 2026-04-29
---
```

docs 한 단위(예: Anthropic API prompt caching 문서)의 정리다. 산문 본문이라 `form=prose` 이고, 여러 docs 페이지를 묶는 index hub 라면 `form=index` 가 된다. 본문의 `as-of: <date>` 같은 시점 표시는 facet 으로 분리하지 않는다 (7절 future considerations).

### 6.6 Source-record 페이지 — chapter index (form=index 예시)

```yaml
---
kind: source-record
form: index
topics: []
subject: [statistics]
source-types: [course]
domains: [statistics]
created: 2026-05-03
updated: 2026-05-03
---
```

`course-XXX-chYY-00-index.md` 같은 챕터 내비게이션 hub 다. 본문이 subchapter 목록이라 `form=index` 다. `kind=source-record` 는 같지만 form 이 prose 와 구분해 준다.

## 7. Future considerations

미래의 care --check 나 care 가 surface 하면 검토할 항목이다. 현재는 도입하지 않는다.

- 14절 자율성 garbage collector 의 결정론 구현: 현재는 LLM 주도 스펙만 존재한다. 30일 윈도 검증 주기가 안정되면 `.naite/scripts/autonomy-gc.py` 추가를 검토한다.
- `as-of: <date>` facet: `source-types ∋ docs` 페이지의 낡음 추적용이다. 현재는 본문 provenance 로 충분하다.
- `classifications:` wrapper: facet 이 다섯을 넘으면(예: `audience`, `certainty`, `maturity` 추가) 검토한다. 현재 5 facet 은 안정 상태다.
- 새 `kind` 값: 페이지 형태의 통증이 다섯 장 이상 누적되고 사용자가 결정한 뒤에 추가한다. 이전의 `role=question`(코퍼스 0건)은 재설계에서 새 `kind` enum 으로 옮기지 않았다. 필요가 surface 되면 C-level 결정이다.
- 새 `form` 값: 현재는 `prose` 와 `index` 뿐이다. 미래에 별도 형식(예: `table`, `gallery`)이 등장하면 검토한다.
- 새 `source-types` 값 (예: `video`, `code-snippet`): 누적 surface 를 기다린다. `book` 과 `essay` 는 사용자 결정으로 추가된 사례다.
- `.naite/ontology/` 분리: 현재는 `topics.md` 와 `subject-tree.md` 두 파일이다. 누적되면 `kinds.md` 와 `source-types.md` 분리를 검토한다.
- insight·project 파일명의 날짜 prefix: decision 에는 날짜 prefix 를 도입했지만 insight 와 project 에는 적용하지 않았다. 누적되면 별도로 결정한다.
- 순수 computed domain (frontmatter cache 제거): Obsidian graph view 의존이 없어지거나 별도 cache 메커니즘이 도입되면 검토한다.
- forest 물리 마이그레이션: forest 는 평평한 `tree/` 위에 manifest 를 투영하는 그림자 단계로 운영된다 (9절). 파일을 실제 나무 디렉터리로 가르는 물리 분할은 다중 나무 수요가 실재할 때 검토한다.

각 항목은 care --check 나 care 가 surface 한 후 사용자가 결정한다. 지금 도입하면 성급하다.

## 8. References

- Ranganathan, S.R. (1933). Colon Classification. Madras Library Association. Faceted classification 의 원전이다. 관련 페이지는 `faceted-classification`.
- W3C SKOS Reference (2009). https://www.w3.org/TR/skos-reference/ 경량 지식 조직 표준이다. 관련 페이지는 `skos`.
- Blondel, V.D., et al. (2008). Fast unfolding of communities in large networks. J. Stat. Mech. Louvain modularity 의 원전이다. 관련 페이지는 `louvain-modularity`.
- Andy Matuschak. Evergreen notes. https://notes.andymatuschak.org/ 원자적이고 개념 중심이고 조밀하게 연결된 노트라는 현대 PKM 정의를 제공한다.
- Maggie Appleton. A Brief History & Ethos of the Digital Garden. https://maggieappleton.com/garden-history folksonomy 와 창발 구조의 배경을 제공한다.

## 9. Forest layer — 왜 vault 에서 숲으로 가나

단일 vault 는 규모가 커지면 서로 무관한 사상 공간을 한 그래프에 묶어 강제 링크를 누적하게 된다. 이 문제를 스키마 범주 하나로 푸는 대신, 독립된 나무들의 숲으로 분화하고 나무 사이를 느슨하게 결합하는 것이 이 층의 방향이다. 운영 규칙은 `docs/CONVENTIONS.md` 의 Forest layer 절이 담당한다.

이 방향은 직관에서 출발했지만, naite 를 개발하며 운영한 dogfood vault 의 관찰로 다듬어졌다. 네 가지 관찰이 근거다. 전부 그 dogfood vault 의 경향이고, 새 vault 가 그대로 재현할 값은 아니다.

1. 잠재 구조는 이미 강하다. 충분히 자란 vault 의 링크 그래프에 Louvain 을 돌리면 modularity 가 높게 나오고, 상향식 군집이 손으로 만든 `subject` 도메인을 거의 복원한다. 분화가 직관이 아니라 측정으로 뒷받침되고, 본질이 데이터에서 떠오른다는 상향식 온톨로지 주장을 지지한다.
2. 숲의 효용은 retrieval 정밀도가 아니다. 콘텐츠 유사도 retrieval 은 이미 도메인 내부로 스스로 걸러져서, 단일 vault 도 거짓 연관을 많이 만들지 않는다. 따라서 숲의 가치는 검색 정밀도가 아니라 에이전트 맥락 범위의 한정과 나무별 독립 거버넌스에 있다. 이 교정 때문에 분화 기준을 수치가 아니라 작업 맥락 효용에 둔다.
3. 소속은 과목이 아니라 개념 계보다. 과목 라벨로 묶으면 한 과목 안에 통계 계보와 ML 계보가 섞여 있을 때 잘못 묶게 된다. 링크 이웃 기반 label propagation 이 페이지를 실제 계보의 나무로 보낸다.
4. synapse 는 나무 사이의 접착제가 아니다. decided-over 나 trade-off 같은 synapse 관용구는 대부분 나무 내부에 머문다 (가설 반증). 그래서 inter-tree 연결은 명시적 라우팅 표면으로 관리하고, 무거운 그래프 스키마를 숲 층위에 다시 올리지 않는다.

분화와 병합과 재배정은 C급(vault 구조)이라 `/naite care --check` 의 Forest health 절이 압력만 surface 하고 사용자가 결정한다. 비어 있거나 작은 vault(Phase 1)에서는 이 층이 비활성 상태다.

이 문서의 운영 규칙은 [`docs/CONVENTIONS.md`](../docs/CONVENTIONS.md) 가, 정본 데이터는 [`.naite/ontology/`](../.naite/ontology/) 가, 워크플로 절차는 `.claude/skills/naite/*` 가 단일 소스다. 이 파일은 왜 그렇게 결정했는지만 장문으로 남긴다.
