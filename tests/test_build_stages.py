"""Tests for build stages 01-03 (Task 3).

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
    "01-layout-secrets.md",
    "02-chroot-desktop.md",
    "03-gateway-guardian.md",
)

PUBLISHED_PORT = "6080"
LOOPBACK_PORTS = ("6081", "5901", "1055")


def _stage_text(stage_name: str) -> str:
    path = REPO_ROOT / "stages" / stage_name
    assert path.is_file(), f"missing stage file: stages/{stage_name}"
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("stage_name", STAGE_NAMES)
def test_stage_passes_contract(stage_name: str) -> None:
    assert validate.check_stage_contract(_stage_text(stage_name)) == [], (
        f"{stage_name} violates the five-section stage contract"
    )


@pytest.mark.parametrize("stage_name", STAGE_NAMES)
def test_stage_is_neutral(stage_name: str) -> None:
    assert validate.check_neutrality(_stage_text(stage_name)) == [], (
        f"{stage_name} contains a forbidden value"
    )


@pytest.mark.parametrize("stage_name", STAGE_NAMES)
def test_stage_has_exactly_one_write_scope(stage_name: str) -> None:
    text = _stage_text(stage_name)
    found = sum(1 for line in text.splitlines() if "Write scope:" in line)
    assert found == 1, f"{stage_name} must have exactly one Write scope line; found {found}"


@pytest.mark.parametrize("stage_name", STAGE_NAMES)
def test_stage_port_topology(stage_name: str) -> None:
    text = _stage_text(stage_name)
    lowered = text.lower()
    assert PUBLISHED_PORT in text, (
        f"{stage_name} must name the published port {PUBLISHED_PORT}"
    )
    for port in LOOPBACK_PORTS:
        assert port in text, f"{stage_name} must name loopback port {port}"
    assert "loopback" in lowered, f"{stage_name} must describe loopback binding"
    assert "publish" in lowered, f"{stage_name} must describe the published port"
