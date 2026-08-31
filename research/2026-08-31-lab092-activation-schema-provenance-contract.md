# LAB-092 — activation-schema installation provenance contract

Date: 2026-08-31
Issue: #176
Related: #169 / PR #175

## Question

How can restart distinguish a legitimate first upgrade from a pre-LAB-090 database from post-install deletion of `provider_generation_activations` and/or `block_intent_during_provider_activation`, without adding a second weak mutable marker surface?

## Current facts

1. PR #175 now installs the activation table and trigger atomically under one `BEGIN IMMEDIATE`, and verifies their exact SQLite definitions.
2. Exact-definition verification rejects a same-name VIEW or altered trigger.
3. If both objects are absent, `CREATE ... IF NOT EXISTS` cannot distinguish first legitimate installation from later deletion.
4. Requiring the objects to pre-exist would break legitimate pre-LAB-090 databases.
5. The pre-existing shared-anchor protocol already has an authenticated `migration` intent type. Confirmed intents are part of contiguous durable history and bind an exact provider generation, position, request id, and authenticated receipt.

## Rejected marker classes

### A. New singleton marker table

Rejected as the authority for provenance. A new `lab090_schema_meta(installed=1)` table is at the same mutable DDL layer as the objects whose deletion it is supposed to detect. If the threat includes deletion of the activation objects, deleting this marker restores an indistinguishable apparent legacy state.

### B. `PRAGMA user_version` / `application_id`

Rejected for the same reason. They are convenient migration metadata, not authenticated provenance. They may be useful as hints, but must not decide fail-open versus fail-closed startup.

### C. Marker column added to `shared_anchor_meta`

Rejected as the sole provenance authority. It avoids a second table but is still mutable local schema. Removing/rebuilding the column can recreate apparent legacy state unless another authenticated fact says installation already happened.

### D. Infer installation from provider-generation number/history length

Rejected. A legitimate pre-LAB-090 database may already contain provider rotations. Generation history therefore cannot unambiguously prove that LAB-090 was installed.

## Proposed contract: authenticated migration-intent provenance

Use the existing shared-anchor history as the provenance authority rather than creating a new authority surface.

Define one canonical migration intent, conceptually:

```text
component_id = "provider-generation-history"
intent_type  = "migration"
payload      = {
  "migration": "lab090-activation-schema",
  "schema_version": 1
}
```

Its normal shared-anchor `intent_id` must be deterministic from the migration name/version (or otherwise fixed by protocol), so restart can query one canonical identity rather than search ambiguous payloads.

The marker is considered durable only when the intent is `CONFIRMED` and its normal historical provider receipt verifies through the inherited LAB-081 history rules. No new signing authority, key, or mutable provenance table is introduced.

## State machine

Startup first verifies the inherited LAB-081/shared-anchor history before using migration provenance.

Then classify:

| authenticated migration intent | activation table/trigger | action |
|---|---|---|
| absent | both absent | legitimate legacy candidate; perform first migration |
| absent | either present | fail closed: unproven partial/ad-hoc installation |
| confirmed | both exact | normal LAB-090 restart |
| confirmed | either absent | fail closed: post-marker deletion or incomplete install |
| confirmed | either definition mismatched | fail closed: schema tamper |
| PREPARED | any | use ordinary shared-anchor unresolved-intent recovery semantics; do not silently install LAB-090 |

A row that merely looks like the marker but does not pass inherited history/receipt verification is not provenance.

## First-migration sequence

The external authenticated marker and local DDL cannot be one SQLite atomic transaction because the external provider is a separate serialization domain. Do not pretend otherwise. Use an explicit two-phase migration with a recoverable boundary:

1. Start from a verified pre-LAB-090 database with both activation objects absent.
2. Execute the canonical migration intent through the existing LAB-081 shared-anchor path and require it to become `CONFIRMED` with authenticated receipt evidence.
3. Open `BEGIN IMMEDIATE`.
4. Re-read and verify the exact canonical confirmed marker while holding the SQLite writer reservation.
5. Create activation table and trigger; verify exact definitions.
6. Commit.

Crash after step 2 but before step 6 leaves a *confirmed marker with missing objects*. That state is distinguishable from legacy and must not be treated as ordinary restart.

For availability, a dedicated migration/recovery entry point may complete installation when and only when all of the following are true: inherited history verifies; the canonical marker verifies; neither activation object exists; no unresolved shared-anchor intent exists; and the installer acquires `BEGIN IMMEDIATE` before creating both objects. Ordinary runtime construction should remain fail-closed rather than silently repairing authenticated post-install state.

This separates `migration recovery` from `runtime repair` and prevents deletion from being normalized away by the normal constructor.

## Why the marker is stronger than local schema metadata

The canonical intent is embedded in the already-existing contiguous shared-anchor history instead of a new mutable schema surface. Deleting only the activation objects cannot erase the marker. Deleting or rewriting the marker must also satisfy/fool the inherited shared-anchor/history verification rules and receipt bindings, so LAB-092 does not create an independent authority mechanism.

This is still bounded by the security properties of the inherited shared-anchor history and external anchor. It is not a claim that arbitrary filesystem rollback can be detected without the external monotonic-anchor/freshness layer.

## Required implementation properties

- `SupportedHistoricalSharedAnchorLedger.__init__` must not create missing LAB-090 objects before provenance classification.
- First-install logic must be a distinct migration path, not implicit `IF NOT EXISTS` repair on every restart.
- Exact table/trigger definition checks from PR #175 remain mandatory.
- Table + trigger creation remains inside one `BEGIN IMMEDIATE` writer transaction.
- Marker identity/version is canonical and single-valued.
- Confirmed marker verification reuses existing LAB-081 receipt/history verification; no new key material.
- A PREPARED marker is not equivalent to installation provenance.
- A confirmed marker plus missing/mismatched objects is fail-closed during ordinary startup.
- Initial migration must reject any pre-existing activation object when the authenticated marker is absent.

## Required regressions

1. verified legacy DB + no marker + no objects -> explicit migration succeeds;
2. verified legacy DB + object present + no marker -> fail closed;
3. confirmed canonical marker + exact objects -> restart succeeds;
4. confirmed marker + table deleted -> ordinary restart fails closed;
5. confirmed marker + trigger deleted -> ordinary restart fails closed;
6. confirmed marker + altered table/trigger -> fail closed;
7. PREPARED marker -> no installation and no runtime start;
8. crash after marker confirmation, before DDL -> ordinary restart fails closed; dedicated migration recovery can finish under `BEGIN IMMEDIATE`;
9. crash inside DDL transaction -> SQLite rollback leaves both objects absent; classification remains the same confirmed-marker recovery state;
10. concurrent writer cannot enter between table and trigger creation;
11. marker/history deletion or substitution exercises inherited durable-history verification and must not be normalized as a fresh legacy install;
12. legitimate pre-LAB-090 database with multiple historical provider generations still migrates; generation count is not used as provenance.

## Scope decision

Do not fold this contract into LAB-090 PR #175. PR #175 should retain its already-published atomic installation and exact-definition hardening. LAB-092 changes the migration/startup contract and deserves its own branch/tests.

## Next implementation slice

Before coding, inspect the exact LAB-081 migration/receipt APIs needed to construct a deterministic canonical migration intent and define a dedicated `migrate_activation_schema_v1(...)` entry point. The first RED tests should cover (a) confirmed marker + deleted table and (b) legitimate legacy first migration. Only then change constructor behavior.