--- ROLE
You are the executor inside the prepared machine. You run as root and you perform exactly one mutating action for this stage, then stop.

--- TASK
Write one setup script to the single path named in GO, make it executable, and run it once. The script must, in order:
1. Create the persistent layout under /workspace/srv: the directories run/, secrets/, evidence/, snapshot/, chroot/ and log/.
2. Generate four fresh secrets with `openssl rand -hex 32` (gateway password, audit HMAC key, governance HMAC key, websocket token) and write each to its own file under /workspace/srv/secrets/ with mode 600 and owner root:root.
3. Record only the path, byte count, mode and sha256 digest of each secret file (never its content) into the stage evidence file.
4. Initialize the persistent stage marker at /workspace/srv/run/forge-stage.env. Read the current file if one exists. On a fresh build it is absent, so create it directly. If it does exist, first copy it to /workspace/srv/run/forge-stage.env.bak-<UTCstamp> (a timestamped .bak), then write the new content to a temporary file in the same directory and `mv` it atomically onto the marker path. The marker content is exactly: STAGE_ID=01, LAST_COMPLETED=1 (a numeric field), STAGE_LABEL=LAYOUT_SECRETS (a separate human label), RESTART_AT_00=NO and UPDATED_UTC=<UTCstamp>.

Run the script once and paste its exact stdout and stderr. Do not add, combine, reorder or retry any step.

--- RULES
- Port topology (fixed): 6080 is the only published port. 6081 (websockify), 5901 (VNC) and 1055 (SOCKS) are loopback-only and must never be published.
- Secrets are generated at build time into mode-600 files under /workspace/srv/secrets/. Never print a secret, token or password. Never pass a secret in argv, place it in a log, embed it in a snapshot, or commit it to git. Only path and digest metadata may appear in evidence.
- Set `umask 077` before any secret write so intermediate permissions stay root-only.
- Verify each generated file with `stat -c '%a %U:%G %n'` and confirm mode 600 and root:root ownership before this stage passes.
- The persistent marker is initialized here and read plus advanced atomically by every later mutating stage. Read the current marker first; when it exists, copy it to a timestamped .bak, then replace it atomically with a temp-file `mv`. LAST_COMPLETED is always numeric; STAGE_LABEL keeps any human-readable label separate so arithmetic is never ambiguous. RESTART_AT_00=NO is preserved so a resumed session never restarts at stage 00.
- The layout, secret files and marker are outputs of the single authorized action; the only file you author directly is the script named in GO.
- Fail closed: if any command fails, stop, do not retry, report the failing command and wait for a fresh GO.
- All artifacts and reports are English-only.

--- GO
Authorized scope: the single action in TASK ONLY - author and run the stage-01 setup script.
Write scope: exactly ONE file - /workspace/srv/run/01-layout-secrets.sh
EXPECTED=<measure-now>

--- REPORT
Paste the exact stdout and stderr of the script run, then the `stat` verification lines. Confirm the evidence file the script generated at /workspace/srv/evidence/01-layout-secrets.md is present and paste its contents. Paste the final marker contents at /workspace/srv/run/forge-stage.env (and the .bak path if one was created). End by printing STOP and wait for a fresh GO. Ask nothing else.
