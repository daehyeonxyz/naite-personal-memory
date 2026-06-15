# .naite/hooks

Repository git hooks for naite. Activate them per clone (one time):

```sh
git config core.hooksPath .naite/hooks
```

## pre-commit

Keeps this **public starter** free of personal information and personal vault
content. It blocks a commit when the staged change contains:

- a `tree/` page or `roots/` source file — the starter ships only the empty
  placeholders (`tree/{trunk,rings,seeds}.md` and `roots/**/.gitkeep`), so any
  other tree page or roots file is your personal vault content;
- a secret (API key / token / private key);
- a generated or per-vault file (`forest-config.json`, `forest-manifest.json`,
  `dashboard.md`);
- any string listed in the local-only denylist (below).

Override a commit you are sure is generic starter content with
`git commit --no-verify`.

### Local denylist (your personal strings)

Create `.naite/hooks/denylist.local` — **gitignored, never committed** — with one
string per line: your email, name, or any marker that must never reach the public
repo. Lines starting with `#` are comments.

```
# personal strings — local only, never committed
you@example.com
Your Name
```

The hook fails the commit if any staged line contains one of these (case-insensitive).
