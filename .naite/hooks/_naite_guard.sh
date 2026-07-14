# naite guard — shared scan logic, sourced by pre-commit (staged changes) and
# pre-push (the range being pushed). Not a git hook itself (leading underscore).
#
# The caller must define, BEFORE calling any naite_* function:
#     fail=0
#     err() { printf '  - %s\n' "$1" >&2; fail=1; }
#
# The secret scan is a best-effort allowlist of known token shapes — NOT exhaustive
# (prefix-less secrets, high-entropy blobs, and secrets in binary files can pass).

ROOT=$(git rev-parse --show-toplevel)
SENTINEL=".naite/PUBLIC_STARTER"
DENY="$ROOT/.naite/hooks/denylist.local"

# Mode precedence: NAITE_HOOK_MODE env ("starter"|"vault") wins outright; any other
# value is warned about and ignored. Otherwise the .naite/PUBLIC_STARTER sentinel —
# committed at HEAD OR present in the working tree — means starter mode. Otherwise
# default is vault. HEAD-based so removing the sentinel in the same change cannot
# silently turn the content guard off; env-based so a user who clones/forks the
# public repo as their own vault escapes with NAITE_HOOK_MODE=vault (no tracked file
# to delete).
naite_starter_mode() {
  case "${NAITE_HOOK_MODE:-}" in
    starter) echo 1; return ;;
    vault)   echo 0; return ;;
    "") : ;;
    *) printf 'naite guard: ignoring unrecognized NAITE_HOOK_MODE=%s (use starter|vault)\n' "$NAITE_HOOK_MODE" >&2 ;;
  esac
  if git cat-file -e "HEAD:$SENTINEL" 2>/dev/null || [ -f "$ROOT/$SENTINEL" ]; then
    echo 1
  else
    echo 0
  fi
}

# Denylist patterns, normalized: strip CR (a CRLF denylist.local edited on Windows),
# a leading UTF-8 BOM on line 1, and surrounding whitespace; then drop comment and
# blank lines. Any of these could otherwise turn a real pattern into 'string\r' or
# ' string' and silently disable it against LF diff lines.
naite_read_deny() {
  [ -f "$DENY" ] || return 0
  sed -e 's/\r$//' -e '1s/^\xef\xbb\xbf//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' \
      -e '/^#/d' -e '/^$/d' "$DENY"
}

# Alternation of known secret token shapes.
naite_secret_re() {
  re='(^|[^A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}'                      # OpenAI/Anthropic (sk-, sk-ant-, sk-proj-, sk-svcacct-)
  re="$re|(sk|pk|rk)_(live|test)_[A-Za-z0-9]{20,}"                 # Stripe
  re="$re|gh[posru]_[A-Za-z0-9]{36,}"                              # GitHub classic
  re="$re|github_pat_[A-Za-z0-9_]{40,}"                            # GitHub fine-grained PAT
  re="$re|glpat-[A-Za-z0-9_-]{20,}"                                # GitLab PAT
  re="$re|xox[baprs]-[A-Za-z0-9-]{10,}|xapp-[0-9]-[A-Za-z0-9-]{10,}"  # Slack
  re="$re|AKIA[0-9A-Z]{16}"                                        # AWS access key id
  re="$re|AIza[0-9A-Za-z_-]{35}|GOCSPX-[A-Za-z0-9_-]{20,}"         # Google API / OAuth
  re="$re|hf_[A-Za-z0-9]{30,}|dapi[0-9a-f]{32}"                    # HuggingFace / Databricks
  re="$re|SG\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}"             # SendGrid
  re="$re|dop_v1_[a-f0-9]{64}|lin_api_[A-Za-z0-9]{20,}"           # DigitalOcean / Linear
  re="$re|npm_[A-Za-z0-9]{36}|pypi-[A-Za-z0-9_-]{40,}"           # npm / PyPI
  re="$re|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"  # JWT
  re="$re|-----BEGIN [A-Z ]*PRIVATE KEY-----"                     # PEM private key
  printf '%s' "$re"
}

# Scan diff/content text for secrets, credential assignments, and denylist strings.
naite_scan_content() {  # $1 = text (a -U0 diff, or blob content)
  _c=$1
  if printf '%s' "$_c" | grep -Eq "$(naite_secret_re)"; then
    err "content contains a secret-like pattern (API key / token / private key)"
  fi
  # Generic credential assignment on an added line, placeholders excluded.
  if printf '%s' "$_c" | grep -E '^\+' \
       | grep -Eiv 'xxx+|your[_-]|example|changeme|redact|placeholder|<[^>]*>|\*{4,}|\.\.\.' \
       | grep -Eiq '(password|passwd|secret|api[_-]?key|access[_-]?token|aws_secret_access_key)[[:space:]]*[=:][[:space:]]*[^[:space:]]{8,}'; then
    err "content contains a credential-like assignment (password/secret/token = …)"
  fi
  # Denylist: one fixed-string pass over the whole content, instead of re-scanning
  # it once per pattern (super-linear in Git Bash for a large diff). Case-insensitive
  # is done by lowercasing both sides and using grep -Ff, NOT grep -iF — the -iF
  # (case-insensitive + fixed-string) combination aborts on some GNU grep 3.0 builds
  # (MSYS/Git Bash), which would silently disable this check.
  _deny=$(naite_read_deny)
  if [ -n "$_deny" ]; then
    _dt=$(mktemp 2>/dev/null || printf '%s/naite-deny.%s' "${TMPDIR:-/tmp}" "$$")
    printf '%s\n' "$_deny" | tr 'A-Z' 'a-z' > "$_dt"
    if [ -s "$_dt" ]; then
      _lc=$(printf '%s' "$_c" | tr 'A-Z' 'a-z')
      if printf '%s' "$_lc" | grep -qFf "$_dt"; then
        _hit=$(printf '%s' "$_lc" | grep -oFf "$_dt" 2>/dev/null | head -1)
        err "content contains a denylisted personal string (e.g. '${_hit:-see denylist}')"
      fi
    fi
    rm -f "$_dt"
  fi
}

# Path checks: private-state files (always) + starter content block (starter only).
naite_scan_paths() {  # $1 = newline paths, $2 = newline deleted paths, $3 = starter(0/1)
  _paths=$1
  _del=$2
  _st=$3
  _oi=$IFS
  IFS='
'
  for f in $_paths; do
    case "$f" in
      USER.md|MEMORY.md|.naite/hooks/denylist.local)
        err "'$f' is per-clone private state and must never be committed (gitignored; do not 'git add -f' it)" ;;
    esac
    # Windows reserved device-name slugs (con/nul/aux/com1…/lpt1…) break checkout on
    # Windows; naite is cross-platform, so block them on every platform.
    _b=$(basename "$f" | tr 'A-Z' 'a-z')
    case "${_b%.*}" in
      con|prn|aux|nul|com[1-9]|lpt[1-9])
        err "'$f' uses a Windows reserved device name — rename the slug (it breaks Windows checkout)" ;;
    esac
  done
  if [ "$_st" -eq 1 ]; then
    for f in $_paths; do
      case "$f" in
        tree/trunk.md|tree/seeds.md|tree/rings.md) ;;
        tree/*)
          err "tree page '$f' looks like personal vault content (this starter ships an empty tree)" ;;
        roots/.gitkeep|roots/*/.gitkeep|roots/*/*/.gitkeep|roots/*/*/*/.gitkeep) ;;
        roots/*)
          err "roots file '$f' looks like personal source material (this starter ships no roots content)" ;;
        .naite/forest/forest-config.json|.naite/ontology/forest-manifest.json|.naite/forest/dashboard.md|.naite/agents/naite-*.md)
          err "'$f' is a per-vault or generated file and should stay gitignored" ;;
      esac
    done
    for f in $_del; do
      if [ "$f" = "$SENTINEL" ]; then
        err "refusing to delete $SENTINEL in the public starter (it gates this content guard; an installed vault removes it at install time, not via commit — to run this clone as a vault set NAITE_HOOK_MODE=vault)"
      fi
    done
  fi
  IFS=$_oi
}

# Commit author email must not match a denylisted personal string.
naite_email_check() {
  _email=$(git config user.email 2>/dev/null || true)
  [ -n "$_email" ] || return 0
  _oi=$IFS
  IFS='
'
  for pat in $(naite_read_deny); do
    case "$_email" in
      *"$pat"*) err "commit email '$_email' matches denylisted '$pat' — set a noreply email: git config user.email <id>+<user>@users.noreply.github.com" ;;
    esac
  done
  IFS=$_oi
}
