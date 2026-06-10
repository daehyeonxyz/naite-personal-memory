# Tree Architecture — naite

**Status**: Stable 5-facet schema (`kind` / `form` / `topics` / `subject` / `source-types` + cached `domains`). 운영 중 정량 검증을 거친 설계다.
**Replaces**: 이전 `type` / `role` / `source-type` schema (facet redesign 으로 `kind` / `form` / `source-types` 로 교체); 그 이전엔 hardcoded `domains: [single-enum]`.
**Origin**: LLM 과의 ontology design 대화 + 사용자 explicit decisions + 후속 care 검토 결과 + zero-base facet redesign 세션.

이 문서는 naite 의 **schema 와 운영 모델의 long-form rationale**. 운영 invariants 는 [`CONVENTIONS.md`](../CONVENTIONS.md), canonical data 는 [`ontology/`](../ontology/), 워크플로 절차는 `.claude/skills/naite/*` 에 분산. 본 문서는 *왜 그렇게 설계했나*, *어떤 대안을 거부했나*, *언제 깨지는가* 를 담는다.

---

## 0. TL;DR

- **다축 분류(faceted) + SKOS-lite 계층 + curated folksonomy + cached materialized view** 의 4 결합. 정보과학 표준 3 개 (Ranganathan 1933, W3C SKOS 2009, modern PKM folksonomy) + DB 패턴 1 개 위에 LLM-driven curation 을 얹음.
- 페이지 frontmatter 는 5 facet (`kind`, `form`, `topics`, `subject`, `source-types`) + 1 cache (`domains`). 각 facet 직교 (Ranganathan). 이전 `type` / `role` / `source-type` schema 를 교체한 결과다.
- Schema 진화는 **cardinality-graded autonomy A/B/C** — autonomy A 는 LLM 자율 (개념 페이지, canonical topic, 명백한 alias), B 는 candidate 제안 (subject 트리 변경), C 는 사용자 결정 (trunk schema).

---

## 1. Motivation — 왜 평평한 enum 을 버렸나

이 tree 는 평평한 단일 도메인 enum (`domains: [ml]`) 으로 시작했다. 페이지가 빠르게 누적되면 두 종류의 통증이 임박한다:

| 문제 | 증상 | 해결 |
|---|---|---|
| Schema split 비용 | `ml` → `ml-llm` / `ml-agents` 분기 시 N 페이지 frontmatter LLM 재분류. 매 split 마다 반복. | SKOS-lite + cached domain (1차 redesign) |
| 단일 도메인 강제 | Cross-domain 페이지를 multi-value 로 강제 표현, 사실은 다축 분류 문제. | 다축 분류 (faceted) — 5 facet 직교 |
| Page role 부재 | Decision · Project · Insight · Question 같은 페이지 성격이 prose convention 으로만 존재 → grep 으로만 추적. | `role` facet → `kind` facet 으로 본질 표현 강화 |
| Source-type 부재 | course / paper / docs / conversation 출처 정보가 본문 prose 또는 파일명 prefix 로만 존재. | `source-type` (singular) → `source-types` (list) 로 multi-provenance 반영 |
| Self-knowledge ↔ study-knowledge 혼재 | "내가 결정한 것" 과 "내가 학습한 것" 이 그래프에서 구분 불가. | `kind=source-record` 도입 — literature note vs permanent note 명시 분리 (Zettelkasten 정통) |

마지막 항목이 가장 결정적 — 이 tree 의 본질은 *사용자가 무엇을 알고 있나* 이고, 이 "앎" 은 두 갈래 (compiled self-knowledge + study knowledge) 의 결합이다. 초기엔 `role` facet 이 그 구분을 명시화했고, redesign 에서 `kind` facet 으로 더 정확히 표현됨 — `kind=source-record` (study knowledge) vs `kind=decision`/`insight`/`project` (compiled self-knowledge).

---

## 2. Theoretical bases — 6 토대 (개요)

각 토대의 풀 설명은 tree 의 concept page 로 grow 됨. 본 섹션은 *왜 그 토대를 채택했는지* 한 단락씩.

### 2.1 Faceted classification (Ranganathan 1933)

한 자료를 *여러 직교 차원* 으로 분류한다. PMEST(Personality, Matter, Energy, Space, Time)는 도서관 도메인 사례지만 핵심은 *facet 직교성*. 한 facet 변경이 다른 facet 에 영향 없음 = schema 변경의 영향 격리. 본 tree 의 5 facet 이 직접 적용. 자세히는 tree 의 `faceted-classification` 개념 페이지로 정리할 수 있다.

### 2.2 SKOS-lite (W3C 2009)

W3C 의 Simple Knowledge Organization System 표준의 *부분집합* 채택. `narrower` 는 path notation (`ml/agents`) 으로 implicit, `altLabel` 은 명시. AltLabel 이 *renaming 비용을 0 으로 만드는* 핵심 메커니즘. 자세히는 tree 의 `skos` 개념 페이지로 정리할 수 있다.

### 2.3 Folksonomy + curated taxonomy

순수 taxonomy (top-down rigid) 는 진화 비용 크고, 순수 folksonomy (bottom-up free) 는 카오스. 두 layer 결합 — `topics` 는 folksonomic emerge, `subject` 는 curated. 미등록 topic 은 입자도 가드 통과 시 LLM 자율 추가 (autonomy A), 가드 실패면 surface 만. 입자도 가드는 `ontology/topics.md § Topic granularity guidance`. 자세히는 tree 의 `folksonomy` 개념 페이지로 정리할 수 있다.

### 2.4 Cached materialized view

DB 의 materialized view 패턴. 매 query 재계산 (computed) 도, 박제 (cached) 도 trade-off. 본 tree 의 `domains` field 는 *cached + care-check refresh* — Obsidian graph view 호환성이 결정 변수. 자세히는 tree 의 `materialized-view` 개념 페이지로 정리할 수 있다.

### 2.5 LLM-as-curator

전통 ontology 는 사람 schema steward. 1 인 운영 tree 에서 LLM 이 그 mechanical 부분 (facet 선택, alias cluster 감지, 모호 케이스 결정, narrower 후보 발견) 을 수행. 비용 가정: Codex Pro / Claude Pro 토큰 풍부. 자세히는 tree 의 `llm-as-curator` 개념 페이지로 정리할 수 있다.

### 2.6 Graph-derived structure (Louvain, Blondel 2008)

페이지간 wikilink graph 가 의미 graph 의 *근사*. modularity 최적화 (Louvain) 로 narrower 후보 추출 가능 — top-down 강제가 아니라 *data-driven evolution*. care-check 의 high-degree neurons 는 단순 centrality. 자세히는 tree 의 `louvain-modularity` 개념 페이지로 정리할 수 있다.

---

## 3. Architecture

### 3.1 Frontmatter schema

```yaml
---
kind: concept | entity | source-record |          # 페이지 본질 (불변)
      project | decision | insight | comparison
form: prose | index                               # 본문 제시 방식
topics: [<canonical-topic>, ...]                  # folksonomy. 0-5. 빈 배열 OK.
subject: [<skos-path>]                            # SKOS-lite path. 다축 가능 (cross-domain).
source-types: [course | conversation | paper |    # 출처 (8-enum, 항상 list)
               article | docs | book |
               essay | external]
domains: [<top-level>]                            # CACHED — subject 의 top-level. care-check 가 derive.
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

운영 룰 (필드별 enum, granularity gate, alias 처리) 은 [`CONVENTIONS.md § Ontology`](../CONVENTIONS.md) 가 단일 source. 본 섹션은 *왜 이 5 facet 인가* 의 rationale 만.

**Facet redesign**: 이전 `type` / `role` / `source-type` schema 가 `kind` / `form` / `source-types` 로 교체됨. 핵심 변화: (1) `kind=source-record` 부활로 literature note (source-bound) 와 permanent note (재사용 개념) 분리, (2) `role` 폐지 + `form` 도입 (page 는 정보 artifact 라 role 개념 부적합), (3) `source-types` plural 화 (multi-provenance).

### 3.2 Field 책임 분리

| Field | 본질 | 진화 방식 |
|---|---|---|
| `kind` | 페이지의 *referent* — 무엇을 가리키는가 (9-enum) | enum 확장 가능 (care-check surface 후 사용자 결정 — C-level) |
| `form` | 페이지의 *모양* — 본문이 어떻게 제시되는가 (2-enum) | enum 거의 불변 (prose / index 외 거의 없음) |
| `topics` | 재사용 가능 키워드 | folksonomic emerge + 주기적 canonicalize |
| `subject` | SKOS-lite tree 위치 | narrower 추가 자유, page 무변경 |
| `source-types` | 출처 종류 (list, 8-enum) | 안정, 새 값 추가 시 C-level |
| `domains` | **cache** — subject 의 top-level (facet 아님) | **care-check 자동 갱신** |

핵심 invariant: **`kind` 는 페이지가 가리키는 *referent 의 본질*, `form` 은 그 본문이 *어떻게 제시되는가***. 두 차원 독립 — 같은 kind 가 다른 form 으로도 가능 (e.g., `kind=source-record, form=prose` = subchapter note; `kind=source-record, form=index` = chapter index hub). 미래 확장 시나리오: `kind=concept, form=index` (개념 hub), `kind=entity, form=index` (tool 카테고리 hub) 등.

### 3.3 Spec storage location

- `ARCHITECTURE.md` (본 파일) — **Why** — 철학·이론적 기반·rationale.
- [`ontology/`](../ontology/) — **What — canonical data** — `subject-tree.md`, `topics.md`. SKOS-lite + folksonomy.
- [`CONVENTIONS.md`](../CONVENTIONS.md) — **What — operating invariants** — Ontology · Schema evolution · Soft ontology · Decision shape. 양 도구 (Claude Code, Codex CLI) 공유.
- [`CLAUDE.md`](../CLAUDE.md) (+ auto-mirror `AGENTS.md`) — **Bootloader** — 라우팅·트리거·hard safety.
- `.claude/skills/naite/*.md` — **How** — workflow 절차.

`ontology/` 디렉토리는 spec data 라 양 surface 가 동일하게 참조. mirror 안 됨 (`scripts/sync-agents.ps1` 갱신 불필요).

### 3.4 Topic governance — graded autonomy

- **Canonical list**: `ontology/topics.md` 에 maintained.
- **신규 topic 도입 (autonomy A)**: 입자도 가드 통과 시 LLM 이 `canonical_topics:` 에 직접 append + 페이지 사용. 가드 실패면 surface 만.
- **Alias 정리**: 명백한 morphology / 약어는 LLM 자율 (autonomy A); 동의어 의심이지만 모호하면 care-check cluster surface (사용자 결정).
- **Topic 부재 페이지**: 허용 (예: `entity` 타입 페이지). topics 빈 배열 OK.

자세한 정책 + 등급 매핑: [`CONVENTIONS.md § Schema evolution`](../CONVENTIONS.md).

---

## 4. Operating model — rationale

본 섹션은 *왜 이렇게 운영하는가*. 절차 자체는 `.claude/skills/naite/{grow,grow-branch,care-check,care,...}.md` 가 단일 source.

### 4.1 Grow 시점 facet 결정 — 왜 LLM 자율

새 페이지 작성 시 LLM 이 5 facet 결정 (입자도 가드 + canonical list 참조). 사람 큐레이터에 비해 *일관성* (같은 룰 매 페이지 동일 적용) 이 강점. 이 가정의 비용 base 는 § 2.5 LLM-as-curator.

### 4.2 care 의 두 모드 — 분리된 책임

- **`care --check`** (`scripts/lint-ontology.py` deterministic + `.claude/skills/naite/care-check.md` LLM-driven) — schema/정책 compliance. report-only. 3a frontmatter completeness, 3b subject tree, 3c topic canonical, 3d domain cache, 3e role/source-type distribution, 3f BOM, 3g legacy drift, 3h language-shape. § 14 autonomy garbage collector (LLM-driven, 30 일 윈도우).
- **`care`** (돌봄 모드) — qualitative review/repair. narrative prose verdict 도 이 모드로 흡수: 점수 없음, threshold 없음. page/branch review, 직접 content 수선, 대규모 sweep, recurring-rule 학습. 사용자 수동 호출.

분리 이유: `care --check` 의 mechanical 검사와 `care` 의 *맥락 판단* 이 다른 영역. 자세히: `.claude/skills/naite/{care-check,care}.md`.

### 4.3 Schema evolution — graded autonomy

| Level | Impact scope | LLM behavior |
|---|---|---|
| **A — autonomous** | 1-2 페이지 추가/변경, edit 으로 reverse 가능 | LLM 직접 작성 + summary surface, care-check 사후 검증 |
| **B — propose** | 트리 구조 (narrower / rename / move), 미래 페이지 영향, altLabel 로 cheap revert | candidate append + summary surface, 사용자 확인 |
| **C — user decision** | trunk schema (top-level domain, enum 값, facet field, deprecation) | LLM 절대 추가 금지 |

이 정책의 *동기* 는 risk inversion 분석이다 — 보수적 정책이 *folksonomy 폭발* 을 가드하는 동안 *thinness* (개념 페이지 미생성, 연결 빈약) 라는 다른 위험을 만들었다는 정량 발견. 정책 완화 후 그래프 활성화 지표 (chapter outbound link 수, zero-link 페이지 수) 로 net positive 를 검증했다.

자세한 등급 매핑 + 입자도 가드: [`CONVENTIONS.md § Schema evolution`](../CONVENTIONS.md).

### 4.4 Tree 발전 궤적 — 4 layer 분산 기록

- **Tactical timeline** — `tree/rings.md` (작업 단위 1 줄)
- **Action delta** — Git commit history (atomic 변경)
- **Architectural rationale** — `ARCHITECTURE.md` (본 파일)
- **Intellectual reasoning** — `tree/` 의 fruit (decision) 페이지

### 4.5 Multi-pass orchestration — 대규모 작업의 default

≥100 페이지 영향의 작업은 **3 패스 cycle** (draft → review → refine, review gate 가 정책 steering) 을 default 로 한다. 대규모 concept layer 작업에서 적용·검증된 패턴이다.

---

## 5. Tooling

### 5.1 Active scripts

- `scripts/lint-ontology.py` — § 3 deterministic sub-check (3a-3h) + § 7 non-tree dirt detection. 매 care --check run 호출.
- `scripts/sync-agents.ps1` — `.claude/skills/naite/*` → `.agents/skills/naite/*` 자동 mirror (`Claude Code` → `Codex` 텍스트 치환). CLAUDE.md → AGENTS.md 동시 처리.

### 5.2 care --check capability

- `--strip-bom` — UTF-8 BOM normalize in-place.
- `--refresh-domains` — `domains` cache 갱신 안내 (idempotent).
- § 14 autonomy garbage collector — 30 일 윈도우로 underused canonical / trivial narrower / orphan spawn 회수. 현재 LLM-driven (deterministic script 미구현 — § 7 future considerations).

---

## 6. Examples — 현재 frontmatter shape

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

재사용 가능한 일반 개념. 같은 topic 의 source-bound 기록은 별도 `kind=source-record` 페이지로 분리.

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

특정 강의 unit (`course-XXX-chYY-ZZ-*`) 의 기록 — source-bound. 본문이 산문 → `form=prose`. 챕터 index hub 면 `form=index`. Zettelkasten 의 literature/permanent 구분이 schema 에 명시화된 형태다.

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

파일명: `decision-YYYY-MM-DD-<slug>.md` (date prefix convention).

### 6.4 Cross-domain 페이지

```yaml
---
kind: concept
form: prose
topics: [human-in-the-loop, oversight, agentic-workflow]
subject: [ai-fluency/human-in-the-loop, ml/agents]
source-types: [conversation]
domains: [ai-fluency, ml]
created: 2026-04-29
updated: 2026-04-29
---
```

Cross-domain 은 `subject` multi-value 로 표현 (kind 와 무관). domains cache 도 multi.

(`source-types=[legacy]` 사용 안 함. Obsidian vault import 페이지도 콘텐츠 본질이 conversation 이었으면 `[conversation]`, article 이었으면 `[article]`.)

### 6.5 Source-record 페이지 — 단일 docs 정리

```yaml
---
kind: source-record
form: prose
topics: [claude-api, prompt-caching]
subject: [ml/runtime]
source-types: [docs]
domains: [ml]
created: 2026-04-29
updated: 2026-04-29
---
```

한 docs unit (예: Anthropic API prompt caching 문서) 의 정리. 산문 본문 → `form=prose`. 만약 여러 docs 페이지를 묶는 index hub 라면 `form=index`. 본문에 `as-of: <date>` 같은 시점 표시 — facet 으로 분리 안 함 (§ 7 future considerations).

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

`course-XXX-chYY-00-index.md` 같은 챕터 navigation hub. 본문이 subchapter list → `form=index`. `kind=source-record` 는 같지만 form 으로 prose 와 구분.

---

## 7. Future considerations

미래 care --check 또는 care 가 surface 하면 검토할 항목 (현재 도입 안 함):

- **§ 14 autonomy garbage collector deterministic 구현** — 현재 LLM-driven spec 만. 30 일 윈도우 검증 cadence 가 안정되면 `scripts/autonomy-gc.py` 추가 검토.
- **`as-of: <date>` facet** — `source-types ∋ docs` 페이지의 staleness 추적용. 현재는 본문 provenance 로 충분.
- **`classifications:` wrapper** — facet 5 개 이상 (예: `audience`, `certainty`, `maturity` 추가) 으로 늘어나면 검토. 현재 5 facet 안정.
- **새 `kind` value** — 누적 page-shape pain ≥5 페이지 + 사용자 결정 후. 이전 `role=question` (corpus 0) 은 redesign 에서 새 `kind` enum 에 옮기지 않음 — needs surface 시 C-level decision.
- **새 `form` value** — 현재 `prose` / `index` 만. 미래에 별도 형식 (예: `table`, `gallery`) 등장 시 검토.
- **새 `source-types` value** (예: `video`, `code-snippet`) — 누적 surface. `book`, `essay` 는 사용자 결정으로 추가된 사례.
- **`ontology/` split** — 현재 `topics.md`, `subject-tree.md`. 누적 시 `kinds.md`, `source-types.md` 분리 검토.
- **insight/project file naming date prefix** — decision 에 date prefix 를 도입했지만 insight/project 는 미적용. 누적 시 별도 결정.
- **Pure computed domain** (frontmatter cache 제거) — Obsidian graph view 의존 없어지거나 별도 cache 메커니즘 도입 시.
- **forest** — vault 의 집합을 한눈에 보는 상위 기능 (1 vault = 1 tree). 예약어만 확보. 다중 vault 수요가 실재할 때 설계.

각 항목은 care --check 또는 care 가 *surface* 한 후 사용자 결정. 지금 도입은 premature.

---

## 8. References

- **Ranganathan, S.R.** (1933). *Colon Classification.* Madras Library Association. — Faceted classification 의 원전. → `faceted-classification`.
- **W3C SKOS Reference** (2009). https://www.w3.org/TR/skos-reference/ — Lightweight knowledge organization 표준. → `skos`.
- **Blondel, V.D., et al.** (2008). *Fast unfolding of communities in large networks.* J. Stat. Mech. — Louvain modularity. → `louvain-modularity`.
- **Andy Matuschak.** *Evergreen notes.* https://notes.andymatuschak.org/ — Atomic, concept-oriented, densely-linked notes 의 modern PKM 정의.
- **Maggie Appleton.** *A Brief History & Ethos of the Digital Garden.* https://maggieappleton.com/garden-history — Folksonomy + emergent structure.

---

본 문서의 *operational rules* 는 [`CONVENTIONS.md`](../CONVENTIONS.md), *canonical data* 는 [`ontology/`](../ontology/), *workflow procedure* 는 `.claude/skills/naite/*` 가 단일 source. 본 파일은 *왜 그렇게 결정했나* 만 long-form 으로 남긴다.
