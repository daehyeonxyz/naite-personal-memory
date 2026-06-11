# Topic governance

Canonical topic list (folksonomy layer) for naite.

- Page frontmatter `topics` field is **0-5 entries**. 빈 배열 허용 (예: `kind=entity` 페이지). 억지 topic 부여 금지.
- Topics 는 **재사용 가능한 개념·기법·패턴 수준** — broad domain 명 아님. 예: `llm-api`, `normal-distribution`, `chain-of-thought`, `sampling-distribution`.
- Canonical preferred. 미등록 topic 은 **warn (block 아님)** — folksonomy 가 emerge 하도록. care-check 가 누적 후보 surface, 사용자 confirm 후 canonical 추가.
- See `docs/ARCHITECTURE.md § 2.3` (folksonomy + curated taxonomy) and `§ 3.4` (governance workflow).

## Canonical topics

아래 목록은 **중립 시작 예시**다. 본인의 콘텐츠가 쌓이면서 입자도 가드 통과 시 LLM 이 직접 append 하고 (autonomy A), care-check § 14 garbage collector 가 30 일 윈도우로 underused canonical 을 회수한다.

```yaml
canonical_topics:
  # statistics (시작 예시)
  - probability
  - conditional-probability
  - bayes-theorem
  - normal-distribution
  - central-limit-theorem

  # ml (시작 예시)
  - prompt-engineering
  - chain-of-thought
  - rag
  - agentic-workflow
  - context-window
```

## Aliases (canonical only)

확실한 것만. 애매한 동의어는 care-check 가 누적 surface 후 사용자 결정.

```yaml
aliases:
  cot: chain-of-thought
  hitl: human-in-the-loop
```

## Evolution rules

- **Add canonical**: care-check 가 미등록 topic 이 ≥3 페이지에서 등장 surface → 사용자 confirm → 본 파일 `canonical_topics:` 끝에 추가. 입자도 가드 통과 시 LLM 직접 append 도 허용 (autonomy A).
- **Add alias**: care-check 가 synonym cluster (Levenshtein + co-occurrence) surface → 사용자가 canonical 결정 → 본 파일 `aliases:` 추가. 명백한 morphology / 약어는 LLM 자율 (autonomy A).
- **Rename canonical**: 새 canonical 선택, 기존 이름은 alias 로 redirect. 페이지 frontmatter 변경 불필요 (care-check 가 alias 해석).
- **Remove canonical**: deprecation. 모든 인용 페이지 page rewrite 필요 — 마지막 수단.

자세한 governance workflow: `docs/ARCHITECTURE.md § 3.4`.

## Topic granularity guidance

**OK examples (re-usable concept-level):**
- `chain-of-thought`, `normal-distribution`, `sampling-distribution`, `prompt-engineering`

**Too broad (use `subject` instead):**
- ❌ `ml`, `statistics` — these are domains, declared in `subject` field

**Too narrow (page-specific, would never appear on other pages):**
- ❌ `course-ma101-ch03-binomial`, `2026-01-15-decision`, `chapter-7-figure-3`

**Borderline (case-by-case):**
- `multi-agent-systems` — slug 도 같은 이름. Topic 으로 쓰면 다른 페이지에서 reference 시 useful. OK.
