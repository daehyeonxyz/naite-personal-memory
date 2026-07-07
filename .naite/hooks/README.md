# .naite/hooks

Repository git hooks for naite. Activate them per clone (one time):

```sh
git config core.hooksPath .naite/hooks
```

> Setting `core.hooksPath` makes git look for **all** hooks here and ignore
> `.git/hooks/` entirely. If you rely on any `.git/hooks/*` hook (e.g. a
> post-commit auto-push), move it under `.naite/hooks/` too or it will stop firing.

`pre-commit` (staged changes) and `pre-push` (the range being pushed) share the
scan logic in `_naite_guard.sh`. `pre-push` exists because commits created by
merge / rebase / cherry-pick / am skip `pre-commit` — the push-time scan re-checks
the whole push range before it reaches a remote (fail-closed: a brand-new ref is
scanned against the empty tree).

## Two modes

The guard resolves its mode in this order:

1. **`NAITE_HOOK_MODE` environment variable** — `starter` or `vault` wins outright
   (any other value is ignored with a warning). This is the clean escape hatch: if
   you cloned or forked the public repo and use it as your own vault, export
   `NAITE_HOOK_MODE=vault` — you never have to delete a tracked file to do it.
2. **`.naite/PUBLIC_STARTER` sentinel** — with no env override, the guard is in
   **starter** mode iff that file is present, checked at `HEAD` **or** in the
   working tree (HEAD-based so a same-commit deletion can't silently turn the block
   off). The sentinel ships **only** in the public `naite-personal-memory` repo;
   installing or scaffolding a vault removes it, so your own clone defaults to vault.
3. **default** — no override and no sentinel: **vault** mode.

- **starter mode** — this clone is the public starter; it additionally blocks
  personal vault content so the starter stays clean (see below).
- **vault mode** — this clone is **your personal vault**, where committing `tree/`
  pages and `roots/` sources is the whole point. The vault-content block is skipped;
  every universal safety check below still runs.

## Always blocked (both modes)

- `USER.md` / `MEMORY.md` / `denylist.local` — per-clone private state that must
  never be committed (gitignored; this catches a deliberate `git add -f`);
- a secret — a known token shape (OpenAI/Anthropic `sk-…`, Stripe, GitHub, GitLab,
  Slack, AWS, Google, HuggingFace, Databricks, SendGrid, DigitalOcean, Linear, npm,
  PyPI, JWT, PEM private keys, …) **or** a generic `password` / `secret` / `api_key`
  key set to a real value (placeholders like `your-…`, `example`, `changeme`, `<…>`
  are excluded);
- a Windows reserved device-name slug (`con`, `prn`, `aux`, `nul`, `com1`…, `lpt1`…)
  that would break checkout on Windows — naite is cross-platform, so it is blocked
  on every OS;
- any string listed in the local-only denylist (below);
- a commit whose author email matches a denylisted personal string.

## Also blocked in starter mode

To keep the public starter free of personal content:

- a `tree/` page or `roots/` source file — the starter ships only the empty
  placeholders (`tree/{trunk,rings,seeds}.md` and `roots/**/.gitkeep`); any other
  `tree/` or `roots/` file is personal vault content;
- a generated / per-vault file (`forest-config.json`, `forest-manifest.json`,
  `dashboard.md`, `.naite/agents/naite-*.md`);
- **deleting `.naite/PUBLIC_STARTER` itself** — the sentinel gates this whole
  content block, so the public repo cannot silently disable it with a commit. An
  installed vault removes the sentinel at install/scaffold time (programmatically),
  not through a commit here. If you deliberately run this public clone as a vault,
  the documented escape is `NAITE_HOOK_MODE=vault`, not deleting the sentinel.

## Honesty caveat

**The secret scan is best-effort and not exhaustive.** It matches known token
prefixes and obvious `KEY=value` lines; it cannot catch prefix-less secrets (a raw
AWS secret access key), arbitrary high-entropy blobs, or secrets embedded in binary
files. Treat it as a seatbelt, not a vault door — keep the repo private and use the
denylist for your own identifiers.

Override a commit or push you are sure is safe with `git commit --no-verify` /
`git push --no-verify`.

### Local denylist (your personal strings)

Create `.naite/hooks/denylist.local` — **gitignored, never committed** — with one
string per line: your email, name, or any marker that must never reach a public
repo. Lines starting with `#` are comments; a trailing CR, a leading UTF-8 BOM, and
surrounding whitespace are stripped so a Windows-editor artifact cannot silently
disable a line.

```
# personal strings — local only, never committed
you@example.com
Your Name
```

The hook fails when any staged line contains one of these (case-insensitive), and
also when your configured commit email contains one.
