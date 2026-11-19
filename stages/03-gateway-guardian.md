--- ROLE
You are the executor inside the prepared machine. You run as root and you perform exactly one mutating action for this stage, then stop.

--- TASK
Write one gateway script to the single path named in GO, make it executable, and run it once. The script must, in order:
1. Enforce the snapshot prerequisite: confirm an atomic snapshot of the chroot exists under /workspace/srv/snapshot/ before starting any service; if it is absent, stop before launch.
2. Configure the gateway to terminate authentication: HTTP Basic Auth on every HTTP path and a per-boot websocket token checked inside the websocket handler before the connection is accepted. Read the password and token from the mode-600 files created in stage 01; never inline their values.
3. Publish only 6080 with `tailscale serve --bg --http=6080 6080` (the target is the local port number). Keep 6081, 5901 and 1055 loopback-only.
4. Start exactly one flock-based guardian: clear the orphaned sleep child holding fd 9, then launch a single guardian under `flock`. Verify there is exactly one guardian process.
5. Write the stage evidence file with the measured auth responses, listener table, guardian process count and snapshot sha256 digest.

Run the script once and paste its exact stdout and stderr. Do not add, combine, reorder or retry any step.

--- RULES
- Port topology (fixed): 6080 is the only published port. 6081 (websockify), 5901 (VNC) and 1055 (SOCKS) are loopback-only and must never be published.
- There is exactly one flock guardian. Clear the orphaned sleep child holding fd 9 before starting the single new guardian; never run two guardians.
- Secrets are read from the mode-600 files under /workspace/srv/secrets/ generated in stage 01. Never print a secret, token or password; never place one in argv, a log, a snapshot or git.
- Authentication terminates at the gateway: an unauthenticated `/` must return 401, and a websocket connection must be rejected before accept without the per-boot token.
- Verify with `ss -ltnp` that only 6080 is exposed while 6081, 5901 and 1055 remain loopback. Verify the guardian count with `pgrep -fc` before this stage passes.
- The gateway configuration and guardian process are outputs of the single authorized action; the only file you author directly is the script named in GO.
- Fail closed: if any command fails, stop, do not retry, report the failing command and wait for a fresh GO.
- All artifacts and reports are English-only.

--- GO
Authorized scope: the single action in TASK ONLY - author and run the stage-03 gateway and guardian script.
Write scope: exactly ONE file - /workspace/srv/run/03-gateway-guardian.sh
EXPECTED=<measure-now>

--- REPORT
Paste the exact stdout and stderr of the script run, then the `ss -ltnp` listener table and the guardian process count. Confirm the evidence file the script generated at /workspace/srv/evidence/03-gateway-guardian.md is present and paste its contents. End by printing STOP and wait for a fresh GO. Ask nothing else.
