# Current Lab State

Last updated: 2026-08-19

## Active objective

Advance from threshold-authorized trust-root transitions to concurrency-safe activation. LAB-038 is complete; LAB-039 must prove that two independently valid threshold proposals derived from the same predecessor cannot both activate, overwrite each other after retry, or create split-brain across crash/restart.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-038.
- Completed Issue #73 / LAB-038.
- Merged PR #74 / LAB-038, squash merge `85ecaf683ed6ac80baa480059be39d061039e901`.
- Active next: Issue #75 / LAB-039 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-038 implemented threshold-authorized normal root rotation plus separately pinned break-glass recovery authority. Normal rotation requires both the old-root threshold and the candidate-root threshold over the same canonical transition. Recovery uses a distinct quorum, advances authority epoch, and invalidates old receipts/rotation state.

A remote patch audit found a threshold robustness defect: the first corrected verifier failed the whole transition when a revoked/duplicate/unknown signature was present, even if a sufficient valid quorum also existed. This could turn irrelevant signature material into denial of service. The verifier was corrected to count only unique, authorized, valid signer identities while ignoring non-contributing signatures; configured thresholds must also remain achievable by non-revoked keys.

## Evidence produced

- `experiments/anchor_threshold_root/protocol.py`
- `experiments/anchor_threshold_root/tests/test_protocol.py`
- `experiments/anchor_threshold_root/tests/unsafe_single_signer_expected_failure.py`
- `research/2026-08-19-threshold-root-recovery.md`
- Exact published protocol SHA `97f3757f4eb79ffc129364eafd00bb2a0fe52a4c` matched locally executed source.
- Exact published corrected-test SHA `14cada11c0d543fdddf0a66a4c2cec07c61bf427` matched locally executed source.
- Exact published unsafe baseline SHA `4d95ce6050f5e841a59cf9244cff23af58bea536` matched locally executed source.
- Corrected deterministic suite: 16/16 passed.
- Unsafe self-authorized one-signer recovery baseline: expected failure.
- `python -m compileall -q experiments` passed.
- Primary donors: TUF dual-threshold root rotation and HashiCorp Vault recovery/rekey quorum.
- PR #74 squash-merged as `85ecaf683ed6ac80baa480059be39d061039e901`.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- LAB-038 HMAC material is reference-only deterministic cryptography, not a production public-key trust store; production verifier state must not contain provider private signing material.
- Threshold authorization does not itself provide rollback resistance; LAB-034/035 replay-watermark and external monotonic-anchor guarantees remain required.
- Threshold authorization also does not serialize two competing valid proposals from the same predecessor. This concurrency/split-brain gap is LAB-039.
- No real TPM/KMS/HSM/transparency service has been proven available; deterministic/local adapters remain the honest experiment boundary.

## Exact next action

Start Issue #75 / LAB-039. Research transactional compare-and-swap/serializable activation plus one primary-source anti-equivocation/transparency mechanism. Build `experiments/anchor_rotation_concurrency/` with two valid competing root proposals, normal-rotation vs recovery race, crash-before-commit, timeout-after-commit reconciliation, restart reconstruction, same-version substitution rejection, and an unsafe check-then-write baseline. Prove exactly one successor activates and stale retries cannot overwrite it; document which guarantees are local serialization versus globally observable anti-equivocation.

## Backlog

- #75 / LAB-039 — concurrent threshold-rotation serialization and anti-equivocation conformance — READY.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
