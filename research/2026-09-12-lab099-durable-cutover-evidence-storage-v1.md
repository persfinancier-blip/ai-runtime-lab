# LAB-099 durable cutover evidence storage V1

Date: 2026-09-12
Status: storage contract frozen; executable RED/GREEN pending
Related: #176, #184, PR #177, PR #186

## Verdict

`LAB099_DURABLE_CUTOVER_EVIDENCE_STORAGE_V1_FROZEN`

LAB-099 must not introduce a second authentication/provenance subsystem. Durable cutover evidence is split into:

1. a small SQLite materialization relation that stores the exact PREPARED bytes plus the confirmation nonce needed for deterministic recovery; and
2. the existing authenticated `shared_anchor_intents` mechanism, whose PREPARED/CONFIRMED state and externally reauthenticated `receipt_binding` remain the authority-bearing phase transition.

The cutover materialization row is not authority by itself. The shared-anchor row is not sufficient by itself either: startup must require their exact cross-binding plus the frozen precursor relation DDL.

No production code is changed by this note.

## Source audit

The current shared-anchor ledger already provides the properties the cutover needs:

- `shared_anchor_intents` has immutable intent identity/content binding (`intent_id`, `component_id`, `intent_type`, `payload_digest`), provider generation, predecessor/position, deterministic request ID, PREPARED/CONFIRMED state and a confirmed `receipt_binding`;
- `reserve()` serializes with `BEGIN IMMEDIATE`, permits one unresolved PREPARED intent, advances the reserved position atomically, and treats reuse of one `intent_id` with changed content as conflict;
- `execute()` reauthenticates the exact request/position with the external anchor and only then transitions the exact unchanged row from PREPARED to CONFIRMED with a stable receipt binding;
- LAB-092 already demonstrates DDL + one deterministic PREPARED shared-anchor migration intent in one SQLite transaction, followed by separate authenticated confirmation.

Provider history separately demonstrates the repository convention for reconstructing and verifying authenticated material rather than trusting a mutable self-hash. LAB-099 should follow the same rule.

## Materialization relation

Exact V1 relation name:

`provider_activation_reservation_cutovers`

Exact V1 DDL:

```sql
CREATE TABLE provider_activation_reservation_cutovers(
  logical_database_identity_digest BLOB NOT NULL CHECK(typeof(logical_database_identity_digest)='blob' AND length(logical_database_identity_digest)=32),
  target_schema_set_id TEXT NOT NULL,
  target_schema_set_version INTEGER NOT NULL CHECK(target_schema_set_version=1),
  predecessor_provenance_head_digest BLOB NOT NULL CHECK(typeof(predecessor_provenance_head_digest)='blob' AND length(predecessor_provenance_head_digest)=32),
  predecessor_provenance_epoch INTEGER NOT NULL CHECK(predecessor_provenance_epoch>=0),
  prepared_canonical BLOB NOT NULL,
  prepared_digest BLOB NOT NULL UNIQUE CHECK(typeof(prepared_digest)='blob' AND length(prepared_digest)=32),
  confirmation_nonce BLOB NOT NULL CHECK(typeof(confirmation_nonce)='blob' AND length(confirmation_nonce)=32),
  anchor_intent_id TEXT NOT NULL UNIQUE,
  PRIMARY KEY(logical_database_identity_digest,target_schema_set_id,target_schema_set_version),
  UNIQUE(logical_database_identity_digest,predecessor_provenance_head_digest,predecessor_provenance_epoch)
)
```

Using the LAB-090/LAB-092 `_normalized_sql(sql) == " ".join(sql.split())` convention, `SHA256(UTF8(normalized DDL))` is:

`0db2587bae8861d0233d939b4283a58b438b947c5336f7af9d0f1687856c860e`

This is the cutover-evidence materialization relation definition digest. It is distinct from the already-frozen precursor relation definition digest `696c54d1afdef52c05c120ce7d09a7a2eeb567daafb3a378b7dc4ca64f80e3bb`.

## Why these fields are stored

`prepared_canonical` is the exact canonical PREPARED object defined by `ytim.lab099.activation-reservation-precursor-cutover-prepared.v1`. Verification must decode/reconstruct the semantic fields and require `SHA256(prepared_canonical) == prepared_digest`; a stored digest alone is not accepted.

The logical-DB, target and predecessor columns intentionally duplicate fields inside the canonical PREPARED object so SQLite can enforce one cutover per logical DB/schema version and reject a non-identical sibling from the same parent/epoch. Verification must require those columns to equal the decoded PREPARED values; they are indexes/constraints, not an alternate authority encoding.

`confirmation_nonce` is generated before the atomic PREPARED transaction and is committed by the authenticated shared-anchor migration payload. It is deliberately not added retroactively to the frozen PREPARED canonical object. Its purpose is deterministic crash recovery and construction of the already-frozen CONFIRMED object.

`anchor_intent_id` cross-binds the materialization row to the single authority-bearing shared-anchor entry.

## Shared-anchor identity and payload

For a PREPARED digest `D` (lower-case hex), the exact intent identity is:

`migration:provider-activation-reservation-precursor-cutover:v1:<D>`

Exact component:

`provider-activation-reservation-precursor`

Exact intent type:

`migration`

The intent payload is JSON-semantic data passed through the existing `Intent.payload_digest` mechanism:

```json
{
  "contract": "provider-activation-reservation-precursor-cutover",
  "version": 1,
  "prepared_digest": "<64 lowercase hex>",
  "confirmation_nonce": "<64 lowercase hex>"
}
```

The materialization row's `anchor_intent_id` must equal the deterministic identity above, and the exact shared-anchor row must have the component/type/payload digest produced from that payload. A different nonce, prepared digest, component, type or payload digest is substitution.

The intent ID prefix is intentionally self-identifying. If the materialization row is deleted but the shared-anchor cutover row survives, startup can still detect cutover provenance damage rather than silently classifying the database as pre-cutover.

## Atomic ABSENT -> PREPARED transaction

The explicit migration transaction is one `BEGIN IMMEDIATE` transaction and must perform, in this order after all read-only preconditions pass:

1. install the exact frozen precursor relation DDL if and only if it is legitimately absent;
2. install the exact cutover-evidence materialization relation DDL if and only if it is legitimately absent;
3. persist exactly one `provider_activation_reservation_cutovers` row containing the byte-exact PREPARED object and precommitted confirmation nonce;
4. reserve exactly one matching `shared_anchor_intents` migration entry with status PREPARED using the existing shared-anchor reservation semantics;
5. advance `shared_anchor_meta.reserved_position` by exactly one under the same CAS semantics;
6. re-read and byte-verify both frozen relation definitions, the materialization row and the PREPARED shared-anchor row before commit.

Any failure rolls the whole transaction back. A process crash before commit therefore leaves neither governed precursor DDL nor durable cutover PREPARED evidence. A crash after commit leaves the exact DDL + materialization row + shared-anchor PREPARED row and must resume only that exact PREPARED.

No external provider call occurs while this SQLite transaction is open.

## PREPARED verification

A PREPARED state is accepted only when all of the following match:

- exact precursor relation definition digest;
- exact cutover materialization relation definition digest;
- exact one materialization row for the logical DB/target version;
- canonical PREPARED bytes decode to the duplicated logical-DB/target/predecessor columns;
- canonical PREPARED digest equals `prepared_digest`;
- exact deterministic `anchor_intent_id` from that digest;
- exact shared-anchor component/type/payload digest;
- shared-anchor row status PREPARED;
- shared-anchor predecessor/position remain a valid contiguous reservation;
- no second target-version row and no sibling row for the same logical DB + predecessor head/epoch;
- the frozen LAB-092 predecessor completion and logical-DB provenance checks succeed.

The materialization row alone never authorizes continuation.

## PREPARED -> CONFIRMED

Confirmation reuses the existing shared-anchor execution path. It must reauthenticate the exact PREPARED request/position against the external anchor and atomically transition the unchanged shared-anchor row to CONFIRMED with its exact `receipt_binding`.

No second cutover phase row and no second authority ledger are created.

After the shared-anchor row is CONFIRMED, LAB-099 reconstructs the frozen CONFIRMED canonical object from:

- logical DB digest from the verified PREPARED;
- exact `prepared_digest`;
- exact LAB-092 predecessor completion digest from PREPARED;
- exact target schema-set identity/version from PREPARED;
- exact installed precursor relation-definition digest;
- resulting provenance-head digest derived from the confirmed shared-anchor entry as defined below;
- resulting epoch equal to the confirmed shared-anchor `position`;
- the precommitted `confirmation_nonce` from the materialization row, which is already committed by the authenticated shared-anchor payload.

CONFIRMED canonical bytes/digest do not need a second mutable persistence slot because they are deterministic from already-persisted, cross-authenticated state. Verification must reconstruct them every time.

## Resulting provenance-head adapter

LAB-099 needs a DIGEST32 to bridge the existing shared-anchor authority into the frozen binary provenance object without inventing another signing mechanism.

Define `LAB099_SHARED_ANCHOR_CONFIRMED_HEAD_V1` as SHA-256 over the existing shared-anchor canonical JSON encoding (`sort_keys=True`, separators `(',', ':')`) of exactly:

```json
{
  "domain": "ytim.lab099.shared-anchor-confirmed-head.v1",
  "intent_id": "...",
  "component_id": "...",
  "intent_type": "migration",
  "payload_digest": "...",
  "provider_id": "...",
  "provider_generation": 1,
  "predecessor_position": 7,
  "position": 8,
  "request_id": "...",
  "status": "CONFIRMED",
  "receipt_binding": "..."
}
```

All values come from the already-validated `LedgerEntry`; no caller-supplied field is accepted. The resulting epoch is `LedgerEntry.position`.

This adapter is only a deterministic digest view of already-authenticated shared-anchor state. It does not create a new key, signer, receipt or authorization path.

## Idempotence and conflicts

- Re-running explicit migration with the exact same materialization row + exact same anchor row is idempotent.
- Reusing the same deterministic anchor intent ID with changed content is a conflict through existing shared-anchor semantics.
- The materialization primary key prevents two target-version cutovers for one logical DB.
- The sibling UNIQUE constraint prevents two non-identical reservations from one logical DB/predecessor head/epoch.
- A changed PREPARED digest creates a different deterministic anchor intent ID but cannot bypass either SQL uniqueness rule.
- A CONFIRMED row is never reverted to PREPARED.
- A materialization row is never rewritten to represent a different PREPARED object.

## Fail-closed classifications

- precursor relation present + missing materialization/anchor PREPARED: `ORPHAN_UNAUTHENTICATED_SCHEMA`;
- materialization row present + missing/mismatched precursor relation: `AUTHENTICATED_CUTOVER_STORAGE_CORRUPTION`;
- materialization row present + missing/mismatched anchor row: `BROKEN_CUTOVER_PROVENANCE`;
- anchor cutover row present + missing materialization row: `BROKEN_CUTOVER_PROVENANCE`;
- PREPARED anchor row: `PREPARED_INCOMPLETE`, resumable only for the exact materialized PREPARED;
- CONFIRMED anchor row + valid reconstructed CONFIRMED object: `PRECURSOR_V1_GOVERNED`;
- CONFIRMED anchor row with changed receipt binding/request/position/provider generation: fail closed;
- valid CONFIRMED + later deletion of precursor or materialization relation: fail closed, never downgrade.

Whole-store rollback/deletion is not solved by another local table. Detection of deletion of all local cutover + anchor state composes with the already-frozen logical-database/provenance authority work in LAB-095/LAB-097; LAB-099 must not claim local SQLite can prove its own total-history deletion.

## Migration ownership

Only the explicit LAB-099 precursor cutover migration owns creation of both V1 relations and the materialization PREPARED row. Ordinary startup is verification-only for these schema objects. It must not CREATE, repair, auto-adopt, backfill legacy LAB-090 tickets, regenerate a missing materialization row, or synthesize PREPARED/CONFIRMED from installed DDL.

## Next RED-owned slice

PR #186 may now add test-only `lab099_precursor_fixture_vectors.py` and mechanically implement `atomic_prepared_plan()` using:

- the frozen precursor DDL;
- the frozen cutover materialization DDL above;
- the existing shared-anchor row shape;
- one byte-exact PREPARED vector and its deterministic anchor intent payload/ID.

The first executable REDs remain:

1. orphan precursor DDL without PREPARED fails closed;
2. crash after atomic DDL + materialization + exact shared-anchor PREPARED resumes only that exact PREPARED;
3. changed/sibling PREPARED cannot reuse the parent/epoch or target-version authority;
4. exact anchor confirmation deterministically reconstructs the frozen CONFIRMED object;
5. deletion/mismatch of either cross-bound half fails closed.

Production LAB-099 behavior remains forbidden until those repository tests are executable and an actual RED is observed.
