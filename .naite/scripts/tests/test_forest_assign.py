from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


def test_override_only_tree_is_preserved(tmp_path: Path) -> None:
    root = tmp_path / "vault"
    scripts = root / ".naite" / "scripts"
    ontology = root / ".naite" / "ontology"
    forest = root / ".naite" / "forest"
    scripts.mkdir(parents=True)
    ontology.mkdir(parents=True)
    forest.mkdir(parents=True)

    source = Path(__file__).resolve().parents[1] / "forest-assign.py"
    target = scripts / "forest-assign.py"
    shutil.copy2(source, target)

    ml_slugs = [f"ml-concept-{i}" for i in range(6)]
    pages = [
        *[
            {
                "slug": slug,
                "kind": "concept",
                "special": False,
                "domains": ["ml"],
                "subject": ["ml"],
            }
            for slug in ml_slugs
        ],
        {
            "slug": "naite-decision",
            "kind": "decision",
            "special": False,
            "domains": ["neutral"],
            "subject": ["neutral/agents"],
        },
    ]
    (ontology / "tree-manifest.json").write_text(
        json.dumps({"pages": pages}), encoding="utf-8"
    )
    dense_ml_neighbors = {
        slug: [other for other in ml_slugs if other != slug] + ["naite-decision"]
        for slug in ml_slugs
    }
    dense_ml_neighbors["naite-decision"] = ml_slugs
    (ontology / "tree-dependencies.json").write_text(
        json.dumps({"outbound": dense_ml_neighbors, "relation_edges": []}),
        encoding="utf-8",
    )
    (forest / "forest-config.json").write_text(
        json.dumps(
            {
                "domain_to_tree": {
                    "ml": "machine-learning",
                    "neutral": "machine-learning",
                },
                "neutral_domains": ["neutral"],
                "tree_overrides": {"naite-decision": "naite"},
            }
        ),
        encoding="utf-8",
    )

    subprocess.run(
        [sys.executable, str(target), "--alpha", "0.01", "--write"],
        check=True,
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    generated = json.loads(
        (ontology / "forest-manifest.json").read_text(encoding="utf-8")
    )
    assert generated["tree_count"] == 2
    assert generated["page_to_tree"]["naite-decision"] == "naite"
