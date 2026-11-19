# Evidence Template

Copy this file to the stage evidence path and fill every field with measured
values. This is a schema only: the checked-in template contains placeholders,
never a real address, hostname, project name, token, or hash. All fields are
English-only. Compute digests locally with `sha256sum`; paste exact measured
output, never invented values.

## Fields

- **STAGE_ID:** `<stage-id>` — identifier of the stage that produced this evidence.
- **UTC:** `<YYYY-MM-DDTHH:MM:SSZ>` — completion time in UTC.
- **WRITE_PATH:** `<write-path>` — the single file or path the GO authorized.
- **SHA_BEFORE:** `<sha256-of-artifact-before>` — digest of the artifact before the change.
- **SHA_AFTER:** `<sha256-of-artifact-after>` — digest of the artifact after the change.
- **VERIFY_CMD:** `sha256sum <write-path>` — command used to compute the digest.
- **VERIFY_RESULT:** `<measured-command-output>` — exact output of the verification.
- **ROLLBACK:** `cp <backup-path> <write-path>` — restores the pre-change artifact.

## Completed record

```
STAGE_ID:      <stage-id>
UTC:           <YYYY-MM-DDTHH:MM:SSZ>
WRITE_PATH:    <write-path>
SHA_BEFORE:    <sha256-of-artifact-before>
SHA_AFTER:     <sha256-of-artifact-after>
VERIFY_CMD:    sha256sum <write-path>
VERIFY_RESULT: <measured-command-output>
ROLLBACK:      cp <backup-path> <write-path>
```

## Rules

- `SHA_BEFORE` and `SHA_AFTER` are computed with the same `sha256sum` command on
  the same `WRITE_PATH`; do not hand-edit a digest.
- Keep the timestamped backup referenced by `ROLLBACK` until the next stage is
  verified; a failed gate stops, records this evidence, and re-prepares once.
- Do not paste a measured secret value into any field; record digests only.
- The checked-in template stays empty of real values; each run writes a filled
  copy to its own evidence path.
