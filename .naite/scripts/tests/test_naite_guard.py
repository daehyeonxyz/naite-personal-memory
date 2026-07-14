from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


def find_bash() -> str | None:
    direct = shutil.which("bash")
    if direct is not None:
        return direct
    git = shutil.which("git")
    if git is None:
        return None
    candidate = Path(git).resolve().parent.parent / "bin" / "bash.exe"
    return str(candidate) if candidate.exists() else None


BASH = find_bash()
GUARD = Path(__file__).resolve().parents[2] / "hooks" / "_naite_guard.sh"


def scan(text: str) -> int:
    if BASH is None:
        pytest.skip("bash is required to exercise the shared hook implementation")
    script = "\n".join(
        [
            "fail=0",
            "err() { fail=1; }",
            f'source "{GUARD.as_posix()}"',
            'naite_scan_content "$1"',
            'exit "$fail"',
        ]
    )
    result = subprocess.run([BASH, "-c", script, "_", text], cwd=GUARD.parents[2])
    return result.returncode


def test_risk_free_slug_is_not_a_secret() -> None:
    assert scan("+ [[course-risk-free-asset-and-one-fund-theorem]]") == 0


def test_openai_shaped_token_is_still_rejected() -> None:
    fake_value = "sk-" + "a" * 24
    assert scan("+ api_key" + "=" + fake_value) == 1
