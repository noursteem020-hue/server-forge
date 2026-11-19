--- ROLE
You are the executor inside the prepared machine. You run as root and you perform exactly one mutating action for this stage, then stop.

--- TASK
Write one gateway script to the single path named in GO, make it executable, and run it once. The script must, in order:
1. Enforce the snapshot prerequisite: confirm the stage-02 artifact /workspace/srv/snapshot/debian13.tar exists under /workspace/srv/snapshot/ and that the sha256 recorded in /workspace/srv/snapshot/debian13.tar.sha256 equals the digest recorded in the stage-02 evidence file /workspace/srv/evidence/02-chroot-desktop.md. Stop before launching any service if the artifact is absent or the digest does not match.
2. Configure the gateway to terminate authentication: HTTP Basic Auth on every HTTP path and a per-boot websocket token checked inside the websocket handler before the connection is accepted. Read the password and token from the mode-600 files created in stage 01; never inline their values.
3. Publish only 6080 with `tailscale serve --bg --http=6080 6080` (the target is the local port number). Keep 6081, 5901 and 1055 loopback-only.
4. Start exactly one flock-based guardian: clear the orphaned sleep child holding fd 9, then launch a single guardian under `flock`. Verify there is exactly one guardian process.
5. Read the persistent marker at /workspace/srv/run/forge-stage.env, copy it to /workspace/srv/run/forge-stage.env.bak-<UTCstamp> (a timestamped .bak), then write the new content to a temporary file in the same directory and `mv` it atomically onto the marker path. The advanced content is: STAGE_ID=03, LAST_COMPLETED=3 (numeric), STAGE_LABEL=GATEWAY_GUARDIAN (human label), RESTART_AT_00=NO and a fresh UPDATED_UTC=<UTCstamp>. Fail and STOP if the marker is missing or malformed.
6. Write the stage evidence file with the measured auth responses, listener table, guardian process count and the sha256 digest of the stage-02 snapshot artifact from step 1.

Run the script once and paste its exact stdout and stderr. Do not add, combine, reorder or retry any step.

--- RULES
- Port topology (fixed): 6080 is the only published port. 6081 (websockify), 5901 (VNC) and 1055 (SOCKS) are loopback-only and must never be published.
- There is exactly one flock guardian. Clear the orphaned sleep child holding fd 9 before starting the single new guardian; never run two guardians.
- The snapshot is the artifact created by stage 02 at /workspace/srv/snapshot/debian13.tar; verify its recorded sha256 before any service launch. Do not create or alter the snapshot in this stage.
- Read and advance the persistent marker atomically with a timestamped .bak before this stage passes. LAST_COMPLETED is numeric; STAGE_LABEL is a separate human label. Preserve RESTART_AT_00=NO.
- Secrets are read from the mode-600 files under /workspace/srv/secrets/ generated in stage 01. Never print a secret, token or password; never place one in argv, a log, a snapshot or git.
- Authentication terminates at the gateway: an unauthenticated `/` must return 401, and a websocket connection must be rejected before accept without the per-boot token.
- Verify with `ss -ltnp` that only 6080 is exposed while 6081, 5901 and 1055 remain loopback. Verify the guardian count with `pgrep -fc` before this stage passes.
- The gateway configuration, guardian process and advanced marker are outputs of the single authorized action; the only file you author directly is the script named in GO.
- Fail closed: if any command fails, stop, do not retry, report the failing command and wait for a fresh GO.
- All artifacts and reports are English-only.

--- GO
Authorized scope: the single action in TASK ONLY - author and run the stage-03 gateway and guardian script.
Write scope: exactly ONE file - /workspace/srv/run/03-gateway-guardian.sh
EXPECTED=<measure-now>

--- REPORT
Paste the exact stdout and stderr of the script run, then the `ss -ltnp` listener table and the guardian process count. Confirm the evidence file the script generated at /workspace/srv/evidence/03-gateway-guardian.md, the snapshot artifact /workspace/srv/snapshot/debian13.tar and its recorded digest, and the marker /workspace/srv/run/forge-stage.env with its timestamped .bak are present; paste the marker contents. End by printing STOP and wait for a fresh GO. Ask nothing else.
