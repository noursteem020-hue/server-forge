"""Tests for the generalized command ledger and evidence template (Task 6).

No fleet value, secret, or raw hash is stored in this repository. These tests
only read the neutral ledger/template markdown and exercise the Task 2
neutrality validator. A pattern block is a ``## PATTERN <n>: <topic>`` heading
plus everything up to the next such heading.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import validate  # noqa: E402

LEDGER = REPO_ROOT / "ledger" / "COMMAND-LEDGER.md"
TEMPLATE = REPO_ROOT / "evidence" / "TEMPLATE.md"

PATTERN_HEADING_RE = re.compile(r"^##\s+PATTERN\s+\d+\s*:", re.MULTILINE)
MIN_PATTERNS = 5
REQUIRED_TOPICS = (
    "go frame",
    "read-only gate",
    "hidden transfer",
    "serve syntax",
    "crlf strip",
    "guardian restart",
)
EVIDENCE_FIELDS = ("stage_id", "utc", "sha_before", "sha_after", "rollback")


def _ledger_text() -> str:
    assert LEDGER.is_file(), (
        f"missing ledger file: {LEDGER.relative_to(REPO_ROOT).as_posix()}"
    )
    return LEDGER.read_text(encoding="utf-8")


def _pattern_blocks(text: str) -> list[str]:
    matches = list(PATTERN_HEADING_RE.finditer(text))
    blocks: list[str] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append(text[match.start():end])
    return blocks


def test_ledger_is_neutral() -> None:
    assert validate.check_neutrality(_ledger_text()) == [], "ledger is not neutral"


def test_ledger_has_at_least_five_pattern_blocks() -> None:
    blocks = _pattern_blocks(_ledger_text())
    assert len(blocks) >= MIN_PATTERNS, (
        f"ledger must contain at least {MIN_PATTERNS} pattern blocks, found {len(blocks)}"
    )


def test_each_pattern_block_has_sha256sum_verification() -> None:
    blocks = _pattern_blocks(_ledger_text())
    assert blocks, "no pattern blocks found"
    for number, block in enumerate(blocks, start=1):
        assert "sha256sum" in block, (
            f"pattern block {number} is missing a sha256sum verification line"
        )


def test_ledger_covers_required_topics() -> None:
    lowered = _ledger_text().lower()
    for topic in REQUIRED_TOPICS:
        assert topic in lowered, f"ledger must document the '{topic}' pattern"


def test_evidence_template_is_neutral_and_complete() -> None:
    assert TEMPLATE.is_file(), (
        f"missing template file: {TEMPLATE.relative_to(REPO_ROOT).as_posix()}"
    )
    text = TEMPLATE.read_text(encoding="utf-8")
    assert validate.check_neutrality(text) == [], "evidence template is not neutral"
    lowered = text.lower()
    for field in EVIDENCE_FIELDS:
        assert field in lowered, f"evidence template must define '{field}'"
