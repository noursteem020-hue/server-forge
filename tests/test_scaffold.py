"""Tests for the repository scaffold and neutral bootstrap (Tasks 1-2)."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import validate  # noqa: E402

PLACEHOLDER = "<RAW_STAGE_00_URL>"


def _bootstrap_text() -> str:
    path = REPO_ROOT / "BOOTSTRAP.md"
    assert path.is_file(), "BOOTSTRAP.md must exist at the repository root"
    return path.read_text(encoding="utf-8")


def test_readme_exists() -> None:
    assert (REPO_ROOT / "README.md").is_file(), "README.md must exist at the repository root"


def test_bootstrap_exists() -> None:
    assert (REPO_ROOT / "BOOTSTRAP.md").is_file(), "BOOTSTRAP.md must exist at the repository root"


def test_bootstrap_has_exactly_one_stage_url_placeholder() -> None:
    text = _bootstrap_text()
    found = text.count(PLACEHOLDER)
    assert found == 1, (
        f"BOOTSTRAP.md must contain exactly one {PLACEHOLDER}; found {found}"
    )


def test_bootstrap_contains_stop_instruction() -> None:
    assert "STOP" in _bootstrap_text(), "BOOTSTRAP.md must contain a STOP instruction"


def test_scaffold_files_are_neutral() -> None:
    for name in ("README.md", "BOOTSTRAP.md"):
        text = (REPO_ROOT / name).read_text(encoding="utf-8")
        assert validate.check_neutrality(text) == [], f"{name} contains a forbidden value"

