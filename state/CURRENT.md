# Current Lab State

Last updated: 2026-08-20

## Active objective

LAB-057 — give LAB-056's separate recovery quorum its own authenticated lifecycle without allowing self-authorized recovery-quorum replacement or creating an infinite recovery chain.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-056.
- Next: Issue #107 / LAB-057 — READY.
- Active implementation branch: none yet.
- Active PR: none.

## Last completed step

LAB-056 removed LAB-055's final single static observer-registry root key. Registry authority is now explicit/versioned/threshold-authenticated; normal root rotation requires old-root and new-root threshold authorization over the same transition, break-glass recovery uses a separate threshold quorum and advances `authority_epoch`, and every registry snapshot binds exact root ID/version/epoch.

A separate authority audit found that the first corrected implementation persisted root states without the threshold proofs of root-to-root transitions. That would have allowed a fabricated but structurally plausible root history to survive restart. The final implementation persists each normal-rotation or recovery proof and re-verifies the complete root chain on load, including bootstrap-root and recovery-authority identities.

Corrected deterministic tests passed 16/16; compileall passed. The unsafe one-signer self-authorized registry rewrite failed as expected. PR #106 was remote patch-audited and squash-merged into `main` as `ee4ea96224bdd12f9c61f0260f56b0baa81e74e8`. Issue #105 was closed DONE.

## Evidence produced

- `experiments/ctv2_observer_registry_threshold_root/protocol.py`
- `experiments/ctv2_observer_registry_threshold_root/tests/test_protocol.py`
- `experiments/ctv2_observer_registry_threshold_root/tests/unsafe_single_signer_expected_failure.py`
- `research/2026-08-20-observer-registry-threshold-root.md`
- Corrected suite: 16/16 passed.
- Unsafe seed: failed as expected.
- Compileall: passed.
- Authority audit regression coverage includes fabricated transition-history rejection and bootstrap-root substitution rejection.
- Merge SHA: `ee4ea96224bdd12f9c61f0260f56b0baa81e74e8`.
- Follow-up Issue #107 / LAB-057 created.

## Known blockers / constraints

- No active blocker.
- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is supported.
- Reliable gossip transport, Byzantine consensus, global total ordering, and fork prevention remain out of scope.
- LAB-056 still treats the recovery quorum as a separately pinned immutable trust input. It is thresholded, but planned recovery-key rotation/revocation has no authenticated lifecycle yet.

## Exact next action

Start Issue #107 / LAB-057. Research a minimal recovery-authority lifecycle using the proven LAB-038/LAB-056 threshold-continuity rules plus primary-source recovery/rekey mechanisms. For planned recovery-authority rotation, require old-recovery threshold + new-recovery threshold + current-root threshold co-authorization so the recovery quorum cannot silently self-expand while root authority is healthy. Persist and re-verify recovery-authority transition proofs across restart, reject stale/revoked recovery signers, bind root break-glass operations to the exact current recovery authority, and preserve exact historical recovery authority identity for replay. Explicitly document the final out-of-band boundary when both normal root authority and recovery quorum are compromised or lost. Add an unsafe self-authorized recovery-quorum swap seed, run deterministic tests + compileall, perform a separate authority audit, then integrate if acceptance criteria pass.

## Backlog

- #107 / LAB-057 — recovery-quorum lifecycle, rotation, and compromise-boundary conformance — READY.
- Reliable gossip transport, Byzantine consensus, and fork prevention remain out of scope unless evidence makes them the next correctness bottleneck.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
