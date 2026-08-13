---
name: naite
description: LLM 이 관리하는 개인 지식 나무인 naite vault 를 유지한다. start, grow, ask, fruit, care, upgrade 의 디스패처다. /naite 뒤에 하위 명령 이름을 붙여 호출한다.
---

# /naite — 디스패처

이 스킬을 받은 에이전트는 naite vault 를 유지한다. vault 하나가 나무 한 그루다. 사용자가 소스를 더하고 질문하면, 에이전트가 사용자 소유의 Markdown 페이지를 읽고 쓰고 연결한다. 이 스킬은 어느 작업 디렉터리에서든 호출될 수 있으므로, 경로는 항상 아래 위치 기준으로 해석하고 현재 CWD 기준으로 해석하지 않는다.

## 고정 경로

- `NAITE_ROOT`: naite vault 의 루트다. 다음 순서로 해석한다.
  1. `AGENTS.md` 와 `tree/` 와 `roots/` 를 함께 담은 가장 가까운 디렉터리 (CWD 부터 상위로).
  2. 없으면 `~/.naite/root` 에 적힌 절대 경로. 이 파일은 파워 유저가 한 번 적어 두는 한 줄짜리 전역 포인터이고, `/naite` 가 어느 작업 디렉터리에서든 vault 를 찾게 해 준다. 가리킨 디렉터리가 실제로 `AGENTS.md` 와 `tree/` 와 `roots/` 를 담고 있는지 확인하고, 낡았으면 조용히 실패하는 대신 낡았다고 말한다.
  - 모든 데이터 경로는 `NAITE_ROOT` 기준으로 해석한다.

- `SKILL_DIR`: `<NAITE_ROOT>/.agents/skills/naite` 다. 이 스킬과 하위 파일이 위치한다.
  - 설치된 플러그인으로 돌 때는 `~/.naite/root` 포인터가 junction 이나 심링크를 불필요하게 만든다. 이 디렉터리를 `~/.agents/skills/naite` 로 링크하는 방식은 플러그인 없는 환경을 위한 legacy 패턴으로 지원된다.

- `HARNESS_SRC`: 이 파일의 위치에서 세 단계 위의 디렉터리다 (이 SKILL.md 를 담은 폴더 기준 `../../..`).
  - clone 된 vault 에서는 `NAITE_ROOT` 자신이다.
  - 설치된 Codex 플러그인으로 돌 때는 starter repo 의 플러그인 캐시 사본이고, 전체 뼈대(`AGENTS.md`, `SOUL.md`, `docs/`, `.naite/`, `tree/`, `roots/`, 두 스킬 표면)를 담고 있다.

`NAITE_ROOT` 를 찾지 못한 경우(CWD 상위에 vault 가 없고 `~/.naite/root` 포인터도 없는, 플러그인만 설치한 직후의 전형적 상태)에도 실패로 처리하지 않는다.

- `start` 는 그대로 진행한다. start 의 0절이 `HARNESS_SRC` 의 뼈대를 복사해서 CWD 에 vault 를 만든다. 부트스트랩 후에는 새 vault 의 절대 경로를 `~/.naite/root` 에 적어 두자고 제안한다. 사용자가 승낙할 때만 쓴다.
- 다른 모든 하위 명령에서는 vault 를 찾지 못했다고 알리고 `/naite start` 를 제안한다. 사용자가 이미 다른 곳에 vault 를 갖고 있으면 그곳을 가리키는 `~/.naite/root` 작성을 제안한다.

모든 호출의 첫 행동은 `<NAITE_ROOT>/AGENTS.md` 전문 읽기다 (부트스트랩 직후라면 0절이 방금 만든 파일을 읽는다). ask 와 care 와 grow 와 fruit 와 모든 tree 변경에서는 증거 파일을 고르기 전에 `<NAITE_ROOT>/docs/CONTEXT.md` 도 읽는다.

현재 CWD 가 이미 `NAITE_ROOT` 이거나 그 하위면 CWD 상대 경로로 동작해도 된다. 그 밖에는 절대 경로를 쓰고, 애매하면 절대 경로를 쓴다. 이 스킬이 플러그인 캐시에서 돌 때도 하위 스킬 파일(`<SKILL_DIR>/*.md`)은 vault 사본이 존재하는 한 vault 쪽에서 해석한다. vault 자신의 하네스가 사용자가 커스터마이즈했을 수 있는 계약이기 때문이다. `HARNESS_SRC` 폴백은 부트스트랩 전에만 쓴다.

## Dispatch

사용자는 `/naite <subcommand> [args]` 로 호출한다. `args` 의 첫 토큰을 하위 명령으로 파싱한다.

| 하위 명령 | 사용 시점 | 로드 |
|------------|-------------|------|
| `start` | 첫 세션 안내다. 신규 사용자가 자기 기억을 import 해서 `/naite grow` 흐름으로 첫 나무를 짓고 그래프로 본다. 1회성 온보딩 진입점이고 이후는 grow 로 간다 | `<SKILL_DIR>/start.md` |
| `grow [args?]` | 나무를 키운다. 학습·자료 반영의 단일 진입점이다. 대화 마무리와 파일·디렉터리 첨부와 장기 과정(과목·책·시리즈 = branch)과 backfill 과 소스만 던져진 경우(받아두기)를 자동 감지해서 분기한다 | `<SKILL_DIR>/grow.md` |
| `ask <question>` | 나무에게 묻는다. 쌓인 tree 에서 답을 합성하고, 가치가 있으면 페이지로 남길지 제안한다 | `<SKILL_DIR>/ask.md` |
| `fruit [topic?]` | 열매를 맺는다. 결정과 trade-off 와 실패 분석을 `kind=decision` 페이지로 기록하는 dialogue scaffold 다. 대화 중 결정 패턴이 감지되면 에이전트가 먼저 제안한다 | `<SKILL_DIR>/fruit.md` |
| `care [scope?]` | 나무를 돌본다. `--check`(report-only 점검, secrets 차단 게이트)와 돌봄(검토·수선·대규모 정리) 두 모드로 나뉜다 | `<SKILL_DIR>/care.md` |
| `upgrade` | 하네스를 올린다. upstream 최신 릴리스로 작업 틀을 갱신하고, 필요한 vault schema migration 은 preview 와 승인 뒤에 적용한다. 사용자 커스텀 파일은 3-way 제안으로 보존한다 | `<SKILL_DIR>/upgrade.md` |

`<SKILL_DIR>` 는 `<NAITE_ROOT>/.agents/skills/naite` 다. 읽을 때 치환한다.

구현 모듈은 디스패처가 로드하는 파일이지 top-level `/naite` 명령이 아니다.

| 사용자 진입 | 내부 모듈 | 역할 |
|---|---|---|
| 새 대화를 받은 `/naite grow` | `capture.md` 다음 `ingest.md` | capture 가 claim 요약과 전사본을 `roots/conversations/` 에 staging 하고, ingest 가 승인된 소스를 `tree/` 로 접는다 |
| `/naite grow <path>` | `ingest.md` | `roots/` 아래의 raw 소스 하나를 연결된 tree 페이지로 만든다 |
| branch 신호를 받은 `/naite grow` | `grow-branch.md` | 진행 중인 장기 과정(과목·책·시리즈) 작업을 담당한다 |
| `/naite grow backfill <slug>` | `grow-backfill.md` | 이미 끝난 과목·아카이브를 dialogue 없이 보강한다 |
| `/naite care --check` | `care-check.md` | care 를 거쳐 로드되는 report-only 건강 점검이다 |

`/naite capture` 와 `/naite ingest` 를 사용자에게 안내하지 않는다. 그 이름들은 구현용이다.

## 실행 방법

> 빈 vault 노트: `grow` 는 진입 시점에 `tree/` 에 일반 페이지가 없으면 `/naite start` 를 먼저 제안한다. 사용자가 거절하면 grow 를 정상 진행한다.

1. `args` 에서 하위 명령을 파싱한다. 없거나 인식되지 않으면 위 표를 보여 주고 어느 하위 명령인지 사용자에게 묻는다.
2. 이 세션에서 아직 안 읽었으면 `<NAITE_ROOT>/AGENTS.md` 를 읽는다.
3. 하위 명령이 tree 컨텍스트나 생성 지도나 의존성 리뷰나 변경을 요구하면 `<NAITE_ROOT>/docs/CONTEXT.md` 를 읽는다.
4. 해당 하위 스킬 파일을 Read 도구로 읽는다 (절대 경로 사용).
5. 그 워크플로를 그대로 따른다. 단계를 의역하거나 즉흥으로 바꾸지 않는다. 하위 파일이 계약이다.
6. 성공한 모든 하위 명령은(기록 없는 ask 제외) `<NAITE_ROOT>/tree/rings.md` 에 `## [YYYY-MM-DD] <op> | <title>` prefix 로 한 줄을 덧붙인다.

## 공유 규칙 (위반 금지)

- `roots/` 는 content-immutable 이다.
  - `roots/` 아래 파일의 내용을 절대 바꾸지 않는다. 범용 `_archive/` 층은 없다. 하위 폴더별 규칙은 `docs/CONVENTIONS.md` 의 grow 이후 처리 절이 담당한다.
  - 요약하면 `roots/articles/` 파일은 grow 후에도 제자리에 있고, `roots/conversations/` 의 claim 요약은 grow 후 삭제되고(`_transcripts/` 의 전사본은 보존), `roots/courses/{slug}/` 는 `branch-finish` 시점에만 `roots/courses/_archive/{slug}/` 로 통째 이동한다 (vault 의 유일한 `_archive/` 경로다).
  - 내용 쓰기의 예외는 두 가지다. legacy import 가 staged 사본에 번역 주석을 더하는 것과, grow 가 `roots/` 아래에 새 파일을 staging 하는 것이다.
- `tree/` 는 LLM 이 소유한다. 사용자는 페이지를 손으로 고치지 않고 에이전트가 고친다. 실질적인 변경은 커밋 전에 반드시 사용자에게 보인다.
- 후보 페이지를 찾기 전에 `.naite/ontology/tree-manifest.json` 을 읽고, 페이지를 쓰기 전에 `tree/trunk.md` 를 읽어서 기존의 큐레이션된 도메인 진입점과 페이지 slug 를 재사용한다.
- 기존 페이지를 바꾸기 전에, 의미 의존 페이지(vein 으로 이어진 잎)의 리뷰가 필요할 수 있으면 `.naite/ontology/tree-dependencies.json` 을 읽는다.
- `AGENTS.md` 의 secrets 정책은 절대적이다. care 가 비밀을 표시하면 모든 git 작업 전에 멈추고 보고한다.
- frontmatter 계약은 `kind`, `form`, `topics`, `subject`, `source-types`, `domains`(cache), `created`, `updated` 다.
  - 스펙은 `docs/CONVENTIONS.md` 의 Ontology 절과 `.naite/ontology/subject-tree.md` 와 `.naite/ontology/topics.md` 와 `docs/ARCHITECTURE.md` 3절에 있다.
  - legacy 인 `type`·`role`·단수 `source-type` 필드는 오류다. care 가 surface 하면 새 스키마로 고친다.
  - care 가 surface 한 압력과 사용자 결정 없이 추측성 필드를 추가하지 않는다.
- 파일 이름은 `lowercase-kebab-case.md` 다. wikilink(vein)는 `[[page-slug]]` 나 `[[page-slug|Display]]` 다.
