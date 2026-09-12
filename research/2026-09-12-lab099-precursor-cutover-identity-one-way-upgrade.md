# LAB-099 precursor cutover identity and one-way upgrade

Date: 2026-09-12
Status: design/versioning contract frozen; executable RED/GREEN pending
Related: LAB-092/#176, LAB-097/#182, LAB-099/#184, PR #177

## Verdict

`PROVIDER_ACTIVATION_RESERVATION_PRECURSOR_CUTOVER_IDENTITY_ONE_WAY_UPGRADE_V1_FROZEN`

This note freezes the minimum authenticated identity and crash/recovery semantics for introducing the LAB-099 provider-activation reservation precursor relation after the already-deployed/frozen LAB-092 V1 activation-schema migration marker.

It does not change production code. Exact repository execution remains unavailable in this run, so the contract remains RED-first.

## Source-proved boundaries carried forward

1. LAB-092 V1 already has a historical marker with identity `migration:provider-generation-activation-schema:v1` and payload `{schema: provider-generation-activation, version: 1}`. That historical event authenticates only the LAB-092 activation schema. It must not be reinterpreted as evidence for a later precursor relation.
2. `PROVENANCE_CANONICAL_BYTE_ENCODING_V1_FROZEN` requires exact domain separation, exact required fields, and protocol-version evolution via a new domain/version rather than ignored or retroactively added fields.
3. LAB-097 treats logical-database initialization/provenance as authority outside the deletable operational provider-history rowset; empty/missing operational history is not allowed to silently become fresh initialization.
4. The already-frozen LAB-099 relation/DDL contract requires ordinary startup to verify the precursor relation rather than auto-create/repair it and requires explicit migration with DDL plus PREPARED evidence atomically installed before a separate authenticated confirmation.
5. Existing LAB-090 activation rows without independent authenticated precursor/V2 ticket evidence remain `LEGACY_LAB090_UNATTESTED`; current mutable rows cannot be self-attested into history.

## Why the new cutover needs its own identity

The precursor relation governs authority that must exist before provider `prepare_activation()` can mutate external provider state. This is a new security boundary, not a cosmetic extension of the LAB-092 activation-state table.

Therefore neither of these is valid:

- treating the old LAB-092 V1 marker as if it had always covered the precursor relation;
- adding a new field to the old marker and continuing to call it V1.

Both would allow a verifier to assign new authenticated meaning to historical bytes that never committed to that meaning.

The cutover is a distinct authenticated migration object with its own domain/version and an explicit predecessor link to the already-authenticated LAB-092 V1 completion.

## Frozen object identities

Use two phase-specific authenticated objects so that a crash cannot turn a local phase bit into authority.

### PREPARED

Domain:

`ytim.lab099.activation-reservation-precursor-cutover-prepared.v1`

Required semantic fields:

1. `logical_database_identity_digest` — DIGEST32
2. `predecessor_lab092_completion_digest` — DIGEST32
3. `predecessor_provenance_head_digest` — DIGEST32
4. `predecessor_provenance_epoch` — U64
5. `target_schema_set_id` — UTF8, exactly `provider-activation-reservation-precursor`
6. `target_schema_set_version` — U64, exactly `1`
7. `precursor_relation_definition_digest` — DIGEST32
8. `precursor_protocol_version` — U64, exactly `1`
9. `transition_provenance_protocol_version` — U64 for the V2 transition-provenance protocol enabled by this cutover
10. `migration_nonce` — BYTES, exactly 32 bytes

The canonical envelope/framing and SHA-256 rule are the already-frozen provenance V1 encoding. The new object domains are new schema identities; they do not mutate an older domain.

### CONFIRMED

Domain:

`ytim.lab099.activation-reservation-precursor-cutover-confirmed.v1`

Required semantic fields:

1. `logical_database_identity_digest` — DIGEST32
2. `prepared_event_digest` — DIGEST32
3. `predecessor_lab092_completion_digest` — DIGEST32
4. `target_schema_set_id` — UTF8
5. `target_schema_set_version` — U64
6. `installed_schema_definition_digest` — DIGEST32
7. `resulting_provenance_head_digest` — DIGEST32
8. `resulting_provenance_epoch` — U64
9. `confirmation_nonce` — BYTES, exactly 32 bytes

`CONFIRMED` is valid only when it references the exact authenticated `PREPARED` event being completed. A generic `version=1` or local status flag is not a substitute.

## One-way state machine

For one logical database and one target schema-set version:

`ABSENT -> PREPARED -> CONFIRMED`

No reverse edge exists.

### ABSENT -> PREPARED

Allowed only if all of the following hold before mutation:

- logical database identity is already authenticated;
- the LAB-092 V1 predecessor completion is present and authentic;
- the current authenticated provenance parent/head and epoch equal the values consumed by the PREPARED event;
- no PREPARED/CONFIRMED event already exists for this target schema-set version and logical database;
- no sibling reservation exists for the same predecessor parent/epoch;
- legacy LAB-090 rows are not being backfilled into authority.

The explicit migration transaction remains the previously frozen Tx M/R boundary: `BEGIN IMMEDIATE`, install the exact repository-owned precursor relation DDL and persist the deterministic authenticated PREPARED cutover evidence atomically, then commit.

A process crash before this SQLite transaction commits leaves neither installed governed DDL nor durable PREPARED state and may retry from the still-current authenticated predecessor.

### PREPARED -> CONFIRMED

The migration must first re-verify:

- exact logical database identity;
- exact PREPARED bytes/digest/authenticators;
- exact LAB-092 predecessor completion digest;
- exact installed relation schema/DDL identity;
- authenticated chain ancestry from the predecessor parent through this PREPARED operation;
- no conflicting sibling/forked cutover event;
- exact target schema-set and protocol versions.

Only then may an authenticated CONFIRMED event for that exact PREPARED digest be appended/persisted according to the global provenance-chain rules.

## Parent/head and epoch consumption

The PREPARED event consumes a specific authenticated predecessor head and epoch. This is mutation authority, not merely audit metadata.

Rules:

1. A PREPARED object created for parent `P`, epoch `E` cannot authorize a fresh cutover under another current parent/epoch.
2. If the global provenance head advances before PREPARED is persisted, that PREPARED attempt is stale and must be rejected/reconstructed from the new authenticated head.
3. Once an exact PREPARED has been durably committed and linked into provenance, later head advancement does not make the historical PREPARED invalid. Recovery must prove authenticated ancestry from the consumed parent through that exact PREPARED rather than requiring the database's current head to remain byte-equal to the old predecessor.
4. CONFIRMED therefore references the exact PREPARED digest and records the resulting provenance head/epoch. It cannot consume a sibling PREPARED or merely match the same target version.
5. Epoch comparison is exact authenticated U64 semantics; wall-clock age is irrelevant.

This distinguishes stale replay from legitimate crash recovery after a durable PREPARED.

## Crash/recovery classification

### Crash before Tx commit

Observable durable state: old governed schema only; no PREPARED.

Classification: `ABSENT`. Retry is permitted only after re-verifying the current authenticated predecessor head/epoch.

### Crash after DDL + PREPARED Tx commit, before CONFIRMED

Observable durable state: exact precursor relation installed and exact authenticated PREPARED durable; CONFIRMED absent.

Classification: `PREPARED_INCOMPLETE`.

Recovery may only continue confirmation of that exact PREPARED. It must not create a new/sibling PREPARED, silently reset to ABSENT, or treat the relation as ordinary startup-owned DDL.

### Physical precursor relation present but PREPARED absent

Classification: `ORPHAN_UNAUTHENTICATED_SCHEMA`.

Fail closed before provider mutation or startup repair. Do not auto-adopt the relation and do not synthesize PREPARED from installed DDL.

### PREPARED present but relation missing or definition mismatched

Classification: `AUTHENTICATED_CUTOVER_STORAGE_CORRUPTION`.

Fail closed. The authenticated PREPARED is evidence that the governed relation was part of the cutover transaction; ordinary startup must not recreate/repair it.

### CONFIRMED present but PREPARED absent/mismatched

Classification: `BROKEN_CUTOVER_PROVENANCE`.

Fail closed. CONFIRMED never stands alone.

### CONFIRMED valid

Classification: `PRECURSOR_V1_GOVERNED`.

Ordinary startup requires the exact relation/schema and the exact authenticated PREPARED -> CONFIRMED lineage. It may not fall back to LAB-092-only/LAB-090 legacy semantics if the relation disappears.

## Idempotence and replay rules

- Re-observing byte-identical PREPARED evidence with the same digest is idempotent; it does not create a second event or new authority.
- Re-observing byte-identical CONFIRMED evidence is likewise idempotent.
- A changed logical DB identity, LAB-092 predecessor digest, predecessor head, epoch, schema-definition digest, target version, nonce, or protocol version is a different object and cannot overwrite/relabel the old event.
- Two PREPARED events targeting the same logical DB/schema-set version from the same predecessor parent/epoch are a conflict, not two retries, unless the canonical bytes/digest are identical.
- A PREPARED copied to another logical database fails identity binding.
- A PREPARED replayed after an unrelated head/epoch advance cannot authorize a new mutation; only authenticated recovery of the already-durable exact event is allowed.
- A future precursor schema/protocol V2 requires a new domain/version and an explicit authenticated predecessor from the V1 completion. It cannot mutate or relabel V1 history in place.

## Anti-downgrade invariant

Once a valid `CONFIRMED` exists for precursor V1:

- absence of the precursor relation is corruption, not evidence of a pre-cutover database;
- absence of later operational activation rows cannot revert the database to LAB-090/LAB-092-only behavior;
- deleting PREPARED while retaining CONFIRMED, or deleting CONFIRMED while retaining later governed history, is fail-closed provenance damage;
- startup cannot choose a lower semantic version because older marker rows still exist.

The highest authenticated one-way cutover lineage defines the minimum accepted protocol generation.

## Minimum RED-first matrix

Freeze executable regressions before production precursor code:

1. Authenticated LAB-092 V1 marker alone does **not** authorize precursor relation semantics.
2. Valid current predecessor + exact DDL => `ABSENT -> PREPARED` can be constructed.
3. PREPARED canonical bytes/digest change when logical DB identity changes.
4. PREPARED changes when LAB-092 predecessor completion digest changes.
5. PREPARED changes when predecessor head or epoch changes.
6. PREPARED changes on one-byte canonical relation-definition change.
7. Exact byte-identical PREPARED retry is idempotent.
8. Non-identical sibling PREPARED at the same predecessor parent/epoch is rejected.
9. PREPARED built on a stale parent/epoch before Tx commit is rejected.
10. Crash before Tx commit leaves no governed precursor relation and no PREPARED; safe retry requires fresh predecessor verification.
11. Crash after atomic DDL+PREPARED commit is classified `PREPARED_INCOMPLETE`.
12. Recovery from case 11 can only confirm the exact PREPARED digest.
13. Physical relation with no authenticated PREPARED fails closed; no auto-adoption.
14. PREPARED with missing relation fails closed; no startup repair.
15. PREPARED with schema mismatch fails closed.
16. CONFIRMED referencing another/sibling PREPARED fails closed.
17. CONFIRMED copied across logical DB identity fails closed.
18. PREPARED from a forked provenance parent fails closed on the canonical lineage.
19. Durable PREPARED remains historically valid after later authenticated head advancement only when exact ancestry through that PREPARED is proven.
20. Stale PREPARED not already durable in the canonical lineage cannot be replayed after head advancement.
21. Valid CONFIRMED + missing PREPARED fails closed.
22. Valid CONFIRMED + missing/mismatched precursor relation fails closed.
23. Valid CONFIRMED prevents fallback to LAB-092-only/LAB-090 legacy startup semantics.
24. Existing `LEGACY_LAB090_UNATTESTED` activation rows cannot be hashed/backfilled to satisfy PREPARED or CONFIRMED.
25. Future schema/protocol version cannot overwrite/relabel V1 events under the same domain.
26. Wrong domain with byte-equivalent field values is rejected by canonical provenance decoding.

## Implementation ordering when executable source returns

1. Add canonical reference vectors for both new domains to the shared provenance encoder RED suite.
2. Add migration-state classifier REDs for orphan DDL, PREPARED-without-DDL, CONFIRMED-without-PREPARED, and anti-downgrade.
3. Add crash/restart REDs for pre-commit and post-PREPARED/pre-CONFIRMED boundaries.
4. Add stale parent/epoch, fork, sibling, logical-DB replay, and exact-idempotence REDs.
5. Only after those regressions are executable and observed RED should production migration/provenance code be changed.
6. Re-run LAB-092, LAB-097, LAB-099 and LAB-100 matrices together; precursor cutover cannot be accepted as a standalone local-schema feature.

## Non-goals

This note does not select a new signing primitive or replace the already-frozen dual predecessor/successor precursor authenticator contract. It does not define the full provider transition V2 implementation. It only freezes the migration/cutover identity, one-way upgrade, lineage consumption and crash classification required so those later objects cannot derive authority from retroactively reinterpreted LAB-092 history.
