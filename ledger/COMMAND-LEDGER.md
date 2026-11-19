# Server Forge — Command Ledger

This ledger records **generalized command patterns**, not fleet values. Every
value below is a placeholder (`<...>`) that the executor fills at build time;
no real address, hostname, project name, token, or hash appears here. The public
repository keeps only the *shape* of each correct command and a
`sha256sum`-based verification step so a future run can check itself against a
digest recorded outside this repository.

Each block follows the same contract:

- **Purpose** — what the pattern achieves and when it is used.
- **Shape** — the generalized command, with placeholders only.
- **Rules** — the invariants that must hold (including English-only artifacts).
- **Verification** — a `sha256sum` command comparing the generated artifact to
  a digest that was computed at build time and stored outside this repository.

Never paste a measured secret value into the command, argv, a log, a snapshot,
or this file. Measure locally, compute the digest locally, and compare digests.

## PATTERN 1: GO frame

**Purpose:** Authorize exactly one action at each owner gate. A GO is valid only
when it names the action and exactly one write path; a generic read-only GO is
rejected for any step that opens an external connection.

**Shape:**

```
ROLE:   <one-sentence seat>
TASK:   <one action>
RULES:  <measured facts; English-only artifacts; no secret printing>
GO:     Authorized scope: <action> ONLY. Write scope: <write-path-or-ZERO files>
        EXPECTED=<measure-now>
REPORT: paste exact measured output, then STOP and wait for a fresh GO
```

**Rules:** one action and at most one write path per GO; never mutate without a
fresh GO; STOP at every gate; emit no public URL unless separately authorized.

**Verification:**

```
GO_FILE=<generated-go-block-path>
RECORDED_SHA=<digest-recorded-outside-repo>
sha256sum "$GO_FILE"
test "$(sha256sum "$GO_FILE" | cut -d' ' -f1)" = "$RECORDED_SHA"
```

## PATTERN 2: Read-only gate

**Purpose:** Preflight a fresh machine with local read-only commands: identity,
root check, cleanliness, and listener inventory. Zero write paths.

**Shape:**

```
id -u                       # expect 0 (root)
whoami && hostname          # record measured output only
ss -lntp                    # inventory current listeners
git status --short          # expect clean tree
```

**Rules:** local reads only; paste measured output, never invent a value; stop
before any write; do not open an external connection under a generic read-only
GO.

**Verification:**

```
STAGE_FILE=<stage-00-path>
RECORDED_SHA=<digest-recorded-outside-repo>
sha256sum "$STAGE_FILE"
test "$(sha256sum "$STAGE_FILE" | cut -d' ' -f1)" = "$RECORDED_SHA"
```

## PATTERN 3: Hidden transfer

**Purpose:** Move a file that cannot be pasted (a secret or any rejected
attachment) from the operator machine to the target without the content ever
appearing in chat, an attachment preview, argv, or logs.

**Shape:**

```
# receiver on target: one-shot loopback HTTP receiver
# + temporary tailnet-only serve binding
# sender on laptop: POST the file once to the loopback receiver
# cleanup: remove the binding and stop the receiver after one delivery
```

**Rules:** one-shot only; bind to loopback and expose through a tailnet-only
path; never print the file content; remove both receiver and binding after the
transfer; all commands and helper scripts are English-only.

**Verification:**

```
DELIVERED=<delivered-file-path>
RECORDED_SHA=<digest-recorded-outside-repo>
sha256sum "$DELIVERED"
test "$(sha256sum "$DELIVERED" | cut -d' ' -f1)" = "$RECORDED_SHA"
```

## PATTERN 4: Serve syntax

**Purpose:** Publish the single application port. The serve target is the local
port number, not a URL; internal ports stay loopback-only.

**Shape:**

```
tailscale serve --bg --http=<APP_PORT> <APP_PORT>
```

**Rules:** publish exactly one app port; internal ports remain bound to
loopback; never expose an internal port or a second gateway; no public URL is
emitted unless the owner authorizes publishing in a separate GO.

**Verification:**

```
SERVE_CFG=<generated-serve-config-path>
RECORDED_SHA=<digest-recorded-outside-repo>
sha256sum "$SERVE_CFG"
test "$(sha256sum "$SERVE_CFG" | cut -d' ' -f1)" = "$RECORDED_SHA"
```

## PATTERN 5: CRLF strip

**Purpose:** Normalize files generated on Windows before executing them on the
target, so a stray carriage return cannot corrupt a command, script, or config.

**Shape:**

```
tr -d '\r' < <windows-generated-file> > <normalized-file>
# or write the file with LF line endings directly
```

**Rules:** strip every CR byte before use; prefer writing LF directly; keep the
original as a timestamped backup; verify the normalized artifact by digest, not
by visual inspection; helper commands are English-only.

**Verification:**

```
NORMALIZED=<normalized-file-path>
RECORDED_SHA=<digest-recorded-outside-repo>
sha256sum "$NORMALIZED"
test "$(sha256sum "$NORMALIZED" | cut -d' ' -f1)" = "$RECORDED_SHA"
```

## PATTERN 6: Guardian restart ordering

**Purpose:** Restart the supervisor safely: clear the orphaned child that still
holds the lock descriptor before starting the single new guardian. Exactly one
guardian may run at a time.

**Shape:**

```
# 1. identify and stop the orphaned 'sleep' child holding fd 9
# 2. confirm no guardian holds the lock
# 3. start the single new guardian under the lock
# 4. confirm exactly one guardian process is alive
```

**Rules:** clear the orphan before the new start; never run a second guardian;
verify the single-process invariant after restart; record the boot/restore
marker in evidence; all scripts and reports are English-only.

**Verification:**

```
GUARDIAN_SCRIPT=<guardian-script-path>
RECORDED_SHA=<digest-recorded-outside-repo>
sha256sum "$GUARDIAN_SCRIPT"
test "$(sha256sum "$GUARDIAN_SCRIPT" | cut -d' ' -f1)" = "$RECORDED_SHA"
```
