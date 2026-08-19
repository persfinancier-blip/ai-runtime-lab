# Current Lab State

Last updated: 2026-08-19

## Active objective

Advance from authenticated anchor responses to trustworthy verifier key/trust-root lifecycle. LAB-035 and LAB-036 are complete; LAB-037 must prove that provider verification keys cannot be silently substituted, rolled back, reused after revocation, or kept authoritative across compromise recovery.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-036.
- Completed Issue #69 / LAB-036.
- Merged PR #70 / LAB-036, squash merge `4f9d6d0d9d12b773d45e9934f517453023c837f5`.
- Active next: Issue #71 / LAB-037 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-036 replaced implicit trust in `anchor.read()` and increment receipts with explicit provider identity/generation + verifier challenge + operation kind + stable request identity authentication. A deterministic HMAC reference provider was used only as an executable trust-boundary model, not as a claim of real TPM/KMS availability.

The unsafe unauthenticated-read seed accepted a spoofed position. The corrected verifier rejected forged position, replay, wrong provider, stale generation, challenge mismatch and operation-kind confusion. UNKNOWN increment transport outcome was reconciled with the same request identity and a new challenge without a duplicate increment.

## Evidence produced

- `experiments/anchor_attestation/protocol.py`
- `experiments/anchor_attestation/tests/test_protocol.py`
- `experiments/anchor_attestation/tests/unsafe_unauthenticated_expected_failure.py`
- `research/2026-08-19-anchor-attestation-provider-identity.md`
- Corrected deterministic suite: 12/12 passed.
- Unsafe baseline: expected failure because spoofed unauthenticated position was accepted.
- `python -m compileall -q experiments` passed.
- Primary mechanisms: RFC 9421 signed-message freshness/replay controls; RFC 9334 RATS freshness separation; NIST nonce/challenge replay resistance.
- PR #70 remote patch-audited and squash-merged as `4f9d6d0d9d12b773d45e9934f517453023c837f5`.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- No real TPM/KMS/remote attestation provider has been proven available; deterministic adapters remain the honest experiment boundary.
- Signed/authenticated observations prove provider-origin/freshness for the covered exchange, not monotonicity by themselves. LAB-034/LAB-035 DB/anchor invariants remain authoritative.
- The LAB-036 verifier keyring is trusted-control input. Its provisioning, rotation, revocation and compromise recovery are not yet proven; this is LAB-037.
- An unavailable attestation path fails closed but must not be mislabeled as authenticated rollback evidence.

## Exact next action

Start Issue #71 / LAB-037. Research primary trust-anchor/key rotation/revocation mechanisms, then build `experiments/anchor_trust_root/`. Reproduce unsafe self-asserted verification-key acceptance; implement a versioned trust-store/authority-epoch model covering pinned current key, unknown key, stale generation, trust-store rollback, revocation, cross-provider substitution, authenticated rotation, crash/restart atomicity and compromise-recovery epoch. Run deterministic tests, separate audit, and integrate only on observed validation.

## Backlog

- #71 / LAB-037 — anchor verifier trust-root rotation and compromise-recovery conformance — READY.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
