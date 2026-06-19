# /naite upgrade: harness upgrade + vault migration

`/naite upgrade` 는 설치된 naite 하네스 (작업 틀) 를 업스트림 최신 릴리스로 올리고, 새 하네스가 요구하는 vault schema migration 이 있으면 계획, 승인, 적용까지 진행한다. 업데이트의 주채널은 git 머지가 아니라 이 스킬이다. 사용자에게 충돌 해결을 떠넘기지 않는다.

Upstream: `https://github.com/daehyeonxyz/naite-personal-memory`

## Hard boundaries

- **Source paths: never rewrite content**: `roots/**`. A migration may move or delete only the staging files that an existing naite workflow already owns, and only after explicit user confirmation.
- **Vault paths: never auto-replace during harness upgrade**: `tree/**`, `.naite/ontology/**`, `.naite/reports/**`. These paths are user-vault state. They can be changed only in the separate Vault migration phase below, after a preview and explicit approval.
- **Harness paths — the only upgrade targets**: exactly the file set defined in `.naite/scripts/build-harness-lock.py` (the root entrypoint and policy files, both skill surfaces, `.claude-plugin/**`, `docs/**`, `.naite/scripts/**`), plus `.naite/harness-lock.json` itself.
- User-created files inside harness directories (e.g. a custom skill the user added under `.claude/skills/`) are not in the lock and not in the new release: **leave them untouched**.
- Destructive steps (deleting a file, moving a path) always require explicit user confirmation, even when a migration note asks for them.
- Do not push. Committing is part of this skill; pushing follows whatever flow this vault already uses.
- If unrelated dirty files exist before editing, classify them first. Do not overwrite or stage user changes that are outside the upgrade.

## Workflow

### 1. Establish versions

1. Read `<NAITE_ROOT>/.naite/harness-lock.json` → installed version `V_old` and the per-file `sha256` map. If the lock is missing, tell the user the vault predates the upgrade system, and offer to bootstrap: treat every harness file as "customized" (3-way proposals only, no auto-replace).
2. Read `<NAITE_ROOT>/.claude-plugin/plugin.json` `version` and confirm it matches the lock. On mismatch, surface and stop.

### 2. Fetch upstream

1. `git clone --depth 1 <upstream> <tmp>/naite-latest` → new version `V_new` from its `.claude-plugin/plugin.json`.
2. If `V_new` == `V_old`: report "already up to date" and stop.
3. When a 3-way comparison is needed (step 4), also fetch the base: `git clone --depth 1 --branch v<V_old> <upstream> <tmp>/naite-base`.

### 3. Collect release notes and migration sources

Fetch GitHub Release bodies for every version in `(V_old, V_new]` when the tags exist (via `gh release view` or the web). A release may contain a `## Migration` section with mechanical steps. Collect reachable migration notes in version order. If some intermediate releases are missing or unreachable, continue with file comparison and latest-version migration sources, then say so in the report.

Migration sources, in priority order:

1. `## Migration` sections from reachable GitHub Releases.
2. Versioned scripts in the latest release under `.naite/scripts/migrations/`, if present.
3. Explicit migration notes in `docs/VERSIONING.md`, `docs/CONVENTIONS.md`, or workflow files.

Treat release-note prose as instructions, not proof that the vault needs the migration. Determine applicability from the current vault state.

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

### 5. Plan vault migrations

Separate harness replacement from vault migration.

For every collected migration step that may touch `tree/**`, `.naite/ontology/**`, `.naite/reports/**`, `USER.md`, or `MEMORY.md`, first produce a migration plan:

- `from` / `to` version range.
- why the migration applies or does not apply.
- files that would be read.
- files that would be written, moved, or deleted.
- whether the step is deterministic script-driven or LLM-written.
- rollback path, usually `git restore <path>` before commit or `git checkout HEAD~1 -- <path>` after commit.
- verification commands that prove the migration worked.

If a versioned migration script supports dry-run or plan mode, run that mode first. If it does not, inspect the script before running it. Never run an unread migration script against a live vault.

### 6. Apply approved vault migrations

Apply only migrations the user has approved. An invocation such as "upgrade and apply all migrations" counts as approval for non-destructive migrations after the plan is shown, but destructive steps still need a separate yes.

Allowed vault migration targets:

- `tree/**` schema rewrites, frontmatter rewrites, link rewrites, and one `tree/rings.md` `migration` entry.
- `.naite/ontology/facets.json`, `.naite/ontology/subject-tree.md`, and `.naite/ontology/topics.md` only when the release explicitly introduces a schema or vocabulary migration.
- generated maps `.naite/ontology/tree-manifest.json` and `.naite/ontology/tree-dependencies.json` after tree or ontology changes.
- root `SOUL.md`, gitignored `USER.md`, and gitignored `MEMORY.md` when the release introduces or changes instruction surfaces.
- `.naite/reports/**` for optional upgrade reports.

Do not hand-edit `roots/**` content. If a migration requires converting sources into tree pages, stop and route through `/naite grow` or `/naite care`.

After applying migrations:

1. Rebuild generated maps when page coordinates, links, or ontology changed.
2. Run `python .naite/scripts/lint-ontology.py`.
3. Run any migration-specific verifier.
4. Inspect `git diff` for every touched vault path before staging.

### 7. Finalize

1. Run `.naite/scripts/sync-agents.ps1` on Windows or `python .naite/scripts/sync-agents.py` on macOS/Linux so `.agents/` + `AGENTS.md` match the upgraded canonical side.
2. Update `.claude-plugin/plugin.json` version to `V_new` if not already replaced in step 4.
3. Rebuild the lock: `python .naite/scripts/build-harness-lock.py`.
4. Sanity check: `python .naite/scripts/lint-ontology.py` must still exit 0 (upgrade must not break the vault).
5. Run `python .naite/scripts/build-harness-lock.py --check`.
6. Clean up `<tmp>` clones.

### 8. Record and commit

1. Append one entry to `<NAITE_ROOT>/tree/rings.md` using the existing `migration` op:

```
## [YYYY-MM-DD] migration | naite harness v<V_old> → v<V_new>
- harness: auto-replaced <n> / merged with user edits <n> / added <n> / removal proposed <n>
- vault migrations: applied <n> / skipped <n> / deferred <n>
```

2. Single commit: `chore: upgrade naite harness v<V_old> -> v<V_new>`.

### 9. Report (Korean, per CLAUDE.md 응답 스타일)

- 결과: 버전 이동, 자동 교체/병합/추가/제거 제안 파일 수, 적용한 vault migration 단계.
- 안 한 것: 사용자 커스텀이라 보존한 파일, 보류된 파괴적 단계.
- 다음에 할 수 있는 것: 보류 항목 처리 방법.

## rings op

`migration` (existing vocabulary — do not invent a new op).
