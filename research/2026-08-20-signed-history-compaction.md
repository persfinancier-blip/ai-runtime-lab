# LAB-062 — Threshold-authenticated compaction integration

## Question

Can already-verified signed transition history be pruned from the live SQLite store without weakening LAB-059 threshold-signature, payload, authority-evolution, or transition-digest verification?

## Reused mechanisms

LAB-062 does not introduce a simplified transition proof format. Retained and archived rows use the existing LAB-059 row/proof schema and call the same `rotation_payload`, `recovery_payload`, `verify_threshold`, authority content-ID lookup, and transition-digest rules.

LAB-061 contributes the storage boundary: exact canonical archive bytes are written and fsynced before destructive change, then archive registration, compaction-base advancement, and prefix deletion occur in one `BEGIN IMMEDIATE` write transaction. SQLite documents that an IMMEDIATE transaction begins the write transaction immediately and that changes persist only through COMMIT; failure paths can roll back the database-side prune atomically.

The archive is content-addressed. This follows the general content-addressing property used by Git objects: identity is derived from exact stored content rather than a caller-selected filename.

## Experiment

A deterministic threshold-signed root/recovery chain is built using LAB-059. A signed compact checkpoint binds history identity, terminal authority IDs, cumulative prefix commitment, previous base/archive identity, external-anchor identity, and signer identity.

Compaction then:

1. verifies the current retained history using LAB-059 proof rules;
2. verifies the checkpoint is current and derived from that history;
3. re-verifies the exact rows selected for archival with the same threshold rules;
4. writes exact content-addressed archive bytes and manifest;
5. rechecks all inputs under `BEGIN IMMEDIATE`;
6. atomically records the new base/archive manifest and deletes only the checkpointed prefix.

Restart verifies the persisted checkpoint and archive-manifest binding, derives the current authority state from the compacted base, and threshold-verifies only retained rows. Explicit forensic audit reads archive bytes and threshold-verifies the archived rows again.

## Audit finding

The first corrected implementation still allowed an archive manifest to commit to an arbitrary `start_root_id/start_recovery_id/start_commitment` while ending at the legitimate checkpoint state. Because the current base referenced the manifest content ID, simple content-addressing alone did not prove that its start state was the checkpoint's actual predecessor base.

The fix binds each archive start to the checkpoint's signed `(base_sequence, base_archive_id)`. For bootstrap this derives the exact bootstrap authority IDs and seed commitment. For later compactions it loads the exact previous content-addressed archive manifest and requires the new manifest start state to equal that previous manifest's authenticated terminal state. Explicit archive audit also requires the selected archive to be reachable from the current compaction chain.

## Observed validation

- Corrected deterministic suite: 15/15 passed.
- Unsafe delete-first seed: failed as expected because deleting live rows before establishing a checkpoint/archive base destroys restart verification.
- `python -m compileall -q experiments/signed_history_compaction`: passed.
- Failure matrix covers retained signature corruption, archive corruption, payload/digest substitution, base/checkpoint substitution, archive-history substitution, suffix gap/head mismatch, pre-commit failures, timeout-after-commit reconciliation, and second compaction after additional signed transitions.

## Boundary / non-goals

- SQL row deletion is not forensic erasure.
- Archive bytes are not a new runtime authority; the checkpoint/base/manifest binding is the live boundary.
- Whole-database rollback freshness still requires LAB-034–037's external monotonic anchor.
- This is local-store compaction, not distributed consensus, remote archive durability, or PostgreSQL tuning.
