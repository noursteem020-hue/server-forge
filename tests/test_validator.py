"""Contract and neutrality validator tests (Task 2).

No raw fleet value is ever stored in this repository. The neutrality probe
below injects a transient digest at runtime instead of embedding a real token.
"""

import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import validate  # noqa: E402

VALID_STAGE = """--- ROLE
You are the executor on a freshly prepared machine.

--- TASK
Run the read-only preflight checks in the order listed below.

--- RULES
- Use only local read-only commands.
- Paste exact measured output; never invent a value.
- All artifacts are English-only.

--- GO
Authorized scope: the read-only commands in TASK ONLY.
Write scope: ZERO files
EXPECTED=<measure-now>

--- REPORT
Print each measured value, then STOP and wait for a fresh GO.
"""


def test_every_stage_has_single_write_scope() -> None:
    assert validate.check_stage_contract(VALID_STAGE) == []

    missing_go = VALID_STAGE.replace("--- GO\n", "")
    violations = validate.check_stage_contract(missing_go)
    assert violations, "a stage without a GO section must be rejected"
    assert any("GO" in v for v in violations), violations

    two_scopes = VALID_STAGE.replace(
        "Write scope: ZERO files\n",
        "Write scope: ZERO files\nWrite scope: /tmp/extra.txt\n",
    )
    violations = validate.check_stage_contract(two_scopes)
    assert violations, "a stage with two Write scope lines must be rejected"
    assert any("Write scope" in v for v in violations), violations


def test_stage_00_passes_contract() -> None:
    stage = (REPO_ROOT / "stages" / "00-preflight.md").read_text(encoding="utf-8")
    assert validate.check_stage_contract(stage) == []
    assert stage.count("Write scope:") == 1
    assert "--- GO" in stage
    assert "STOP" in stage


def test_public_files_are_neutral() -> None:
    public_paths = [REPO_ROOT / "README.md", REPO_ROOT / "BOOTSTRAP.md"]
    stages_dir = REPO_ROOT / "stages"
    if stages_dir.is_dir():
        public_paths.extend(sorted(stages_dir.glob("*.md")))
    for path in public_paths:
        text = path.read_text(encoding="utf-8")
        assert validate.check_neutrality(text) == [], f"{path.name} is not neutral"

    # A string whose sha256 is in FORBIDDEN_DIGESTS must be flagged. Use a
    # transient probe digest so no real fleet value is persisted in this repo.
    sentinel = "SERVER_FORGE_NEUTRALITY_PROBE"
    probe_digest = hashlib.sha256(sentinel.encode("utf-8")).hexdigest()
    original = validate.FORBIDDEN_DIGESTS
    try:
        validate.FORBIDDEN_DIGESTS = set(original) | {probe_digest}
        assert validate.check_neutrality(f"probe value: {sentinel}"), (
            "a value with a forbidden sha256 must be flagged"
        )
        assert validate.check_neutrality("a fully neutral string") == []
    finally:
        validate.FORBIDDEN_DIGESTS = original
