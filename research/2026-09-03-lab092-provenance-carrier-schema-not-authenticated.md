# LAB-092 — provenance carrier schema is not authenticated

Date: 2026-09-03
Scope: PR #177 / issue #176 source audit

## Finding

`activation_schema_provenance.py` treats the LAB-080 `shared_anchor_intents` relation as the durable carrier for the LAB-092 migration-completion marker. Both `_classify()` and `_install_and_reserve_prepared()` only establish that a relation named `shared_anchor_intents` exists and has SQLite type `table`.

They do **not** verify that the carrier table still has the exact LAB-080 schema/constraints that give the marker its intended identity and sequencing semantics.

The migration logic then trusts rows selected by `intent_id` and, for a fresh marker, directly executes:

- `INSERT INTO shared_anchor_intents VALUES(..., 'PREPARED', NULL)`;
- tail advancement in `shared_anchor_meta`;
- later inherited `execute()` / `entry()` to authenticate and confirm the marker.

`SharedAnchorLedger._row_entry()` validates row contents after reading them, including the deterministic request id and predecessor/position relation, but it does not prove the underlying relation still enforces the canonical table definition (PRIMARY KEY/UNIQUE/CHECK/NOT NULL constraints or exact column layout). `SharedAnchorLedger._init()` itself uses `CREATE TABLE IF NOT EXISTS` and does not validate an existing table definition.

Therefore LAB-092 can reach `COMPLETE` while its own provenance evidence lives in a schema-substituted carrier that has only the expected name/type and compatible columns. This is different from the already-recorded activation-table/trigger deletion TOCTOU findings: the activation DDL can remain exact while the *provenance carrier* is weakened or substituted.

## Concrete regression shape

Construct a legitimate pre-LAB-092 database, then replace `shared_anchor_intents` with a same-name table exposing the columns expected by the code but weakening one or more authority-relevant constraints, for example removing the primary-key/unique guarantees on intent/request/position or the status/check constraints while preserving query compatibility.

Then run explicit LAB-092 migration.

Pre-fix source path:

1. `_classify()` accepts the carrier because `sqlite_master.type == 'table'`.
2. `_install_and_reserve_prepared()` accepts the same carrier check.
3. exact activation DDL + PREPARED marker can be committed into the substituted carrier.
4. inherited confirmation can authenticate one selected marker row and move it to CONFIRMED without ever proving the carrier definition is canonical.
5. subsequent `_classify()` can report `COMPLETE` because it again checks only activation DDL + marker content, not the carrier schema.

The exact executable RED remains pending because exact branch execution is unavailable in this run; this is a source-proved trust-boundary gap, not a claimed behavioral PASS/RED.

## Required fix contract

LAB-092 migration provenance must not be stronger than the schema semantics of the relation carrying it.

Before classifying, reserving, confirming, or accepting `COMPLETE`, verify the exact authority-relevant LAB-080 carrier schema (and `shared_anchor_meta` singleton schema if it participates in the migration transaction) or bind LAB-092 to a separately authenticated/schema-versioned carrier whose definition is itself proven.

Do not fix this with only another content-level `_marker_state()` check: row-shape validation cannot establish uniqueness/check/constraint semantics of the underlying relation.

The carrier-schema proof must also compose with the existing LAB-092 mutation-boundary requirement; an unsynchronized schema check performed earlier would merely introduce another TOCTOU window.

## Relationship to existing work

- #176 / LAB-092 remains the correct issue; no duplicate issue is needed.
- This is distinct from the three retained LAB-092 TOCTOU groups (explicit migration completion, constructor/restart, post-construction): those assume a trusted provenance carrier and show the trusted predicate can change between check/use. This finding shows the carrier itself is never fully authenticated.
- LAB-091/#170 hardens mutable DML writer authorization, but PR #177 currently depends on the LAB-080 carrier surface and does not establish LAB-091 as a prerequisite. LAB-092 therefore needs an explicit carrier-schema contract rather than silently assuming downstream LAB-091 guards.

## Next regression

Add a deterministic source-executable regression that substitutes a query-compatible but constraint-weakened `shared_anchor_intents` table before explicit migration and requires fail-closed before activation DDL installation, marker reservation, shared-anchor tail advancement, provider I/O, receipt creation, or CONFIRMED provenance. Add a second case that mutates the carrier schema after a valid COMPLETE state and require restart/post-construction operations to fail before authority mutation.
