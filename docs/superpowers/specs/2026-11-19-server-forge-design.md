# Server Forge — design (2026-11-19)

## Intent and why

SERVER-3 was created successfully from a single neutral platform-chat prompt (v7), then wired into a live controller through many manual, carefully gated steps. The owner wants that hard-won sequence turned into a reusable product: a **server-creation tool on GitHub** that creates SERVER-4 from one command, pauses at exactly the stages where the owner must intervene, and asks for the next command in the same precise GO format that made SERVER-3 work.

Success is concrete: the repository link is pasted into a platform chat on a **different account**, and a SERVER-4 is created without rediscovering the failures we already paid for.

## Goals

- G1 — Public GitHub repo `noursteem020-hue/server-forge`, content neutral: a standard Debian 13 desktop builder with no fleet architecture, no SERVER-2 fingerprints, no secrets.
- G2 — One-command entry: a single bootstrap prompt/link in the platform chat starts the whole build.
- G3 — Staged execution with explicit owner gates: at each stage that needs the owner, emit a ready English GO block (ROLE / TASK / RULES / GO / REPORT) naming exactly one action and one write path, with `EXPECTED=<measure-now>` and measured evidence.
- G4 — Two shipped skills: `server-forge` (create a server) and `server-code-writer` (write and patch code on a server after creation).
- G5 — A command ledger recording the **correct command patterns** that completed SERVER-3, generalized with placeholders and sha checks — no real IPs, hostnames or hashes from our fleet.
- G6 — Continuous, resumable state on the persistent volume: a stage file plus backup so a recycle or new session resumes instead of restarting.
- G7 — Reproduce the v7 invariants: one guardian, loopback-only VNC/websockify, generated secrets outside the image, atomic chroot snapshot/restore, two verification passes, kill-switch drill, no fabricated URL.

## Non-goals / anti-goals

- N1 — No fleet architecture, no SERVER-2 IP, no real hostnames/hashes, no internal registry mechanics in the public repo.
- N2 — No secret in chat, argv, logs, snapshots, or git. Owner supplies anything sensitive through the platform console.
- N3 — No public listener beyond the single app port; no port 1055 exposure; no second guardian.
- N4 — No trial-and-error loop: a failed gate stops, records, and re-prepares once.
- N5 — The tool does not create servers by itself on the platform — the owner performs the account/workspace steps; the tool supplies exact prompts.

## Constraints (measured, binding)

- `SERVER-CREATOR-v7-RULES.md` is sha-frozen (41,241 B, `341eea48…`). The new tool builds on its pattern but does not edit that file; payloads are generated per build and hash-checked.
- The executor accepts GO only when it names the action and the exact write path; one file/path per GO. Generic "read-only" GO is rejected for external connections.
- Windows-generated files must be transferred with CRLF stripped (`tr -d '\r'`) or written with LF.
- `tailscale serve --bg --http=<PORT> <PORT>` — target is the local port number, not a URL.
- A guardian restart must clear the orphaned `sleep` child holding fd 9 before starting the single new guardian.
- Platform chat attachments expose plaintext; use the hidden-file-transfer pattern for secrets.

## Approaches considered

| # | Approach | Trade-off | Pick |
|---|---|---|---|
| 1 | Public repo with neutral content | Platform can read the link directly; simplest; architecture stays with us because the repo contains none of it | ✅ |
| 2 | Private repo + neutral stub link | Protects source; needs a deploy credential provisioned on SERVER-4 — extra bootstrap surface | rejected |
| 3 | Short-lived signed link | Balanced; link expiry becomes a manual operations chore | rejected |

Chosen: **1**. The platform sees a standard cloud-desktop builder; the real intelligence (GO framing, staged gates, memory) lives in our skills and vault, not in the repo.

## Design

### Repository layout
```
server-forge/
  README.md                    neutral: what it builds, one-command usage
  BOOTSTRAP.md                 single prompt text to paste in platform chat
  stages/
    00-preflight.md            read-only cleanliness + root gate
    01-layout-secrets.md       layout, ports, generated secrets
    02-chroot-desktop.md       debootstrap + XFCE + VNC + websockify
    03-gateway-guardian.md     Basic Auth + WS token + single flock guardian
    04-snapshot-verify.md      atomic snapshot, two verification passes
    05-resume.md               resume state, stage markers
  skills/
    server-forge/SKILL.md      create server; staged GO contract
    server-code-writer/SKILL.md  write/patch code on the created server
  ledger/COMMAND-LEDGER.md     generalized command patterns + sha checks
  evidence/TEMPLATE.md         evidence schema (empty fields)
```

### One-command flow
`BOOTSTRAP.md` is the only thing pasted. It names the raw repo URL, instructs the agent to fetch stage 00, print the cleanliness gate, and **stop for owner GO** before any write. Each stage ends with one ready GO block and one evidence file; the next stage is fetched only after the owner pastes that GO.

### Stage contract (every stage)
- ROLE: one sentence, correct seat.
- TASK: exactly one command or one file change.
- RULES: measured facts, English-only artifacts, no secret printing.
- GO: explicit authorization naming the exact action and exactly one write path.
- REPORT: paste exact output, ask nothing.
- Evidence: stage ID, UTC, sha of changed artifact, before/after, rollback line.

### Skills
- `server-forge`: when invoked, runs the stage loop, refuses to mutate without a fresh GO, and emits owner-gate prompts in the proven format.
- `server-code-writer`: writes or patches code on a created server with backup, `bash -n`/`py_compile`, atomic replace, and a verification command; one file per GO.

### Command ledger
Records patterns, not our fleet values: gate command shape, GO frame shape, hidden-file-transfer shape, serve syntax, CRLF stripping, guardian restart sequencing. Every pattern carries a sha/check command so a future run can verify itself.

### Success check for SERVER-4
Owner pastes the repo link in a new platform account ⇒ agent reads `BOOTSTRAP.md` ⇒ stage 00 returns a clean gate with root ⇒ owner approves each emitted GO ⇒ SERVER-4 reaches a verified local stack with one guardian and a snapshot. No public URL unless the owner explicitly authorizes publishing.

## Builder-check resolutions (my calls)

1. **Execution substrate:** the platform-native executor agent inside the new container (CodeBuddy/WorkBuddy), running as root, is the consumer of every stage prompt — the same pattern that produced SERVER-3. Skills ship as prompt contracts plus CLI fallback: if the runtime's SkillTool cannot load them, the stage prompt names the CLI commands directly. No laptop-side runner is assumed for SERVER-4.
2. **Secrets:** the tool generates all secrets at build time (gateway password, audit/governance HMAC keys, WS token) into mode-600 files under `/workspace/srv/secrets/`, never printed, never in argv, never in a snapshot. The owner supplies no secret value in chat; N2 is reconciled to mean "owner supplies values only through the platform console if the platform demands one." Hidden-file-transfer is the pattern for moving any file that cannot be pasted.
3. **Ports:** publish only `6080` (the app port) via `tailscale serve`. Internals stay loopback: `6081` websockify, `5901` VNC, `1055` SOCKS if userspace networking is used (never exposed). Auth terminates at the gateway: Basic Auth on every HTTP path and a per-boot token inside the WebSocket handler before accept.
4. **Stage 00:** it runs **local** read-only commands only (identity, root, cleanliness, listeners). The earlier rejection applied to cross-server SSH under a generic read-only GO, not to local reads. Stage 00 carries an explicit GO naming each read-only command and zero write paths; it stops before any write.
5. **v7 source:** the canonical frozen file lives in the coordinator's local `server3/` folder (`SERVER-CREATOR-v7-RULES.md`, sha `341eea48…`). The public repo contains only generalized patterns and sha-check commands, never that file or fleet values. The builder reads the local frozen source when generating the ledger; the ledger records how to verify the hash, not the content.
6. **Verification passes:** pass 1 immediately after build — `healthz 200`, unauthenticated `/` returns `401`, VNC/websockify loopback-only, exactly one guardian, snapshot sha recorded. Pass 2 after a kill-switch drill — stop the stack once, confirm the boot/snapshot restore returns the same checks, record boot_id change and restore marker. Evidence is a computed report file, not prose.
7. **Persistent path:** `/workspace/srv/run/forge-stage.env` holds stage ID, completed markers, and UTC timestamps; `/workspace/srv/run/forge-stage.env.bak-<stamp>` is the backup. `/workspace/srv` is the persistent root per v7; a recycle preserves it while `/srv/debian13` is restored from snapshot.
8. **Egress/auth fallback:** stage 00 first checks GitHub reachability and Tailscale auth state. If raw fetch is unavailable, BOOTSTRAP instructs the owner to attach the stage file through the platform chat; if Tailscale is unauthenticated, the owner completes the platform login before stage 02. No silent fallback.

## What is left to the builder

- Exact wording of `BOOTSTRAP.md` and all six stage prompts.
- The two SKILL.md files with frontmatter and invocation triggers.
- The generalized command ledger content.
- GitHub repo creation, initial commit, and public visibility.
- A handover note telling the owner precisely what to paste on the new account.

## Owner decisions already made

- Approach 1 (public neutral repo) — chosen 2026-11-19.
- Laptop is sole commander; SERVER-3 is the pattern, not a second commander.
- No public URL by default; publishing requires separate GO.
