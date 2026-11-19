--- ROLE
You are the executor inside the prepared machine. You run as root and you perform exactly one mutating action for this stage: build the verification and kill-switch drill script, run it once, then stop.

--- TASK
Write one verification script to the single path named in GO, make it executable, and run it once. The script must, in order:
1. PASS 1 (immediately post-build): run the post-build checks and record computed evidence - an authenticated `healthz` probe yields `healthz 200`; an unauthenticated `/` yields `401`; `ss -ltnp` shows 6080 published and 6081/5901/1055 loopback-only; `pgrep -fc` shows exactly one guardian; and the sha256 of the stage-02 snapshot artifact at /workspace/srv/snapshot/debian13.tar (read from /workspace/srv/snapshot/debian13.tar.sha256) is recorded and matches the stage-02 evidence.
2. One-time kill-switch drill: stop the running stack exactly once, confirm it is down, then trigger the single boot/snapshot restore from the stage-02 artifact /workspace/srv/snapshot/debian13.tar. Confirm the restore with a changed boot_id and a computed `RESTORE_MARKER=PASS` line, and confirm the restored snapshot sha256 equals the sha256 recorded in pass 1. Run the drill only once; do not repeat it.
3. PASS 2 (after restore): re-run the identical check set from step 1 and confirm the results match pass 1, including the same snapshot sha256 and a present `RESTORE_MARKER`. Record both passes and the boot_id change as computed evidence, not prose.
4. Read the persistent marker at /workspace/srv/run/forge-stage.env before changing it. If it is absent, unreadable, or missing STAGE_ID or LAST_COMPLETED, STOP and report the missing marker before making any change - stage 01 initializes it and stages 02 and 03 advance it, so a missing marker here is a broken build, not a signal to create one. Otherwise copy the current file to /workspace/srv/run/forge-stage.env.bak-<UTCstamp> (a timestamped .bak), then write the new content to a temporary file in the same directory and `mv` it atomically onto the marker path. The advanced content is: STAGE_ID=04, LAST_COMPLETED=4 (a numeric stage field), STAGE_LABEL=VERIFY (a separate human label), RESTART_AT_00=NO and a fresh UPDATED_UTC=<UTCstamp>. Do not write a non-numeric value into LAST_COMPLETED.

Run the script once and paste its exact stdout and stderr. Do not add, combine, reorder or retry any step.

--- RULES
- Two verification passes are mandatory. Pass 2 happens only after the single kill-switch drill and a confirmed snapshot restore. Evidence is computed output written by the script, not prose you author.
- The snapshot is the artifact created by stage 02 at /workspace/srv/snapshot/debian13.tar with its digest in the .sha256 sidecar; both verification passes hash this same artifact. Do not create a new snapshot in this stage.
- The persistent marker is read first and advanced atomically with a timestamped .bak. LAST_COMPLETED is numeric (4); STAGE_LABEL carries the human label VERIFY and is never used in arithmetic. A missing or malformed marker is an explicit STOP condition, never a create-and-continue.
- Fail closed: if any check fails (a non-200 healthz, a non-401 unauthenticated response, a stray listener, a guardian count other than one, a snapshot sha mismatch, or a missing restore marker), stop, do not retry, report the failing command and wait. There is no retry and no silent fallback; the kill-switch drill is never repeated.
- STOP means stop. Print STOP and wait for a fresh GO. Never loop or re-run the script to force a pass.
- Never print a secret, token or password. Read any needed value from the mode-600 files under /workspace/srv/secrets/; never place one in argv, a log, evidence, a snapshot or git.
- Port topology (fixed): 6080 is the only published port. 6081, 5901 and 1055 are loopback-only and must stay unpublished.
- Exactly one flock guardian; verify the count with pgrep -fc before this stage passes.
- The persistent root is /workspace/srv. The forge-stage.env marker and its timestamped .bak must remain on that volume; a recycle preserves them so a resumed session continues from the recorded stage instead of restarting.
- English-only artifacts and reports.

--- GO
Authorized scope: the single action in TASK ONLY - author and run the stage-04 verification and kill-switch script.
Write scope: exactly ONE file - /workspace/srv/run/04-snapshot-verify.sh
EXPECTED=<measure-now>

--- REPORT
Paste the exact stdout and stderr of the script run, the computed evidence for pass 1 and pass 2, the boot_id change and RESTORE_MARKER. Confirm the evidence file at /workspace/srv/evidence/04-snapshot-verify.md, the marker at /workspace/srv/run/forge-stage.env and its timestamped .bak are present, and paste the marker contents (including numeric LAST_COMPLETED=4). End by printing STOP and wait for a fresh GO. Ask nothing else.
