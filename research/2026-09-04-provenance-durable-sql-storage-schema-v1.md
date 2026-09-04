# Provenance durable SQL/storage schema V1

Date: 2026-09-04
Status: design contract frozen; exact RED/GREEN pending
Related: LAB-080/081, LAB-086/#163, LAB-090/#169, LAB-092/#176, LAB-093/#178, LAB-097..100/#182..185

## Objective

Freeze the exact durable SQLite/storage shape for the already-frozen canonical provenance encoding, parent-linked authenticated chain, and atomic append/recovery protocol without creating a second anchor or idempotency subsystem.

This is a design contract only. In this run a fresh direct `git clone --no-checkout` again failed before repository access with `Could not resolve host: github.com`; no production table/trigger mutation and no exact repository behavioral PASS are claimed.

## Existing authority reused

LAB-080 remains the outer monotonic-anchor/idempotency authority. Its live schema already provides:

- `shared_anchor_intents.intent_id` primary identity;
- globally unique contiguous `position`;
- globally unique deterministic `request_id`;
- `PREPARED|CONFIRMED` lifecycle;
- `receipt_binding` only on CONFIRMED rows;
- `shared_anchor_meta.reserved_position` as the local allocation tail;
- external `reconcile_increment(request_id=...)` as timeout-after-commit/UNKNOWN reconciliation.

The provenance schema MUST reference these rows. It MUST NOT duplicate external positions, receipts, request ids, or create another independently advancing counter.

## Storage model

Four tables are frozen for V1:

1. `provenance_events_v1` — exact domain-event bytes frozen before external mutation;
2. `provenance_chain_links_v1` — exact canonical successor-link bytes;
3. `provenance_transitions_v1` — PREPARED/COMMITTED append coordinator record tied 1:1 to LAB-080 intent identity;
4. `provenance_chain_head_v1` — one cached terminal `(epoch, link_digest)` for fast lookup, never standalone authority.

SQLite constraints are defense-in-depth. Authenticity still comes from canonical bytes/digests + complete parent chain + exact LAB-080 CONFIRMED/re-authenticated evidence + retained authority graph.

## Canonical storage types

Security-relevant digests are stored as **32-byte BLOB**, never hex TEXT. Exact canonical event/link bytes are stored as BLOB and reparsed under the frozen canonical V1 decoder before trust decisions.

Epoch/event kind/protocol fields are INTEGER only after explicit Python-side strict type/range validation. SQLite affinity/coercion is not accepted as canonical typing. Every verifier must reject `typeof(epoch) != 'integer'`, negative values, values outside signed-SQLite-safe V1 range, malformed UTF-8 inside canonical payloads, duplicate TLV fields, unknown fields, trailing bytes, or digest/byte mismatch.

V1 operational epoch range is frozen to `0 <= epoch <= 2^63-1` because SQLite INTEGER is signed 64-bit. The canonical U64 format remains reusable, but append MUST fail before PREPARE once the current epoch is `2^63-1`; V1 does not silently reinterpret negative SQLite values.

## Table 1 — `provenance_events_v1`

```sql
CREATE TABLE provenance_events_v1(
  event_digest BLOB PRIMARY KEY,
  event_kind INTEGER NOT NULL,
  canonical_event BLOB NOT NULL,
  CHECK(length(event_digest)=32)
) STRICT;
```

Frozen rules:

- `event_digest = SHA-256(canonical_event)` under the event's domain-separated canonical V1 encoding.
- rows are immutable after insertion;
- byte-identical duplicate insertion is idempotent only when existing `event_kind` and `canonical_event` are exact matches;
- same digest with different bytes/kind is corruption and must fail closed;
- no status column lives here: PREPARED vs COMMITTED belongs to the transition that references the immutable event.

## Table 2 — `provenance_chain_links_v1`

```sql
CREATE TABLE provenance_chain_links_v1(
  link_digest BLOB PRIMARY KEY,
  logical_database_identity_digest BLOB NOT NULL,
  epoch INTEGER NOT NULL,
  parent_link_digest BLOB,
  event_digest BLOB NOT NULL,
  canonical_link BLOB NOT NULL,
  CHECK(length(link_digest)=32),
  CHECK(length(logical_database_identity_digest)=32),
  CHECK(parent_link_digest IS NULL OR length(parent_link_digest)=32),
  CHECK(length(event_digest)=32),
  UNIQUE(logical_database_identity_digest, epoch),
  UNIQUE(logical_database_identity_digest, parent_link_digest)
) STRICT;
```

Frozen rules:

- genesis is the only row with `epoch=0` and `parent_link_digest IS NULL`;
- every non-genesis row has `epoch>=1` and a 32-byte parent;
- `link_digest = SHA-256(canonical_link)` and the decoder must reproduce the stored DB identity, epoch, parent and event digest exactly;
- `UNIQUE(DB, epoch)` prevents two durable links claiming the same epoch;
- `UNIQUE(DB, parent_link_digest)` is defense-in-depth against sibling children/forks;
- a link row may exist while its transition is PREPARED, but it is not current/authenticated merely because it exists.

The NULL behavior of SQLite UNIQUE means genesis sibling prevention cannot rely on `UNIQUE(DB,parent=NULL)` alone. Startup and insertion logic MUST separately require exactly one epoch-0 genesis for the logical DB identity.

## Table 3 — `provenance_transitions_v1`

```sql
CREATE TABLE provenance_transitions_v1(
  transition_id BLOB PRIMARY KEY,
  logical_database_identity_digest BLOB NOT NULL,
  parent_link_digest BLOB NOT NULL,
  parent_epoch INTEGER NOT NULL,
  event_digest BLOB NOT NULL,
  successor_link_digest BLOB NOT NULL,
  resulting_provider_head_digest BLOB NOT NULL,
  resulting_authority_digest BLOB NOT NULL,
  resulting_schema_state_digest BLOB NOT NULL,
  protocol_version INTEGER NOT NULL,
  anchor_intent_id TEXT NOT NULL UNIQUE,
  state TEXT NOT NULL CHECK(state IN ('PREPARED','COMMITTED')),
  CHECK(length(transition_id)=32),
  CHECK(length(logical_database_identity_digest)=32),
  CHECK(length(parent_link_digest)=32),
  CHECK(length(event_digest)=32),
  CHECK(length(successor_link_digest)=32),
  CHECK(length(resulting_provider_head_digest)=32),
  CHECK(length(resulting_authority_digest)=32),
  CHECK(length(resulting_schema_state_digest)=32),
  UNIQUE(logical_database_identity_digest, parent_link_digest),
  UNIQUE(logical_database_identity_digest, parent_epoch)
) STRICT;
```

Frozen rules:

- `transition_id` is the exact frozen canonical transition-identity digest;
- one transition has exactly one LAB-080 `anchor_intent_id` and vice versa;
- no copied `position`, `request_id`, receipt or provider generation columns are stored here; those remain canonical in `shared_anchor_intents` and are joined by `anchor_intent_id`;
- the LAB-080 intent must have `component_id='provenance-chain'` and the exact canonical transition commitment as its payload digest under the adopted executable integration;
- PREPARED transition fields except `state` are immutable;
- the only normal transition-row mutation is exact `PREPARED -> COMMITTED` in Transaction B;
- no `COMMITTED -> PREPARED`, deletion, parent rewrite, event rewrite, successor rewrite, anchor rebind or post-state rewrite is supported.

The two UNIQUE constraints intentionally make concurrent sibling PREPARE attempts conflict before external mutation when they target the same parent/epoch. Application logic still re-reads the authenticated head under `BEGIN IMMEDIATE`; UNIQUE constraints are not the authority proof.

## Table 4 — `provenance_chain_head_v1`

```sql
CREATE TABLE provenance_chain_head_v1(
  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
  logical_database_identity_digest BLOB NOT NULL,
  epoch INTEGER NOT NULL,
  link_digest BLOB NOT NULL,
  CHECK(length(logical_database_identity_digest)=32),
  CHECK(length(link_digest)=32)
) STRICT;
```

Frozen rules:

- exactly one row after initialized genesis;
- it is a cache/index, not an authenticated root by itself;
- it advances only in Transaction B together with transition PREPARED->COMMITTED;
- startup never repairs it by selecting MAX(epoch), MAX(rowid), newest timestamp, lexicographically greatest digest, or any other local heuristic;
- if it differs from the uniquely authenticated terminal chain link, startup fails closed unless exact atomic-recovery evidence proves a single already-PREPARED transition is eligible for deterministic completion.

## Genesis / initialization storage

LAB-097 initialization is special: there is no previous provenance transition/anchor history to reference.

V1 requires initialization to atomically establish:

- the authenticated logical database identity / initialization certificate;
- one immutable genesis event in `provenance_events_v1`;
- one epoch-0 link in `provenance_chain_links_v1` with NULL parent;
- the singleton head at epoch 0;
- the one-time external/shared-anchor initialization commitment defined by the initialization contract.

After this succeeds, an empty/missing provenance schema or missing genesis/head is corruption, never permission to run bootstrap initialization again.

## Transaction A — exact SQL shape

Under one `BEGIN IMMEDIATE`:

1. verify current retained authority graph and authenticated chain/head;
2. require no other unresolved provenance transition;
3. build exact canonical event/link/transition bytes in memory;
4. reserve the exact LAB-080 intent using existing LAB-080 allocation/idempotency semantics;
5. insert event row if absent, requiring exact byte match on duplicate;
6. insert successor link row if absent, requiring exact byte match on duplicate;
7. insert one PREPARED transition row tied to the exact `anchor_intent_id`;
8. commit.

No head movement and no transition COMMITTED state occurs in Transaction A.

If the LAB-080 reservation already exists for the exact transition, retry may reuse it only after every stored field/event/link byte is exact. A conflicting LAB-080 intent id/content is fail-closed `IntentConflict` semantics.

## External phase

Use only the LAB-080 `shared_anchor_intents` row referenced by `anchor_intent_id`:

- PREPARED + no provider result at predecessor => exact retry permitted;
- PREPARED + exact reconciled request committed => eligible for Transaction B;
- CONFIRMED + exact receipt re-authenticates => eligible for Transaction B if local provenance still PREPARED;
- different request/position/receipt or unexplained provider advance => fail closed.

No local provenance status may substitute for re-authentication of the LAB-080 receipt.

## Transaction B — exact SQL shape

Under one `BEGIN IMMEDIATE`, re-read and re-verify:

- the transition is PREPARED and byte-for-byte unchanged;
- referenced event and link bytes/digests match;
- current authenticated head is the exact parent/parent_epoch;
- no sibling child/transition exists;
- LAB-080 intent is the exact referenced row and is CONFIRMED with a receipt that has just been externally re-authenticated;
- event-specific provider/schema/authority preconditions remain valid.

Then in the same SQL transaction:

1. `UPDATE provenance_transitions_v1 SET state='COMMITTED' WHERE transition_id=? AND state='PREPARED'` and require exactly one row changed;
2. update `provenance_chain_head_v1` from exact parent `(epoch,parent_digest)` to exact successor `(epoch+1,successor_digest)` using a compare-and-swap WHERE predicate and require exactly one row changed;
3. perform only the event-specific durable post-state mutation authorized by the event contract, if it is part of this atomic commit boundary;
4. commit.

Any zero/multiple-row result fails and rolls back.

## Immutability / DML authorization

When LAB-091 exact executable integration becomes available, provenance tables join its one-shot operation-scoped writer model.

Required guards:

- `provenance_events_v1`: INSERT-only through PREPARE permit; UPDATE/DELETE forbidden;
- `provenance_chain_links_v1`: INSERT-only through PREPARE permit; UPDATE/DELETE forbidden;
- `provenance_transitions_v1`: INSERT PREPARED through PREPARE permit; only exact state-only PREPARED->COMMITTED through COMMIT permit; DELETE forbidden;
- `provenance_chain_head_v1`: initialization insert or exact compare-and-swap COMMIT update only; DELETE forbidden.

These SQL guards are defense-in-depth inside the LAB-087 sole-writable-broker boundary. They are not a standalone same-privilege SQLite sandbox claim.

## Startup classification queries

Startup classifies before provider release, repair writes, migration writes, re-bootstrap, or worker delegation.

### 1. Schema presence

After authenticated initialization provenance says V1 is installed, all four tables and exact expected definitions must exist. Missing/renamed/retyped objects fail closed; ordinary startup does not recreate them.

### 2. Genesis

Require exactly one link for the DB identity at epoch 0, NULL parent, matching initialization provenance, and a head reachable from that genesis.

### 3. Transition/link cardinality

For every non-genesis link require exactly one transition whose `successor_link_digest` equals that link digest and whose event digest matches the link. No orphan links, orphan transitions, duplicate epochs or sibling parent children.

### 4. COMMITTED prefix

Starting at genesis, COMMITTED transitions must form one contiguous prefix ending at the cached head. A COMMITTED transition beyond the head or a head pointing through PREPARED evidence is corruption.

### 5. Unresolved transition

At most one PREPARED provenance transition may exist, and only as the exact immediate child of current head. Its referenced LAB-080 intent must be PREPARED or CONFIRMED. Any older PREPARED transition, two PREPARED transitions, wrong parent, wrong epoch, missing event/link, or changed LAB-080 identity fails closed.

### 6. Recovery classes

- no PREPARED transition: verify full chain/head/anchor and start;
- one PREPARED + LAB-080 PREPARED + provider has no request and position remains predecessor: exact retry allowed;
- one PREPARED + LAB-080 PREPARED but reconcile proves exact request committed: UNKNOWN-after-commit recovery may persist/confirm LAB-080 then run Transaction B;
- one PREPARED + LAB-080 CONFIRMED: re-authenticate exact receipt then run Transaction B;
- transition COMMITTED + head successor + LAB-080 not exact CONFIRMED: corruption;
- LAB-080 externally ahead without explainable contiguous confirmed ledger positions: fail unexplained advance.

## Defense-in-depth versus authority

### Defense-in-depth

- PRIMARY KEY / UNIQUE constraints;
- STRICT tables and CHECK(length(...)=32);
- foreign-key-like application joins;
- LAB-091 triggers/one-shot permits;
- `BEGIN IMMEDIATE` serialization;
- cached head singleton.

These make corruption/bugs harder but do not establish authenticity by themselves.

### Authenticated authority

A transition is trusted only from the combination of:

- canonical byte parser + domain-separated digest;
- authenticated initialization/root identity;
- full parent-linked chain and event-specific legal state delta;
- construction-bound retained DB/bootstrap/history/activation authority graph;
- exact LAB-080 intent identity and externally re-authenticated CONFIRMED receipt;
- terminal continuity with the external/shared monotonic anchor.

No SQLite row, trigger, timestamp, rowid, local hash, status flag, UNIQUE constraint, or cached head can replace these proofs.

## RED-first storage matrix

Freeze before production schema work:

1. clean genesis + normal PREPARE/anchor/COMMIT;
2. byte-identical event duplicate is idempotent;
3. same event digest with different bytes fails;
4. byte-identical link duplicate is idempotent;
5. same link digest with different bytes fails;
6. two children for one parent fail before external call;
7. two links for one DB epoch fail;
8. second PREPARED transition on current parent fails;
9. PREPARED transition on historical parent fails startup;
10. orphan event allowed only as exact referenced PREPARED evidence; otherwise startup classification rejects unexplained durable object according to executable cleanup policy;
11. orphan link fails;
12. transition missing event fails;
13. transition missing successor link fails;
14. link event digest mismatch fails;
15. transition successor digest mismatch fails;
16. transition anchor intent missing fails;
17. anchor intent id reused with different transition commitment fails;
18. PREPARED transition referencing LAB-080 CONFIRMED wrong request/receipt fails;
19. COMMITTED transition referencing LAB-080 PREPARED fails;
20. head advanced while transition remains PREPARED fails/recovery never guesses;
21. transition COMMITTED while head stays parent is recoverable only if same SQL transaction cannot actually produce that state; injected state fails closed;
22. head points to nonexistent link fails;
23. head points to PREPARED successor fails;
24. MAX(epoch)/rowid attacker row cannot redirect startup;
25. second genesis with NULL parent fails explicit genesis cardinality check;
26. TEXT hex digest where BLOB32 required fails;
27. BLOB length 31/33 fails;
28. REAL/TEXT epoch fails strict verifier even if SQLite comparison is numerically equal;
29. negative epoch fails;
30. epoch `2^63-1` permits verification but next append fails before PREPARE;
31. event canonical bytes with unknown/duplicate/trailing field fail;
32. canonical digest mismatch fails before recovery/provider writes;
33. delete historical COMMITTED transition fails startup;
34. delete historical link fails startup;
35. delete genesis/head fails startup, never re-bootstrap;
36. change cached head to older valid link under newer external anchor fails rollback;
37. one PREPARED + provider no-result at predecessor retries same LAB-080 request only;
38. one PREPARED + timeout-after-commit reconciles exact request and commits once;
39. crash after LAB-080 confirmation before Transaction B completes exact frozen bytes once;
40. changed event/link after external confirmation blocks Transaction B;
41. provider-generation event cannot mutate schema/authority columns/state;
42. migration event cannot mutate provider head/authority;
43. authority event cannot mutate provider head/schema;
44. LAB-093 worker cannot directly insert/update/delete provenance rows or obtain raw DB/anchor capability;
45. LAB-087 broker restart performs classification before worker endpoint publication;
46. LAB-080/081/086 existing ordinary intents remain valid and cannot impersonate provenance solely by using `intent_type='migration'` because inner canonical domain/commitment differs.

## Deferred executable choices

Do not change production schema while exact RED/GREEN execution is unavailable. The following remain implementation details to prove on real source:

- whether SQLite in the supported deployment is new enough for `STRICT`; if not, preserve the exact verifier rules and use explicit `typeof()` checks/triggers instead of weakening typing;
- whether dedicated `intent_type='provenance_transition'` can replace the temporary LAB-080 `migration` outer slot compatibly;
- exact foreign-key declarations: direct FK to `shared_anchor_intents` is useful defense-in-depth but must not create initialization/order problems with legacy migration;
- whether unreferenced immutable event rows should be rejected at startup or tolerated as non-authoritative garbage. Links/transitions/head remain strict regardless; no unreferenced event may ever influence authority.

## Verdict

`PROVENANCE_DURABLE_SQL_STORAGE_SCHEMA_V1_FROZEN`

The provenance mechanism now has one durable SQL shape tied directly to existing LAB-080 intent/receipt authority. PREPARED/COMMITTED is represented once at the transition layer; exact immutable event/link bytes are frozen before external mutation; the cached head is never its own proof; sibling/fork prevention is both constraint-backed and authenticated; restart has a deterministic classification path and never repairs from rowid/time/MAX heuristics.