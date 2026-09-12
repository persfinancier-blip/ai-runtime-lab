# LAB-099 — precursor physical relation V1

Date: 2026-09-12
Status: `LAB099_PRECURSOR_PHYSICAL_RELATION_V1_FROZEN`
Scope: design/protocol freeze only. This slice does **not** wire DDL into the PR #186 fixture adapter and does not change production behavior.

## Objective

Resolve the implementation-gated physical SQLite identity for the authenticated provider-activation reservation precursor using existing repository conventions plus the already-frozen LAB-099 authority contract, without inventing a second storage/authentication subsystem.

## Source audit

### LAB-090 / provider-generation history convention

`experiments/provider_generation_history/protocol.py` already persists provider-generation transition authority as semantic fields plus two authenticators:

- `new_generation_id`, `old_generation_id`, `provider_id`;
- `old_mac`, `new_mac`;
- HMAC-SHA256 is computed independently under the predecessor and successor generation keys;
- the canonical transition object is reconstructed for verification rather than storing a serialized canonical body.

Generation IDs, key IDs and MACs are persisted as hexadecimal `TEXT` values. Verification reconstructs the semantic object and uses `hmac.compare_digest` against freshly computed MACs.

### LAB-090 activation relation convention

PR #175 defines a small literal SQLite table constant and verifies the exact schema via normalized `sqlite_master.sql`. Authority-relevant scalar fields are stored directly with simple SQLite `TEXT` / `INTEGER` types. Application verification checks semantic ranges/identity; SQL is not overloaded with redundant validation constraints.

### LAB-092 migration convention

PR #177 makes the literal normalized DDL a protocol identity:

- schema state is classified read-only from `sqlite_master` plus the authenticated migration marker;
- explicit migration owns DDL installation;
- exact DDL and `PREPARED` are committed in the same `BEGIN IMMEDIATE` transaction;
- `CONFIRMED` is a separate authenticated step;
- ordinary startup does not repair/create missing DDL;
- authenticated migration provenance plus missing/mismatched DDL fails closed.

These conventions remove the earlier ambiguity around whether LAB-099 should persist canonical serialization, invent another proof relation, or use startup auto-DDL.

## Decision: storage model

Use the same repository pattern as provider-generation transitions:

1. Persist the precursor's semantic fields as scalar columns.
2. Persist the predecessor and successor authenticators as lowercase hexadecimal `TEXT` HMAC-SHA256 values.
3. Do **not** persist `PRECURSOR_CANONICAL_BYTES` or a separate precursor digest column. Reconstruct the exact `ytim.provider-activation-reservation.v1` canonical bytes from the row and hash/authenticate those bytes during verification.
4. Predecessor MAC uses the durable predecessor `GenerationDescriptor.key`; successor MAC uses the exact successor generation key supplied by the candidate/runtime descriptor whose key-id is bound in the precursor. Both MAC the identical canonical precursor bytes.
5. MAC comparison must use `hmac.compare_digest`.
6. Persist digest-valued semantic fields as lowercase 64-hex-character `TEXT`; conversion to/from the frozen canonical `DIGEST32` wire type is strict and application-verified.

This reuses the existing provider-history trust primitive rather than creating a new signature scheme. The earlier PR #186 HMAC vectors were explicitly prototype-only; this decision promotes HMAC-SHA256 dual authentication to the LAB-099 V1 production protocol contract, but does not promote the reference keys or synthetic relation-definition digest.

## Exact V1 relation identity

Table name:

`provider_activation_reservation_precursors`

Literal DDL:

```sql
CREATE TABLE provider_activation_reservation_precursors(
  activation_id TEXT PRIMARY KEY,
  logical_database_identity_digest TEXT NOT NULL,
  parent_chain_link_digest TEXT NOT NULL,
  parent_epoch INTEGER NOT NULL,
  old_generation_id TEXT NOT NULL,
  new_generation_id TEXT NOT NULL,
  successor_provider_id TEXT NOT NULL,
  successor_generation INTEGER NOT NULL,
  successor_key_id TEXT NOT NULL,
  expected_position INTEGER NOT NULL,
  protocol_version INTEGER NOT NULL CHECK(protocol_version=1),
  predecessor_mac TEXT NOT NULL,
  successor_mac TEXT NOT NULL,
  UNIQUE(logical_database_identity_digest,parent_chain_link_digest,parent_epoch)
)
```

Column mapping to the already-frozen precursor canonical record:

- field 1 -> `logical_database_identity_digest` (strict DIGEST32 <-> lowercase hex TEXT);
- field 2 -> `parent_chain_link_digest` (strict DIGEST32 <-> lowercase hex TEXT);
- field 3 -> `parent_epoch`;
- field 4 -> `old_generation_id`;
- field 5 -> `new_generation_id`;
- field 6 -> `successor_provider_id`;
- field 7 -> `successor_generation`;
- field 8 -> `successor_key_id`;
- field 9 -> `expected_position`;
- field 10 -> `activation_id`;
- field 11 -> `protocol_version` (exactly `1`).

`predecessor_mac` and `successor_mac` authenticate the exact reconstructed canonical record and are not themselves members of that record.

## Uniqueness contract

Two independent database-enforced identities are required and sufficient for V1:

- `activation_id` is the primary key;
- `(logical_database_identity_digest, parent_chain_link_digest, parent_epoch)` is `UNIQUE`.

The second constraint prevents sibling reservations from the same authenticated provenance parent/epoch. No additional uniqueness on `new_generation_id`, provider, or expected position is added because those constraints were not part of the frozen authority contract and would silently create new protocol semantics.

## Relation-definition digest

LAB-099 PREPARED/CONFIRMED bind the exact relation definition by:

`SHA256(UTF8(_normalized_sql(EXACT_V1_DDL)))`

where `_normalized_sql(sql)` is the repository's existing LAB-090/LAB-092 rule: `" ".join(sql.split())`.

For the literal V1 DDL above, the frozen relation-definition digest is:

`696c54d1afdef52c05c120ce7d09a7a2eeb567daafb3a378b7dc4ca64f80e3bb`

The digest is represented as 32 bytes in the frozen canonical PREPARED/CONFIRMED wire record and as lowercase hex when rendered in documentation/storage surfaces that use text.

## Schema verification rule

Read-only classification must query `sqlite_master` by the exact relation name and require:

1. object exists and `type == "table"`;
2. `sql` is non-null;
3. `_normalized_sql(sql) == _normalized_sql(EXACT_V1_DDL)`;
4. the authenticated PREPARED/CONFIRMED relation-definition digest equals the frozen digest above;
5. row-level verification reconstructs exact precursor canonical bytes from each row, validates strict types/ranges/hex encodings, checks activation identity, resolves predecessor/successor authority, and verifies both HMACs.

An object with the right columns but different normalized DDL is not equivalent and must fail closed.

## Migration ownership

The already-frozen LAB-099 one-way cutover remains authoritative:

`ABSENT -> PREPARED -> CONFIRMED`

- explicit LAB-099 migration only;
- install the exact V1 table and reserve the exact authenticated PREPARED cutover evidence in one `BEGIN IMMEDIATE` transaction;
- verify durable predecessor authority and runtime successor/provider pairing before any provider mutation;
- perform separate authenticated CONFIRMED binding to the exact PREPARED digest;
- ordinary startup never executes `CREATE TABLE IF NOT EXISTS` for this relation;
- orphan DDL, authenticated marker with missing/mismatched DDL, stale/forked parent+epoch, and post-CONFIRMED deletion/downgrade all fail closed;
- existing LAB-092 V1 completion is a prerequisite but is not precursor authority.

## Why this is now a justified single design

Earlier LAB-099 work correctly refused to guess literal SQL because frozen authority semantics alone did not choose a storage representation. The source audit supplies the missing repository convention:

- transition proofs already use scalar semantic persistence + dual HMACs, not stored canonical payloads;
- digest/key/MAC identities are already hex text at rest;
- activation schema identity is already literal normalized SQLite DDL;
- migration DDL ownership is already explicit/atomic with PREPARED.

Choosing a different LAB-099 storage family now would create an unnecessary second authority-persistence model without a security benefit.

## Audit / non-claims

- No production LAB-099 code changed in this slice.
- PR #186 fixture mutation plans remain disabled/fail-closed.
- The existing synthetic `REFERENCE_ONLY_RELATION_DEFINITION_DIGEST` remains test-only and is now superseded for future LAB-099 V1 schema-identity vectors by the frozen real digest above; it must not be silently reinterpreted in-place without an explicit test-vector update.
- No repository RED/GREEN PASS is claimed because exact connector-to-local source materialization remains unavailable.
- No LAB-086 PASS is claimed.

## Next implementation slice

After the mandatory LAB-086 materialization probe, update PR #186 test-only reference/oracle layers to use the frozen V1 relation name, literal DDL and real relation-definition digest. Keep mutation plans and production code disabled. Validate any changed standalone test-only files that can be executed without importing unavailable connector-only modules, verify local blob hashes against published GitHub blobs, and only after executable repository RED is observable may production LAB-099 implementation begin.
