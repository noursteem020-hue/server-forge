"""Run both validators over every tracked markdown file (Task 2).

Prints one line per violation and exits 1 if any violation is found.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import validate  # noqa: E402


def tracked_markdown(repo_root: Path) -> list[Path]:
    """Return tracked .md files, falling back to a filesystem walk."""
    result = subprocess.run(
        ["git", "ls-files", "-z", "*.md"],
        cwd=str(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return sorted(
            path
            for path in repo_root.rglob("*.md")
            if ".git" not in path.parts and ".superpowers" not in path.parts
        )
    return [
        repo_root / name.decode("utf-8")
        for name in result.stdout.split(b"\0")
        if name
    ]


def main() -> int:
    repo_root = TOOLS_DIR.parent
    violations = 0
    for path in tracked_markdown(repo_root):
        rel = path.relative_to(repo_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"{rel}: UNREADABLE: {exc}")
            violations += 1
            continue
        for violation in validate.check_neutrality(text):
            print(f"{rel}: NEUTRALITY: {violation}")
            violations += 1
        for violation in validate.check_stage_contract(text):
            print(f"{rel}: CONTRACT: {violation}")
            violations += 1

    if violations:
        print(f"check_all: {violations} violation(s)")
        return 1
    print("check_all: clean - no violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
