# Handover — Server Forge

## Repository

- URL: https://github.com/noursteem020-hue/server-forge
- Visibility: public
- Default branch: `main`
- Bootstrap entry point: `BOOTSTRAP.md`
- Stage 00 raw URL: https://raw.githubusercontent.com/noursteem020-hue/server-forge/main/stages/00-preflight.md

## Start a build in the new platform account

Copy the entire block between the BEGIN and END markers below and paste it as the first message to the platform agent in a new session. Do not paste the marker lines themselves. This is the only prompt needed to begin; after stage 00, each stage ends with one `GO` block to paste for approval.

```text
--- BEGIN PASTE ---
ROLE: You are the executor inside a fresh machine being prepared by Server Forge. You run as root and you follow the stage contract below exactly.

TASK: Perform one read-only preflight. Fetch the stage 00 instruction file from:

  https://raw.githubusercontent.com/noursteem020-hue/server-forge/main/stages/00-preflight.md

Read it and run only the read-only checks it lists (identity, privilege, disk cleanliness, and listening ports). Print the cleanliness gate exactly as stage 00 defines it. Write nothing. Make no change to the machine.

RULES:
- This is a read-only stage. Create, modify, or delete no file. Start no service. Install no package.
- Run only the commands stage 00 lists, in order, and paste their exact output.
- All artifacts and reports are English-only.
- Never print a secret, a token, or a password. If a sensitive value must be acknowledged, show only that it exists.
- If any preflight check fails, do not continue and do not retry. Report the failing check and wait.
- Do not invent a URL, a hash, or a result. If a value cannot be measured, write `MEASURE` for it.

GO: Authorized scope: the read-only commands in stage 00 ONLY. Write scope: ZERO files — no write path is authorized in this stage. Source of stage instructions: the single raw URL above.

REPORT: Print the cleanliness gate and the exact output of each read-only check. Then print the word STOP and wait for the next GO. Ask nothing else.
--- END PASTE ---
```

STOP. Nothing is written in this stage. Do not proceed to any build step until a fresh `GO` is pasted.

## Stage flow

1. Paste the block above in a new platform session. The agent fetches stage 00 and runs only read-only checks.
2. Review the printed gate. Approve by pasting the single `GO` block the agent emits to authorize the next stage.
3. Repeat for stages 00 through 05. Each stage writes nothing until a fresh `GO` names one action and one write path; a failed gate stops and waits.

The full prompt contract lives in `BOOTSTRAP.md`; the numbered prompts live in `stages/`; the two skills (`server-forge`, `server-code-writer`) ship in `skills/`.

## Verification at publish time

- `python -m pytest -q` — 33 passed.
- `python tools/check_all.py` — `check_all: clean - no violations`.
- `git ls-tree origin/main` — all product files present; no `docs/superpowers/` (local-only process artifacts, untracked and gitignored).

## Owner action

Creating the new server itself is an owner action: paste the block above in the new platform account and drive the gates. This repository is documentation and prompt contracts only; it performs no build on its own.
