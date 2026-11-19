# Server Forge

Server Forge builds a clean Debian 13 desktop environment on a fresh machine from a single bootstrap prompt. It is a staged, gated builder: every change happens one stage at a time, and nothing is written until you explicitly authorize it.

## What it builds

- A minimal Debian 13 (trixie) base with a lightweight XFCE desktop.
- A local VNC server and websockify bridge bound to the loopback interface.
- A single authenticated gateway that publishes one application port; all other services stay loopback-only.
- Secrets generated at build time into root-only files, never printed and never stored here.
- An atomic snapshot and a repeatable verification pass so a build can be checked and resumed.

## One-command usage

1. Copy the entire contents of `BOOTSTRAP.md` — the single paste-ready entry.
2. Paste it as the first message to your platform agent in a new session.
3. The agent fetches stage 00, runs the read-only cleanliness gate, prints the result, and stops.
4. Review the gate. When you are satisfied, paste the single `GO` block the agent prints to authorize the next stage.
5. Repeat: each stage ends with one `GO` block and a small evidence report. Nothing is written without a fresh `GO`.

That is the whole interface: one paste to start, then one `GO` per stage.

## Stage contract

Every stage uses the same five-section frame so the agent always knows what it may do:

- `ROLE` — who is executing, in one sentence.
- `TASK` — exactly one action or one file change.
- `RULES` — measured facts; English-only artifacts; no secret is printed.
- `GO` — explicit authorization naming one action and exactly one write path.
- `REPORT` — paste the exact output, ask nothing.

A stage that fails a gate stops, records the reason, and waits for a fresh `GO`. There is no silent retry and no fallback write.

## Repository layout

- `BOOTSTRAP.md` — the single paste that starts a build.
- `stages/` — numbered stage prompts, each ending in one `GO` and one evidence file.
- `skills/` — the builder and post-build code-writing contracts.
- `ledger/` — generalized command patterns with verification checks.
- `evidence/` — the report template each stage fills in.
- `tools/` — validators that enforce neutrality and the stage contract.

## Safety

- Secrets are generated at build time into root-only files; none are stored in this repository.
- Only one application port is ever published; internal services remain on loopback.
- A failed gate stops the build; it is never retried silently.
- All stage-facing text is English-only.
