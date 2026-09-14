# LAB-086 — post-cutoff proof INSERT authorization

## Finding

The current post-cutoff history fence makes existing rows in `provider_asymmetric_break_glass_proofs` and `provider_asymmetric_recovery_public_root_proofs` immutable/non-deletable and blocks replacement of an existing primary key. It still permits an ordinary SQL writer to INSERT a previously unseen key.

That is a correctness/security blocker for LAB-086 rather than merely harmless debris. The LAB-086 verifier counts these proof rows against authenticated root/public-recovery history. A bogus new proof row therefore creates a persistent fail-closed restart/verification failure.

Unlike `asymmetric_provider_receipts`, these two proof tables do not need an open-ended runtime append surface. New rows are created only by the final LAB-086 consequential writers after their cryptographic authorization has already been checked. Therefore the stronger rule is feasible here:

- after cutoff, every new proof INSERT requires the transaction-scoped final-writer thaw;
- existing proof rows remain immutable/non-deletable even while the creation gate is temporarily removed;
- the final writer verifies first, removes only the creation/writer fence inside the same `BEGIN IMMEDIATE`, inserts the proof and performs the associated mutation, reinstalls/asserts the fence, re-verifies history, then commits.

## Executed counterexample / design probe

A focused SQLite probe reproduced the current behavior: a previously unseen proof key was accepted under the existing `no replace` trigger. The strengthened split was then exercised: direct new-key INSERT was rejected, while `BEGIN IMMEDIATE -> remove creation gate -> INSERT verified proof -> reinstall gate -> COMMIT` succeeded.

This focused probe is semantic evidence only. The branch now contains an intentionally red real regression `test_post_cutoff_evidence_insert_authorization.py`; the current runtime has not yet been rewritten, so no passing exact-source result is claimed.

## Patch plan

`research/2026-08-25-lab086-post-cutoff-proof-insert-authorization.patch` records the minimal source change:

1. treat the two post-cutoff proof INSERT triggers as removable final-writer creation gates;
2. make those triggers reject every post-cutoff INSERT rather than only replacement of an existing key;
3. move the final public-recovery root-proof INSERT inside the already verified transaction-scoped thaw.

The asymmetric break-glass writer already inserts its proof inside the thaw, so it needs no ordering change.

## Boundary

This does not claim protection against arbitrary same-privilege DDL/schema control (LAB-087/#166). It also does not solve open-ended provider-receipt/shared-anchor writer authorization (LAB-091/#170). This finding is narrower: LAB-086-only proof tables can and should be closed to ordinary post-cutoff INSERT because the final LAB-086 writer is their sole legitimate creator.
