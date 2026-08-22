# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-080 — allow multiple authenticated durable intents to share one monotonic anchor without weakening LAB-079 rollback detection. Any observed anchor advancement beyond a component's local watermark must be explained by a contiguous authenticated intent/receipt ledger; unexplained positions remain fail-closed.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-079.
- Completed Issue #149 / LAB-079.
- Merged PR #150 / LAB-079 as `7f283b14cc67d50c223a1c13c349b8183084696b`.
- Next: Issue #151 / LAB-080 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-079 was taken through its exact-source integration gate. A new real-stack test exercised the actual final LAB-077 threshold registry, LAB-078 `SupportedMigrationCoordinator`, and LAB-036 authenticated anchor. During the final audit, a real fail-open was reproduced: a corrupted `migration_anchor_meta.global_sequence` could disagree with the binding row while `catch_up()` still advanced the external provider. The supported boundary was hardened so the local sequence/binding pair is checked before provider action and CAS-rechecked before local confirmation.

The final exact-source regression set passed after the fix and PR #150 was moved out of draft and squash-merged normally.

## Evidence produced

- LAB-079 merge: `7f283b14cc67d50c223a1c13c349b8183084696b`.
- Final PR #150 HEAD before merge: `c5998774755e11170e3120320c474ff6b094f80b`.
- Final supported LAB-079 blob executed locally: `f8a915db4de86f62f87bf987f1244b5e08ad96f9`.
- Sequence-fencing regression blob: `9631dbe39fbb9679403c6dd340e3045cc16ead46`.
- Real-stack integration regression blob: `5870ebeb14e1b13771c8c2bd1b4aa620a9ad26fc`.
- Combined exact-source LAB-079 + LAB-036 + final LAB-077 gate: 41/41 passed.
- Exact LAB-036 regression: 12/12 passed.
- Final LAB-077 audit regression: 4/4 passed.
- `python -m compileall -q experiments` passed.
- Unsafe local-only rollback seed failed as expected.
- Real-stack scenarios proved: pre-migration SQLite snapshot restore detection, unrelated pre-advanced anchor rejection, timeout-after-commit reconciliation without a duplicate increment, and first post-migration threshold successor followed by anchored restart.

## Known blockers / constraints

- No owner/product blocker.
- Direct shell GitHub DNS remained unavailable in the LAB-079 run; connector reconstruction plus Git blob verification is a proven exact-source fallback.
- LAB-079 deliberately treats an external position ahead of the local migration sequence as unexplained/fail-closed. That is safe for a dedicated anchor but prevents legitimate sharing of one anchor among multiple components.
- A higher anchor position must never be accepted merely because it is monotonic or signed; every intervening advancement needs exact authenticated intent identity.
- Shared-anchor verification is not distributed consensus, provider availability, or a general event bus.

## Exact next action

Start Issue #151 / LAB-080. Create a branch and build an unsafe baseline showing that `anchor >= local` accepts unrelated advancement. Then implement a minimal append-only shared-anchor intent ledger: persist stable intent identity/payload/provider/predecessor before increment, use exact request IDs for LAB-036 execution/reconciliation, persist authenticated receipt identity for each resulting position, and verify a contiguous suffix from a component's local watermark to the observed external position. Demonstrate two independent authorized components sharing one provider, plus gaps, duplicate positions, content substitution, provider-generation rotation, ledger rollback, UNKNOWN/retry and unknown intent-type failure cases. Keep consensus and remote ledger services out of scope.

## Backlog

- #151 / LAB-080 — shared monotonic-anchor intent ledger and explained-ahead conformance — READY.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
