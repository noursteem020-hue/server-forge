"""Tests for the verification / kill-switch and resume stages (Task 4).

No fleet value, secret, or raw token is stored in this repository. These tests
only read the neutral stage documents and exercise the Task 2 validators.
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import validate  # noqa: E402

STAGE_NAMES = (
    "04-snapshot-verify.md",
    "05-resume.md",
)

MARKER = "forge-stage.env"
BACKUP = "forge-stage.env.bak"
RESTORE_MARKER = "RESTORE_MARKER"
HEALTH_OK = "healthz 200"
HEALTH_DENIED = "401"


def _stage_text(stage_name: str) -> str:
    path = REPO_ROOT / "stages" / stage_name
    assert path.is_file(), f"missing stage file: stages/{stage_name}"
    return path.read_text(encoding="utf-8")


def _assert_common_stage_contract(text: str, stage_name: str) -> None:
    """Assertions required of BOTH lifecycle stages by the task brief."""
    assert validate.check_stage_contract(text) == [], (
        f"{stage_name} violates the five-section stage contract"
    )
    assert validate.check_neutrality(text) == [], (
        f"{stage_name} contains a forbidden value"
    )
    write_scope_lines = sum(1 for line in text.splitlines() if "Write scope:" in line)
    assert write_scope_lines == 1, (
        f"{stage_name} must have exactly one Write scope line; found {write_scope_lines}"
    )
    assert MARKER in text, f"{stage_name} must define the {MARKER} marker"
    assert "STOP" in text, f"{stage_name} must carry a STOP clause"
    assert HEALTH_OK in text, f"{stage_name} must assert '{HEALTH_OK}'"
    assert HEALTH_DENIED in text, f"{stage_name} must assert '{HEALTH_DENIED}'"
    assert RESTORE_MARKER in text, (
        f"{stage_name} must include a restore-marker check ({RESTORE_MARKER})"
    )


@pytest.mark.parametrize("stage_name", STAGE_NAMES)
def test_stages_fail_closed(stage_name: str) -> None:
    """Both stages must pass the validators and fail closed with STOP/no retry."""
    text = _stage_text(stage_name)
    _assert_common_stage_contract(text, stage_name)

    lowered = text.lower()
    assert "fail closed" in lowered, f"{stage_name} must state a fail-closed rule"
    assert "no retry" in lowered, f"{stage_name} must forbid retries"
    assert text.count("--- GO") == 1, f"{stage_name} must contain exactly one GO section"
    # A hard stop must appear in the REPORT and wait for a fresh GO.
    assert "STOP" in text and "fresh GO" in text, (
        f"{stage_name} must end with STOP and wait for a fresh GO"
    )


@pytest.mark.parametrize("stage_name", STAGE_NAMES)
def test_resume_marker_contract(stage_name: str) -> None:
    """Both stages must define the persistent marker, .bak and resume-from rules."""
    text = _stage_text(stage_name)
    _assert_common_stage_contract(text, stage_name)

    assert BACKUP in text, f"{stage_name} must define the timestamped {BACKUP}"
    assert "STAGE_ID" in text, f"{stage_name} must read/write STAGE_ID"
    assert "LAST_COMPLETED" in text, f"{stage_name} must read/write LAST_COMPLETED"
    assert "RESTART_AT_00=NO" in text, (
        f"{stage_name} must resume from the last completed stage, not stage 00"
    )
    assert "resume" in text.lower(), f"{stage_name} must describe resume behaviour"
