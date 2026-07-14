# docs/VERSIONING.md: 버전 및 호환성 규약

이 문서는 naite 하네스의 버전 부여 방식과 비공개 naite-app과의 호환성 판단 방법을 정의합니다.

---

## 앱과 하네스의 버전 분리 (2026-07-10)

naite-app(데스크톱 앱)과 naite 하네스(이 키트)는 **각자의 버전 라인을 따로** 관리합니다. 하네스 버전은 하네스가 실제로 바뀔 때만 올립니다. 앱 릴리스를 따라가기 위한 번호 맞춤 릴리스(과거 0.5.1·0.6.5·0.6.7·0.8.2·0.8.3 같은 "버전 라인 동기화")는 더 이상 만들지 않습니다.

- **patch (`0.0.X`)**: 버그 수정, 문서·스크립트 다듬기 등 하위 호환 변경.
- **minor (`0.Y.0`)**: 큰 기능 추가, 또는 C-level 스키마 변경.

두 산출물의 호환성은 번호가 같은지가 아니라 아래 `min-harness-version` 계약으로 판단합니다. 앱은 vault의 `harness-lock.json`에서 하네스 버전을 읽어 자신이 요구하는 최소 버전 이상인지 확인합니다.

> 연혁: 2026-06-21부터 두 산출물이 하나의 번호를 공유했으나(0.5.0~0.8.3), 하네스 변경이 없는 앱 릴리스마다 빈 동기화 릴리스가 쌓이는 비용만 남아 2026-07-10 사용자 결정으로 분리했습니다.

---

## 앱과 하네스의 분업 (함께 진화)

naite-app과 이 하네스는 한 제품의 두 면이라, 역할을 나눠 함께 자랍니다.

- **하네스(이 레포)가 소유하는 것**: vault 스키마(facet·kind·form), 워크플로우 스킬(`/naite grow·ask·fruit·care·upgrade`), 그리고 에이전트가 답할 때의 말투·출력 규칙(`SOUL.md § 응답 스타일`, `.claude/skills/naite/ask.md`). 채팅 답변이 어떻게 들리고 무엇을 인용하는지는 여기서 정합니다.
- **앱(naite-app)이 소유하는 것**: 그 산출물을 읽어 보여주는 화면·렌더링·상호작용. 앱은 vault에 쓰지 않고 `roots/`에만 스테이징합니다(뷰어 원칙).
- **함께 가는 것**: 스키마와 호환 계약(`harness-lock.json` 버전 ↔ 앱의 `min-harness-version`). 하네스가 새 표면을 더하면 앱이 읽어 표시하고, 앱에 필요한 맵·매니페스트는 하네스 스크립트가 만듭니다. 버전 번호는 각자 관리합니다(위 참조).

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

현재 버전: **0.8.6**

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
| 0.6.5 | 앱과 버전 라인 동기화 (naite-app 채팅 홈 재편 릴리스에 맞춤). 앱: 홈을 상용 AI 식 가운데 채팅으로, 지난 대화는 레일 목록으로, 에이전트 라이브 모니터 탭 폐기. 하네스 기능·스키마 변경 없음 (0.5.1 과 같은 버전 라인 동기화 릴리스). |
| 0.6.7 | 앱과 버전 라인 동기화 (naite-app 0.6.7 에 맞춤, 0.6.6 건너뜀). 앱: 슬래시 스킬 연동(`/` 팔레트가 엔진 실제 스킬을 dispatch)·모델/노력 엔진 연동·마크다운 강화·iOS 스퀘어클 모서리. 하네스 기능·스키마 변경 없음. |
| 0.7.0 | 앱과 하네스 0.7.0 동시 릴리스. 앱: 셸 프레임(상단+좌측=한 프레임, 메인 떠있는 카드), 숲을 나무 단위 지도로(perf·읽힘), 그래프 실제 연결 표시, 나무/검색/도움말 고급화, 마크다운 복사 버튼·코드블록 정제, codex 식 작업 요약, 대화 펼침/접힘. 하네스: 답변 출력 규약을 `SOUL.md § 응답 스타일` 에 명시(답변을 코드블록으로 감싸지 않기, GFM alert 콜아웃 문법) + CLAUDE/AGENTS 미러. C-level 스키마 변경은 없음. |
| 0.8.0 | 하네스 minor 릴리스 (plugin vault-scaffold + guard starter/vault 모드 + secret/PII 강화 + 크로스플랫폼 + 문서·코드 정합). 신규 기능: 플러그인만 설치해 vault 가 없는 사용자를 위해 `/naite start` §0 이 열린 폴더에 vault 뼈대(`roots/`·`tree/`·`docs/`)를 scaffold 함 (새 user-facing 기능이라 minor). 가드 훅을 starter/vault 모드로 분기(`.naite/PUBLIC_STARTER` sentinel + `NAITE_HOOK_MODE` override)해 개인 vault 의 `tree/`·`roots/` 커밋을 막지 않으면서 secret 스캔은 유지하고, pre-push 백스톱·KV/PII 스캔·`sk-ant-`/`AIza` 등 키 패턴·Windows 예약어·비ASCII 경로 우회 차단을 추가. 크로스플랫폼: `sync-agents`/harness-lock LF 출력, 진단 스크립트 cp949 콘솔 가드, NFC 슬러그 정규화. 문서·코드 정합: `plugin.json`==`marketplace.json` 버전 패리티 가드, CI starter-repo 가드, lint/ARCHITECTURE/CONVENTIONS 문서를 검증기(2-tier subject·lint 3a-3k) 와 일치. C-level 스키마 변경은 없음. |
| 0.8.1 | `/naite care` 품질 계약 강화 (patch, 기능·스키마 변경 없음). Sweep: 대량 삭제·압축을 기계 정규화와 의미 편집으로 분리하고 비-빈 줄 불변량 diff 로 무손실을 증명하도록 의무화. Repair: 최소침습 우선, scope 밖 결함은 defer, 구조 수술은 무손실 증명 동반 시에만. System Learning: enum/schema 전체 불일치(수선)와 의도된 subset(유지)을 구별. |
| 0.8.2 | 앱과 버전 라인 동기화 (하네스 기능·스키마 변경 없음) |
| 0.8.3 | 앱과 버전 라인 동기화 (하네스 기능·스키마 변경 없음). 분리 규약 이전의 마지막 동기화 릴리스. |
| 0.8.4 | 응답 출력 규약 강화 (patch). `SOUL.md § 응답 스타일` + `ask.md`: 적극적 구조화(두 단락 넘으면 H태그, 식별자 인라인 코드, 표·목록), 핵심 한 가지 콜아웃 승격(답변당 1~2개), 인용·참조는 문장 끝 고정(문장을 인용으로 시작하지 않음). |
| 0.8.5 | 버전 규약 변경 (patch): 앱과 하네스 버전 라인 분리 (2026-07-10 사용자 결정). 하네스는 하네스 변경으로만 릴리스하고, 호환성은 `min-harness-version` 계약으로 판단. |
| 0.8.6 | 응답 voice 규약 강화 (patch). 메타 프리앰블 금지: "이제 답하겠습니다"·"좋은 질문입니다" 같은 사고·전환 문장을 본문에서 배제하고 첫 문장을 곧장 결론으로 시작 (`SOUL.md § 응답 스타일` + `ask.md`). 시의성 질문(최신·오늘 기준·현재 버전)은 나무·학습지식 대신 웹 검색을 먼저 조회하고, 웹에서 가져온 내용은 tree 밖 정보로 구분. 데이터 안전: 새 page workflow 는 `domains` cache 를 `subject` 와 함께 도출하고, `care --check` 는 stale domain cache·BOM을 보고만 하며, 쓰기 플래그는 사용자 승인 후 `care` Repair 모드에서만 실행. 스키마 변경 없음. |

### v0.8.6 vault migration

`V_old <= 0.8.5` 에서 `V_new >= 0.8.6` 으로 올릴 때 `.naite/ontology/subject-tree.md` 의 `Cached domains derivation` 운영 문구를 확인한다. 기존 stock 문구가 care-check 의 자동 갱신과 `--refresh-domains` 직접 실행을 안내하면, 다음 계약으로 바꾸는 text-only vault migration 을 계획한다.

- 새 page workflow 가 `subject` path 의 top-level 에서 `domains` cache 를 기계적으로 도출해 함께 작성한다.
- `care --check` 는 stale cache 를 보고만 한다.
- 실제 갱신은 사용자 승인 후 `/naite care` Repair 모드에서만 실행한다.

이 migration 은 `.naite/ontology/subject-tree.md` 의 해당 설명 문단만 대상으로 하며 taxonomy YAML 과 `tree/**` 는 쓰지 않는다. 적용 전 exact diff 를 보여 주고 승인을 받는다. 문구가 사용자 커스텀 상태면 파일을 덮어쓰지 말고 위 세 문장만 반영하는 3-way 수동 병합안을 제시한다. 적용 후 care-check 를 실행해 stale cache 를 보고하되, 그 실행에서 `--refresh-domains` 를 안내하거나 실행하지 않는다.
