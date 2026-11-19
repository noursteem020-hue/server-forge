# Server Forge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a public, neutral GitHub tool that creates SERVER-4 from one platform-chat command with owner GO gates at every mutating stage.

**Architecture:** A stage-driven prompt system: `BOOTSTRAP.md` fetches stage files from the public repo, each stage emits one ready GO block and one evidence file, and a resumable stage marker lives on the persistent volume. Two skills encode the creation and code-writing contracts. All fleet-specific values stay in the coordinator's local vault; the public repo contains only generalized patterns.

**Tech Stack:** Markdown prompt contracts, Python 3 stdlib validators, pytest, GitHub CLI (`gh`), git.

**Spec:** `docs/superpowers/specs/2026-11-19-server-forge-design.md`

## Global Constraints

- Public repo `noursteem020-hue/server-forge`; no fleet architecture, IP, hostname, project name, or secret in any public file (including tests).
- Stage contract: exactly `ROLE / TASK / RULES / GO / REPORT`, one action, one write path per GO.
- GO form: `Authorized scope: the one command in TASK ONLY. Write scope: exactly ONE file — <path>.` plus `EXPECTED=<measure-now>`.
- Secrets generated at build into mode-600 files under `/workspace/srv/secrets/`; never printed, never in argv, never in a snapshot.
- Only port `6080` published; VNC `5901`, websockify `6081`, SOCKS `1055` stay loopback.
- `tailscale serve --bg --http=<PORT> <PORT>` — target is the local port number.
- Persistent root `/workspace/srv`; stage file `/workspace/srv/run/forge-stage.env` + timestamped `.bak`.
- Windows-generated artifacts use LF or are passed through `tr -d '\r'`.
- English-only inside all server-facing files; Arabic only in chat and vault.

## Review Focus

1. A public file accidentally contains a real fleet IP/hostname/project name — expect neutrality validator to fail before push. Test: `test_public_files_are_neutral` in Task 2.
2. A stage prompt omits one of the five required sections or names two write paths — expect contract validator to fail. Test: `test_every_stage_has_single_write_scope` in Task 2.
3. A HARD STOP is skipped or retried — expect stage text to contain the stop clause and no retry loop. Test: `test_stages_fail_closed` in Task 4.
4. A resumed session restarts at stage 00 — expect the stage marker contract to define resume from the last completed stage. Test: `test_resume_marker_contract` in Task 4.
5. Skills are documented but not invocable — expect frontmatter `name`/`description` plus an invocation trigger in each SKILL.md. Test: `test_skills_have_invocation_contract` in Task 5.

---

### Task 1: Repository scaffold and neutral bootstrap

**Files:**
- Create: `README.md`, `BOOTSTRAP.md`, `.gitignore`
- Test: `tests/test_scaffold.py`

**Interfaces:**
- Produces: `BOOTSTRAP.md` containing the single paste-ready command and the raw stage-URL pattern; later tasks add stages it references.

- [ ] **Step 1:** Write `tests/test_scaffold.py` asserting `README.md` and `BOOTSTRAP.md` exist; `BOOTSTRAP.md` contains exactly one URL placeholder `<RAW_STAGE_00_URL>` and the string `STOP` at least once.
- [ ] **Step 2:** Run `python -m pytest tests/test_scaffold.py -v`; expect FAIL (files absent).
- [ ] **Step 3:** Create the three files. README describes a standard Debian 13 desktop builder with one-command usage and no fleet terms. BOOTSTRAP fetches stage 00, prints the cleanliness gate, and stops before any write.
- [ ] **Step 4:** Run the test; expect PASS.
- [ ] **Step 5:** Commit `feat: scaffold neutral server forge repo`.

### Task 2: Validator and stage 00

**Files:**
- Create: `tools/validate.py`, `tools/check_all.py`, `stages/00-preflight.md`, `tests/test_validator.py`
- Modify: `tests/test_scaffold.py` (add neutrality assertion)

**Interfaces:**
- Consumes: `BOOTSTRAP.md` URL placeholder from Task 1.
- Produces: `validate.check_stage_contract(text: str) -> list[str]` (empty means valid); `validate.check_neutrality(text: str) -> list[str]` using `FORBIDDEN_DIGESTS`; `validate.FORBIDDEN_DIGESTS` populated from locally-held tokens (digests only in the public repo).

- [ ] **Step 1:** Write `test_every_stage_has_single_write_scope` and `test_public_files_are_neutral`: a sample valid stage returns `[]`; a stage missing `--- GO` returns a violation; a stage with two `Write scope:` lines returns a violation; `check_neutrality` flags a string whose sha256 is in `FORBIDDEN_DIGESTS`.
- [ ] **Step 2:** Run tests; expect FAIL (module absent).
- [ ] **Step 3:** Implement `tools/validate.py` with the two functions. Populate `FORBIDDEN_DIGESTS` offline from the coordinator's local fleet tokens; store only digests. Implement `tools/check_all.py` as a thin loop calling both validators over every tracked `.md` and printing one line per violation with exit code 1 when any exist.
- [ ] **Step 4:** Write `stages/00-preflight.md` with the five sections, local read-only commands (identity, root, cleanliness, listeners), and zero write paths.
- [ ] **Step 5:** Run `python -m pytest -q`; expect PASS.
- [ ] **Step 6:** Commit `feat: add stage validator and read-only preflight`.

### Task 3: Build stages 01–03

**Files:**
- Create: `stages/01-layout-secrets.md`, `stages/02-chroot-desktop.md`, `stages/03-gateway-guardian.md`, `tests/test_build_stages.py`

**Interfaces:**
- Consumes: `validate.check_stage_contract`, `validate.check_neutrality` from Task 2.
- Produces: three stage files each ending with one GO block and one evidence path; port topology fixed to 6080 published / 6081+5901+1055 loopback.

- [ ] **Step 1:** Write a parametrized test over the three stage files asserting each returns `[]` from both validators, contains exactly one `Write scope:` line, and names port 6080 with 6081/5901 as loopback.
- [ ] **Step 2:** Run it; expect FAIL (files absent).
- [ ] **Step 3:** Write the three stages. 01: layout under `/workspace/srv`, generated secrets mode 600, no printing. 02: debootstrap trixie, XFCE, VNC/websockify loopback. 03: gateway Basic Auth + WS token, one flock guardian, snapshot prerequisite.
- [ ] **Step 4:** Run full suite; expect PASS.
- [ ] **Step 5:** Commit `feat: add layout, desktop and guardian stages`.

### Task 4: Verification, resume, and kill-switch stage

**Files:**
- Create: `stages/04-snapshot-verify.md`, `stages/05-resume.md`, `tests/test_lifecycle_stages.py`

**Interfaces:**
- Consumes: validators from Task 2; stage contract from Task 3.
- Produces: two stage files defining `/workspace/srv/run/forge-stage.env` marker with `.bak`, two verification passes, and a kill-switch drill with explicit pass evidence.

- [ ] **Step 1:** Write `test_stages_fail_closed` and `test_resume_marker_contract` asserting both stages pass validators, contain `forge-stage.env`, the string `STOP`, and `healthz 200`/`401` plus a restore marker check.
- [ ] **Step 2:** Run; expect FAIL.
- [ ] **Step 3:** Write stages 04 and 05. Pass 1 immediately post-build; pass 2 after stopping the stack once and confirming snapshot restore. Resume reads stage ID and last completed marker; no restart at 00.
- [ ] **Step 4:** Run full suite; expect PASS.
- [ ] **Step 5:** Commit `feat: add verification and resume stages`.

### Task 5: Two skills

**Files:**
- Create: `skills/server-forge/SKILL.md`, `skills/server-code-writer/SKILL.md`, `tests/test_skills.py`

**Interfaces:**
- Consumes: stage files from Tasks 2–4.
- Produces: each SKILL.md with frontmatter `name`/`description` and an explicit invocation trigger.

- [ ] **Step 1:** Write `test_skills_have_invocation_contract` asserting each file starts with `---`, contains `name:` and `description:`, and names at least one trigger phrase.
- [ ] **Step 2:** Run; expect FAIL.
- [ ] **Step 3:** Implement both skills. `server-forge`: stage loop, refuse mutation without fresh GO, emit owner-gate prompts. `server-code-writer`: backup → patch → `bash -n`/`py_compile` → atomic replace → verification command; one file per GO.
- [ ] **Step 4:** Run full suite; expect PASS.
- [ ] **Step 5:** Commit `feat: add forge and code-writer skills`.

### Task 6: Command ledger and evidence template

**Files:**
- Create: `ledger/COMMAND-LEDGER.md`, `evidence/TEMPLATE.md`, `tests/test_ledger.py`

**Interfaces:**
- Consumes: validators from Task 2.
- Produces: generalized patterns with sha verification commands and no real fleet values.

- [ ] **Step 1:** Write tests asserting the ledger passes `check_neutrality`, contains at least five pattern blocks, and each block has a `sha256sum` verification line.
- [ ] **Step 2:** Run; expect FAIL.
- [ ] **Step 3:** Write the ledger (GO frame, read-only gate, hidden transfer, serve syntax, CRLF strip, guardian restart ordering) and the evidence template (stage ID, UTC, sha before/after, rollback line).
- [ ] **Step 4:** Run full suite; expect PASS.
- [ ] **Step 5:** Commit `feat: add generalized command ledger`.

### Task 7: Publish and hand over

**Files:**
- Create: `HANDOVER.md`
- Test: full suite plus a live repo check.

**Interfaces:**
- Consumes: all prior artifacts.

- [ ] **Step 1:** Run `python -m pytest -q`; expect all PASS.
- [ ] **Step 2:** Run `python tools/check_all.py` (a thin script calling both validators over every tracked `.md`); expect zero violations.
- [ ] **Step 3:** Create the public repo with `gh repo create noursteem020-hue/server-forge --public --source=. --remote=origin --push` and verify with `gh repo view`.
- [ ] **Step 4:** Confirm `git ls-tree origin/main` lists README, BOOTSTRAP, all six stages, two skills, ledger, evidence template.
- [ ] **Step 5:** Write `HANDOVER.md` with the exact link and the exact text to paste in the new platform account; commit and push.
- [ ] **Step 6:** Report the repo URL to the owner; SERVER-4 creation itself is an owner action.

## Execution Handoff

Recommend **subagent-driven**: seven tasks share the validator interface and the stage contract, and a leaked fleet value in a public repo would be expensive to undo.
