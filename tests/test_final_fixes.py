"""Covering tests for the final whole-branch review findings.

CRITICAL 1: a stage must actually create the atomic snapshot that later stages
consume. CRITICAL 2: the persistent stage marker must be initialized and read /
advanced by every mutating stage. IMPORTANT 4: the marker's LAST_COMPLETED field
must be numeric so stage 05's LAST_COMPLETED + 1 arithmetic is defined.

These tests read only the neutral stage documents and exercise the Task 2
validators; no fleet value, secret, or raw token is stored in this repository.
"""

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import validate  # noqa: E402

ALL_STAGES = (
    "00-preflight.md",
    "01-layout-secrets.md",
    "02-chroot-desktop.md",
    "03-gateway-guardian.md",
    "04-snapshot-verify.md",
    "05-resume.md",
)
MUTATING_STAGES = ALL_STAGES[1:]  # stages 01-05

SNAPSHOT = "/workspace/srv/snapshot/debian13.tar"
SNAPSHOT_SHA = "/workspace/srv/snapshot/debian13.tar.sha256"
MARKER = "/workspace/srv/run/forge-stage.env"
MARKER_BAK = "/workspace/srv/run/forge-stage.env.bak"


def _stage(name: str) -> str:
    path = REPO_ROOT / "stages" / name
    assert path.is_file(), f"missing stage file: stages/{name}"
    return path.read_text(encoding="utf-8")


# --- CRITICAL 1: a stage writes the snapshot ---------------------------------


def test_stage_02_creates_atomic_snapshot() -> None:
    text = _stage("02-chroot-desktop.md")
    assert SNAPSHOT in text, "stage 02 must create the authoritative snapshot artifact"
    assert SNAPSHOT_SHA in text, "stage 02 must write the snapshot sha256 sidecar"
    assert "tar -C / -cf" in text, "stage 02 must archive the chroot with tar"
    assert ".tmp" in text and "mv" in text, (
        "stage 02 must build the snapshot to a temp file and mv it into place atomically"
    )
    assert "sha256sum" in text, "stage 02 must compute the snapshot sha256"
    assert "stage-02 evidence" in text.lower() or "stage evidence" in text.lower(), (
        "stage 02 must record the snapshot digest in its evidence"
    )


@pytest.mark.parametrize("name", ("02-chroot-desktop.md", "03-gateway-guardian.md",
                                  "04-snapshot-verify.md", "05-resume.md"))
def test_snapshot_artifact_is_referenced_by_build_chain(name: str) -> None:
    text = _stage(name)
    assert SNAPSHOT in text, f"{name} must reference the stage-02 snapshot artifact"


def test_stage_03_verifies_snapshot_before_launch() -> None:
    text = _stage("03-gateway-guardian.md")
    lowered = text.lower()
    assert SNAPSHOT in text and SNAPSHOT_SHA in text
    assert "02-chroot-desktop.md" in text, (
        "stage 03 must compare the snapshot digest to the stage-02 evidence"
    )
    assert "stop before launching any service" in lowered, (
        "stage 03 must stop before service launch when the snapshot is absent"
    )


# --- CRITICAL 2: marker initialized and advanced by every mutating stage -----


@pytest.mark.parametrize("name", MUTATING_STAGES)
def test_every_mutating_stage_reads_and_advances_marker(name: str) -> None:
    text = _stage(name)
    assert validate.check_stage_contract(text) == [], f"{name} violates the stage contract"
    assert validate.check_neutrality(text) == [], f"{name} is not neutral"
    assert sum(1 for line in text.splitlines() if "Write scope:" in line) == 1, (
        f"{name} must keep exactly one Write scope line"
    )

    assert MARKER in text, f"{name} must reference the persistent marker"
    assert MARKER_BAK in text, f"{name} must back up the marker with a timestamped .bak"
    for field in ("STAGE_ID", "LAST_COMPLETED", "RESTART_AT_00=NO", "UPDATED_UTC"):
        assert field in text, f"{name} must handle the {field} marker field"

    lowered = text.lower()
    assert "read" in lowered, f"{name} must read the marker before writing"
    assert "atomically" in lowered or "atomic" in lowered, (
        f"{name} must replace the marker atomically"
    )
    assert "advance" in lowered, f"{name} must advance the marker"


def test_stage_01_initializes_marker() -> None:
    text = _stage("01-layout-secrets.md")
    lowered = text.lower()
    assert "initializ" in lowered, "stage 01 must initialize the marker on a fresh build"
    assert "STAGE_ID=01" in text and "LAST_COMPLETED=1" in text
    assert "STAGE_LABEL=LAYOUT_SECRETS" in text


def test_stage_04_handles_missing_marker_explicitly() -> None:
    text = _stage("04-snapshot-verify.md")
    lowered = text.lower()
    assert "missing" in lowered and "marker" in lowered
    assert "stop" in lowered, "stage 04 must STOP on a missing marker"
    assert "stage 01 initializes it" in lowered or "stage 01 initializes" in lowered, (
        "stage 04 must name where the marker comes from rather than creating one"
    )
    assert "not a signal to create" in lowered or "create one" in lowered


# --- IMPORTANT 4: numeric LAST_COMPLETED arithmetic --------------------------


def test_last_completed_is_numeric_in_every_stage() -> None:
    for name in MUTATING_STAGES:
        text = _stage(name)
        values = re.findall(r"LAST_COMPLETED=([A-Za-z0-9_]+)", text)
        assert values, f"{name} must write a LAST_COMPLETED value"
        for value in values:
            assert value.isdigit(), (
                f"{name} must keep LAST_COMPLETED numeric; found non-numeric {value!r}"
            )
    assert "LAST_COMPLETED=VERIFY" not in _stage("04-snapshot-verify.md"), (
        "stage 04 must not put a human label in LAST_COMPLETED"
    )


def test_numeric_stage_arithmetic_is_pinned() -> None:
    stage_04 = _stage("04-snapshot-verify.md")
    stage_05 = _stage("05-resume.md")
    assert "LAST_COMPLETED=4" in stage_04
    assert "LAST_COMPLETED=5" in stage_05
    assert "LAST_COMPLETED + 1" in stage_05
    assert "NEXT=$((LAST_COMPLETED + 1))" in stage_05, (
        "resume must compute the next stage with numeric arithmetic"
    )
    assert "STAGE_LABEL=VERIFY" in stage_04 and "STAGE_LABEL=RESUME" in stage_05, (
        "human labels must stay in the separate STAGE_LABEL field"
    )
    assert "never add to a human label" in stage_05.lower()


# --- All stages still satisfy the invariants --------------------------------


@pytest.mark.parametrize("name", ALL_STAGES)
def test_all_stages_pass_validators(name: str) -> None:
    text = _stage(name)
    assert validate.check_stage_contract(text) == []
    assert validate.check_neutrality(text) == []
