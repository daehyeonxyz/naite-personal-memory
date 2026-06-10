# Subject tree

Canonical SKOS-lite hierarchical subject taxonomy for naite.

- Page frontmatter `subject` field uses path notation: `parent/child[/grandchild]`.
- Cross-domain pages declare multi-value subject: `subject: [a/x, b/y]`.
- Renaming uses `altLabels` — old name continues to resolve via lint.
- Adding `narrower` doesn't affect existing pages (prefix match: `subject ⊑ ml` catches `ml`, `ml/agents`, `ml/agents/multi-agent`).
- See `ARCHITECTURE.md § 2.2` for theoretical basis (W3C SKOS) and `§ 4.3` for the full evolution table.

아래 트리는 **중립 시작 예시**다. 본인의 학습·작업 도메인에 맞게 교체하거나 확장한다. 새 top-level domain 추가는 사용자 결정 (autonomy C), narrower 추가는 LLM candidate 제안 (autonomy B) 을 따른다 (`CONVENTIONS.md § Schema evolution`).

## Tree

```yaml
subjects:
  ml:
    # machine learning. 시작 예시 도메인 — 본인 도메인으로 교체 가능.
    altLabels:
      - machine-learning
    narrower:
      - agents
      - rag
      - prompting

  statistics:
    # 시작 예시 도메인 — 본인 도메인으로 교체 가능.
    altLabels: []
    narrower:
      - probability
      - distribution
      - estimation

  personal:
    # 학문 도메인에 속하지 않는 사용자 개인 글쓰기 및 프로젝트.
    # essay (kind=essay), 개인 프로젝트 (kind=project, kind=decision) 에 사용한다.
    # index.md Knowledge domains 노출 임계를 의도적으로 통과하지 않도록 concept/entity 페이지를 두지 않는다.
    altLabels: []
    narrower: []
```

## Cross-domain mapping conventions

진짜 cross-domain 일 때만 multi-subject. 단일이 default. 예시:

- `bayes-theorem` → `[statistics/probability, ml/reasoning]`

LLM 이 본문 보고 가장 자연스러운 narrower 선택. Migration 시 dry-run 에서 사용자가 confirm.

## Cached `domains` derivation

Frontmatter 의 `domains:` field 는 **lint 가 자동 갱신** — `subject` path 의 top-level 만 추출:

- `subject: [ml/agents]` → `domains: [ml]`
- `subject: [statistics/probability, ml/reasoning]` → `domains: [statistics, ml]`
- `subject: [ml]` → `domains: [ml]` (broad-only also valid)

`lint --refresh-domains` 가 idempotent 하게 cache 갱신. 사용자가 직접 `domains:` 작성 금지.

## Evolution rules

`CONVENTIONS.md § Schema evolution` 의 cardinality-graded autonomy A/B/C 가 본 트리 변경의 권한 base. 요약:

| 시나리오 | 등급 | 액션 | 페이지 변경 |
|---|---|---|---|
| Subject narrower 추가 (예: `ml/agents/multi-agent` 신설) | **B** | LLM 이 candidate append + ingest summary 에 surface, 사용자 confirm/revert | 없음 — 새 페이지부터 narrower path |
| Subject rename (예: `ml` → `machine-learning`) | **B** | LLM 이 canonical 변경 + altLabel 후보 제안, 사용자 confirm | 없음 — lint 가 alias 해석 |
| Subject move/reparent | **B** | LLM 이 candidate 제안 + altLabels 양방향 | 없음 (점진 갱신 가능, 강제 X) |
| Subject deprecation | **C** | 사용자 결정 → tree 에서 remove + LLM-driven script | **페이지 rewrite 필요** (유일 케이스, 마지막 수단) |
| 새 top-level domain | **C** | 사용자 결정 → tree 에 추가 | 없음 |

**Autonomy B 후보는 LLM 이 직접 트리에 append + surface; autonomy C 는 LLM 절대 추가 안 함.** Lint 가 cluster detection (Louvain modularity) 으로 narrower 후보 surface, 사용자 결정 후 confirm.

자세한 정책: `CONVENTIONS.md § Schema evolution`.
