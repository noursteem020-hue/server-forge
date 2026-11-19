"""Neutrality and stage-contract validators for Server Forge (Task 2).

The public repository stores only sha256 digests of sensitive fleet values.
No raw token, IP address, hostname, project name, or hash fragment is present
in this file or anywhere else in the tracked tree.
"""

from __future__ import annotations

import hashlib
import re

# sha256 digests of locally-held sensitive values, computed offline when this
# validator was introduced. Digests only - never the plaintext values.
FORBIDDEN_DIGESTS: frozenset[str] = frozenset({
    "48cb37d59b344c2c8210e4a0a6e208efbdb50b23cbbb55bf9f721fcf0191c2f5",
    "d0bf901de63b2ac9f0a2982a3bc2924fbc22a99f19dd683d5922c0590296f53f",
    "02eec536fbf3a2dd8d610fd1419ecc88c16d5c19fad6a2a0cf126aa67f3d0e15",
    "2f8e24dc23d6c5fa81deaba81232d9eafbcb6ac0f4b6317f77e0ddf3bae16de1",
    "a7c0b65129833f376d18f37b2c5b652cf94ea73dce1fd83da300d695aae5ae47",
    "c7dde1b91c06be5dc35740ec2bfc02342427107518590caeda8aeacc053b5913",
    "ec0ad2b11d153efa2845708c4ad5db3e5105650def5791aa4cac07b98d6a2a2c",
    "afec5d6f7b3252bf0a2c3bcdfedfee27649033889b9a66d071ff128b6275ef0b",
    "cd79ca01abc4c00531548b77868901334c317d4765fed75b16c538c64fe74ea9",
    "78f4e58ffb9c18aaf93de1ddd8f24ac338e4488cfd6768cf7f0dda09b5c43718",
    "04f39dc5af1df5f1583c9c0b8fe6288eeb3082fe81608a0daf86e96fee87778a",
    "9aac48aec760ab7e7e1c8eb161596a44604bb4cd82c27cc73affeea254fa0624",
    "a55e976604708bb70e2c0486622779f360e99970140d6f09f645936c67dee5fe",
    "6216bdd1d53ea66e71132861a336e54fd75ab56c20fa8c3f0f2562cac43e8e05",
    "35302e177fd6c185b231fa3c86644737fe5d7d52e7b05fcda7cdf9a01e966871",
})

SECTIONS: tuple[str, ...] = ("ROLE", "TASK", "RULES", "GO", "REPORT")

_SECTION_RE = re.compile(
    r"^[ \t]*---[ \t]*(ROLE|TASK|RULES|GO|REPORT)[ \t]*$", re.MULTILINE
)
_TOKEN_RE = re.compile(r"[A-Za-z0-9._-]+")


def check_stage_contract(text: str) -> list[str]:
    """Return contract violations for a stage document; empty means valid.

    A document with no ``--- <SECTION>`` markers is ordinary repository
    markdown and is not subject to the stage contract. A document that uses
    stage markers must define all five sections exactly once and must contain
    exactly one ``Write scope:`` line.
    """
    violations: list[str] = []
    found = _SECTION_RE.findall(text)
    if not found:
        return violations

    for section in SECTIONS:
        count = found.count(section)
        if count == 0:
            violations.append(f"missing required section: --- {section}")
        elif count > 1:
            violations.append(f"duplicate section: --- {section} (found {count})")

    write_scope_count = sum(1 for line in text.splitlines() if "Write scope:" in line)
    if write_scope_count != 1:
        violations.append(
            f"exactly one 'Write scope:' line required, found {write_scope_count}"
        )
    return violations


def _candidates(text: str):
    """Yield the whole text, each line, and each verbatim token in the text."""
    whole = text.strip()
    if whole:
        yield whole
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            yield stripped
    for match in _TOKEN_RE.finditer(text):
        token = match.group(0)
        yield token
        trimmed = token.strip("._-")
        if trimmed and trimmed != token:
            yield trimmed


def check_neutrality(text: str) -> list[str]:
    """Return one violation per distinct value whose sha256 is forbidden.

    Detection is digest-based, so the forbidden plaintext values never have to
    be stored in the public repository. Only the offending digest prefix is
    reported; the matched value itself is never echoed.
    """
    violations: list[str] = []
    seen: set[str] = set()
    for candidate in _candidates(text):
        if candidate in seen:
            continue
        seen.add(candidate)
        digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()
        if digest in FORBIDDEN_DIGESTS:
            violations.append(
                f"forbidden value present (sha256 {digest[:12]}...); "
                "replace with a placeholder"
            )
    return violations
