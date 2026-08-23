# LAB-086 — non-forgeable public-recovery mutation fence

## Finding

The earlier LAB-086 SQL fence treated the presence of a structurally matching row in `provider_asymmetric_recovery_public_root_proofs` as permission for stale LAB-085/LAB-086 writers to mutate `provider_recovery_public_authorities`, `provider_recovery_public_transitions`, and `provider_recovery_public_head`.

That is not a safe authority boundary. SQLite triggers can compare stored metadata, but they cannot cryptographically validate the stored root quorum signatures. A forged/corrupted proof row could therefore satisfy the trigger predicate, let a stale mutation-first writer commit a successor, and leave later restart verification to discover the damage. This is persistent fail-closed DoS.

## Corrected design

Durable root-proof rows are now **evidence only**. They are never interpreted by SQL as a capability.

After the authenticated migration cutoff, unconditional SQLite triggers deny all underlying public-recovery authority/transition/head mutation. The final supported writer is the only supported bypass:

1. acquire `BEGIN IMMEDIATE`;
2. verify the migration boundary;
3. verify old-public Ed25519 threshold;
4. verify new-public Ed25519 threshold;
5. verify current normal/root threshold;
6. persist or match the exact historical root-proof row;
7. transactionally remove the deny triggers;
8. execute the underlying authority/transition/head mutation;
9. reinstall and assert the current deny-trigger policy;
10. verify the resulting public-recovery history;
11. commit.

SQLite schema DDL is transactional. If any step after trigger removal fails or the transaction rolls back, the trigger removal rolls back with the data changes. `BEGIN IMMEDIATE` excludes a second writer from entering the temporary unfenced interval.

No durable boolean/token is introduced as mutation authority.

## Executed evidence

Exact published `strict_fence.py` blob `9d18bd929b39b311767f6b1662fbc471c9c16899` and exact published self-contained test blob `8343169c7b3cc4336ec3d9568a7ad6a5877b71e3` were executed locally.

`test_strict_fence` result: **4/4 passed**.

Covered cases:
- forged structurally matching proof row cannot authorize an authority insert;
- controlled write-locked mutation can remove/reinstall the fence and commit;
- rollback after temporary trigger removal restores the fence;
- obsolete proof-row-authorizing trigger names are replaced.

The exact updated `migration_guard.py` and `final_supported.py` blobs are `770dd9cd653d48d569c3792dbe43b899079383d3` and `518297c1191c444478efabe8081ec5b1bf533952`; both corresponding locally generated exact bytes passed Python compilation before publication.

## Remaining gate

This closes the forged-proof-row design blocker, but it does not substitute for the full merged-stack regression gate. Before merge, current-head LAB-086 integration tests and LAB-085/084/083/082/080 regressions still need exact-source execution, unsafe seed, compileall, and a fresh audit of alternate mutation entry points and restart/race semantics.
