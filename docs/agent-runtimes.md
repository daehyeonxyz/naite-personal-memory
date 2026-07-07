# Agent runtimes and plugin surfaces

**Status**: operational note for contributors.
**Last checked**: 2026-07-06.

naite keeps one harness but exposes it through several agent runtimes. The command contract should stay stable (`/naite start`, `/naite grow`, `/naite ask`, `/naite fruit`, `/naite care`, `/naite upgrade`) even when each runtime loads context, skills, plugins, and prompt cache differently.

Official references checked for this note:

- Claude Code Skills: https://docs.anthropic.com/en/docs/claude-code/skills
- Claude Code Plugins: https://docs.anthropic.com/en/docs/claude-code/plugins
- Anthropic prompt caching: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
- Codex AGENTS.md: https://developers.openai.com/codex/guides/agents-md
- OpenAI prompt caching: https://platform.openai.com/docs/guides/prompt-caching

## Surface map

| Runtime | Entry surface | Skill or plugin loading | naite repo contract |
|---|---|---|---|
| Claude Code, project checkout | `CLAUDE.md` + `.claude/skills/naite/` | Project skills are available from `.claude/skills/`; skill bodies load when used. | Edit `.claude/` and `CLAUDE.md` as canonical. |
| Claude Code plugin install | `.claude-plugin/plugin.json` + plugin skill paths | Plugins package skills, agents, hooks, MCP servers, and settings for sharing. Plugin skills are namespaced when installed as plugin skills. | Keep plugin metadata aligned with the same `/naite` dispatcher. |
| Codex project checkout | `AGENTS.md` + `.agents/skills/naite/` | Codex reads `AGENTS.md` instruction chains at session start and routes `/naite …` in-context (there is no Codex plugin manifest — `.claude-plugin/` is Claude-only). Optional MCP is wired manually via `~/.codex/config.toml` (see `docs/connect-mcp.md`). | Do not hand-edit `.agents/` or `AGENTS.md`; regenerate them from `.claude/`. |
| Manual clone / other agent | Markdown files in the repo | The agent must be told to read `CLAUDE.md` or `AGENTS.md` and the matching skill file. | The documented fallback prompt in `README.md` is the supported path. |

## Prompt caching implications

Prompt caching is a model-provider behavior, not a naite feature. The harness should be written so provider caches can help without making correctness depend on a cache hit.

| Provider surface | Current behavior to account for | naite guidance |
|---|---|---|
| Anthropic Claude API / Claude Code-backed flows | Prompt caching can be automatic or explicit via `cache_control`. It caches exact reusable prefixes such as tools, system content, and message blocks. Default cache lifetime is 5 minutes, with 1-hour TTL available at additional cost on supported surfaces. | Keep stable routing and safety instructions near the front of `CLAUDE.md` and skill entrypoints. Put large step-by-step workflows in skills so they load only when needed. |
| OpenAI API / Codex-backed flows | Prompt caching works automatically on recent models for prompts at least 1024 tokens long. Exact prefix matches matter. `prompt_cache_key` and retention policy can influence cache routing and retention in API usage. | Keep `AGENTS.md` stable and avoid embedding per-user volatile state in shared harness files. Put user-specific state in gitignored `USER.md` and `MEMORY.md`. |

Both providers reward the same basic shape: stable instructions first, dynamic user/task content later, and long rarely used procedures outside the always-loaded bootloader.

## Contributor rules

1. Add new user-visible commands only in the dispatcher tables first (`CLAUDE.md`, `.claude/skills/naite/SKILL.md`, `README.md`), then regenerate the Codex mirror.
2. Treat `capture.md`, `ingest.md`, `grow-branch.md`, `grow-backfill.md`, and `care-check.md` as implementation modules unless the dispatcher explicitly exposes a user entry. Today, `grow-backfill.md` is exposed only as `/naite grow backfill <slug>`.
3. Do not move personal or volatile context into shared docs to improve caching. That would make open-source installs leakier and less portable.
4. When runtime docs change, update this note with a new checked date and keep the sources official.
