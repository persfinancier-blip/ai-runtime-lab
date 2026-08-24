# LAB-086 — inherited consequential-writer fence

## Finding

The first final LAB-086 wrapper re-verified complete migration/asymmetric history around public-recovery rotation, but normal root-authority rotation and provider-generation rotation were still inherited from LAB-083/LAB-084 through `__getattr__`.

Those lower writers are correct for their own layers. They are not aware of LAB-086 migration/asymmetric proof tables. Therefore an already-corrupted LAB-086 proof could coexist with a newly committed normal root/provider successor, with the corruption detected only by a later restart verifier. That is a persistent fail-closed availability/correctness defect even though it does not grant attacker authority.

A Python-only override on the final wrapper is not sufficient: callers can still hold the direct `SupportedAsymmetricBreakGlassLedger` or its lower controller objects. The durable migration boundary therefore now also installs SQL deny triggers at the canonical lower write points:

- `provider_rotation_authority_transitions` for normal root rotation;
- `provider_rotation_threshold_proofs` for threshold-authorized provider rotation;
- `asymmetric_provider_transitions` as a second provider-history fence.

The final supported writer owns one `BEGIN IMMEDIATE`, verifies complete LAB-086 history, temporarily removes the deny fence transactionally, performs the lower mutation, reinstalls/asserts the fence, re-verifies complete LAB-086 history, and only then commits. A transaction abort rolls both data changes and temporary trigger removal back.

The fence intentionally targets canonical supported/controller write points rather than arbitrary raw SQL. A same-privilege process with unrestricted SQLite DDL can drop triggers; that broader schema-control trust boundary remains LAB-087 / Issue #166.

## Failure semantics

- Corrupt LAB-086 history + final normal-root/provider rotation: fail before mutation.
- Direct lower normal-root/provider rotation after cutoff: SQL trigger abort; whole transaction rolls back.
- Final controlled writer: fence removed only under the write lock after pre-verification, restored before post-verification/commit.
- Pre-cutoff lower rotations remain available because the triggers are conditional on the authenticated LAB-086 boundary row.

## Evidence in this pass

- New exact branch paths are recorded by GitHub; full merged-stack execution remains the merge gate.
- A focused SQLite harness exercised the inherited trigger policy: direct lower root/provider canonical inserts were denied, while transaction-scoped remove/mutate/reinstall succeeded and the restored fence denied later writes (2/2). This harness validates SQL semantics but is not counted as exact current-head regression evidence.
- Dedicated real-schema regressions are now present for final inherited-writer guards and direct lower supported surfaces; they must be executed in the one-shot connector-reconstructed LAB-080→086 closure before merge.
