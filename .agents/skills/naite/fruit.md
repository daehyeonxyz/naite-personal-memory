# /naite fruit

결정 thread 를 나무의 **열매** 로 맺는 dialogue scaffold. tree 의 노드(concept/entity/source) 들이 뉴런이라면, 시냅스 layer 는 그 위를 가로지르며 의사결정 흐름을 형성하는 별도 차원의 결합. 한 page 가 14 섹션을 다 담는 form 으로 나올 수도 있고, 짧은 prose 단락이 다른 concept 페이지에 박혀 그 자체가 시냅스 한 가닥이 될 수도 있다 — 둘 다 정당.

All data paths below resolve against **NAITE_ROOT** (the root of the naite repo). Sub-skill references resolve against **SKILL_DIR** (`<NAITE_ROOT>\.agents\skills\naite`). See `SKILL.md` for context.

## When to use — 3 triggers

1. **명시 슬래시**: `/naite fruit [topic?]`. 사용자가 "이 결정 정리해두자" 라고 의식적으로 부를 때.
2. **자연 감지**: 대화 중 "선택했다 / 고민했다 / 보류했다 / 실패했다 / 결정했다 / 비교했다" 신호 + trade-off 정황이 감지되면 Codex 가 한 줄로 제안 — "이거 열매로 정리해둘까요?" 사용자 확인 후에만 실행. grow.md § Branch pre-check 와 같은 cadence.
3. **작업 종료 트리거**: 사용자가 "끝났어 / 마무리 / 완료 / 다 됐어" 신호 + 그 작업이 의사결정·trade-off 를 포함한 흐름이면 wrap-up 제안. 단순 task 종료엔 발동 안 함.

세 trigger 모두 동일 워크플로로 진입. 차이는 모드 판별 단계에서 사용자 확인 한 줄 추가될 뿐.

## Hard rules

- **출력은 `kind: decision` 페이지** (적합 시 `kind: concept`/`entity`/`source-record` 페이지에 decision-shape content 인라인 embed 도 가능). `form: prose`. `subject` 는 `ontology/subject-tree.md` 의 path 1개; 진짜 cross-domain 일 때만 multi (`[a/x, b/y]`). `dmu/`, `failure-*/`, `career-*/`, `synapse/` 같은 메타 subject path 또는 별도 kind enum 추가는 **금지** — 시냅스의 본질은 카테고리화 거부 (`CONVENTIONS.md § Decision thread shape` 참조). Decision-shape thread 자체는 page-level enum 으로 좁히지 않고 cross-page 시냅스 layer 로 흐른다.
- **파일명**: `decision-YYYY-MM-DD-<slug>.md` 형식. `YYYY-MM-DD` 는 페이지 `created` 날짜 (frontmatter 와 일치). `<slug>` 부분은 `lowercase-kebab-case`. `DMU-` prefix 금지. 예: `decision-2026-01-15-vector-db-selection`, `decision-2026-02-03-retrieval-strategy`.
- **본문은 DMU 14 섹션을 참조 구조** 로 사용. 사용자 답변에 따라 일부 섹션은 통째로 생략. 빈 헤더 작성 금지.
- **최소 3개 outbound wikilink** (mechanism / related concept / project / failure mode 중 어느 조합이든). 부족하면 사용자에게 "어떤 개념 페이지에 연결되나요?" 푸시.
- **누락 개념 발견 시** `tree/seeds.md` 에 stub 제안 — DMU 가 graph 의 빈 공간을 채우는 압력으로 작동.
- **prose idiom 박힘 강제**: 본문에 `decided X over Y when ...`, `failed when ...`, `trade-off: A vs B`, `validates`, `falsifies` 중 적어도 1~2개 등장. CONVENTIONS.md § Soft ontology 의 어휘를 반드시 재사용.
- 기타 `AGENTS.md § Secrets & privacy`, `CONVENTIONS.md § Schema evolution` 전부 그대로 적용.

## Dialogue scaffold (template filler 가 아니라 사고 캐묻기)

skill 의 핵심 가치는 빈 헤더를 채우게 하는 게 아니라 **누락된 thinking 을 끌어내는 것**.

- DMU 14 섹션을 **차례 질문** 으로 던짐. 한꺼번에 보내지 말고 한 번에 1~2개씩.
- **표면 답변 거부**: "좋아 보여서 / 유명해서 / 사람들이 많이 써서 / 그냥 해보고 싶어서" 류는 받지 않고 다시 push — "그 선택의 trade-off 는 무엇이었나요? latency? maintenance cost? data quality? rollback 가능성?"
- **실패 조건은 조건문 형태로 강제**: "잘 안 됐다" 거부 → "어떤 입력일 때 깨졌나요? / 어떤 사용자 행동 패턴에서 무너졌나요?"
- **Invariant 는 형식 강요**: `[조건/상황]에서는 [구조/전략]이 [효과]를 만들지만, [제약/실패 조건]에서는 [보완책]이 필요하다`. 이 형식 안 맞으면 다시 적게 함.
- **Cross-link 부족 시**: 사용자에게 "이 결정이 tree 의 어떤 개념과 닿아 있나요? `[[laplace-transform]]`, `[[chain-of-thought]]` 같은 기존 페이지 중에" 같이 candidate 제시.

## Workflow

### 0. Pre-flight (every invocation)

1. Read `<NAITE_ROOT>/AGENTS.md` — 특히 § Soft ontology, § Decision threads (시냅스 layer), § Personal tree scope, § Ontology. 그리고 `ontology/subject-tree.md` (canonical paths) + `ontology/topics.md` (canonical vocabulary).
2. Read `<NAITE_ROOT>/tree/trunk.md` 전체 — 도메인·기존 hub 페이지 candidate 수집.
3. Last ~20 lines of `<NAITE_ROOT>/tree/rings.md` — 최근 맥락.
4. Trigger 모드 판별. 자연 감지·작업 종료 모드면 사용자에게 한 줄 확인 후 진행.

### 1. Question pass (14 sections)

각 섹션을 dialogue 로 끌어냄. 사용자 응답 부족하면 push, 형식 이탈하면 재요청.

1. **Context** — 어떤 프로젝트·학습·맥락에서 이 결정이 발생했나? 자원·시간·데이터·시스템 제약은?
2. **Problem** — 한 문장으로: `[대상]에서 [조건] 때문에 [원하는 결과]가 달성되지 않았다`.
3. **Decision** — 실제로 무엇을 선택·보류·기각했나?
4. **Alternatives** — 비교한 대안과 각 대안의 장단점 / 기각 이유.
5. **Rationale** — 왜 그 선택? **Trade-off 형태로 강제** (latency / maintenance / data quality / rollback / 목표가 benchmark vs 실사용성 등).
6. **Mechanism** — 이 선택이 작동한다고 예상한 구조적 이유. 입력→처리→중간 표현→병목 흡수→trade-off 수용 흐름.
7. **Outcome** — 실제 결과 (정량 + 정성). 결과 미검증이면 명시: "Outcome 미검증. 검증하려면 `[필요 실험]`."
8. **Failure mode** — 조건문 형태 ≥ 1. 단순 "잘 안 됐다" 거부.
9. **Iteration** — 결과 보고 무엇을 바꿨나? 변경 전/후 + 이유. 없으면 "아직 iteration 없음. 다음 관찰 기준은 `[기준]`."
10. **Invariant** — 일반화 가능 규칙. 위 강요 형식 사용. 도구 이름 대신 구조 우선.
11. **Reusability — Use when**: 조건들 (≥ 2).
12. **Reusability — Avoid when**: 조건들 (≥ 1).
13. **Related** — 관련 개념·프로젝트·실험·실패 기록 wikilinks.
14. **Next action** — 이 결정에서 이어지는 다음 행동 1개 (선택 사항, 없으면 생략).

빈 섹션은 본문에 헤더 자체를 쓰지 않음. 14개 다 채우려고 억지 부리지 않음.

### 2. Cross-link 검수

본문의 outbound wikilink 개수 셈. < 3 이면:
- 사용자에게 "이 결정이 닿는 기존 tree 페이지 더 없나요? 후보: `[[...]]` `[[...]]`" 제시.
- 응답 받아 본문에 prose idiom 으로 박음 (`builds on`, `applies to`, `trade-off: A vs B` 등).

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
domains: [<one knowledge domain>]   # cross-domain 진짜일 때만 복수. dmu, decision, synapse, course-* 메타 태그 금지
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

본문에 prose idiom 박혔는지 self-check:
- `decided ... over` / `failed when` / `trade-off:` / `validates` / `falsifies` / `builds on` / `instance of` / `applies to` 중 ≥ 1.

### 5. `tree/trunk.md` 업데이트 (hub 자격 있을 때만)

이 열매 페이지가 **hub 후보** 면 (즉 다른 페이지에서 자주 link 받을 가능성이 높으면) `## Knowledge domains § <domain>` 의 "주요" 라인에 한 줄 추가. 한도 (4-7개) 도달 시 사용자에게 어느 줄을 빼고 추가할지 물음.

대부분의 열매 페이지는 작은 결정 한 건이라 **hub 후보가 아님** — 이때는 trunk 미등재, 본문 wikilink 와 prose idiom 으로만 발견되게 둠. care --check 의 high-degree neurons 가 자동으로 promotion candidate 를 surface.

`CONVENTIONS.md § trunk.md discipline` 참조.

### 6. `tree/rings.md` append

```
## [YYYY-MM-DD] fruit | <slug>
- pages created: [[<slug>]]
- pages updated (back-prose 박은 경우): [[...]]
- domain: <ai-fluency | ml | engineering-math | statistics>
- stubs added: N
```

### 7. Bidirectional prose 제안

이 결정이 닿는 기존 concept 페이지가 있으면, 그 페이지에도 한 줄 박을지 사용자 확인:
> "`[[other-page]]` 에 'used in [[this-decision-slug]]' / '`[[this-decision-slug]]` 의 trade-off 분석 참조' 같은 prose 한 줄 추가할까요?"

승인 시 그 페이지 Edit. 시냅스가 양방향으로 자라남.

### 8. Checkpoint

사용자에게 한 단락 요약:
- 작성된 페이지 경로
- 추가된 stub 목록
- bi-directional prose 박은 페이지 목록
- 14 섹션 중 채워진 것 / 빠진 것
- 다음 행동 (있으면)

## Templates

### Synapse page (DMU 14 sections, 모두 채운 예시)

```markdown
---
kind: decision
form: prose
topics: [<canonical-topics>]
subject: [<path>]
source-types: [conversation]
domains: [ml]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# {Decision title in plain words}

## Context

{프로젝트·학습·맥락. 자원·제약. 결정이 필요했던 이유.}

## Problem

> `[대상/시스템]에서 [조건] 때문에 [원하는 결과]가 달성되지 않았다.`

## Decision

> `[선택한 방법]을 적용했다.` 또는 `현재 보류, 추가 검증 기준 먼저 세우기로.`

## Alternatives

- **Alt A**: 장점 / 단점 / 기각 이유
- **Alt B**: 장점 / 단점 / 기각 이유

## Rationale

`decided [[A]] over [[B]] when [[constraint]]`. 

{trade-off 형태 prose. 표면 표현 금지.}

## Mechanism

{입력·처리·병목·흡수 메커니즘. `builds on [[concept]]`.}

## Outcome

- 정량: latency / cost / accuracy / precision / recall
- 정성: 좋아진 점 / 나빠진 점 / 예상과 달랐던 점

## Failure mode

`failed when [[condition]]`.
- 조건 1
- 조건 2

## Iteration

- 변경 전 / 후 / 이유 / 다음 실험

## Invariant

`[조건]에서는 [구조]가 [효과]를 만들지만, [제약]에서는 [보완책]이 필요하다.`

## Reusability

### Use when
- 조건 1
- 조건 2

### Avoid when
- 조건 1

## Related

- builds on [[...]]
- applies to [[project-...]]
- trade-off: [[a]] vs [[b]]
- see also [[...]]

## Next action

- [ ] 다음 행동 1개
```

### Synapse 짧은 형태 (다른 concept 페이지에 박는 prose)

DMU 가 별도 페이지가 될 만큼 무겁지 않으면, 기존 concept 페이지의 본문에 짧은 단락으로 박음:

```markdown
## In my projects

2026-04 [[project-portfolio-site]] 에서 retrieval precision 부족 문제로 도입을 고려했으나 latency budget 때문에 보류. `decided [[lightweight-similarity-filter]] over [[2-stage-reranking]] when [[interactive-latency-budget]]`. failed when [[corpus-noisy-and-abstract-queries-coexist]] — 이때는 lightweight 도 무너짐. invariant: noisy corpus 에서 recall-first → rerank 패턴은 precision 회복에 유리하지만 latency budget 엄격하면 caching/router 선행 필요.
```

이런 prose 가 여러 페이지에 박혀 있으면 grep 으로 의사결정 thread 가 즉시 surface.

## What this command never does

- 새 type / 새 frontmatter 필드 / 새 메타 도메인 태그 신설 안 함.
- DMU shape 페이지를 별도 인덱스 (`## Domain: dmu`) 로 분리 안 함 (애초 그 섹션은 폐기됨).
- Career 관련 frontmatter / `[[fde-skill-*]]` 페이지 사전 생성 안 함 (CONVENTIONS.md § Decision thread shape 의 grep-on-demand 원칙 준수).
- 파일명 `DMU-YYYYMMDD-...` prefix 안 씀.
- 빈 14 섹션을 강제로 채우지 않음 — 누락은 생략.
- frontmatter `domains` 에 `course`, `course-{slug}`, `dmu`, `decision`, `synapse` 등 메타·컬렉션 태그 안 씀 — 콘텐츠 도메인 1개만.
- 모든 열매 페이지를 자동으로 trunk.md 에 등재 안 함 — hub 후보일 때만.
- `git commit` 안 함.
