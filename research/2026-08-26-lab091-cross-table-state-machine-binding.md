# LAB-091 — cross-table state-machine binding for one-shot SQL permits

## Finding

The first operation-scoped LAB-091 candidate correctly bound a one-shot permit to the exact row bytes being inserted or updated, but that was still weaker than binding the mutation to the authoritative LAB-080/LAB-082 state machine.

A focused executable counterexample showed two fail-closed durable-corruption paths even when the caller supplied an exact matching permit:

1. a `PREPARED` intent could be inserted with `provider_id='attacker'` / generation `999` while the durable asymmetric provider head was `anchor-A` generation `1`;
2. an asymmetric provider receipt could be inserted for an orphan `request_id` with no matching `PREPARED` intent.

The v2 trigger layer therefore proved only “this is exactly the row the permit issuer requested”, not “this row is a legal successor of the current durable state”. A buggy or compromised permit issuer inside the broker could persist logically impossible rows that later verification would reject only after the mutation had committed.

## Corrected mechanism

An additive v3 cross-table guard layer now binds exact one-shot permits to authoritative state:

- intent creation requires `NEW.predecessor_position == shared_anchor_meta.reserved_position`;
- intent provider ID/generation must match the current `asymmetric_provider_head` joined to `asymmetric_provider_generations`;
- meta tail advancement requires a matching `PREPARED` intent whose predecessor is the old tail and whose position is the new tail;
- provider receipt creation requires `kind='RECONCILE'` and a matching `PREPARED` intent with the same request ID, provider ID, provider generation and position;
- the v3 trigger names are distinct from both legacy and v2 namespaces, so the older installer does not remove them.

The candidate final surface `SupportedStateMachineOperationScopedAsymmetricSharedAnchorLedger` installs both the exact v2 row guards and the v3 cross-table guards in one `BEGIN IMMEDIATE` transaction.

## Focused evidence

The additive runtime files were published from the locally executed candidate and their Git blobs match exactly:

- `cross_table_guards.py`: `b73c7ae95669a561a13c5fc2c1eca752721fe8a4`;
- `state_machine_operation_scoped.py`: `b359a9a191ea9632e97c227193b3bde886f904dc`.

Focused execution passed 6/6 scenarios:

- wrong provider/generation intent rejected despite exact permit;
- wrong predecessor/tail intent rejected despite exact permit;
- meta advancement rejected without its matching PREPARED intent and accepted after that intent exists;
- orphan receipt rejected despite exact permit;
- READ receipt rejected while matching RECONCILE receipt is accepted;
- after durable provider-head rotation, an old-generation intent is rejected and the new generation is accepted.

The published regression file is semantically the same six-case matrix, but its Git blob differs from the earlier local harness because of formatting/transcription during Contents API publication. Therefore the 6/6 result is focused candidate evidence, **not** exact execution of the published test blob.

## Remaining boundary

This does not complete LAB-091. The real-stack gate still must execute the final state-machine surface against actual LAB-080/LAB-082 implementations, including restart, concurrent workers, crash rollback, timeout/UNKNOWN reconciliation and LAB-087 restricted-worker composition.

The permit issuer remains part of the broker trust boundary. The v3 guards reduce the damage from a wrong permit by enforcing key cross-table invariants, but they do not turn SQLite triggers into a security boundary against arbitrary same-privilege DDL/UDF control; LAB-087 owns the external writable-handle/process/filesystem boundary.
