# capture — grow internal module

사용자 노출 명령이 아니다. /naite grow 가 위임하는 내부 모듈이다.

Snapshot knowledge from the **current conversation** into `roots/conversations/`. Does not touch `tree/`. Merging into the tree happens in a separate grow ingest step, user-initiated.

## When to use

The user is in a learning conversation with the agent (desktop chat, cowork, or code surface) and says something like "tree 업데이트해줘", "capture this", or "save what we just covered." This is the trigger.

## Hard rules

- **Write only under `roots/conversations/`.** Never create or modify pages under `tree/`. Never edit `trunk.md`, `rings.md`, or `seeds.md`.
- **Two files per capture**, with different lifetimes:
  - **Claim summary** at `roots/conversations/YYYY-MM-DD-<slug>.md` — **ephemeral staging**. The grow ingest step deletes it after successful grow (see `ingest.md § 8`). Think of this file as a handoff envelope for the ingester, not a long-term artifact.
  - **Verbatim transcript twin** at `roots/conversations/_transcripts/YYYY-MM-DD-<slug>.md` — **permanent insurance copy**. Never deleted by any skill. If the claim summary's extraction was lossy, the transcript enables re-capture.
  Both files are required — the transcript alone is not a capture.
- **Filename slug**: `YYYY-MM-DD-<topic-kebab>.md`. If the slug already exists for today, append `-2`, `-3`, …
- **Tell the user the follow-up step** at the end: "run `/naite grow roots/conversations/<file>` to fold this in."

## Workflow

> [!IMPORTANT]
> Run **§ 4 (Secrets + PII pre-check) on the conversation content BEFORE writing anything in § 2 or § 3.** The section numbers are the write order, but the scan is a gate that precedes both writes: once text is on disk (especially the permanent `_transcripts/` twin) a secret is already leaked. Decide the slug (§ 1), scan (§ 4), then write (§ 2, § 3).

### 1. Decide the topic slug

If the user named a topic (`/naite grow transformer-attention`), kebab-case it and use it directly. Otherwise, propose a slug based on the conversation's focus and confirm with the user in one line before writing.

### 2. Write the claim-level summary

Path: `roots/conversations/YYYY-MM-DD-<topic-kebab>.md`

Frontmatter:

```yaml
---
source: <the assistant/service this came from, e.g. claude-desktop, chatgpt, gemini, codex>
surface: chat | cowork | code
date: YYYY-MM-DD
topic: <natural language topic>
---
```

Body structure:

```markdown
# <Topic>

## Context
One or two sentences on what the user was doing or thinking about.

## Claims
- <Claim 1, self-contained. One concept per bullet.>
- <Claim 2>
- ...

## Open threads
- <Things the user wanted to look into later, unresolved questions.>

## Proposed tree touchpoints
- new: `[[proposed-slug]]` (type) — one-line rationale
- update: `[[existing-slug]]` — what changes
```

Keep claims **atomic and source-attributable** — a claim should be something that could live on its own in a tree page. Skip small talk, tool-use logs, and anything you couldn't cite later.

### 3. Write the verbatim transcript twin

Path: `roots/conversations/_transcripts/YYYY-MM-DD-<topic-kebab>.md` (same slug as step 2).

This is the insurance file. If your claim extraction is lossy or wrong, the full transcript is preserved for re-capture later.

Content: the conversation as raw prose, labeled `**User:**` and `**Claude:**` turns. Collapse tool-call output unless it carried substantive signal the user cared about. A few-thousand-word paste is fine; don't truncate.

### 4. Secrets + PII pre-check

Run this **before writing either file** (both the claim summary and the verbatim transcript twin — the twin is permanent, so an unscanned secret there is permanent). Scan the content for:

- **API keys / tokens / private keys** — the same families the guard hook blocks (`.naite/hooks/pre-commit` part 2 is the single source of truth; keep this list in step with it): `sk-...` (Anthropic `sk-ant-...`, OpenAI `sk-proj-...`), GitHub `ghp_`/`gho_`/`ghs_`/`github_pat_`, GitLab `glpat-`, Slack `xox[baprs]-`, AWS `AKIA...`, Google `AIza...`, JWT (`eyJ....eyJ...`), PEM `-----BEGIN ... PRIVATE KEY-----`. Also Stripe `sk_live_`, HuggingFace `hf_`, npm `npm_`, SendGrid `SG.`, and Slack webhook URLs when present.
- **Credential lines**: `password:`, `api_key:`, `token:`, `Authorization: Bearer ...` with a real-looking value (not `xxx` / `<redacted>` / `your-key-here`).
- **High-entropy 40+ char strings** that don't look like URLs or hashes.
- **PII** (personal identifiers): Korean RRN (`######-#######`), phone numbers, credit-card-shaped 16-digit runs, full street addresses, national ID numbers. The deterministic guard hook does **not** catch PII, so this LLM-judgment pass is the primary PII gate — do not assume a downstream layer will catch it.

If anything matches: **do not write**. Report to the user and offer to redact. If a secret has **already reached a prior commit** (past this gate, or committed with `--no-verify`), tell the user that redacting the file now does not remove it from git history or from the permanent `_transcripts/` twin, and that the safe response is to **rotate/revoke the exposed credential** and, if needed, rewrite history (`git filter-repo`) before any push to a shared remote.

### 5. Tell the user the follow-up

Finish with exactly one sentence:

> roots/conversations/YYYY-MM-DD-<topic>.md 에 기록해 두었습니다. 나무에 심으려면 /naite grow roots/conversations/YYYY-MM-DD-<topic>.md 를 실행해 주세요 (전부 심으려면 /naite grow roots/conversations/).

### 6. No rings entry

The capture step does **not** write to `tree/rings.md`. The rings log belongs to tree-layer mutations. The subsequent grow ingest step is what gets logged.

## What this command never does

- Never writes under `tree/`.
- Never commits to git.
- Never decides on its own to grow — only captures.
- Never overwrites an existing file with the same slug — it appends `-2`, `-3` to disambiguate.
