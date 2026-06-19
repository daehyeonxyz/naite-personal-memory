## PR 체크리스트 (PR Checklist)

PR을 열기 전에 아래 항목을 모두 확인하고 체크하세요.
Check all items before opening this PR.

### 범위 (Scope)

- [ ] 하네스 파일만 변경했습니다 (`tree/`, `roots/`는 건드리지 않았습니다).
  (Changed harness files only; did not touch `tree/` or `roots/`.)

### 정본 + 미러 규율 (Canonical + mirror discipline)

- [ ] `.claude/` + `CLAUDE.md`만 편집했습니다. `.agents/` + `AGENTS.md`는 직접 수정하지 않았습니다.
  (Edited `.claude/` + `CLAUDE.md` only. Did not directly edit `.agents/` or `AGENTS.md`.)
- [ ] `sync-agents.ps1`을 실행하여 `.agents/` 미러를 재생성했습니다.
  (Ran `sync-agents.ps1` to regenerate the `.agents/` mirror.)

### 로컬 검사 통과 (Local checks pass)

- [ ] `python .naite/scripts/build-harness-lock.py --check` = 0
- [ ] `python .naite/scripts/lint-ontology.py` = 0

### 스키마 보호 (Schema protection)

- [ ] `.naite/ontology/facets.json`의 enum 값이나 facet 필드를 직접 추가/수정하지 않았습니다.
  C-level 변경은 PR이 아니라 schema-change issue로 제안해야 합니다 (core enum 변경은 C-level 메인테이너 결정; user kind 선언은 vault 소유자 행위로, 공유 하네스 repo의 PR 범위가 아닙니다).
  (Did not directly add or modify enum values or facet fields in `.naite/ontology/facets.json`.
  C-level changes must be proposed via a schema-change issue, not a PR.)

### 스타일 (Style)

- [ ] 응답 스타일을 준수했습니다: em dash 없음, 완결 문장, `lowercase-kebab-case` 파일명.
  (Followed response style: no em dash, complete sentences, `lowercase-kebab-case` filenames.)

---

## 변경 요약 (Change summary)

<!-- 무엇을, 왜 변경했는지 간략히 설명해 주세요. -->
<!-- Briefly describe what you changed and why. -->

## 관련 이슈 (Related issue)

<!-- 해당하는 경우 #이슈번호를 적어 주세요. -->
<!-- If applicable, reference the issue: Closes #NNN -->
