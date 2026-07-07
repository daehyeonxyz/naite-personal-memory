#!/usr/bin/env python3
"""sync-agents.py — .claude 정본을 .agents Codex mirror 로 동기화 (cross-platform).

sync-agents.ps1 의 충실한 python 포팅. pwsh 가 없는 환경(Linux/macOS CI, 컨테이너)
에서도 mirror 를 돌릴 수 있게 한다. 치환 규칙·순서·surface repair 를 ps1 과 일치시킨다.

치환(대소문자 구분, 순서 중요):
  CLAUDE.md       -> AGENTS.md
  Claude Code     -> Codex
  Claude(낱말)    -> Codex
  \\.claude\\     -> \\.agents\\   (Windows 경로)
  .claude/        -> .agents/

정본은 .claude/ 와 CLAUDE.md. 편집 후 본 스크립트를 돌리고 .agents/ + AGENTS.md 를
같은 커밋에 stage 한다.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SKILL_SRC = REPO / ".claude" / "skills" / "naite"
SKILL_DST = REPO / ".agents" / "skills" / "naite"
CLAUDE_MD = REPO / "CLAUDE.md"
AGENTS_MD = REPO / "AGENTS.md"

SURFACE_SECTION = """## Surface mirror discipline

This file is the Codex-facing mirror of the Claude Code surface. Keep `.agents/` + `AGENTS.md` aligned with `.claude/` + `CLAUDE.md`.

- **Canonical edit target**: `.claude/` and `CLAUDE.md`. Regenerate this Codex mirror with `.naite/scripts/sync-agents.ps1` on Windows or `python .naite/scripts/sync-agents.py` on macOS/Linux when the canonical side changes.
- **Mirror review**: after sync, review `AGENTS.md` and `.agents/skills/naite/` for tool-specific wording before staging.
- **Run sync in the same commit** that edits the canonical side. Both surfaces stage together.
- **Shared (NOT mirrored)**: `docs/CONTEXT.md`, `docs/CONVENTIONS.md`, `docs/ARCHITECTURE.md`, `SOUL.md`, `USER.md`, `MEMORY.md`, `.naite/`. Both tools read the same files. Tool-specific tokens (`.claude/`, `.agents/`, `CLAUDE.md`, `AGENTS.md`, `Claude Code`, `Codex`, etc.) are allowed where they carry meaning.

---"""


def convert_to_codex(text: str) -> str:
    text = re.sub(r"CLAUDE\.md", "AGENTS.md", text)
    text = text.replace("Claude Code", "Codex")
    text = re.sub(r"Claude(?![a-zA-Z])", "Codex", text)
    text = text.replace("\\.claude\\", "\\.agents\\")
    text = text.replace(".claude/", ".agents/")
    return text


def repair_agents_entrypoint(text: str) -> str:
    pattern = re.compile(r"(?ms)^## Surface mirror discipline\r?\n\r?\n.*?^---")
    return pattern.sub(lambda _m: SURFACE_SECTION, text, count=1)


def write_text(path: Path, text: str) -> None:
    # UTF-8 no BOM. Normalize to LF so output matches the committed blobs on any
    # platform (repo blobs are LF; CI diffs the mirror on a checkout without
    # autocrlf, so writing CRLF would show every line as changed).
    data = text.replace("\r\n", "\n").encode("utf-8")
    path.write_bytes(data)


def main() -> None:
    SKILL_DST.mkdir(parents=True, exist_ok=True)
    src_names = set()
    for src in sorted(SKILL_SRC.glob("*.md")):
        src_names.add(src.name)
        dst = SKILL_DST / src.name
        converted = convert_to_codex(src.read_text(encoding="utf-8"))
        write_text(dst, converted)
        print(f"synced  {src.name}")

    # Remove orphan mirrors (canonical skill deleted but mirror left behind —
    # otherwise the CI mirror gate passes on a stale .agents/ copy).
    for dst in sorted(SKILL_DST.glob("*.md")):
        if dst.name not in src_names:
            dst.unlink()
            print(f"removed orphan  {dst.name}")

    agents = convert_to_codex(CLAUDE_MD.read_text(encoding="utf-8"))
    agents = repair_agents_entrypoint(agents)
    write_text(AGENTS_MD, agents)
    print("synced  AGENTS.md")
    print("\nDone. Review with:  git diff .agents AGENTS.md")


if __name__ == "__main__":
    main()
