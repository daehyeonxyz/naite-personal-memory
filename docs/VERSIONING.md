# docs/VERSIONING.md: 버전 및 호환성 규약

이 문서는 naite 하네스의 버전 부여 방식과 비공개 naite-app과의 호환성 판단 방법을 정의합니다.

---

## 앱과 하네스의 버전 통일 (2026-06-21)

naite-app(데스크톱 앱)과 naite 하네스(이 키트)는 **하나의 버전 번호를 공유**하며 함께 올립니다. 전에는 앱(0.3.1)과 하네스(0.5.0)가 따로 움직여 번호가 어긋났는데, 앱을 0.5.0으로 올려 하네스에 맞췄습니다. 이후로는 한쪽만 올리지 않고 두 산출물을 같은 번호로 함께 릴리스합니다.

- **patch (`0.0.X`)**: 버그 수정, 다듬기 등 작은 변경.
- **minor (`0.Y.0`)**: 큰 기능 추가, 또는 C-level 스키마 변경.

아래 `min-harness-version` 호환 판단은 그대로 유효합니다. 번호를 통일해도, 앱만 먼저 올리고 vault의 하네스는 아직 옛 버전인 경우가 있을 수 있으므로 앱은 vault의 하네스 버전을 확인합니다.

---

## 앱과 하네스의 분업 (함께 진화)

naite-app과 이 하네스는 한 제품의 두 면이라, 역할을 나눠 함께 자랍니다.

- **하네스(이 레포)가 소유하는 것**: vault 스키마(facet·kind·form), 워크플로우 스킬(`/naite grow·ask·fruit·care·upgrade`), 그리고 에이전트가 답할 때의 말투·출력 규칙(`SOUL.md § 응답 스타일`, `.claude/skills/naite/ask.md`). 채팅 답변이 어떻게 들리고 무엇을 인용하는지는 여기서 정합니다.
- **앱(naite-app)이 소유하는 것**: 그 산출물을 읽어 보여주는 화면·렌더링·상호작용. 앱은 vault에 쓰지 않고 `roots/`에만 스테이징합니다(뷰어 원칙).
- **함께 가는 것**: 버전(같은 번호로 동시 릴리스, 위 참조)과 스키마. 하네스가 새 표면을 더하면 앱이 읽어 표시하고, 앱에 필요한 맵·매니페스트는 하네스 스크립트가 만듭니다.

작업이 두 레포에 걸치면, "에이전트가 무엇을·어떻게 말하는가"는 하네스에서, "그걸 어떻게 보여주는가"는 앱에서 고칩니다.

---

## 하네스 버전 (Harness version)

하네스 버전은 `.claude-plugin/plugin.json`과 `.claude-plugin/marketplace.json`의 `"version"` 필드가 단일 소스입니다.
`build-harness-lock.py`가 이 값을 `harness-lock.json`에 embed합니다.

### 버전 스킴: semver (major.minor.patch)

- **1.0 이전에는 느리고 보수적으로 증가합니다.** 숫자가 커질수록 의미가 무거워지도록 관리합니다.
- **minor 증가 (예: 0.2.0 → 0.3.0)**: 새 기능 추가, 또는 C-level 스키마 변경 (새 `kind`/`form`/`facet` 등) 포함 시.
- **patch 증가 (예: 0.3.0 → 0.3.1)**: 버그 수정, 문서 개선, 스크립트 수정 등 하위 호환 변경 시.
- **major 증가 (예: 0.x.y → 1.0.0)**: 하네스 구조가 전면 개편될 때 (1.0 전까지는 major 증가 없음).

현재 버전: **0.6.0**

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
| 0.5.1 | 앱과 버전 라인 동기화 (naite-app IA/UX 정비 릴리스에 맞춤, 하네스 기능 변경 없음) |
| 0.5.2 | 기본 정체성·라우팅 하네스: 모든 모델이 첫 응답부터 "사용자의 나이테를 관리하는 에이전트"로 발화하도록 `CLAUDE.md`에 always-on 계약을 박고, `/naite ask`를 tree 내용 조회·추론(또는 명시 호출)으로 한정. 정체성·말투·선호·라우팅 질문은 ask 없이 기본 정체성으로 답함 (`SOUL.md`/`CONVENTIONS.md` 명문화) |
| 0.6.0 | 앱과 하네스 0.6.0 동시 릴리스. 앱: 루프 닫기(핸드오프·roots 인박스·유지보수 CTA·완료 토스트), 라이브 에이전트 탭, feel-better(이미지 아웃라인·누름 scale·stagger), min-harness 게이트·forest 메모이즈, OKF 인덱스(description/updated), 크로스플랫폼 코드(OS 추상화). 하네스: 0.5.2 정체성·라우팅 계약 포함. |
