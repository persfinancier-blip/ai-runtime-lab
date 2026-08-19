# Current Lab State

Last updated: 2026-08-19

## Active objective

Advance from single-key verifier trust-root lifecycle to threshold-authorized trust rotation and explicit break-glass recovery authority. LAB-037 is complete; LAB-038 must prove that a single compromised signer or self-authorized recovery path cannot replace the verifier root of trust.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-037.
- Completed Issue #71 / LAB-037.
- Merged PR #72 / LAB-037, squash merge `1d5531f5325f1dd9153566817c09e47f843b703c`.
- Active next: Issue #73 / LAB-038 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-037 implemented a deterministic versioned verifier trust-store with provider identity, key generation, key ID, revocation and authority epoch. Normal rotation must advance exactly one generation and be authenticated by the currently trusted authority. Compromise recovery advances the authority epoch so old receipts are no longer authorized even if their old signature still verifies cryptographically.

A remote patch audit found a same-version substitution flaw: the first corrected snapshot loader rejected lower versions but allowed different trust-store contents at the same version. This was fixed before integration; same-version non-identical state now fails closed. Explicit current-key revocation was also added.

## Evidence produced

- `experiments/anchor_trust_root/protocol.py`
- `experiments/anchor_trust_root/tests/test_protocol.py`
- `experiments/anchor_trust_root/tests/unsafe_self_asserted_expected_failure.py`
- `research/2026-08-19-anchor-trust-root-rotation.md`
- Exact published-source blob SHA matched locally executed protocol/test/unsafe files.
- Corrected deterministic suite: 11/11 passed.
- Unsafe self-asserted-key baseline: expected failure because forged key authenticated itself.
- `python -m compileall -q experiments` passed.
- Primary donors: TUF versioned root/rollback/rotation semantics and Sigstore TrustedRoot/TUF delivery.
- PR #72 squash-merged as `1d5531f5325f1dd9153566817c09e47f843b703c`.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- No real TPM/KMS/remote attestation provider has been proven available; deterministic adapters remain the honest experiment boundary.
- LAB-037's HMAC key is a reference verification-authority model, not a production public-key trust store; production verifier state must not contain provider private signing material.
- Full storage rollback after restart cannot be defeated by an in-memory trust-store version alone; LAB-034/LAB-035 external freshness/anchor layer remains required.
- LAB-037 normal rotation uses a single trusted signer and `recover()` is trusted-control input. Threshold rotation and authenticated compromise recovery are not yet proven; this is LAB-038.

## Exact next action

Start Issue #73 / LAB-038. Research TUF threshold root rotation plus an independent multi-party/break-glass recovery mechanism. Build `experiments/anchor_threshold_root/` with old-root threshold + new-root threshold validation, unique signer counting, revocation, provider/version/epoch binding, and a separately pinned recovery quorum. Reproduce unsafe one-signer/self-authorized recovery, run deterministic tests and a separate remote patch audit, then integrate only on observed validation.

## Backlog

- #73 / LAB-038 — threshold trust-root rotation and authenticated break-glass recovery — READY.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
