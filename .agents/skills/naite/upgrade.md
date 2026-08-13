# /naite upgrade — 하네스 갱신과 vault migration

`/naite upgrade` 는 설치된 naite 하네스(작업 틀)를 upstream 최신 릴리스로 올리고, 새 하네스가 요구하는 vault schema migration 이 있으면 계획과 승인과 적용까지 진행한다. 업데이트의 주 채널은 git 머지가 아니라 이 스킬이다. 사용자에게 충돌 해결을 떠넘기지 않는다.

upstream: `https://github.com/daehyeonxyz/naite-personal-memory`

## 경계

- 소스 경로의 내용은 절대 다시 쓰지 않는다: `roots/**`.
  - migration 은 기존 naite 워크플로가 이미 소유한 staging 파일만, 그것도 사용자의 명시적 확인 후에만 이동하거나 삭제할 수 있다.
- vault 경로는 하네스 upgrade 중에 자동 교체하지 않는다: `tree/**` 와 `.naite/ontology/**` 와 `.naite/reports/**`.
  - 이 경로들은 사용자 vault 의 상태다. 아래의 별도 vault migration 단계에서 preview 와 명시적 승인을 거친 뒤에만 바뀔 수 있다.
- upgrade 의 유일한 대상은 하네스 경로다.
  - 정확한 파일 집합은 `.naite/scripts/build-harness-lock.py` 가 정의한다 (루트 진입점과 정책 파일 `AGENTS.md`·`AGENTS.md`·`SOUL.md`·`README.md`·`LICENSE`·`.gitignore`, 두 스킬 표면, `.claude-plugin/**`, `docs/**`, `.naite/scripts/**`, `.naite/templates/**`, `.naite/hooks/**`)과 `.naite/harness-lock.json` 자신이다.
  - 이 집합의 단일 소스는 그 스크립트다.
- 하네스 디렉터리 안의 사용자 생성 파일(예: 사용자가 `.agents/skills/` 아래에 추가한 커스텀 스킬)은 lock 에도 새 릴리스에도 없다. 건드리지 않고 둔다.
- 파괴적 단계(파일 삭제, 경로 이동)는 migration 노트가 요구하더라도 항상 사용자의 명시적 확인을 받는다.
- push 는 하지 않는다. 커밋은 이 스킬의 일부이고, push 는 이 vault 가 이미 쓰는 흐름을 따른다.
- 편집 전에 무관한 dirty 파일이 있으면 먼저 분류한다. upgrade 범위 밖의 사용자 변경을 덮어쓰거나 staging 하지 않는다.

## Workflow

### 1. 버전 확정

1. `<NAITE_ROOT>/.naite/harness-lock.json` 을 읽어 설치된 버전 `V_old` 와 파일별 `sha256` 지도를 얻는다.
   - lock 이 없으면 이 vault 가 upgrade 체계 이전에 만들어졌다고 알리고 부트스트랩을 제안한다. 부트스트랩에서는 모든 하네스 파일을 "커스터마이즈됨"으로 취급한다 (자동 교체 없이 3-way 제안만).
2. `<NAITE_ROOT>/.claude-plugin/plugin.json` 의 `version` 을 읽어 lock 과 일치하는지 확인한다. 어긋나면 surface 하고 멈춘다.

### 2. upstream 가져오기

1. `git clone --depth 1 <upstream> <tmp>/naite-latest` 를 실행하고, 그 사본의 `.claude-plugin/plugin.json` 에서 새 버전 `V_new` 를 얻는다.
2. `V_new` 가 `V_old` 와 같으면 "이미 최신"이라고 보고하고 멈춘다.
3. 3-way 비교가 필요하면(4단계) base 도 가져온다: `git clone --depth 1 --branch v<V_old> <upstream> <tmp>/naite-base`.

### 3. 릴리스 노트와 migration 소스 수집

`(V_old, V_new]` 범위의 모든 버전에 대해 tag 가 존재하면 GitHub Release 본문을 가져온다 (`gh release view` 나 웹). 릴리스에는 기계적 단계를 담은 `## Migration` 절이 있을 수 있다. 접근 가능한 migration 노트를 버전 순서로 모은다. 중간 릴리스 일부가 없거나 접근 불가면 파일 비교와 최신 버전의 migration 소스로 계속 진행하고, 그 사실을 보고에 적는다.

migration 소스의 우선순위는 다음과 같다.

1. 접근 가능한 GitHub Release 의 `## Migration` 절.
2. 최신 릴리스의 `.naite/scripts/migrations/` 아래 버전별 스크립트 (있으면).
3. `docs/VERSIONING.md` 와 `docs/CONVENTIONS.md` 와 워크플로 파일의 명시적 migration 노트.

릴리스 노트의 산문은 지시로 취급하되, 이 vault 에 그 migration 이 필요하다는 증명으로 취급하지 않는다. 적용 여부는 현재 vault 상태에서 판정한다.

### 4. 모든 하네스 파일의 분류

hash 규칙: CRLF 를 LF 로 정규화한 파일 바이트의 sha256 이다. `build-harness-lock.py` 와 같은 규칙이다. raw 바이트를 비교하지 않는다. git 설정에서 온 줄 끝 차이는 커스터마이즈가 아니다.

lock 지도와 새 릴리스 하네스 집합의 합집합에 있는 각 파일을 다음 표로 분류한다.

| lock 대비 로컬 상태 | 새 릴리스에서 | 행동 |
|---|---|---|
| hash 가 lock 과 일치 (무수정) | 변경됨 | 새 버전으로 자동 교체한다 |
| hash 가 lock 과 일치 | 무변경 | 건너뛴다 |
| hash 가 다름 (사용자 커스터마이즈) | 변경됨 | 3-way 제안: base(`naite-base`)와 로컬과 신판을 보이고 병합안을 제안한다. 사용자가 고른다 |
| hash 가 다름 | 무변경 | 로컬을 유지한다 (보고에 적는다) |
| lock 에 없음 (사용자 추가 파일) | 없음 | 로컬을 그대로 둔다 |
| lock 에 있는데 로컬에서 삭제됨 | 무관 | 보고에 적고 복원을 제안한다 |
| 로컬과 lock 에 없음 | 릴리스의 새 파일 | 추가한다 |
| lock 에 있음 | 릴리스에서 제거됨 | 제거를 제안한다. 자동 삭제는 절대 하지 않는다 |

### 5. vault migration 계획

하네스 교체와 vault migration 을 분리한다.

`tree/**` 나 `.naite/ontology/**` 나 `.naite/reports/**` 나 `USER.md` 나 `MEMORY.md` 에 닿을 수 있는 모든 수집된 migration 단계에 대해 먼저 계획을 만든다.

- `from` 과 `to` 버전 범위.
- 이 migration 이 적용되는 이유나 적용되지 않는 이유.
- 읽게 될 파일.
- 쓰거나 이동하거나 삭제하게 될 파일.
- 그 단계가 결정론 스크립트 주도인지 LLM 작성인지.
- 롤백 경로. 보통 커밋 전에는 `git restore <path>` 이고 커밋 후에는 `git checkout HEAD~1 -- <path>` 다.
- migration 이 성공했음을 증명하는 검증 명령.

버전별 migration 스크립트가 dry-run 이나 plan 모드를 지원하면 그 모드를 먼저 실행한다. 지원하지 않으면 실행 전에 스크립트를 읽어 본다. 읽지 않은 migration 스크립트를 실제 vault 에 실행하는 일은 절대 없다.

### 6. 승인된 vault migration 의 적용

사용자가 승인한 migration 만 적용한다. "업그레이드하고 migration 전부 적용해" 같은 호출은 계획을 보인 뒤의 비파괴 migration 에 대한 승인으로 치지만, 파괴적 단계에는 여전히 별도의 승낙이 필요하다.

허용되는 vault migration 대상은 다음과 같다.

- `tree/**` 의 스키마 재작성과 frontmatter 재작성과 링크 재작성과 `tree/rings.md` 의 `migration` 항목 하나.
- `.naite/ontology/facets.json` 과 `.naite/ontology/subject-tree.md` 와 `.naite/ontology/topics.md`. 릴리스가 스키마나 어휘나 온톨로지 운영 계약의 migration 을 명시적으로 도입할 때만 해당한다.
- 생성 지도 `.naite/ontology/tree-manifest.json` 과 `.naite/ontology/tree-dependencies.json`. tree 나 ontology 변경 후에 재생성한다.
- 루트 `SOUL.md` 와 gitignore 된 `USER.md` 와 gitignore 된 `MEMORY.md`. 릴리스가 지시 표면을 도입하거나 바꿀 때 해당한다.
- 선택적 upgrade 보고를 위한 `.naite/reports/**`.

`roots/**` 의 내용은 손으로 편집하지 않는다. migration 이 소스를 tree 페이지로 변환하라고 요구하면 멈추고 `/naite grow` 나 `/naite care` 로 라우팅한다.

migration 적용 후에는 다음을 실행한다.

1. 페이지 좌표나 링크나 ontology 가 바뀌었으면 생성 지도를 재생성한다.
2. `python .naite/scripts/lint-ontology.py` 를 실행한다.
3. migration 전용 검증기가 있으면 실행한다.
4. staging 전에 바뀐 모든 vault 경로의 `git diff` 를 확인한다.

### 7. 마무리

1. Windows 에서는 `.naite/scripts/sync-agents.ps1` 을, macOS 와 Linux 에서는 `python .naite/scripts/sync-agents.py` 를 실행해서 `.agents/` 와 `AGENTS.md` 가 올라간 정본과 일치하게 만든다.
2. 4단계에서 이미 교체되지 않았다면 `.claude-plugin/plugin.json` 과 `.claude-plugin/marketplace.json`(`plugins[0].version`) 두 곳의 버전을 `V_new` 로 갱신한다. `build-harness-lock.py --check` 가 두 값의 일치를 검사한다.
3. lock 을 재생성한다: `python3 .naite/scripts/build-harness-lock.py`.
   > [!IMPORTANT]
   > 재생성된 lock 은 현재 로컬 하네스 파일을 hash 하는데, 여기에는 4단계에서 커스터마이즈 유지로 결정한 파일(3-way 의 "로컬 유지" 결과)이 포함된다. 그러면 lock 이 커스터마이즈된 hash 를 새 기준선으로 기록하게 되고, 다음 upgrade 가 그 파일을 "lock 대비 무수정"으로 분류해서 조용히 자동 교체하게 된다. 사용자가 지키기로 한 커스터마이즈가 지워지는 것이다. 이를 막기 위해, 커스터마이즈를 유지한 각 파일을 지속되는 목록(예: `MEMORY.md` 의 `## kept-customized` 블록)에 기록해서 미래의 upgrade 가 lock 과 무관하게 그 파일을 커스터마이즈된 것으로 취급하게 하고, 그 목록에 있는 하네스 파일을 자동 교체하기 전에는 항상 사용자에게 다시 확인한다. lock 은 앱 호환 버전 도장이지 커스터마이즈의 기준선이 아니다.
4. 정상 동작 확인: `python3 .naite/scripts/lint-ontology.py` 가 여전히 exit 0 이어야 한다 (upgrade 가 vault 를 깨면 안 된다).
5. `python .naite/scripts/build-harness-lock.py --check` 를 실행한다.
6. `<tmp>` clone 을 정리한다.

### 8. 기록과 커밋

1. `<NAITE_ROOT>/tree/rings.md` 에 기존 `migration` op 로 항목 하나를 덧붙인다.

```
## [YYYY-MM-DD] migration | naite harness v<V_old> → v<V_new>
- harness: auto-replaced <n> / merged with user edits <n> / added <n> / removal proposed <n>
- vault migrations: applied <n> / skipped <n> / deferred <n>
```

2. 커밋은 하나로 한다: `chore: upgrade naite harness v<V_old> -> v<V_new>`.

### 9. 보고 (한국어, `SOUL.md` 응답 스타일 절)

- 결과: 버전 이동, 자동 교체·병합·추가·제거 제안 파일 수, 적용한 vault migration 단계.
- 안 한 것: 사용자 커스텀이라 보존한 파일, 보류된 파괴적 단계.
- 다음에 할 수 있는 것: 보류 항목의 처리 방법.

## rings op

`migration` 을 쓴다 (기존 어휘다. 새 op 를 발명하지 않는다).
