# LAB-093 application-idempotency registry installation provenance + retention authority V1

Date: 2026-09-04
Status: FROZEN DESIGN / RED-FIRST; production implementation waits for executable branch gates.

## Objective

Freeze how the broker proves that `worker_application_idempotency_v1` was legitimately installed, how restart distinguishes a first migration from post-install deletion, and who may convert a durable `COMMITTED` application-idempotency record into a non-reusable `TOMBSTONED` record after result payload retirement.

Required property:

> Cleanup may retire result payload bytes, but it can never erase the authenticated fact that an application key was already consumed by one exact operation. Once application-idempotency support is authenticated as installed, missing or downgraded registry state is corruption, not an invitation to recreate an empty table or reuse historical keys.

This composes with:
- `WORKER_REQUEST_EFFECT_REGISTRY_STORAGE_V1_FROZEN`;
- `WORKER_EFFECT_COMPLETION_RESULT_DELIVERY_APPLICATION_IDEMPOTENCY_V1_FROZEN`;
- the shared canonical V1 encoder and global parent-linked provenance chain;
- atomic provenance append/recovery;
- startup verifier/recovery planner;
- LAB-080 exact external request identity;
- LAB-087 sole-writer ownership and LAB-091 operation-scoped SQL authorization;
- the finite broker startup/recovery state machine and LAB-093 session revocation/re-entry.

It MUST NOT introduce a second self-asserted installation marker, permit `CREATE TABLE IF NOT EXISTS` to normalize a deleted registry after authenticated installation, or define TTL expiry as permission to reuse a historical key.

## 1. Installation provenance is part of the global authority history

The first successful installation of the application-idempotency registry is represented by one authenticated provenance transition in the same global chain used by the other retained authority state.

Freeze event class:

`APPLICATION_IDEMPOTENCY_REGISTRY_INSTALL_V1`

Canonical event body binds at minimum:
- logical database/history identity;
- schema name and exact schema digest;
- exact required index/trigger/guard digests;
- application-idempotency protocol version = 1;
- canonical-encoder version;
- retention-authority policy digest;
- migration source class (`LEGACY_PRE_INSTALL` only in V1);
- parent provenance head digest/epoch;
- resulting installation generation/epoch.

The install event is appended through the already-frozen atomic provenance transition and LAB-080 external-anchor path. No independent local marker can substitute for this authenticated event.

### First-install rule

A database may be classified as legitimately pre-install only when the existing authenticated provenance chain proves that its terminal history predates the application-idempotency installation feature and there is no contradictory durable worker envelope/effect evidence requiring an application-key registry.

Absence of the table by itself is never proof of first install.

### Post-install rule

After an authenticated install event exists, startup requires the exact registry schema and all required guards. Missing table/index/trigger/guard is `INSTALLED_SCHEMA_MISSING` and fails closed before repair, worker delegation, result lookup, retention mutation, provider calls, or ordinary effect execution.

Ordinary startup MUST NOT recreate missing installed schema.

## 2. Explicit migration only

Installation is an explicit broker-owned migration, not constructor side effect.

Freeze command:

`MIGRATE_APPLICATION_IDEMPOTENCY_V1(expected_preconditions_digest)`

The command is legal only when the startup verifier classifies the durable state as `LEGACY_PRE_INSTALL_ELIGIBLE`.

Preconditions include:
- authenticated logical database/history identity;
- current clean provenance head;
- aligned external terminal anchor;
- no unresolved recovery plan;
- no unresolved activation fence;
- no active worker sessions;
- sole-writer ownership;
- exact absence of application-idempotency V1 schema;
- no durable keyed worker request whose canonical envelope proves application-idempotency use;
- exact expected schema/policy/version digests.

The migration command re-checks these preconditions inside the final authorized write boundary.

## 3. Atomic installation protocol

Installation uses the existing two-phase external-anchor/provenance machinery rather than inventing a migration-specific commit system.

Transaction A / prepare:
1. `BEGIN IMMEDIATE` under broker sole-writer authority;
2. reverify preconditions;
3. create exact STRICT table + required indexes/guards;
4. classify exact DDL bytes/SQL normalized digest against the frozen schema descriptor;
5. prepare the canonical install provenance event/link/transition;
6. reserve/reuse the exact LAB-080 intent for that transition;
7. commit local PREPARED state.

External phase:
8. execute/reconcile only the exact LAB-080 request identity from the prepared transition;
9. UNKNOWN uses the existing exact-request recovery path only.

Transaction B / commit:
10. re-authenticate exact receipt/external evidence;
11. advance the same provenance transition to COMMITTED;
12. leave the installed DDL intact;
13. commit.

A crash after DDL creation but before authenticated install completion does not convert the database into ordinary installed state. Startup classifies this as a migration recovery condition only when exact PREPARED provenance and exact DDL match the frozen install operation. It never accepts arbitrary pre-created lookalike DDL.

## 4. Startup classification

Freeze side-effect-free classes:

- `LEGACY_PRE_INSTALL_ELIGIBLE`: authenticated history proves legitimate pre-feature state; exact V1 schema absent; no keyed-operation contradiction.
- `INSTALL_PREPARED_RECOVERABLE`: exact schema present + exact PREPARED install transition + exact LAB-080 intent/evidence relation.
- `INSTALLED_CLEAN`: authenticated COMMITTED install transition exists and exact schema/guards are present.
- `INSTALLED_SCHEMA_MISSING`: committed install provenance exists but table/index/guard is absent.
- `INSTALLED_SCHEMA_MISMATCH`: installed object exists but canonical descriptor differs.
- `UNMARKED_SCHEMA_PRESENT`: schema exists without authenticated install provenance.
- `HISTORY_CONTRADICTION`: keyed worker history requires the registry but authenticated install provenance is absent or temporally impossible.
- `CORRUPT_FAIL_CLOSED`: any canonical/provenance/receipt/authority inconsistency.

Only the first two classes may lead to migration/recovery work. None of the fail-closed classes may auto-repair.

## 5. Retention authority is distinct from application-effect authority

An ordinary worker/application key holder has no authority to retire a committed result.

Freeze a separate broker-admin capability:

`RetentionAuthorityV1`

Its construction-bound identity is represented by:
- authority class/version;
- principal/role policy digest;
- allowed retention classes;
- minimum committed age / policy predicates if any;
- current policy version;
- authorization adapter/capability identity digest;
- provenance authority epoch.

A retention action must be authorized under the current retention policy at execution time. Historical commit authority or possession of the application key does not imply retention authority.

The retained authority object/capability follows the same LAB-094..096 construction-bound rules: no mutable public strategy slot, no path/bootstrap rebinding, no caller-supplied permissive subclass trusted solely by return values.

## 6. Canonical retention policy identity

Freeze:

`RetentionPolicyV1 {
  policy_id: UTF8_NONEMPTY,
  policy_version: INTEGER_NONNEGATIVE,
  retention_class: UTF8_NONEMPTY,
  result_payload_action: ENUM('KEEP','RETIRE_TO_TOMBSTONE'),
  min_commit_age_seconds: INTEGER_NONNEGATIVE,
  principal_scope_digest: BLOB32,
  policy_document_digest: BLOB32,
}`

Canonical encoding uses the shared domain-separated V1 encoder.

`retention_policy_digest = SHA256(domain || canonical_policy)`.

Every `COMMITTED -> TOMBSTONED` action binds the exact current policy digest and version. Policy changes do not retroactively rewrite historical tombstones.

V1 deliberately does not define reusable-key TTL semantics. A policy may decide when result bytes can be retired, but the key remains permanently consumed.

## 7. Canonical tombstone provenance event

Freeze event class:

`APPLICATION_IDEMPOTENCY_RESULT_TOMBSTONE_V1`

Canonical body binds at minimum:
- application key digest;
- application operation digest;
- worker request digest;
- effect binding digest;
- original committed result digest;
- original committed provenance head digest/epoch;
- retention policy digest + policy version;
- retention-authority identity digest;
- current parent provenance head digest/epoch;
- tombstone digest;
- tombstone action version.

`tombstone_digest` is computed from the complete canonical tombstone body excluding only the digest field itself, using the shared domain-separated canonical V1 rules.

The event proves that result payload retirement happened under a specific authenticated policy/authority while preserving the consumed-key history.

## 8. Crash-safe COMMITTED -> TOMBSTONED protocol

Normal deletion is forbidden. Tombstoning is the only V1 result-retirement path.

### Preconditions

Before any mutation the broker requires:
- clean startup verification;
- fresh aligned external evidence;
- no recovery plan;
- current retention authority valid for the exact namespace/principal/retention class;
- exact application row state `COMMITTED`;
- exact worker request/effect/result joins verify;
- current result digest matches canonical result bytes;
- exact policy predicate is satisfied;
- no prior tombstone event exists for this application key;
- sole-writer ownership.

### Prepare transaction

Within one `BEGIN IMMEDIATE`:
1. re-check all preconditions;
2. freeze canonical tombstone event/link bytes;
3. prepare the provenance transition and exact LAB-080 intent;
4. record broker-owned tombstone PREPARED state if an implementation needs a local transition record;
5. DO NOT delete or clear committed result bytes yet;
6. commit.

The original committed result remains available until the tombstone transition is externally anchored and durably committed.

### External anchor

Issue/reconcile only the exact prepared LAB-080 request id. UNKNOWN follows ordinary broker recovery; no second retention request id is generated.

### Commit transaction

After exact receipt re-authentication:
1. re-check preconditions digest/current authority invariants that must remain stable;
2. commit the tombstone provenance transition;
3. atomically change application row `COMMITTED -> TOMBSTONED`;
4. bind exact `tombstone_digest`;
5. retire/clear result payload bytes according to the frozen policy;
6. preserve original `result_digest` in authenticated tombstone provenance even if the application table no longer stores it;
7. commit.

At no point is the application key absent or reusable.

## 9. Tombstone storage semantics

The previously frozen application table allowed:
- `COMMITTED`: `result_digest != NULL`, `tombstone_digest == NULL`;
- `TOMBSTONED`: `result_digest == NULL`, `tombstone_digest != NULL`.

This remains valid only because authenticated tombstone provenance permanently binds the original result digest and operation identity.

Startup must prove one-to-one consistency:
- each `TOMBSTONED` application row has exactly one matching committed tombstone provenance transition;
- the transition refers to the same application key/operation/worker/effect identity;
- its parent lineage descends from the original committed effect/result state;
- no later event reopens/rebinds the key;
- no second tombstone exists for the same key;
- no result payload exists if policy says it was retired, unless an explicitly frozen encrypted archival extension is later added.

A tombstone is evidence, not new effect authority.

## 10. Deletion detection and non-reuse proof

After authenticated install:

- deleting the entire application registry fails startup;
- deleting one historical `BOUND`, `COMMITTED`, or `TOMBSTONED` row whose keyed envelope/provenance proves it existed fails startup;
- deleting a tombstone event fails startup;
- deleting the original worker request/effect/result evidence fails the corresponding existing verifier;
- recreating an empty registry does not restore service because install provenance requires historical continuity, not mere DDL presence;
- recreating a row with the same key but different operation fails canonical/provenance joins;
- changing a tombstoned key to `MISS` is impossible through supported lookup semantics;
- policy expiry cannot make the key reusable.

The permanent consumed-key fact is therefore rooted in both the registry state and authenticated global provenance rather than a deletable local row alone.

## 11. Policy upgrade semantics

Retention policy may evolve, but upgrades are explicit authenticated authority events.

Freeze event class:

`APPLICATION_IDEMPOTENCY_RETENTION_POLICY_UPDATE_V1`

It binds old policy digest/version, new policy digest/version, authority identity, parent provenance head, and effective epoch.

Rules:
- version must advance monotonically under the frozen policy authority contract;
- historical tombstones continue verifying against the policy digest/version that authorized them;
- a policy update cannot reinterpret a tombstone as reusable;
- a weaker future policy cannot erase historical retention evidence;
- startup verifies policy-chain continuity before allowing new tombstones.

## 12. Authorization and least-capability surfaces

Worker façades may call result lookup but never installation or retention mutation.

Only broker-private/admin-authorized surfaces may expose:
- `migrate_application_idempotency_v1(...)` while startup is in migration-required state;
- `prepare_tombstone(...)` / broker-owned recovery;
- authenticated policy update.

No worker receives:
- raw SQLite connection;
- table/DDL authority;
- LAB-080 request mutation capability;
- provenance writer capability;
- retention authority handle;
- ability to choose a historical policy version after the fact.

## 13. Failure taxonomy

Freeze externally/audit-distinguishable classes:

- `MIGRATION_REQUIRED`
- `MIGRATION_RECOVERY_REQUIRED`
- `INSTALLED_SCHEMA_MISSING`
- `INSTALLED_SCHEMA_MISMATCH`
- `UNMARKED_SCHEMA_PRESENT`
- `HISTORY_CONTRADICTION`
- `RETENTION_UNAUTHORIZED`
- `RETENTION_POLICY_MISMATCH`
- `RETENTION_NOT_YET_ELIGIBLE`
- `RETENTION_ALREADY_TOMBSTONED`
- `RETENTION_RECOVERY_REQUIRED`
- `TOMBSTONE_EVIDENCE_MISSING`
- `CORRUPT_FAIL_CLOSED`

None of these statuses authorizes an effect or provider mutation by itself.

## 14. RED-first matrix

Minimum executable matrix before production implementation:

1. legitimate pre-feature DB with no keyed operations classifies migration-required;
2. ordinary startup does not auto-create registry;
3. explicit migration installs exact STRICT schema/guards;
4. install event is in the shared authenticated provenance chain;
5. install uses exactly one LAB-080 intent/request identity;
6. crash before local PREPARED install commit leaves DB legitimately pre-install;
7. crash after exact DDL + PREPARED install state is recoverable only through exact prepared transition;
8. UNKNOWN during install reuses original LAB-080 request id;
9. crash after external install anchor/before local COMMIT recovers exact transition;
10. clean completed install restarts as INSTALLED_CLEAN;
11. committed install + deleted table fails closed without recreation;
12. committed install + deleted required index fails closed;
13. committed install + altered trigger/guard fails closed;
14. lookalike schema without authenticated install event is UNMARKED_SCHEMA_PRESENT;
15. keyed worker history with missing install provenance is HISTORY_CONTRADICTION;
16. migration cannot run with active worker session;
17. migration cannot run with unresolved recovery/activation fence;
18. stale migration preconditions reject before mutation;
19. migration authority cannot be invoked through worker façade;
20. COMMITTED result is unchanged before tombstone external anchor commits;
21. unauthorized caller cannot tombstone;
22. application-key possession alone cannot tombstone;
23. stale/old retention policy version cannot authorize a new tombstone;
24. policy digest one-byte mismatch rejects;
25. current policy age predicate enforced from authenticated commit metadata, not caller timestamp;
26. tombstone prepare creates one exact provenance transition;
27. tombstone uses one exact LAB-080 request id;
28. UNKNOWN during tombstone preserves COMMITTED result and original request id;
29. crash after tombstone PREPARED/before provider call preserves result;
30. crash after provider commit/before local tombstone commit recovers exact operation;
31. final tombstone commit atomically changes COMMITTED->TOMBSTONED and retires payload;
32. original result digest remains authenticated in tombstone provenance;
33. tombstoned lookup returns COMMITTED_RESULT_RETIRED, never MISS;
34. tombstoned key cannot bind a new worker effect;
35. same raw key + different operation after tombstone is conflict/retired, never new effect;
36. deleting tombstoned application row fails startup;
37. deleting tombstone provenance event fails startup;
38. altering tombstone policy digest fails startup;
39. altering original result digest in tombstone evidence fails startup;
40. two tombstones for one application key are rejected;
41. a retention policy update is itself authenticated and parent-linked;
42. historical tombstone verifies under historical policy digest after policy upgrade;
43. policy downgrade cannot make a historical key reusable;
44. deleting policy-update history fails startup when later tombstones depend on it;
45. recreation of empty application table after deletion is still corruption because install/history evidence disagrees;
46. normal DELETE on application rows is denied by LAB-091 guards;
47. normal UPDATE TOMBSTONED->BOUND/COMMITTED is denied;
48. restart never restores old worker/session authority from application/tombstone evidence;
49. final broker delegation occurs only after full reverify and fresh aligned evidence following migration/recovery;
50. audit proves no cleanup path can convert a historically consumed key into MISS or prepare a second effect.

## 15. Decision

Freeze as:

`APPLICATION_IDEMPOTENCY_REGISTRY_INSTALLATION_PROVENANCE_RETENTION_AUTHORITY_V1_FROZEN`.

Implementation order when exact executable RED/GREEN becomes available:
1. exact schema descriptor + installation classifier RED tests;
2. explicit migration command using existing provenance/LAB-080 machinery;
3. post-install deletion/mismatch fail-closed tests;
4. retention policy/authority canonical value types;
5. tombstone RED crash/UNKNOWN/authorization tests;
6. broker-only COMMITTED->TOMBSTONED executor;
7. LAB-091 one-shot guards for install/tombstone/policy-update transitions;
8. startup verification joins and non-reuse/deletion tests;
9. full LAB-087/LAB-080/provenance/LAB-093 downstream audit.

No production code is claimed or changed by this design freeze.