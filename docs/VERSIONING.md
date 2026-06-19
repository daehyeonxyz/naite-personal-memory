# docs/VERSIONING.md: 버전 및 호환성 규약

이 문서는 naite 하네스의 버전 부여 방식과 비공개 naite-app과의 호환성 판단 방법을 정의합니다.

---

## 하네스 버전 (Harness version)

하네스 버전은 `.claude-plugin/plugin.json`과 `.claude-plugin/marketplace.json`의 `"version"` 필드가 단일 소스입니다.
`build-harness-lock.py`가 이 값을 `harness-lock.json`에 embed합니다.

### 버전 스킴: semver (major.minor.patch)

- **1.0 이전에는 느리고 보수적으로 증가합니다.** 숫자가 커질수록 의미가 무거워지도록 관리합니다.
- **minor 증가 (예: 0.2.0 → 0.3.0)**: 새 기능 추가, 또는 C-level 스키마 변경 (새 `kind`/`form`/`facet` 등) 포함 시.
- **patch 증가 (예: 0.3.0 → 0.3.1)**: 버그 수정, 문서 개선, 스크립트 수정 등 하위 호환 변경 시.
- **major 증가 (예: 0.x.y → 1.0.0)**: 하네스 구조가 전면 개편될 때 (1.0 전까지는 major 증가 없음).

현재 버전: **0.5.0**

---

## harness-lock.json과 버전 embed

`python .naite/scripts/build-harness-lock.py`를 실행하면 현재 하네스 버전이 `harness-lock.json`에 기록됩니다.
harness-lock.json은 vault에 체크인되며, naite-app이 이 파일을 읽어 버전을 확인합니다.

---

## naite-app과의 호환성 (min-harness-version)

비공개 naite-app은 자신이 지원하는 최소 하네스 버전(`min-harness-version`)을 내부 설정으로 선언합니다.
app은 실행 시 vault의 `harness-lock.json`에서 하네스 버전을 읽고, `min-harness-version` 이상인지 확인하여 호환 여부를 판단합니다.

예시 판단 흐름:

1. app의 `min-harness-version = 0.3.0`
2. vault의 `harness-lock.json`에서 `version = 0.2.0` 읽음
3. `0.2.0 < 0.3.0` 이므로 app이 호환 경고 또는 업그레이드 안내를 표시합니다.

### C-level 스키마 변경과 minor bump

C-level 스키마 변경(새 facet, 새 kind enum 값 등)이 하네스에 추가되면 반드시 minor 버전을 올립니다.
app은 해당 minor 버전 이상의 하네스에서만 새 facet을 신뢰하고 UI에 표시합니다.
그 이전 버전의 하네스를 사용하는 vault에서는 새 facet을 무시하거나 fallback 처리합니다.

### cross-repo 표기

naite-app 쪽의 `min-harness-version` 선언과 호환 판단 로직은 비공개 repo(naite-app)에 위치합니다.
이 문서는 공개 하네스 쪽 규약만 정의하며, app 쪽 실제 구현은 해당 비공개 repo의 문서를 참조합니다.

---

## 버전 bump 절차

1. `.claude-plugin/plugin.json`과 `.claude-plugin/marketplace.json`의 `"version"` 필드를 동일하게 수정합니다.
2. `python .naite/scripts/build-harness-lock.py`를 실행하여 harness-lock.json을 재빌드합니다.
3. `python .naite/scripts/lint-ontology.py`로 온톨로지 검사를 통과합니다.
4. 변경된 파일을 함께 커밋합니다.

---

## 버전 히스토리 요약

| 버전 | 주요 변경 |
|---|---|
| 0.1.0 | 초기 하네스 (grow/ask/fruit/care/upgrade 기본 워크플로우) |
| 0.2.0 | forest layer, naite-mcp, Claude Code plugin 등록 |
| 0.3.0 | Phase 3 공진화 계약: CONTRIBUTING, PR/issue 템플릿, schema governance, VERSIONING 규약 |
| 0.4.0 | `SOUL.md` / `USER.md` / `MEMORY.md` instruction surfaces, `/naite start`, onboarding 품질 기준 |
| 0.5.0 | `/naite upgrade`가 하네스 갱신 뒤 필요한 vault schema migration을 계획, 승인, 적용하는 흐름으로 확장 |
