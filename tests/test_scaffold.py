"""Tests for the repository scaffold and neutral bootstrap (Task 1)."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
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
