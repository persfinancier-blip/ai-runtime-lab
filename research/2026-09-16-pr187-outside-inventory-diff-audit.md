# PR #187 outside-inventory diff audit — 2026-09-16

## Scope

Audited PR #187 at observed head `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057` against the executable closure inventory in `research/2026-09-16-lab094-096-closure-inventory.md`.

The purpose was narrow: identify changed files not named as retained-authority/hash inventory entries or direct pytest gate paths that can materially affect supported startup, provider rotation, or database identity. This is source audit only; no executable GREEN is inferred.

## Observed PR shape

PR #187 remains draft and open with 44 changed files. The changed-file list includes the retained-authority files already inventoried, direct gate tests already listed, and several production modules whose behavior is exercised indirectly by those gates.

Production files outside the seven-file retained-authority blob list include:

- `experiments/provider_generation_history/activation.py`
- `experiments/provider_generation_history/activation_coordinator.py`
- `experiments/provider_generation_history/activation_schema.py`
- `experiments/provider_generation_history/activation_schema_migration.py`
- `experiments/provider_generation_history/activation_schema_provenance.py`
- `experiments/provider_generation_history/activation_schema_startup.py`
- `experiments/provider_generation_history/activation_transition.py`

The PR also contains LAB-095 canonical-reference/red-intent test helpers. Those are test/reference surfaces, not production startup/rotation/database-identity authority.

## Concrete audit result

No new executable gate omission was found.

`activation.py` defines provider-owned activation fencing (`ActivationState`, immutable `ActivationTicket`, `FencedActivationProvider`) and blocks ordinary increments while an activation reservation is pending. Its supported behavior is directly exercised by the already-required `test_activation_fence_composed.py` and by the rotation/integration gates.

`activation_coordinator.py` owns durable activation acknowledgement/recovery. It reconciles only the durable current generation, requires `FencedActivationProvider` for a durable activation ticket, rejects released-before-acknowledgement and lost-reservation states, and rejects historical unresolved `SQL_COMMITTED` rows. Its ordering/recovery surface is already covered by the required `tests/test_activation_coordinator_ordering.py`, `tests/test_activation_restart_recovery.py`, composed fence tests, and integration tests.

The activation-schema/migration/provenance/startup/transition production modules are already represented by the explicit bootstrap, bootstrap-failure, migration-writer, schema-contract, provenance-guard, startup, transition-ordering, supported-wiring, and integration gates in the closure inventory. Adding file names to the hash list would not add behavioral evidence; exact-tree execution of the existing gates is the required evidence.

The LAB-095 reference/red-intent files should remain non-authoritative test scaffolding. Production must not depend on them; the existing closure decision already records that boundary.

## Decision

Do not broaden LAB-094/095/096 or add speculative tests from this audit. The existing executable inventory covers every changed production surface in PR #187 that can materially affect supported startup, provider rotation, or database identity, either directly or through composed/integration gates.

The remaining acceptance blocker is unchanged: byte-exact materialization followed by retained blob/hash verification, focused/composed/downstream execution, full pytest, and compileall. No executable PASS is claimed from this source audit.
