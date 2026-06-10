# Sync .claude/ canonical skill set to .agents/ (Codex mirror) with text substitutions.
#
# Usage (from repo root):
#     .\scripts\sync-agents.ps1
#
# Substitutions applied to every mirrored file (case-sensitive, UTF-8 preserved):
#   - "CLAUDE.md"              -> "AGENTS.md"            (must run BEFORE Claude->Codex)
#   - "Claude Code"            -> "Codex"
#   - "Claude" (whole word)    -> "Codex"
#   - "\.claude\"              -> "\.agents\"            (Windows abs path inside content)
#   - "/.claude/"              -> "/.agents/"            (Unix-style ref)
#   - ".claude/"               -> ".agents/"             (other ./.claude/ paths)
#
# Edits to .claude/* are canonical. Run this script after editing them, then
# git add the regenerated .agents/ and AGENTS.md.

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path "$PSScriptRoot\..").Path

# UTF-8 no-BOM (matches our skill / md files)
$utf8 = New-Object System.Text.UTF8Encoding($false)

function Convert-ToCodex {
    param([string]$Path)
    $text = [System.IO.File]::ReadAllText($Path, $utf8)
    # Order matters: CLAUDE.md before Claude -> Codex (because -creplace is case-sensitive
    # but Claude -> Codex would still leave CLAUDE.md untouched if case-sensitive,
    # we still front-load it for clarity and safety).
    $text = $text -creplace 'CLAUDE\.md', 'AGENTS.md'
    $text = $text -creplace 'Claude Code', 'Codex'
    $text = $text -creplace 'Claude(?![a-zA-Z])', 'Codex'
    $text = $text -creplace '\\\.claude\\', '\.agents\'
    $text = $text -creplace '\.claude/', '.agents/'
    [System.IO.File]::WriteAllText($Path, $text, $utf8)
}

function Repair-AgentsEntrypoint {
    param([string]$Path)
    $text = [System.IO.File]::ReadAllText($Path, $utf8)
    $surfaceSection = @'
## Surface mirror discipline

This file is the Codex-facing mirror of the Claude Code surface. Keep `.agents/` + `AGENTS.md` aligned with `.claude/` + `CLAUDE.md`.

- **Canonical edit target**: `.claude/` and `CLAUDE.md`. Regenerate this Codex mirror with `scripts/sync-agents.ps1` when the canonical side changes.
- **Mirror review**: after sync, review `AGENTS.md` and `.agents/skills/wiki/` for tool-specific wording before staging.
- **Run sync in the same commit** that edits the canonical side. Both surfaces stage together.
- **Shared (NOT mirrored)**: `CONTEXT.md`, `CONVENTIONS.md`, `ARCHITECTURE.md`, `ontology/`. Both tools read the same files. Tool-specific tokens (`.claude/`, `.agents/`, `CLAUDE.md`, `AGENTS.md`, `Claude Code`, `Codex`, etc.) are allowed where they carry meaning.

---
'@
    $pattern = '(?ms)^## Surface mirror discipline\r?\n\r?\n.*?^---'
    $text = [regex]::Replace($text, $pattern, $surfaceSection, 1)
    [System.IO.File]::WriteAllText($Path, $text, $utf8)
}

# 1) Mirror skill files .claude/skills/wiki/*.md -> .agents/skills/wiki/
$srcDir = Join-Path $repo ".claude\skills\wiki"
$dstDir = Join-Path $repo ".agents\skills\wiki"
New-Item -ItemType Directory -Force -Path $dstDir | Out-Null

Get-ChildItem -LiteralPath $srcDir -Filter "*.md" | ForEach-Object {
    $dst = Join-Path $dstDir $_.Name
    Copy-Item -LiteralPath $_.FullName -Destination $dst -Force
    Convert-ToCodex -Path $dst
    Write-Host "synced  $($_.Name)"
}

# 2) Mirror CLAUDE.md -> AGENTS.md
$claudeMd = Join-Path $repo "CLAUDE.md"
$agentsMd = Join-Path $repo "AGENTS.md"
Copy-Item -LiteralPath $claudeMd -Destination $agentsMd -Force
Convert-ToCodex -Path $agentsMd
Repair-AgentsEntrypoint -Path $agentsMd
Write-Host "synced  AGENTS.md"

Write-Host "`nDone. Review with:  git diff .agents AGENTS.md"
