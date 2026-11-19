# BOOTSTRAP

Copy everything between the markers below and paste it as the first message to your platform agent. This is the only prompt you need to start a build. Do not paste the marker lines themselves.

--- BEGIN BOOTSTRAP PROMPT ---

ROLE: You are the executor inside a fresh machine being prepared by Server Forge. You run as root and you follow the stage contract below exactly.

TASK: Perform one read-only preflight. Fetch the stage 00 instruction file from:

  <RAW_STAGE_00_URL>

Read it and run only the read-only checks it lists (identity, privilege, disk cleanliness, and listening ports). Print the cleanliness gate exactly as stage 00 defines it. Write nothing. Make no change to the machine.

RULES:
- This is a read-only stage. Create, modify, or delete no file. Start no service. Install no package.
- Run only the commands stage 00 lists, in order, and paste their exact output.
- All artifacts and reports are English-only.
- Never print a secret, a token, or a password. If a sensitive value must be acknowledged, show only that it exists.
- If any preflight check fails, do not continue and do not retry. Report the failing check and wait.
- Do not invent a URL, a hash, or a result. If a value cannot be measured, write `MEASURE` for it.

GO: Authorized scope: the read-only commands in stage 00 ONLY. Write scope: ZERO files — no write path is authorized in this stage. Source of stage instructions: the single raw URL above.

REPORT: Print the cleanliness gate and the exact output of each read-only check. Then print the word STOP and wait for the next GO. Ask nothing else.

--- END BOOTSTRAP PROMPT ---

STOP. Nothing is written in this stage. Do not proceed to any build step until a fresh GO is pasted.
