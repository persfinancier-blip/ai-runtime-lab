# LAB-099 PREPARED authority prerequisite gap

Date: 2026-09-13

## Context

LAB-086 remains priority #1, but exact byte-preserving repository materialization is still unavailable in this runtime. A direct raw-GitHub fallback was probed and failed before bytes could be transferred, so no LAB-086 executable gate was weakened or claimed.

The permitted fallback was therefore LAB-099: source-audit LAB-092 durable completion/provenance and existing provider-history/shared-anchor primitives, then implement the smallest independent authenticated PREPARED migration authority without importing `tests/lab099_*`.

## Finding

The currently frozen LAB-099 precursor/cutover storage contract requires two authority-bearing values that production LAB-092/LAB-090 does not currently provide:

- `logical_database_identity_digest`
- `parent_chain_link_digest`

The production LAB-099 table introduced in draft PR #186 includes these fields as `NOT NULL` and uniqueness inputs. The independent test vectors deliberately use synthetic fixed bytes for them, but those vectors are test authority only and must not become production authority.

A repository code search on current `main` found no production definition/use of `logical_database_identity_digest` or `parent_chain_link_digest`. LAB-095/#180 already identifies the underlying missing construction-bound logical database/history identity and explicitly requires a lifetime-stable database identity rather than mutable `path` rebinding.

LAB-092's production provenance proves activation-schema completion through a CONFIRMED shared-anchor migration intent and verifies provider history/runtime authority before reauthentication. It does not create or authenticate a logical database identity digest or a parent chain-link identity suitable for LAB-099's precursor record.

## Why the obvious fallbacks are unsafe

The following would synthesize authority and were rejected:

1. Copy the test-only frozen bytes (`00..1f`, `20..3f`) into production.
2. Hash `str(path)` or the SQLite filename. `path` is explicitly mutable/rebindable today and LAB-095 exists because that is not an authenticated database identity.
3. Hash mutable local table contents and call the result a logical database identity. That would be self-asserted by the same state LAB-099 is intended to protect.
4. Re-label the LAB-092 completion marker digest as `logical_database_identity_digest`. It proves one migration event, not construction-bound database identity.
5. Accept caller-supplied digests in `migrate_precursor_cutover_v1()`. That would let the migrator choose the root identity being authenticated.

## Useful production authority that *is* available

The source audit did confirm that existing production primitives are sufficient for the ticket-specific half once a construction-bound database/chain identity exists:

- `provider_generation_transitions` binds old/new generation IDs with old/new MACs;
- `provider_generations` provides the corresponding verification keys;
- `provider_generation_activations` contains `activation_id`, successor generation/provider, `expected_position`, `fence`, and durable status;
- LAB-092 verifies full durable provider history and runtime generation before confirming its migration marker;
- the shared-anchor ledger can authenticate a migration intent through PREPARED -> provider increment/reconcile -> CONFIRMED receipt.

Therefore the smallest safe LAB-099 PREPARED migration is now blocked specifically on a production construction-bound database/history identity (and deterministic parent-chain-link derivation from it), not on the activation-ticket cryptographic material itself.

## Decision

Do not implement LAB-099 PREPARED persistence yet. Treat LAB-095/#180 as a prerequisite for the frozen LAB-099 schema unless the LAB-099 storage contract is deliberately revised to remove the database/parent identity fields with a new independently frozen contract.

This is not an owner-level product decision: the current safest engineering action is to preserve the fail-closed migration API, document the dependency, and avoid manufacturing authority.

## Next engineering action

1. Keep LAB-086 first priority and re-probe exact byte-preserving materialization next run.
2. If still unavailable, advance LAB-095 enough to define the construction-bound logical database/history identity and parent-chain-link derivation contract, regression-first.
3. Then return to LAB-099 and derive PREPARED authority from that production identity + verified provider transition/activation data + LAB-092 completion state.
4. Only after those identities are production-derived should `migrate_precursor_cutover_v1()` atomically install precursor DDL/cutover evidence/PREPARED shared-anchor state.

No production code was changed in this slice because every currently available implementation path for those two fields would weaken the frozen authority model.
