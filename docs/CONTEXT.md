# docs/CONTEXT.md — naite 컨텍스트 라우팅

## 개요

- 정의: 이 파일은 에이전트가 무엇을 먼저 로드하고, 무엇을 필요할 때만 로드하고, 소스가 많은 작업을 언제 Reader·Writer·Verifier 역할로 분리해야 하는지를 정의한다.

- 지위: 이 파일은 운영 계약이다.
  - 스키마 설계 근거는 `docs/ARCHITECTURE.md` 가, 변경 정책은 `docs/CONVENTIONS.md` 가, 워크플로 절차는 `.claude/skills/naite/*.md` 와 `.agents/skills/naite/*.md` 가 담당한다.

## 목적

나무가 커지면 "중요한 파일을 전부 읽는다"는 접근이 실패 요인이 된다. 컨텍스트는 역할별로 들여야 한다.

1. 권위: 무엇이 허용되는지를 정하는 규칙이다.
2. 절차: 지금 켜져 있는 워크플로 계약이다.
3. 지도: 관련 페이지를 빠르게 찾아 주는 압축 생성 색인이다.
4. 증거: 이 작업에 필요한 특정 소스 파일과 tree 페이지다.
5. 검증: 편집 후에 실행하는 결정론 검사와 의존성 리뷰다.

에이전트는 작업을 안전하게 결정할 수 있는 최소 집합을 먼저 로드하고, 켜진 워크플로나 증거가 요구할 때만 로드 범위를 넓힌다.

## 기반 문서

| 역할 | 파일 |
|---|---|
| Claude bootloader | `CLAUDE.md` |
| Codex bootloader | `AGENTS.md` |
| 에이전트 정체성·persona | `SOUL.md` |
| 사용자 선호 | `USER.md` (양식 `.naite/templates/USER.md`) |
| 운영 기억 | `MEMORY.md` (양식 `.naite/templates/MEMORY.md`) |
| 컨텍스트 라우팅 | `docs/CONTEXT.md` |
| 변경 불변식 | `docs/CONVENTIONS.md` |
| 설계 근거 | `docs/ARCHITECTURE.md` |
| 출력 품질 기준 | `docs/QUALITY.md` |
| subject 분류 체계 | `.naite/ontology/subject-tree.md` |
| topic 어휘 | `.naite/ontology/topics.md` |
| 에이전트 페이지 맵 | `.naite/ontology/tree-manifest.json` |
| 에이전트 의존성 맵 | `.naite/ontology/tree-dependencies.json` |
| Claude 워크플로 계약 | `.claude/skills/naite/*.md` |
| Codex 워크플로 계약 | `.agents/skills/naite/*.md` |
| 사람용 대문 페이지 | `tree/trunk.md` |
| 반영 이력 | `tree/rings.md` |
| 미작성 페이지 대장 | `tree/seeds.md` |

`.naite/ontology/tree-manifest.json` 과 `.naite/ontology/tree-dependencies.json` 은 압축된 생성 지도다. 에이전트가 빠른 진입 컨텍스트로 쓰기 때문에 git 으로 추적하지만, 손으로는 편집하지 않는다. 재생성은 `.naite/scripts/` 의 스크립트가 담당한다.

## 기본 로딩 순서

1. bootloader 와 지시 표면: 켜진 표면의 `CLAUDE.md` 나 `AGENTS.md` 를 읽고, `SOUL.md` 는 항상, `USER.md` 와 `MEMORY.md` 는 있으면 읽는다. 상세는 `docs/CONVENTIONS.md` 의 Instruction surfaces 절에 정리되어 있다.
2. 의도 분류: 사용자 요청을 워크플로나 무변경 답변으로 분류한다.
3. 컨텍스트 계약: 작업이 tree 변경이나 tree 조회나 컨텍스트 선택이나 라우팅이나 care 나 care-check 에 해당하면 이 파일을 읽는다.
4. 변경 권위: tree 를 바꾸는 모든 작업 전에 `docs/CONVENTIONS.md` 를 읽는다.
5. 워크플로 절차: 켜진 표면 아래의 정확한 워크플로 파일을 읽는다. 예를 들어 `.claude/skills/naite/grow-branch.md` 나 `.agents/skills/naite/care.md` 다.
6. 생성 지도: 대상 페이지를 찾기 전에 `.naite/ontology/tree-manifest.json` 을 조회하고, 기존 페이지를 바꾸거나 의미 의존 페이지를 리뷰하기 전에 `.naite/ontology/tree-dependencies.json` 을 조회한다.
7. 지역 증거: 이 작업이 요구하는 소스 파일과 tree 페이지와 ontology 절과 최근 rings 항목만 읽는다.
8. 검증: 편집 후에 관련 결정론 스크립트를 실행하고, 페이지 좌표나 링크가 바뀌었으면 생성 지도를 재생성한다.

첫 세션에서는 `/naite start` 가 `.claude/skills/naite/start.md` 를 따르고, 기억 내보내기 수입과 첫 나무 구축의 안내에는 `docs/QUALITY.md` 와 `docs/migrate-prompt.md` 를 참조한다.

`tree/trunk.md` 는 사람이 보는 큐레이션된 대문 페이지이고, domain 과 hub 페이지와 한 줄 요약의 지도다. 방향을 잡을 때는 trunk 를 읽되, trunk 는 전체 페이지 색인이 아니다. 전체 색인은 `.naite/ontology/tree-manifest.json` 이 담당하고, 이 지도가 모든 페이지의 좌표와 별칭과 heading 을 담고 있다. subject 구조나 domain 별 개수가 필요하거나 후보 페이지를 찾아야 하면 manifest 를 조회한 뒤, manifest 가 가리킨 tree 페이지를 읽는다.

> [!IMPORTANT]
> 생성 지도는 vault 와 함께 커진다. `tree-manifest.json` 은 페이지 3,000장 근처에서 1MB 를 넘고, `tree-dependencies.json` 은 500장 이전에 1MB 를 넘으며, 두 파일 다 한 줄로 기록된다. 큰 지도를 통째로 Read 하면 잘려서 쓸모가 없어진다. slug 나 별칭을 `grep` 으로 찾거나 `jq` 로 필드를 조회해서 걸러 낸 조각만 읽어야 한다. "검색 전에 manifest 를 읽는다"는 조회하라는 뜻이지 통째로 컨텍스트에 올리라는 뜻이 아니다.

## 워크플로별 컨텍스트 표

| 워크플로 | 항상 로드 | 필요할 때 로드 |
|---|---|---|
| `/naite start` | bootloader, `docs/CONTEXT.md`, `docs/CONVENTIONS.md`, 켜진 `start.md`, `docs/QUALITY.md`, `docs/migrate-prompt.md`, `.naite/ontology/tree-manifest.json` | `.naite/ontology/subject-tree.md`, `.naite/ontology/topics.md`, `roots/conversations/` 의 붙여넣은 기억 내보내기 (+ `roots/conversations/_transcripts/`) |
| `/naite ask` | bootloader, `docs/CONTEXT.md`, `tree/trunk.md` | subject 구조나 domain 별 개수가 필요할 때의 `.naite/ontology/tree-manifest.json`, `.naite/ontology/tree-dependencies.json`, 대상 페이지 본문, 타임라인 질문에서의 `tree/rings.md` |
| `/naite grow` (단발: 대화·파일·stage 한정) | bootloader, `docs/CONTEXT.md`, `docs/CONVENTIONS.md`, 켜진 `grow.md` (+ 내부 `ingest.md`·`capture.md`), `.naite/ontology/tree-manifest.json`, `tree/trunk.md`, `tree/seeds.md`, 최근 `tree/rings.md` | `.naite/ontology/subject-tree.md`, `.naite/ontology/topics.md`, `.naite/ontology/tree-dependencies.json`, 소스 파일 |
| `/naite grow` (branch 모드) | bootloader, `docs/CONTEXT.md`, `docs/CONVENTIONS.md`, 켜진 `grow-branch.md`, `.naite/ontology/tree-manifest.json`, `tree/trunk.md`, 최근 `tree/rings.md` | `.naite/ontology/subject-tree.md`, `.naite/ontology/topics.md`, `.naite/ontology/tree-dependencies.json`, 과목 소스 파일, 이전 과목 페이지 |
| `/naite fruit` | bootloader, `docs/CONTEXT.md`, `docs/CONVENTIONS.md`, 켜진 `fruit.md`, `tree/trunk.md`, `.naite/ontology/subject-tree.md`, `.naite/ontology/topics.md`, 최근 `tree/rings.md` | 교차 링크와 양방향 산문 리뷰에서의 `.naite/ontology/tree-dependencies.json`, 대상 decision 페이지, 관련 concept 페이지, 스키마 근거가 필요할 때만 `docs/ARCHITECTURE.md` |
| `/naite care` / `care --check` | bootloader, `docs/CONTEXT.md`, `docs/CONVENTIONS.md`, 켜진 `care.md` 나 `care-check.md`, 생성 지도 | 스크립트, ontology 파일, 대상 페이지, inbound 의존 페이지, `tree/rings.md`, `tree/seeds.md`, 결함이 반복될 때의 생산자 워크플로 파일 |
| `/naite upgrade` | bootloader, 켜진 `upgrade.md`, `.naite/harness-lock.json`, `.claude-plugin/plugin.json`, vault migration 이 tree 나 ontology 파일에 닿을 수 있을 때의 `docs/CONVENTIONS.md` | upstream clone (latest 와 base tag), 릴리스 노트, 3-way 제안을 위한 커스터마이즈된 하네스 파일, 버전별 migration 스크립트, 생성 지도, `tree/rings.md`, 지시 표면이 바뀌었을 때의 `SOUL.md`·`USER.md`·`MEMORY.md` |
| 스키마·워크플로 재설계 | bootloader, `docs/CONTEXT.md`, `docs/CONVENTIONS.md`, `docs/ARCHITECTURE.md`, 관련 워크플로 파일 | decision 페이지, 검증 스크립트, 미러 sync 스크립트 |

## Reader·Writer·Verifier 분리

도구 표면이 서브에이전트를 지원하고 사용자가 에이전트 위임을 허용했으면 별도 에이전트로 분리한다. 물리적 서브에이전트를 쓸 수 없으면 같은 역할을 한 세션 안의 순차 단계로 유지한다.

### 분리 조건

아래 중 하나라도 해당하면 분리를 적용한다.

- 소스가 길거나 밀도가 높거나 여러 파일에 걸쳐 있다.
- PDF 나 전사본이나 강의 묶음이나 디렉터리 단위 반영이 포함되어 있다.
- 워크플로가 엄격한 출력 계약을 갖고 있다. 특히 `/naite grow` branch 모드와 파일 반영과 `/naite fruit` 가 해당한다.
- tree 페이지 다섯 장 이상이 바뀔 수 있다.
- ontology 선택이 모호하다.
- inbound 의존이 있는 기존 페이지가 바뀔 수 있다.

### Reader 역할

- Reader 는 소스 자료와 최소한의 작업 맥락을 받는다.
- Reader 는 주장과 개념과 예시와 수식과 도식과 용어와 wikilink 후보와 불확실한 부분을 추출한다.
- Reader 는 `tree/*.md` 를 쓰지 않고, 최종 frontmatter 를 정하지 않고, `.naite/ontology/` 를 바꾸지 않는다.
- Reader 의 출력은 다음을 담은 압축 원료 덩어리여야 한다.
  - 소스 단위의 식별 정보.
  - 핵심 주장.
  - 재사용 가능한 개념 후보.
  - 예시와 수식.
  - 용어와 별칭.
  - 질문이나 모호한 부분.
  - 명백할 때의 기존 tree 링크 제안.

### Writer 역할

- Writer 는 Reader 의 덩어리와 `docs/CONVENTIONS.md` 와 켜진 워크플로 파일과 생성 지도와 관련 ontology 파일을 받는다.
- Writer 는 워크플로 계약에 따라 tree 페이지를 쓰거나 갱신한다.
- Writer 는 Reader 덩어리가 부족하거나 워크플로가 정확한 대조를 요구하는 경우가 아니면 원본 소스를 다시 통째로 로드하지 않는다.

### Verifier 역할

- Verifier 는 바뀐 페이지를 다음 기준과 대조한다.
  - frontmatter 계약.
  - 출력 품질 계약.
  - 링크의 유용성.
  - Source 블록의 배치.
  - `tree/rings.md` 규칙.
  - 생성 manifest 의 최신성.
  - 의존성 지도의 inbound 후보.
- Verifier 는 의미 의존 페이지를 리뷰 대상으로 surface 한다.
  - 켜진 워크플로와 사용자 요청이 수리를 허용하지 않는 한, 의존 페이지를 자동으로 다시 쓰지 않는다.

## 생성 지도 정책

### `.naite/ontology/tree-manifest.json`

- 빌드 명령:

```powershell
python .naite/scripts/build-tree-manifest.py
```

- 용도: slug 직접 조회, `kind`·`form`·`topics`·`subject`·`source-types`·`domains` 좌표 조회, 본문을 읽기 전의 후보 좁히기, trunk 드리프트와 hub 후보 탐지를 지원한다.
- 이 지도는 의도적으로 압축되어 있다. 페이지 좌표와 제목과 별칭만 담고 본문은 담지 않는다.
- 재생성 시점: tree 페이지가 생성·삭제·개명됐을 때, frontmatter 가 바뀌었을 때, 제목이나 별칭 절이 바뀌었을 때, 워크플로가 새 검색 지도를 요구할 때다.

### `.naite/ontology/tree-dependencies.json`

- 빌드 명령:

```powershell
python .naite/scripts/build-tree-dependencies.py
```

- 용도: inbound wikilink 조회, outbound 의존 조회, soft relation 관용구 조회, 편집 후 의미 의존 후보 surface, 고연결 페이지와 orphan 탐지를 지원한다.
- 이 지도는 의도적으로 slug 수준이다. 어느 페이지가 어느 slug 를 가리키는지와 어떤 soft relation 관용구가 나타나는지만 담고 전체 줄 텍스트는 담지 않는다.
- 재생성 시점: tree 페이지 본문이 바뀌었을 때, wikilink 가 바뀌었을 때, soft ontology 관용구가 바뀌었을 때, 워크플로가 의존 전파 리뷰를 요구할 때다.

## 의존 전파 정책

모든 의존이 자동 편집을 일으켜야 하는 것은 아니다. 의존은 세 수준으로 나뉜다.

| 수준 | 예 | 행동 |
|---|---|---|
| 하드 의존 | `CLAUDE.md` 와 `AGENTS.md`, `.claude/skills/naite/*` 와 `.agents/skills/naite/*` | Windows 에서는 `.naite/scripts/sync-agents.ps1` 로, macOS 와 Linux 에서는 `python .naite/scripts/sync-agents.py` 로 sync 한다 |
| 계약 의존 | `docs/CONVENTIONS.md` 변경이 워크플로 파일이나 검증 스크립트에 영향을 줄 때 | 영향을 받는 계약과 검증기를 같은 변경 안에서 갱신한다 |
| 의미 의존 | concept·decision·source-record 내용 변경이 링크된 페이지에 영향을 줄 때 | `.naite/ontology/tree-dependencies.json` 에서 후보를 surface 하고, 요청이 있을 때만 `/naite care` 로 수리한다 |

Python 스크립트가 후보를 찾고 LLM 이 의미를 판단한다. inbound edge 가 있다는 이유만으로 의미 편집을 자동 전파하지 않는다.

## 검증 체크리스트

운영 문서나 워크플로 파일을 바꿨을 때는 다음 순서로 검증한다.

1. 정본 `.claude/` 와 루트 공유 파일을 먼저 갱신한다.
2. `.claude/` 나 `CLAUDE.md` 가 바뀌었으면 Windows 에서는 `.naite/scripts/sync-agents.ps1` 을, macOS 와 Linux 에서는 `python .naite/scripts/sync-agents.py` 를 실행한다.
3. tree 페이지 좌표나 링크가 바뀌었으면 생성 지도를 재생성한다.
4. 관련 결정론 스크립트를 실행한다.
5. staging 전에 `git diff` 를 리뷰한다.

tree 페이지를 바꿨을 때는 다음 순서로 검증한다.

1. `/naite care` 의 content guard 를 실행한다.
2. 페이지 좌표가 바뀌었으면 `python .naite/scripts/build-tree-manifest.py` 를 실행한다.
3. wikilink 나 본문 관계가 바뀌었으면 `python .naite/scripts/build-tree-dependencies.py` 를 실행한다.
4. 바뀐 slug 의 inbound 의존 페이지를 점검한다.
5. 완료를 주장하기 전에 관련 care-check 를 실행한다.

## 검증 무효화와 완료 규율

검증은 안정된 스냅샷과 명시된 범위에 결부된다. 한 번 통과한 검사는 다른 곳에서 작업이 이어졌다는 이유만으로 무효가 되지 않는다. 그 검사가 소유한 파일이나 생성 의존물이나 주장을 나중의 편집이 바꿨을 때만 무효가 된다.

### 무효화 표

| 나중의 변경 | 다시 실행할 것 | 유효하게 유지되는 것 |
|---|---|---|
| 보고서의 문구·수치·링크만 변경 | 보고서 산술과 링크 해석, `git diff --check` | tree 내용 리뷰, ontology lint, 지도, 하네스 테스트 |
| tree 산문이나 끝의 Source 경로만 변경 | 바뀐 페이지의 content guard, 해당할 때 Source 존재 확인, ontology lint, `git diff --check` | manifest, wikilink 와 soft relation 관용구가 안 바뀌었을 때의 의존성 지도, 무관한 리뷰 |
| frontmatter·제목·별칭 변경 | ontology lint, tree manifest, 영향 범위 산정, `git diff --check` | 본문 관계가 안 바뀌었을 때의 의존성 지도 |
| wikilink 나 soft relation 관용구 변경 | 바뀐 페이지의 guard, 의존성 지도, 영향받는 inbound 리뷰, ontology lint, `git diff --check` | 좌표와 제목과 별칭이 안 바뀌었을 때의 manifest |
| 정본 워크플로나 운영 계약 변경 | Claude 에서 Codex 로의 미러 sync, 미러 의미 리뷰, 직접 관련된 워크플로 검사, `git diff --check` | 계약 편집이 tree 파일을 함께 바꾸지 않았을 때의 tree 지도와 내용 리뷰 |
| 검증기·guard·테스트·harness-lock 입력 변경 | 명시된 테스트 경로, 해당할 때 정상 CLI 경로와 무효 입력 경로 각 하나, harness lock 재생성과 검사, `git diff --check` | 입력이 안 바뀌었을 때의 tree 내용 리뷰와 생성 지도 |
| 생성 산출물만 변경 | 그 산출물의 문서화된 생산자와 의미 재현 검사, `git diff --check` | 무관한 검증기와 리뷰 |

한 편집이 여러 행에 걸치면 그 행들이 요구하는 검사의 합집합을 실행한다. 저장소의 모든 검사를 합집합으로 잡지는 않는다.

### 안정 스냅샷 리뷰 계약

- 최종 리뷰 전에 리뷰 대상 파일 집합을 기록하거나 특정한다. 커밋된 작업에는 커밋 SHA 가 이상적이고, dirty 워크트리에서는 정확한 변경 파일 집합을 쓰고 리뷰 중에 그 집합이 안 바뀌었는지 확인한다.
- PASS 는 그 검사가 소유한 파일과 의존물이 그대로인 동안 유효하다. 영향받은 lane 하나만 다시 실행하고 전체 리뷰 스택을 다시 돌리지 않는다.
- 읽기 전용 verifier 는 파일을 편집하지 않고 생성기를 실행하지 않는다. `--check` 나 `--dry-run` 이나 `--help` 모드를 짐작으로 쓰기 전에 그 명령의 문서화된 동작을 확인한다.
- blocking 판정은 재현 가능하고 요청된 결과나 안전 불변식을 막는 결함에만 적용한다. 파일과 줄과 기대 상태와 실제 상태와 재현 증거와 최소 수리 경계를 보고한다.
- 개선 아이디어와 문체 선호와 알려진 과거 부채와 무관한 dirty 파일은 요청된 결과를 무효화하지 않는 한 잔여 사항이다. 비밀과 데이터 손실 위험은 범위와 무관하게 blocking 이다.

### 완료 게이트

적용되는 조건이 전부 성립하면 실행을 멈춘다.

1. 요청된 모든 산출물이 의도된 위치에 존재한다.
2. 대장이나 전수 조사가 요구될 때 범위 산정이 정확하다. 누락과 중복과 잘못된 소유자가 없다.
3. 마지막 편집이 무효화한 모든 검사가 통과했다.
4. 요청된 변경에 대해 `git diff --check` 가 통과했다.
5. staging 과 커밋과 push 와 그 밖의 외부 행동이 사용자의 허가 범위와 일치한다.
6. 무관한 사용자 작업이 건드려지지 않았다.
7. 재현 가능한 blocker 가 남아 있지 않다.

게이트가 통과하면 결과를 보고하고 멈춘다. 사용자가 새 범위를 열지 않는 한 새 감사나 정리나 리팩터링이나 선택적 개선을 추가하지 않는다.
