#!/usr/bin/env python3
"""Build ontology/tree-manifest.json for fast agent routing."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


NAITE_ROOT = Path(__file__).resolve().parent.parent
TREE_DIR = NAITE_ROOT / "tree"
OUT_PATH = NAITE_ROOT / "ontology" / "tree-manifest.json"
SPECIALS = {"trunk.md", "rings.md", "seeds.md"}


def parse_flow_list(value: str) -> list[str]:
    value = value.strip()
    if value == "[]":
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip("\"'") for item in inner.split(",") if item.strip()]
    if not value:
        return []
    return [value.strip().strip("\"'")]


def split_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    if not text.startswith("---"):
        return None, text
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.DOTALL)
    if not match:
        return None, text
    frontmatter: dict[str, str] = {}
    for line in match.group(1).splitlines():
        field = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if field:
            frontmatter[field.group(1)] = field.group(2).strip()
    return frontmatter, match.group(2)


def first_heading(body: str, fallback: str) -> str:
    for line in body.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return fallback


def collect_headings(body: str) -> list[str]:
    headings: list[str] = []
    for line in body.splitlines():
        match = re.match(r"^(#{1,3})\s+(.+?)\s*$", line)
        if match:
            headings.append(match.group(2).strip())
    return headings[:6]


def collect_aliases(body: str) -> list[str]:
    lines = body.splitlines()
    aliases: list[str] = []
    in_aliases = False
    for line in lines:
        if re.match(r"^##\s+Also known as\s*$", line.strip(), re.IGNORECASE):
            in_aliases = True
            continue
        if in_aliases and line.startswith("## "):
            break
        if in_aliases:
            item = re.match(r"^-\s+(.+?)\s*$", line.strip())
            if item:
                aliases.append(item.group(1).strip())
    return aliases


def page_record(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    frontmatter, body = split_frontmatter(text)
    slug = path.stem
    title = first_heading(body, slug)
    record: dict[str, object] = {
        "slug": slug,
        "file": path.relative_to(NAITE_ROOT).as_posix(),
        "title": title,
        "special": path.name in SPECIALS,
        "aliases": collect_aliases(body),
    }

    if frontmatter:
        for key in ("kind", "form", "created", "updated"):
            record[key] = frontmatter.get(key, "")
        for key in ("topics", "subject", "source-types", "domains"):
            record[key] = parse_flow_list(frontmatter.get(key, "[]"))
    else:
        record.update(
            {
                "kind": "special" if path.name in SPECIALS else "",
                "form": "",
                "topics": [],
                "subject": [],
                "source-types": [],
                "domains": [],
                "created": "",
                "updated": "",
            }
        )
    return record


def main() -> int:
    pages = [page_record(path) for path in sorted(TREE_DIR.glob("*.md"))]
    by_kind: dict[str, int] = {}
    by_domain: dict[str, int] = {}
    by_source_type: dict[str, int] = {}
    for page in pages:
        kind = str(page.get("kind", ""))
        by_kind[kind] = by_kind.get(kind, 0) + 1
        for domain in page.get("domains", []):
            by_domain[str(domain)] = by_domain.get(str(domain), 0) + 1
        for source_type in page.get("source-types", []):
            by_source_type[str(source_type)] = by_source_type.get(str(source_type), 0) + 1

    data = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "scripts/build-tree-manifest.py",
        "page_count": len(pages),
        "content_page_count": sum(1 for page in pages if not page["special"]),
        "summary": {
            "by_kind": dict(sorted(by_kind.items())),
            "by_domain": dict(sorted(by_domain.items())),
            "by_source_type": dict(sorted(by_source_type.items())),
        },
        "pages": pages,
    }
    OUT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT_PATH.relative_to(NAITE_ROOT)} ({len(pages)} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
