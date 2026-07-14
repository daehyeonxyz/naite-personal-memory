# Contributing to naite

naite는 개인 지식 관리 하네스입니다. 외부 기여자는 하네스(harness)만 개선할 수 있습니다.
(naite is a personal knowledge harness. External contributors may improve the harness only.)

---

## What is in scope

기여 가능 대상 (harness files):

- `.claude/` and `CLAUDE.md` (canonical; see mirror discipline below)
- `docs/` (CONVENTIONS.md, CONTEXT.md, ARCHITECTURE.md, VERSIONING.md, etc.)
- `.naite/scripts/` and `.naite/ontology/`
- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
- `README.md`

기여 불가 대상 (personal vault content):

- `tree/`: LLM이 작성하는 개인 지식 페이지 (personal knowledge pages)
- `roots/`: 원천 자료 (source materials; each owner's private content)

---

## Contribution flow

1. Fork this repository.
2. Create a feature branch from `main` (`git checkout -b fix/my-change`).
3. Edit **only harness files** listed above.
4. Run the pre-PR checks locally (see below).
5. Open a PR and fill in the PR template checklist fully.
6. A maintainer reviews and squash-merges.

CI runs four consistency gates on every PR (`.github/workflows/ci.yml`): the committed `PUBLIC_STARTER` sentinel (`test -f .naite/PUBLIC_STARTER`), ontology lint (`lint-ontology.py`), harness-lock freshness (`build-harness-lock.py --check` — version + file-hash embed, plus `plugin.json`/`marketplace.json` version parity), and the `.claude` → `.agents` mirror sync. Run the same checks locally before opening the PR (see "Pre-PR local checks" below) so the gates pass. A maintainer still reviews and squash-merges; the PR template checklist covers what CI cannot (schema-governance intent, scope). The CI job is guarded to run only on the starter repo (`if: github.repository == 'daehyeonxyz/naite-personal-memory'`), so a personal vault created by cloning this repo does not inherit a permanently red Actions tab.

---

## Pre-PR local checks

Before opening a PR, install the script dependencies once, then run the local checks and confirm each exits clean:

```bash
# 0. Install Python dependencies used by optional analysis scripts
python3 -m pip install -r .naite/scripts/requirements.txt

# 1. Regenerate the .agents/ mirror from the canonical .claude/ side
# Windows PowerShell
powershell -File .naite/scripts/sync-agents.ps1

# macOS / Linux / CI without PowerShell
python3 .naite/scripts/sync-agents.py

# 2. Rebuild harness-lock (embed version + dependency snapshot)
python3 .naite/scripts/build-harness-lock.py

# 3. Lint ontology (must exit 0)
python3 .naite/scripts/lint-ontology.py
```

> 명령은 `python3` 기준입니다 (최신 macOS 는 `python` 이 없고 `python3` 만 있습니다). Windows 에서는 `python3` 대신 `python` 을 쓰세요.

- `.agents/` + `AGENTS.md`는 `sync-agents.ps1` 또는 `sync-agents.py`의 생성물입니다. 직접 수정하지 마세요.
- `requirements.txt` 는 주로 `forest-*` 진단 스크립트용입니다. `build-*`, `lint-*`, `sync-agents.py` 는 표준 라이브러리만으로 동작하지만, 첫 기여자는 위 설치를 먼저 해 두면 script 실행 중 `ImportError` 로 막히지 않습니다.
- 외부 기여자는 PR로 `.naite/ontology/facets.json` 을 직접 편집하지 않습니다. core enum 변경은 C-level 메인테이너 결정 사항입니다. user kind 선언은 vault 소유자의 행위이므로, 공유 하네스 repo의 PR 범위에 들어가지 않습니다. 아래 Schema governance 섹션을 참고하세요.

---

## Script map

`.naite/scripts/` 의 주요 스크립트는 아래 상황에서 실행합니다.

| Script | 언제 실행하나 | 비고 |
|---|---|---|
| `sync-agents.ps1` | Windows에서 `.claude/` 또는 `CLAUDE.md` 정본을 고친 뒤 | `.agents/` + `AGENTS.md` mirror 재생성 |
| `sync-agents.py` | macOS, Linux, CI, PowerShell 없는 환경에서 mirror를 재생성할 때 | `sync-agents.ps1`의 cross-platform 대체재 |
| `build-harness-lock.py` | 하네스 파일을 고친 뒤 release 또는 PR 전 | `--check` 로 lock drift 검증 가능 |
| `lint-ontology.py` | PR 전, 또는 `/naite care --check` 검증 중 | tree/schema report-only 검사 |
| `build-tree-manifest.py` | `tree/` 페이지를 만들거나 삭제한 뒤, 또는 manifest가 없거나 stale 할 때 | agent가 page 후보를 빠르게 찾기 위한 generated map |
| `build-tree-dependencies.py` | `tree/` 페이지의 wikilink나 의미 의존성을 바꾼 뒤 | inbound/outbound dependency map 생성 |
| `forest-*.py` | `/naite care --check` 또는 maintainer가 forest layer를 진단할 때 | `requirements.txt` 의 `networkx`, `numpy`, `scikit-learn` 이 필요할 수 있음 |
| `gen-subagents.py` | `.naite/ontology/forest-manifest.json` 이 있고 나무별 subagent 정의를 만들 때 | 보통 `forest-assign.py --write` 이후 선택적으로 실행 |

외부 기여자는 보통 `tree/` 와 `roots/` 를 건드리지 않으므로 `build-tree-*`, `forest-*`, `gen-subagents.py` 를 직접 실행할 일이 거의 없습니다. 문서나 skill, plugin metadata 를 고쳤다면 `sync-agents`, `build-harness-lock.py`, `lint-ontology.py` 가 기본 검사입니다.

---

## Schema governance (A / B / C)

naite의 스키마는 영향 범위에 따라 세 등급으로 관리됩니다.
Full rules: `docs/CONVENTIONS.md § Schema evolution`

| Level | Scope | External contributor action |
|---|---|---|
| **A (autonomous)** | Single-page doc fix, script bug, obvious alias | PR directly. Maintainer merges. |
| **B (propose)** | Subject narrower / rename / move | PR + append candidate to ontology file with `# PROPOSED` comment. Maintainer confirms or reverts. |
| **C (user decision)** | New `kind`/`form`/`source-types` enum value, new facet field, new top-level domain, subject deprecation | **Do not add in a PR.** 외부 기여자는 C 등급(내부 기준 'user decision') 스키마를 PR로 직접 추가하지 못합니다. issue로 제안하고, 실제 변경은 메인테이너만 합니다. Open a schema-change issue instead (`.github/ISSUE_TEMPLATE/schema-change.md`). |

---

## Style and naming conventions

- 응답 스타일 (response style): 대화 본문은 한국어, 식별자/경로/코드는 영어 그대로 유지합니다.
- 완결 문장: 모든 문장은 서술어까지 완성합니다. 명사형 종결, em dash는 사용하지 않습니다.
- 파일명: `lowercase-kebab-case.md`. 공백, 대문자 금지.
- Wikilinks: `[[page-slug]]` 또는 `[[page-slug|Display Text]]`. Plain `[[...]]`만 사용합니다.

Detail: `docs/CONVENTIONS.md § Naming`, `SOUL.md § 응답 스타일`.

---

## Mirror discipline

| Canonical (edit here) | Generated mirror (do NOT edit directly) |
|---|---|
| `.claude/` + `CLAUDE.md` | `.agents/` + `AGENTS.md` |

Windows 에서는 `sync-agents.ps1`, macOS/Linux 에서는 `sync-agents.py` 를 실행하면 미러가 자동 재생성됩니다. 두 표면이 같은 커밋에 스테이징되어야 합니다.

---

## Questions

Schema proposals: open a [schema-change issue](.github/ISSUE_TEMPLATE/schema-change.md).
General questions: open a regular GitHub issue.
