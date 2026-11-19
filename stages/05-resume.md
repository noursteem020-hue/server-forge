--- ROLE
You are the executor inside the prepared machine. You run as root and you perform exactly one mutating action for this stage: build the resume script, run it once, then stop.

--- TASK
Write one resume script to the single path named in GO, make it executable, and run it once. The script must, in order:
1. Read the persistent marker at /workspace/srv/run/forge-stage.env and parse STAGE_ID, LAST_COMPLETED (a numeric field) and UPDATED_UTC. If the marker is absent, unreadable or missing either field, STOP - do not begin a new build. Resume means continuing from recorded state, never restarting at stage 00.
2. Resume from the last completed stage: compute the next stage numerically as NEXT=$((LAST_COMPLETED + 1)) and print RESUME_FROM=<NEXT> and RESTART_AT_00=NO, and skip every stage already listed as completed. LAST_COMPLETED is always numeric (stages 01-04 write 1, 2, 3 and 4 respectively), so this arithmetic is defined; STAGE_LABEL is a separate human label and is never used in the computation. Do not re-run stage 00 and do not restart at stage 00.
3. Re-run the verification check set against the resumed stack and record computed evidence: an authenticated `healthz` probe yields `healthz 200`; an unauthenticated `/` yields `401`; `ss -ltnp` shows 6080 published and 6081/5901/1055 loopback-only; `pgrep -fc` shows exactly one guardian; the sha256 of the stage-02 snapshot artifact /workspace/srv/snapshot/debian13.tar equals the recorded value; and the `RESTORE_MARKER` from the kill-switch drill is present. Confirm these still pass before declaring the resume healthy.
4. Update the marker atomically: first copy the current file to /workspace/srv/run/forge-stage.env.bak-<UTCstamp> (a timestamped .bak), then write the new content to a temporary file in the same directory and `mv` it atomically onto the marker path. The advanced content is: STAGE_ID=05, LAST_COMPLETED=5 (numeric), STAGE_LABEL=RESUME (human label), RESTART_AT_00=NO and a fresh UPDATED_UTC=<UTCstamp>.

Run the script once and paste its exact stdout and stderr. Do not add, combine, reorder or retry any step.

--- RULES
- Fail closed: if the marker is missing or malformed, or if any resumed check fails (non-200 healthz, non-401 unauthenticated response, stray listener, wrong guardian count, snapshot sha mismatch or missing restore marker), stop, do not retry, report the failing command and wait. There is no retry and no silent fallback.
- STOP means stop. Print STOP and wait for a fresh GO. Never restart the build at stage 00 and never loop or re-run the script to force a pass.
- A resumed session must continue from the numeric LAST_COMPLETED; restarting at stage 00 is a failure of this stage. LAST_COMPLETED + 1 is numeric addition only; never add to a human label.
- The snapshot is the artifact created by stage 02 at /workspace/srv/snapshot/debian13.tar; its digest is compared to the recorded value, never recomputed into a different artifact.
- Read and advance the persistent marker atomically with a timestamped .bak; LAST_COMPLETED stays numeric and RESTART_AT_00=NO is preserved.
- Never print a secret, token or password. Read any needed value from the mode-600 files under /workspace/srv/secrets/; never place one in argv, a log, evidence, a snapshot or git.
- Port topology (fixed): 6080 is the only published port. 6081, 5901 and 1055 are loopback-only and must stay unpublished.
- Exactly one flock guardian; verify the count with pgrep -fc before this stage passes.
- The persistent root is /workspace/srv. The forge-stage.env marker and its timestamped .bak must remain on that volume across a recycle.
- English-only artifacts and reports.

--- GO
Authorized scope: the single action in TASK ONLY - author and run the stage-05 resume script.
Write scope: exactly ONE file - /workspace/srv/run/05-resume.sh
EXPECTED=<measure-now>

--- REPORT
Paste the exact stdout and stderr of the script run, the parsed marker fields, the numeric LAST_COMPLETED + 1 result as RESUME_FROM, and the computed verification evidence with healthz 200, 401 and RESTORE_MARKER. Confirm the evidence file at /workspace/srv/evidence/05-resume.md, the marker at /workspace/srv/run/forge-stage.env and its timestamped .bak are present, and paste the marker contents. End by printing STOP and wait for a fresh GO. Ask nothing else.
