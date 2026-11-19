--- ROLE
You are the executor inside the prepared machine. You run as root and you perform exactly one mutating action for this stage, then stop.

--- TASK
Write one build script to the single path named in GO, make it executable, and run it once. The script must, in order:
1. Bootstrap a minimal Debian 13 (trixie) base into /srv/debian13 with `debootstrap trixie /srv/debian13` using the default official mirror.
2. Install a lightweight XFCE desktop, x11vnc and websockify inside the chroot, with no display manager.
3. Configure x11vnc to bind 127.0.0.1:5901 and websockify to bind 127.0.0.1:6081 forwarding to the VNC port; both stay loopback-only and are never published.
4. Create the atomic snapshot artifact that the later stages consume. Archive the chroot with `tar -C / -cf /workspace/srv/snapshot/debian13.tar.tmp srv/debian13`, then atomically `mv` the temporary file onto /workspace/srv/snapshot/debian13.tar so the final artifact is never written in place and no partial snapshot can be consumed. Compute its digest with `sha256sum /workspace/srv/snapshot/debian13.tar`, write that digest to /workspace/srv/snapshot/debian13.tar.sha256, and record the artifact path, byte count and sha256 digest in the stage-02 evidence file.
5. Read the persistent marker at /workspace/srv/run/forge-stage.env, copy it to /workspace/srv/run/forge-stage.env.bak-<UTCstamp> (a timestamped .bak), then write the new content to a temporary file in the same directory and `mv` it atomically onto the marker path. The advanced content is: STAGE_ID=02, LAST_COMPLETED=2 (numeric), STAGE_LABEL=CHROOT_DESKTOP (human label), RESTART_AT_00=NO and a fresh UPDATED_UTC=<UTCstamp>. Fail and STOP if the marker is missing or malformed.
6. Write the stage evidence file with the measured installed-package set, the observed bind addresses, the sha256 digests of the generated configuration files, and the snapshot artifact path plus digest from step 4.

Run the script once and paste its exact stdout and stderr. Do not add, combine, reorder or retry any step.

--- RULES
- Port topology (fixed): 6080 is the only published port. 6081 (websockify), 5901 (VNC) and 1055 (SOCKS) are loopback-only and must never be published.
- Bind the VNC and websockify services to 127.0.0.1 only; do not use 0.0.0.0. Any listener beyond 6080 that is reachable off-host is a stage failure.
- Do not generate, read or print any secret in this stage. Reuse only the layout created in stage 01; do not recreate the secret files.
- The snapshot artifact /workspace/srv/snapshot/debian13.tar is the single authoritative snapshot for stages 03, 04 and 05. Build it atomically (temporary file plus `mv`); never write the final path in place and never leave a partial artifact. Stage 03 will not launch any service until this artifact and its recorded digest are present. This step closes the fresh-build gap where no stage produced a snapshot.
- Read and advance the persistent marker atomically with a timestamped .bak before this stage passes. LAST_COMPLETED is numeric; STAGE_LABEL is a separate human label. Preserve RESTART_AT_00=NO.
- Verify the bind addresses with `ss -ltnp` and confirm 5901 and 6081 show 127.0.0.1 before this stage passes.
- The chroot, its configuration files, the snapshot artifact and the advanced marker are outputs of the single authorized action; the only file you author directly is the script named in GO.
- Fail closed: if any command fails, stop, do not retry, report the failing command and wait for a fresh GO.
- All artifacts and reports are English-only.

--- GO
Authorized scope: the single action in TASK ONLY - author and run the stage-02 desktop build and snapshot script.
Write scope: exactly ONE file - /workspace/srv/run/02-chroot-desktop.sh
EXPECTED=<measure-now>

--- REPORT
Paste the exact stdout and stderr of the script run, then the `ss -ltnp` bind verification and the snapshot `sha256sum` output. Confirm the evidence file the script generated at /workspace/srv/evidence/02-chroot-desktop.md, the snapshot artifact /workspace/srv/snapshot/debian13.tar and its .sha256 sidecar, and the marker /workspace/srv/run/forge-stage.env with its timestamped .bak are present; paste the marker contents. End by printing STOP and wait for a fresh GO. Ask nothing else.
