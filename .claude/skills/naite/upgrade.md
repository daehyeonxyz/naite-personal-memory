# /naite upgrade — harness upgrade

`/naite upgrade` 는 설치된 naite 하네스 (작업 틀) 를 업스트림 최신 릴리스로 올린다. **사용자 자료는 절대 건드리지 않는다.** 업데이트의 주채널은 git 머지가 아니라 이 스킬이다. 사용자에게 충돌 해결을 떠넘기지 않는다.

Upstream: `https://github.com/daehyeonxyz/naite-personal-memory`

## Hard boundaries

- **Protected paths — never write, never delete, under any circumstance**: `roots/**`, `tree/**`, `.naite/ontology/**`, `.naite/reports/**`.
- **Harness paths — the only upgrade targets**: exactly the file set defined in `.naite/scripts/build-harness-lock.py` (the root entrypoint and policy files, both skill surfaces, `.claude-plugin/**`, `docs/**`, `.naite/scripts/**`), plus `.naite/harness-lock.json` itself.
- User-created files inside harness directories (e.g. a custom skill the user added under `.claude/skills/`) are not in the lock and not in the new release: **leave them untouched**.
- Destructive steps (deleting a file, moving a path) always require explicit user confirmation, even when a Migration note asks for them.
- Do not push. Committing is part of this skill; pushing follows whatever flow this vault already uses.

## Workflow

### 1. Establish versions

1. Read `<NAITE_ROOT>/.naite/harness-lock.json` → installed version `V_old` and the per-file `sha256` map. If the lock is missing, tell the user the vault predates the upgrade system, and offer to bootstrap: treat every harness file as "customized" (3-way proposals only, no auto-replace).
2. Read `<NAITE_ROOT>/.claude-plugin/plugin.json` `version` and confirm it matches the lock. On mismatch, surface and stop.

### 2. Fetch upstream

1. `git clone --depth 1 <upstream> <tmp>/naite-latest` → new version `V_new` from its `.claude-plugin/plugin.json`.
2. If `V_new` == `V_old`: report "already up to date" and stop.
3. When a 3-way comparison is needed (step 4), also fetch the base: `git clone --depth 1 --branch v<V_old> <upstream> <tmp>/naite-base`.

### 3. Collect release notes

Fetch GitHub Release bodies for every version in `(V_old, V_new]` (via `gh release view` or the web). Each release may contain a `## Migration` section with mechanical steps. Collect them in order. If releases are unreachable (offline), continue with file comparison only and say so in the report.

### 4. Classify every harness file

Hash rule: sha256 over file bytes with CRLF normalized to LF — the same rule as `build-harness-lock.py`. Never compare raw bytes; line-ending differences from git config are not customization.

For each file in the union of (lock map, new release harness set):

| Local state vs lock | In new release | Action |
|---|---|---|
| hash matches lock (unmodified) | changed | **auto-replace** with the new version |
| hash matches lock | unchanged | skip |
| hash differs (user-customized) | changed | **3-way proposal**: show base (`naite-base`), local, new; propose a merged version; user picks |
| hash differs | unchanged | keep local (note it in the report) |
| not in lock (user-added file) | absent | keep local, untouched |
| in lock, deleted locally | any | note in report; offer to restore |
| absent locally and in lock | new file in release | **add** |
| in lock | removed in release | **propose removal**; never auto-delete |

### 5. Apply migrations

Execute collected `## Migration` steps in version order. Steps touching protected paths are **read-only suggestions** — surface them, let the user run them via the normal naite workflows. Destructive steps need confirmation (Hard boundaries).

### 6. Finalize

1. Run `.naite/scripts/sync-agents.ps1` so `.agents/` + `AGENTS.md` match the upgraded canonical side.
2. Update `.claude-plugin/plugin.json` version to `V_new` if not already replaced in step 4.
3. Rebuild the lock: `python .naite/scripts/build-harness-lock.py`.
4. Sanity check: `python .naite/scripts/lint-ontology.py` must still exit 0 (upgrade must not break the vault).
5. Clean up `<tmp>` clones.

### 7. Record and commit

1. Append one entry to `<NAITE_ROOT>/tree/rings.md` using the existing `migration` op:

```
## [YYYY-MM-DD] migration | naite harness v<V_old> → v<V_new>
- auto-replaced: <n> files / merged with user edits: <n> / added: <n> / removal proposed: <n>
```

2. Single commit: `chore: upgrade naite harness v<V_old> -> v<V_new>`.

### 8. Report (Korean, per CLAUDE.md 응답 스타일)

- 결과: 버전 이동, 자동 교체/병합/추가/제거 제안 파일 수, 수행한 Migration 단계.
- 안 한 것: 사용자 커스텀이라 보존한 파일, 보류된 파괴적 단계.
- 다음에 할 수 있는 것: 보류 항목 처리 방법.

## rings op

`migration` (existing vocabulary — do not invent a new op).
