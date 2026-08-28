# LAB-086: full PR patch is the current byte source

Date: 2026-08-28

## Observation

The current draft PR #165 still adds `experiments/asymmetric_break_glass_history/strict_fence.py` relative to `main`. GitHub's per-file PR patch endpoint therefore returns the complete current file as a single `@@ -0,0 +1,949 @@` addition, not a truncated diff fragment.

The exact live branch file was independently identified as blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`. Inspection of the complete PR patch confirms the current source contains both already-required protections:

- provider receipt `NEW.request_id IS NULL` rejection;
- alternate `(provider_id,generation)` collision rejection for `asymmetric_provider_generations`.

The current source does not yet contain the hidden-rowid guards preserved in `research/2026-08-28-lab086-hidden-rowid-replace.patch` (blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`).

## Execution capability probe

A fresh direct `git clone --branch lab/086-asymmetric-break-glass-history --single-branch ...` was attempted in the current executor and failed before transfer with `Could not resolve host: github.com`.

The GitHub connector can return the complete exact source, but this run has no supported byte-preserving bridge that writes the connector response directly into the execution filesystem. Manually transcribing a 949-line security-critical runtime remains disallowed because it would weaken byte-identity assurance.

## Consequence

The earlier source-availability blocker is narrowed: **the exact current source bytes are available through the GitHub PR patch surface; only connector-response -> executable-filesystem byte transfer remains unavailable in this runtime.**

Do not reconstruct from historical `eb219835...` or the obsolete hidden-rowid candidate `b78e7c98...`. The next executable candidate must be derived from exact current blob `d4a6a40f...` and only the saved hidden-rowid patch.

## Exact next gate

1. Materialize the complete PR-file patch payload into an execution filesystem without manual transcription and strip only the diff `+` prefix/header, verifying resulting Git blob == `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` before any edit.
2. Apply only `research/2026-08-28-lab086-hidden-rowid-replace.patch`.
3. Compute the candidate Git blob and run unchanged focused regressions for provider-receipt NULL identity, alternate UNIQUE collision, and hidden rowid collision/sentinel behavior.
4. Require full strict/thaw subgate + compileall before publication.
5. Publish only exact tested bytes and verify the returned GitHub blob equals the tested candidate.

No new unittest PASS is claimed by this note.