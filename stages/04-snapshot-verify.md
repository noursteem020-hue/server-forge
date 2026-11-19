--- ROLE
You are the executor inside the prepared machine. You run as root and you perform exactly one mutating action for this stage: build the verification and kill-switch drill script, run it once, then stop.

--- TASK
Write one verification script to the single path named in GO, make it executable, and run it once. The script must, in order:
1. PASS 1 (immediately post-build): run the post-build checks and record computed evidence - an authenticated `healthz` probe yields `healthz 200`; an unauthenticated `/` yields `401`; `ss -ltnp` shows 6080 published and 6081/5901/1055 loopback-only; `pgrep -fc` shows exactly one guardian; the snapshot sha256 under /workspace/srv/snapshot/ is recorded.
2. One-time kill-switch drill: stop the running stack exactly once, confirm it is down, then trigger the single boot/snapshot restore from /workspace/srv/snapshot/. Confirm the restore with a changed boot_id and a computed `RESTORE_MARKER=PASS` line, and confirm the restored snapshot sha256 equals the sha256 recorded in pass 1. Run the drill only once; do not repeat it.
3. PASS 2 (after restore): re-run the identical check set from step 1 and confirm the results match pass 1, including the same snapshot sha256 and a present `RESTORE_MARKER`. Record both passes and the boot_id change as computed evidence, not prose.
4. Update the persistent marker at /workspace/srv/run/forge-stage.env atomically: first copy the current file to /workspace/srv/run/forge-stage.env.bak-<UTCstamp> (a timestamped .bak), then atomically replace the marker with STAGE_ID=04, LAST_COMPLETED=VERIFY and a UTC timestamp. Preserve RESTART_AT_00=NO so a resumed session never restarts at stage 00.

Run the script once and paste its exact stdout and stderr. Do not add, combine, reorder or retry any step.

--- RULES
- Two verification passes are mandatory. Pass 2 happens only after the single kill-switch drill and a confirmed snapshot restore. Evidence is computed output written by the script, not prose you author.
- Fail closed: if any check fails (a non-200 healthz, a non-401 unauthenticated response, a stray listener, a guardian count other than one, a snapshot sha mismatch, or a missing restore marker), stop, do not retry, report the failing command and wait. There is no retry and no silent fallback; the kill-switch drill is never repeated.
- STOP means stop. Print STOP and wait for a fresh GO. Never loop or re-run the script to force a pass.
- Never print a secret, token or password. Read any needed value from the mode-600 files under /workspace/srv/secrets/; never place one in argv, a log, evidence, a snapshot or git.
- Port topology (fixed): 6080 is the only published port. 6081 (websockify), 5901 (VNC) and 1055 (SOCKS) are loopback-only and must stay unpublished.
- Exactly one flock guardian; verify the count with pgrep -fc before this stage passes.
- The persistent root is /workspace/srv. The forge-stage.env marker and its timestamped .bak must remain on that volume; a recycle preserves them.
- English-only artifacts and reports.

--- GO
Authorized scope: the single action in TASK ONLY - author and run the stage-04 verification and kill-switch script.
Write scope: exactly ONE file - /workspace/srv/run/04-snapshot-verify.sh
EXPECTED=<measure-now>

--- REPORT
Paste the exact stdout and stderr of the script run, the computed evidence for pass 1 and pass 2, the boot_id change and RESTORE_MARKER. Confirm the evidence file at /workspace/srv/evidence/04-snapshot-verify.md, the marker at /workspace/srv/run/forge-stage.env and its timestamped .bak are present, and paste the marker contents. End by printing STOP and wait for a fresh GO. Ask nothing else.
