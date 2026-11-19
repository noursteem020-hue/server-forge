"""Tests for the two shipped skills (Task 5).

No fleet value, secret, or raw token is stored in this repository. These tests
only read the neutral SKILL.md prompt contracts and exercise the Task 2
validators. A skill is a prompt contract: it must be invocable by name, carry a
documented trigger, and pass the neutrality validator.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import validate  # noqa: E402

SKILLS = {
    "server-forge": REPO_ROOT / "skills" / "server-forge" / "SKILL.md",
    "server-code-writer": REPO_ROOT / "skills" / "server-code-writer" / "SKILL.md",
}

# A trigger phrase is what makes a skill invocable by name from a prompt.
TRIGGER_RE = re.compile(r"use\s+(?:this\s+)?when|invoke\s+when|trigger", re.IGNORECASE)
FIVE_SECTIONS = ("ROLE", "TASK", "RULES", "GO", "REPORT")


def _skill_text(name: str) -> str:
    path = SKILLS[name]
    assert path.is_file(), f"missing skill file: {path.relative_to(REPO_ROOT).as_posix()}"
    return path.read_text(encoding="utf-8")


def _frontmatter(text: str) -> str:
    assert text.startswith("---"), "SKILL.md must start with a --- frontmatter delimiter"
    end = text.find("\n---", 3)
    assert end != -1, "SKILL.md must close its YAML frontmatter with a --- line"
    return text[:end]


def test_skills_have_invocation_contract() -> None:
    """Each SKILL.md starts with ---, has name:/description:, names a trigger."""
    for name, path in SKILLS.items():
        text = _skill_text(name)
        assert text.startswith("---"), f"{name}: file must start with ---"
        frontmatter = _frontmatter(text)
        assert re.search(r"^name\s*:", frontmatter, re.MULTILINE), (
            f"{name}: frontmatter must contain name:"
        )
        assert re.search(r"^description\s*:", frontmatter, re.MULTILINE), (
            f"{name}: frontmatter must contain description:"
        )
        declared = re.search(r"^name\s*:\s*(\S+)", frontmatter, re.MULTILINE)
        assert declared is not None and declared.group(1) == name, (
            f"{name}: frontmatter name must equal the skill directory name '{name}'"
        )
        assert TRIGGER_RE.search(frontmatter), (
            f"{name}: description must name at least one trigger phrase"
        )


def test_skill_files_are_neutral() -> None:
    """No forbidden fleet value may appear in either public SKILL.md."""
    for name in SKILLS:
        text = _skill_text(name)
        assert validate.check_neutrality(text) == [], f"{name}: not neutral"


def test_server_forge_stage_contract() -> None:
    """server-forge drives the stage loop and emits five-section owner gates."""
    text = _skill_text("server-forge")
    lowered = text.lower()

    assert "stage loop" in lowered, "server-forge must describe a stage loop"
    for section in FIVE_SECTIONS:
        assert section in text, f"server-forge must document the {section} section"
    assert "five-section" in lowered or "five section" in lowered, (
        "server-forge must name the five-section GO format"
    )
    assert "fresh go" in lowered, (
        "server-forge must require a fresh GO before any mutation"
    )
    assert "refuse" in lowered, (
        "server-forge must refuse mutation without a fresh GO"
    )
    assert "write scope" in lowered, (
        "server-forge must name exactly one write path per GO"
    )
    assert "stop" in lowered, "server-forge must STOP and wait at each owner gate"


def test_server_code_writer_change_contract() -> None:
    """server-code-writer performs one-file changes with backup and checks."""
    text = _skill_text("server-code-writer")
    lowered = text.lower()

    assert "one file per go" in lowered, "server-code-writer must allow one file per GO"
    for token in ("backup", "patch", "bash -n", "py_compile", "atomic", "verification"):
        assert token in lowered, f"server-code-writer must document '{token}'"
    assert "rollback" in lowered, "server-code-writer must document rollback"
