# LAB-099 — fixture DDL wiring and authority-storage boundary

Date: 2026-09-12
Status: test-owned implementation slice complete; authenticated PREPARED persistence still intentionally gated
Related: #184, PR #186, PR #177

## Result

The PR #186 test-only fixture adapter now consumes the already-frozen physical precursor relation identity directly from `lab099_precursor_relation_reference.py` for operations that require only schema corruption/setup semantics.

Specifically:

- `install_precursor_relation_without_prepared()` installs the exact frozen `provider_activation_reservation_precursors` V1 literal DDL from the independent relation oracle;
- `delete_precursor_relation()` resolves the exact frozen relation name from the same oracle;
- the adapter validates the oracle's exact relation name, literal SQL, 32-byte definition digest and standalone self-check before mutation;
- authority-bearing PREPARED/CONFIRMED/provenance mutation helpers remain separately fail-closed on the absent `lab099_precursor_fixture_vectors` module;
- `install_atomic_prepared_cutover()` additionally requires any future mutation plan to begin with the exact frozen precursor DDL, preventing a fixture vector from silently installing a different schema.

Branch commit: `1bea1eb519f07ce6eb32388eb923ed53d0f99e86`.
Published adapter blob: `6419a2bde9a13b88d4b3718ce4dab19e67ba145b`.

## Why this split is safe

The physical relation DDL is already frozen as protocol identity by `LAB099_PRECURSOR_PHYSICAL_RELATION_V1_FROZEN`; importing that identity into a test-only mutation adapter does not invent new authority.

By contrast, the durable storage representation for authenticated LAB-099 cutover PREPARED/CONFIRMED objects is not yet frozen as a concrete SQLite mutation contract. The canonical bytes/digests are frozen, but choosing where/how their authenticators and lineage records are persisted would create production protocol semantics. The adapter therefore must not fabricate those rows merely to make the crash test executable.

This means the orphan-DDL scenario can now be staged mechanically without any synthetic authority, while the atomic DDL+PREPARED scenario remains correctly gated on an independently frozen durable evidence representation.

## Actually executed local evidence

A standalone file-backed SQLite probe executed the exact frozen V1 literal DDL inside `BEGIN IMMEDIATE`, committed it, read `sqlite_master`, and verified:

- object type is `table`;
- normalized stored SQL is byte-equivalent under the repository normalization rule to the frozen literal DDL;
- SHA-256 of normalized DDL equals `696c54d1afdef52c05c120ce7d09a7a2eeb567daafb3a378b7dc4ca64f80e3bb`.

Result: PASS.

This is schema-fixture evidence only. It is not a repository RED/GREEN, not a full PR #186 import/execution pass, and not LAB-086 evidence.

## Audit

PR #186 remains test-only. Compare against pinned PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c` after the change: ahead 10, behind 0, with the same six changed files, all under `experiments/provider_generation_history/tests/`.

No production file changed.

## Remaining authority-storage gap

Before `atomic_prepared_plan()` can be implemented safely, freeze one concrete durable persistence contract for LAB-099 cutover evidence, including:

1. relation/table identity or reuse of an existing authenticated provenance relation;
2. exact fields persisted for PREPARED and CONFIRMED;
3. how canonical bytes/digests are reconstructed from storage;
4. where authenticators are stored and under which authority keys they are verified;
5. exact linkage to logical DB identity, LAB-092 predecessor completion, provenance parent/head+epoch, and PREPARED->CONFIRMED digest binding;
6. exact idempotence/sibling uniqueness constraints;
7. migration ownership and read-only startup classification.

Until that contract is frozen, the adapter should continue to raise `FixtureVectorUnavailable` for authority-bearing mutation helpers rather than fabricate test evidence.

## Next action

After the mandatory LAB-086 materialization probe, source-audit the existing authenticated provenance/shared-anchor persistence surfaces and freeze the smallest LAB-099 cutover-evidence persistence representation that reuses those mechanisms without creating a duplicate authority subsystem. Only then add `lab099_precursor_fixture_vectors.py` and make atomic DDL+exact PREPARED mechanically executable in PR #186.
