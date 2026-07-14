from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace


MODULE_PATH = Path(__file__).resolve().parents[1] / "lint-ontology.py"
SPEC = importlib.util.spec_from_file_location("lint_ontology", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
LINT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LINT)


def test_em_dash_is_blocked_in_general_page_body(tmp_path: Path) -> None:
    page = tmp_path / "example.md"
    page.write_text(
        "---\nkind: insight\n---\n# Example\n\n앞 문장—뒤 문장\n\n## Source\n- title—subtitle\n",
        encoding="utf-8",
    )

    findings = LINT.find_output_quality_findings(page)

    assert findings == [(6, "em-dash", "—")]


def test_em_dash_in_source_block_is_not_body_violation(tmp_path: Path) -> None:
    page = tmp_path / "example.md"
    page.write_text(
        "---\nkind: source-record\n---\n# Example\n\n본문은 일반 문장입니다.\n\n## Source\n- title—subtitle\n",
        encoding="utf-8",
    )

    assert LINT.find_output_quality_findings(page) == []


def test_em_dash_is_blocked_in_special_page_without_frontmatter(tmp_path: Path) -> None:
    page = tmp_path / "trunk.md"
    page.write_text("# Tree Trunk\n\ncourse—description\n", encoding="utf-8")

    assert LINT.find_output_quality_findings(page) == [(3, "em-dash", "—")]
    assert LINT.OUTPUT_QUALITY_SPECIALS == {"trunk.md", "rings.md", "seeds.md"}


def test_h1_title_and_inline_code_are_not_body_violations(tmp_path: Path) -> None:
    page = tmp_path / "example.md"
    page.write_text(
        "---\nkind: insight\n---\n# Original—Title\n\n`left—right`는 보존할 literal입니다.\n\n## Source\n- title—subtitle\n",
        encoding="utf-8",
    )

    assert LINT.find_output_quality_findings(page) == []


def test_source_heading_in_code_fence_does_not_truncate_body(tmp_path: Path) -> None:
    page = tmp_path / "example.md"
    page.write_text(
        "---\nkind: insight\n---\n# Example\n\n```markdown\n## Source\n```\n\n앞 문장—뒤 문장\n\n## Source\n- title—subtitle\n",
        encoding="utf-8",
    )

    assert LINT.find_output_quality_findings(page) == [(10, "em-dash", "—")]


def test_non_trailing_source_heading_does_not_truncate_body(tmp_path: Path) -> None:
    page = tmp_path / "example.md"
    page.write_text(
        "---\nkind: insight\n---\n# Example\n\n## Source\n\n## Continued\n\n앞 문장—뒤 문장\n",
        encoding="utf-8",
    )

    assert LINT.find_output_quality_findings(page) == [(10, "em-dash", "—")]


def test_new_rings_file_is_checked_without_git_baseline(tmp_path: Path) -> None:
    page = tmp_path / "rings.md"
    page.write_text("# Wiki Log\n\n새 기록—설명\n", encoding="utf-8")

    assert LINT.find_rings_output_quality_findings(page) == [(3, "em-dash", "—")]


def test_tracked_rings_diff_is_compared_with_head(tmp_path: Path, monkeypatch) -> None:
    page = tmp_path / "tree" / "rings.md"
    page.parent.mkdir()
    page.write_text("# Wiki Log\n\nnew entry\n", encoding="utf-8")
    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        if "ls-files" in args:
            return SimpleNamespace(returncode=0, stdout="tree/rings.md\n")
        return SimpleNamespace(returncode=0, stdout="@@ -2,0 +3 @@\n+new entry\n")

    monkeypatch.setattr(LINT, "NAITE_ROOT", tmp_path)
    monkeypatch.setattr(LINT.subprocess, "run", fake_run)

    assert LINT.git_added_line_numbers(page) == {3}
    assert calls[1][4] == "HEAD"
