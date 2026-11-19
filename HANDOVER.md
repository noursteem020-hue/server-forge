# Handover — Server Forge

## Repository

- URL: https://github.com/noursteem020-hue/server-forge
- Visibility: public
- Default branch: `main`
- Bootstrap entry point: `BOOTSTRAP.md` (the single paste-ready prompt)
- Stage 00 raw URL: https://raw.githubusercontent.com/noursteem020-hue/server-forge/main/stages/00-preflight.md

## Start a build in the new platform account

`BOOTSTRAP.md` is the single paste-ready entry. Copy the entire prompt block between its BEGIN and END markers and paste it as the first message to the platform agent in a new session. Do not paste the marker lines themselves. No other file contains a competing paste block; this one block is all you need to begin. After stage 00, each stage ends with one `GO` block to paste for approval.

Refer to `BOOTSTRAP.md` for the exact text. It already names the real public stage 00 raw URL above, so nothing needs substituting before you paste.

## Stage flow

1. Paste the `BOOTSTRAP.md` block in a new platform session. The agent fetches stage 00 and runs only read-only checks.
2. Review the printed gate. Approve by pasting the single `GO` block the agent emits to authorize the next stage.
3. Repeat for stages 00 through 05. Each stage writes nothing until a fresh `GO` names one action and one write path; a failed gate stops and waits.

Stage 02 creates the authoritative atomic snapshot at `/workspace/srv/snapshot/debian13.tar` (digest in the .sha256 sidecar) that stages 03, 04 and 05 consume. Every mutating stage 01-05 reads and advances the persistent marker at `/workspace/srv/run/forge-stage.env` with a timestamped backup; `LAST_COMPLETED` is numeric so stage 05's resume arithmetic is defined.

The full prompt contract lives in `BOOTSTRAP.md`; the numbered prompts live in `stages/`; the two skills (`server-forge`, `server-code-writer`) ship in `skills/`.

## Verification at publish time

- `python -m pytest -q`
- `python tools/check_all.py` — `check_all: clean - no violations`.
- `git ls-tree origin/main` — all product files present; no `docs/superpowers/` (local-only process artifacts, untracked and gitignored).

## Owner action

Creating the new server itself is an owner action: paste the `BOOTSTRAP.md` block in the new platform account and drive the gates. This repository is documentation and prompt contracts only; it performs no build on its own.
