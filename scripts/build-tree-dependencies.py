#!/usr/bin/env python3
"""Build ontology/tree-dependencies.json from wikilinks and soft relation idioms."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


NAITE_ROOT = Path(__file__).resolve().parent.parent
TREE_DIR = NAITE_ROOT / "tree"
OUT_PATH = NAITE_ROOT / "ontology" / "tree-dependencies.json"
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]")

RELATION_PATTERNS = [
    ("builds-on", re.compile(r"\bbuilds on\b", re.IGNORECASE)),
    ("extends", re.compile(r"\bextends\b", re.IGNORECASE)),
    ("contradicts", re.compile(r"\bcontradicts\b", re.IGNORECASE)),
    ("instance-of", re.compile(r"\binstance of\b", re.IGNORECASE)),
    ("applies-to", re.compile(r"\bapplies to\b|\bused in\b", re.IGNORECASE)),
    ("see-also", re.compile(r"\bsee also\b", re.IGNORECASE)),
    ("decided-over", re.compile(r"\bdecided\b.*\bover\b", re.IGNORECASE)),
    ("failed-when", re.compile(r"\bfailed when\b", re.IGNORECASE)),
    ("trade-off", re.compile(r"\btrade-off\b", re.IGNORECASE)),
    ("validates", re.compile(r"\bvalidates\b", re.IGNORECASE)),
    ("falsifies", re.compile(r"\bfalsifies\b", re.IGNORECASE)),
]


def normalize_target(target: str) -> str:
    target = target.strip().replace("\\", "/").split("/")[-1]
    if target.endswith(".md"):
        target = target[:-3]
    return target.strip()


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    match = re.match(r"^---\r?\n.*?\r?\n---\r?\n?(.*)$", text, re.DOTALL)
    if match:
        return match.group(1)
    return text


def line_relations(line: str) -> list[str]:
    return [name for name, pattern in RELATION_PATTERNS if pattern.search(line)]


def scan_page(path: Path, existing_slugs: set[str]) -> dict[str, object]:
    text = strip_frontmatter(path.read_text(encoding="utf-8-sig", errors="replace"))
    slug = path.stem
    outbound: set[str] = set()
    soft_relations: set[tuple[str, str]] = set()

    in_code_block = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        links = []
        for match in WIKILINK_RE.finditer(line):
            target = normalize_target(match.group(1))
            link = {"target": target, "exists": target in existing_slugs}
            links.append(link)
            outbound.add(target)

        if links:
            for relation in line_relations(line):
                for link in links:
                    soft_relations.add((relation, str(link["target"])))

    return {
        "outbound": sorted(outbound),
        "soft_relations": [
            {"relation": relation, "target": target}
            for relation, target in sorted(soft_relations)
        ],
    }


def main() -> int:
    paths = sorted(TREE_DIR.glob("*.md"))
    existing_slugs = {path.stem for path in paths}
    pages: dict[str, dict[str, object]] = {}
    inbound_sets: dict[str, set[str]] = {slug: set() for slug in existing_slugs}
    missing_target_sets: dict[str, set[str]] = {}
    relation_counts: dict[str, int] = {}
    relation_edges: set[tuple[str, str, str]] = set()

    for path in paths:
        slug = path.stem
        scan = scan_page(path, existing_slugs)
        pages[slug] = {
            "file": path.relative_to(NAITE_ROOT).as_posix(),
            **scan,
        }
        for target in scan["outbound"]:
            target = str(target)
            if target in existing_slugs:
                if target != slug:
                    inbound_sets.setdefault(target, set()).add(slug)
            else:
                missing_target_sets.setdefault(target, set()).add(slug)
        for relation in scan["soft_relations"]:
            name = str(relation["relation"])
            relation_counts[name] = relation_counts.get(name, 0) + 1
            relation_edges.add((slug, name, str(relation["target"])))

    inbound_counts = {
        slug: len(sources)
        for slug, sources in sorted(inbound_sets.items(), key=lambda item: (-len(item[1]), item[0]))
    }
    high_degree = [
        {"slug": slug, "inbound_count": count}
        for slug, count in list(inbound_counts.items())[:25]
    ]
    orphans = sorted(slug for slug, count in inbound_counts.items() if count == 0)

    data = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "scripts/build-tree-dependencies.py",
        "page_count": len(paths),
        "summary": {
            "edge_count": sum(len(page["outbound"]) for page in pages.values()),
            "missing_target_count": len(missing_target_sets),
            "orphan_count": len(orphans),
            "relation_counts": dict(sorted(relation_counts.items())),
            "high_degree": high_degree,
        },
        "inbound_counts": inbound_counts,
        "inbound": {
            slug: sorted(sources)
            for slug, sources in sorted(inbound_sets.items())
            if sources
        },
        "outbound": {
            slug: page["outbound"]
            for slug, page in sorted(pages.items())
            if page["outbound"]
        },
        "orphans": orphans,
        "missing_targets": {
            target: sorted(sources)
            for target, sources in sorted(missing_target_sets.items())
        },
        "relation_edges": [
            [source, relation, target]
            for source, relation, target in sorted(relation_edges)
        ],
    }
    OUT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(
        f"wrote {OUT_PATH.relative_to(NAITE_ROOT)} "
        f"({len(paths)} pages, {data['summary']['edge_count']} edges)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
