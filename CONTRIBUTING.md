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

No CI automation runs on PRs at this time (D1 decision: manual maintainer review). The checklist in the PR template is the enforcement surface.

---

## Pre-PR local checks

Before opening a PR, run these three commands and confirm each exits clean:

```bash
# 1. Regenerate the .agents/ mirror from the canonical .claude/ side
#    Windows (PowerShell)
powershell -File .naite/scripts/sync-agents.ps1
#    Mac / Linux
python .naite/scripts/sync-agents.py

# 2. Rebuild harness-lock (embed version + dependency snapshot)
python .naite/scripts/build-harness-lock.py

# 3. Lint ontology (must exit 0)
python .naite/scripts/lint-ontology.py
```

- `.agents/` + `AGENTS.md`는 `sync-agents` 스크립트의 생성물입니다. 직접 수정하지 마세요.
- 외부 기여자는 PR로 `.naite/ontology/facets.json` 을 직접 편집하지 않습니다. core enum 변경은 C-level 메인테이너 결정 사항입니다. user kind 선언은 vault 소유자의 행위이므로, 공유 하네스 repo의 PR 범위에 들어가지 않습니다. 아래 Schema governance 섹션을 참고하세요.

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

Detail: `docs/CONVENTIONS.md § Naming`, `CLAUDE.md § 응답 스타일`.

---

## Mirror discipline

| Canonical (edit here) | Generated mirror (do NOT edit directly) |
|---|---|
| `.claude/` + `CLAUDE.md` | `.agents/` + `AGENTS.md` |

`sync-agents` 스크립트를 실행하면 미러가 자동 재생성됩니다. 두 표면이 같은 커밋에 스테이징되어야 합니다.

---

## Questions

Schema proposals: open a [schema-change issue](.github/ISSUE_TEMPLATE/schema-change.md).
General questions: open a regular GitHub issue.
