# Sink-fence restore, parser equivalence, schema downgrade, tombstone propagation, and PQ resumption DR — v1

Date: 2026-09-09
Status: `SINK_FENCE_RESTORE_PARSER_SCHEMA_TOMBSTONE_PQ_DR_V1_FROZEN`
Scope: distinct evidence fallback while LAB-086 remains blocked on byte-exact local executable closure.

## Why this slice exists

The retained handoff identified five unresolved failure surfaces that are easy to misclassify as ordinary availability problems but can silently re-authorize stale state after rollback, schema change, deletion, or regional recovery:

1. a protected sink may restore an older snapshot and forget the highest fencing generation it previously accepted;
2. two verifiers can each accept a signed/canonical payload while disagreeing about the semantic object they parsed;
3. schema evolution can silently make a formerly mandatory dependency/authority field optional or invisible to an older verifier;
4. a deletion can reach the primary record while stale caches/indexes/replicas later reintroduce the deleted authority/data;
5. disaster recovery can duplicate TLS/PQ resumption ticket decryption and anti-replay authority across regions or mixed-version nodes.

These are one pattern: **durable monotonic authority cannot be reconstructed from the current surviving object alone.** Recovery must preserve or independently re-establish the monotonic floor and the semantics used to interpret it.

## Primary donors

- etcd disaster recovery: snapshot restore can move revisions backwards; `--bump-revision` exists to prevent decreasing revisions, and `--mark-compacted` invalidates watchers/caches that otherwise retain observations from revisions no longer present after restore. https://etcd.io/docs/v3.8/op-guide/recovery/
- Consul sessions/locks: lock ownership is advisory and sequencer-style state must be checked at the protected resource; a stale owner cannot be made harmless merely by releasing an advisory lock. https://developer.hashicorp.com/consul/docs/dynamic-app-config/sessions
- RFC 8785 JSON Canonicalization Scheme: JCS requires I-JSON, forbids duplicate property names, constrains numbers, and preserves Unicode string data as-is. https://www.rfc-editor.org/rfc/rfc8785.html
- RFC 8949 CBOR: duplicate map keys can be lost, rejected, or interpreted differently by generic decoders; deterministic encoding and application data-model equivalence must therefore be explicit. https://www.rfc-editor.org/rfc/rfc8949.html
- RFC 9052 COSE: applications must not generate or process duplicate labels in a map and must enforce that either in the parser or application. https://www.rfc-editor.org/rfc/rfc9052.html
- Protocol Buffers evolution guidance: binary schema changes are only safe under defined compatibility rules; field-number changes are wire-unsafe and old/new serializers can otherwise disagree. https://protobuf.dev/programming-guides/proto3/
- DynamoDB global tables: replication carries deletion state (`aws:rep:deleting` in legacy global-table metadata), replica changes are asynchronous, and stale regional reads/writes can exist while replication converges. https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/globaltables_HowItWorks.html
- RFC 9846 TLS 1.3: single-use tickets are the strongest simple TLS-layer replay defense; in distributed deployments a single authoritative zone per ticket is stronger than independent per-zone replay caches; fresh starts should reject 0-RTT while the recording window overlaps startup. https://www.rfc-editor.org/rfc/rfc9846.html

## Frozen security contract

### 1. Sink fence persistence survives rollback/restore

`LOCK_RELEASED != OLD_OWNER_UNABLE_TO_WRITE` remains the predecessor invariant.

This slice adds:

`RESTORED_SINK_STATE != AUTHORITY_TO_REUSE_OLD_FENCE`

A protected sink MUST durably reject any mutation whose fencing generation is less than the highest generation that sink has ever accepted for the same authority lineage, including after:

- snapshot restore;
- replica promotion;
- storage engine rollback;
- disaster-recovery reconstruction;
- rehydration from an archive that predates later accepted generations.

The fence floor therefore cannot live only inside the same rollback domain as the data it protects. One of the following must hold:

1. the restore protocol carries an authenticated monotonic `restore_generation`/fence floor from an independent continuity authority;
2. the sink's accepted-fence floor is stored in an independent monotonic domain;
3. the restored sink enters a fail-closed epoch in which consequential writes are rejected until a new generation strictly above the pre-restore maximum is authenticated.

A snapshot integrity hash proves the snapshot is intact; it does **not** prove that it is the newest authorized state.

etcd's restore revision bump is a donor for this distinction: restoring valid old data can still move observable revisions backwards, so recovery explicitly bumps revision and can mark prior future revisions compacted to invalidate stale watchers.

#### Restore-generation rule

Each protected mutation is bound to:

`authority_lineage_id || authority_generation || sink_restore_generation || operation_id || canonical_payload_digest`

The sink retains the lexicographic/monotonic floor required by policy. A restore that cannot prove a floor at least as high as the previously accepted one MUST NOT resume consequential writes.

### 2. Dual-verifier transition requires semantic equivalence, not two green lights

`VERIFIER_A_ACCEPTS && VERIFIER_B_ACCEPTS != SAME_SEMANTICS`

A dual-verifier migration window is safe only when both independent implementations produce the same **canonical semantic projection** before the authorization decision.

Required projection includes every authority-relevant field after parsing, defaulting, unknown-field handling, integer/string conversion, Unicode handling, duplicate-key handling, and extension processing.

A signed byte string is insufficient if verifier A and verifier B parse it into different authority objects.

#### Fail-closed parser rules

- duplicate JSON object names: reject before canonicalization/authorization;
- duplicate/equivalent CBOR map keys: reject according to the protocol's specific data model;
- non-finite/over-precision numbers where the schema expects exact integers: reject rather than round/coerce;
- unknown critical fields: reject unless the schema explicitly defines forward-compatible handling;
- Unicode normalization: never let one verifier normalize while another compares raw strings unless the protocol explicitly canonicalizes that layer;
- aliases/defaults: expansion must be versioned and included in the canonical semantic projection;
- parser disagreement: `VERIFIER_DIVERGENCE`, no majority choice and no "new verifier wins" shortcut.

The canonical projection itself receives a schema/version identifier and digest. During migration both verifiers must agree on `(schema_id, semantic_digest, authorization_result)`.

### 3. Dependency-attestation schema evolution cannot downgrade mandatory edges

`OLDER_VERIFIER_IGNORES_FIELD != FIELD_OPTIONAL`

Each dependency-attestation generation carries:

- `schema_id` and monotonic `schema_generation`;
- the exact set of mandatory dependency classes;
- critical-field bitmap/list;
- canonical semantic digest;
- predecessor schema digest and migration authorization.

A successor schema MAY add a new mandatory dependency class only at a declared future policy boundary. Once mandatory for generation `g`, an older verifier that cannot interpret that class is not authorized to validate generation `g+`; it must return `UNSUPPORTED_CRITICAL_SCHEMA`, not silently ignore the edge.

Likewise, removal or relaxation of a mandatory class is a consequential policy downgrade and requires explicit downgrade authority; ordinary schema compatibility machinery is not downgrade authority.

This distinguishes transport compatibility from security compatibility. Protobuf can preserve unknown fields in some binary paths, but a security decision still cannot rely on an older application that does not understand the authority semantics of the field it preserved.

### 4. Tombstone propagation prevents deleted authority/data from reappearing

`PRIMARY_ROW_ABSENT != DELETION_CONVERGED`

A security-relevant deletion is a versioned state transition, not merely absence. The durable tombstone binds:

`logical_object_id || deletion_generation || predecessor_digest || reason_class || policy_epoch || retention/GC_boundary`

Every read/write/index/cache path must compare candidate live state against the highest known tombstone generation. A live object with generation <= a surviving tombstone is stale and MUST NOT be reintroduced.

Deletion closure covers:

- primary rows;
- secondary/deterministic indexes;
- negative and positive caches;
- materialized views;
- embeddings/features used for consequential lookup/authorization;
- async queues/retry jobs;
- replicas/DR copies;
- backups subject to restore;
- authorization/session caches derived from the deleted object.

#### Reintroduction rule

A restore/import/replay from a snapshot older than the tombstone must either:

1. replay authenticated tombstones after restore before serving consequential reads/writes; or
2. advance the entire restored domain into a new generation whose reconciliation proves no stale object shadows a later tombstone.

`CACHE_MISS != TOMBSTONE_FORGETTING`:

negative caches are performance state; durable deletion authority cannot depend on their survival. Conversely, deleting a negative cache must not permit a stale positive copy to become authoritative again.

Tombstone GC is allowed only after proving that every copy domain capable of reintroduction is beyond the deletion generation or cryptographically incapable of serving the predecessor object. "TTL elapsed" alone is not such proof.

### 5. PQ/TLS resumption authority migration across regional DR

`TICKET_DECRYPTS != TICKET_SPEND_AUTHORITY_OWNED_HERE`

`REGIONAL_FAILOVER != AUTHORITY_TO_DUPLICATE_0RTT_ACCEPTANCE`

Ticket decryption keys and single-use/anti-replay authority are separate capabilities. A DR region may possess enough key material to decrypt a ticket while still lacking authority to accept consequential 0-RTT.

For every issued ticket, the authenticated ticket policy binds:

- issuing crypto-policy epoch and minimum PQ/hybrid floor;
- server/service identity lineage;
- ticket-key generation;
- authoritative spend region/domain;
- maximum lifetime and local shorter validity policy;
- 0-RTT eligibility and application replay class;
- migration/failover generation.

#### Disaster-recovery transition

Before old and new regions can both accept consequential resumption, one of these must be proven:

1. a globally linearizable single-spend authority remains available; or
2. the old region's acceptance authority is fenced/revoked and a new authority generation is activated; or
3. 0-RTT is disabled and resumption falls back to replay-safe 1-RTT/full handshake until ownership is unambiguous.

A regional outage that prevents proving old-owner fencing MUST select option 3.

#### Post-compromise ticket-key rotation

Compromise of ticket key `K1` creates a policy boundary. Rotation to `K2` does not make tickets issued under `K1` trustworthy merely because another server can still decrypt them. Policy must be able to mark `K1` ticket generations rejected for new consequential use while retaining them only as historical evidence/telemetry.

A mixed-version cluster must evaluate the **current** crypto floor. An older node unable to enforce the current PQ/hybrid policy must reject/fallback, not accept because the predecessor ticket was valid when issued.

RFC 9846's single authoritative zone per ticket is the donor: independent replay caches per zone weaken the guarantee to once per zone, while a single authority prevents the same ticket from being accepted as fresh in several zones.

## Cross-cutting state model

All five surfaces use the same minimum record shape:

```text
SecurityGeneration {
  lineage_id,
  generation,
  predecessor_digest,
  policy_epoch,
  schema_id,
  authority_set_digest,
  canonical_state_digest,
  created_at_evidence,
  transition_authorization,
}
```

No recovery path may infer a missing predecessor generation merely from the internally consistent state that survived.

### Monotonic degradation rule

Historical compromise, parser divergence, missing tombstone coverage, or ambiguous ticket-spend ownership creates a new status/event. A later clean generation can restore forward operation, but MUST NOT rewrite the historical generation as if it had always been trustworthy.

## RED-first executable matrix

The following are requirements for later LAB-093+ executable work, not claimed passes.

### A. Sink restore/fencing — 8 cases

1. accept fence 10; restore snapshot containing floor 7; stale writer fence 8 -> reject;
2. same restore with authenticated independent floor 10 and new writer 11 -> accept;
3. snapshot hash valid but older than accepted fence -> reject consequential writes;
4. restored DB starts without proof of prior floor -> fail closed;
5. old owner retries a previously valid operation after restore generation changes -> reject replay;
6. restored sink receives current payload signed under old restore generation -> reject;
7. legitimate new generation above pre-restore max survives restart -> accept;
8. stale watcher/cache created before rollback is invalidated before serving authority decisions.

### B. Canonicalization/parser differential — 8 cases

9. duplicate JSON authority key with first/last-wins parsers -> both must reject;
10. Unicode-normalized vs raw-distinct principal identifiers -> divergence -> reject;
11. integer beyond exact supported range rounded by one parser -> reject;
12. CBOR duplicate/equivalent map key interpreted differently -> reject;
13. unknown critical extension preserved but ignored by old verifier -> reject old verifier;
14. alias/default expansion differs between versions -> semantic digest mismatch -> reject;
15. both signatures valid but semantic projections differ -> reject;
16. independent implementations agree byte parsing + semantic digest + decision -> transition candidate may proceed.

### C. Schema evolution downgrade — 8 cases

17. new mandatory `kms_control_domain` field with old verifier -> unsupported-critical, not PASS;
18. successor removes mandatory cloud-control edge without downgrade authorization -> reject;
19. field renumber/rebinding changes meaning while wire parse remains possible -> reject schema lineage;
20. unknown noncritical descriptive field -> permit if canonical policy says ignorable;
21. mandatory-field list itself omitted -> reject;
22. attacker supplies older `schema_id` under newer policy epoch -> reject rollback;
23. predecessor-to-successor schema bridge signed by insufficient authority -> reject;
24. authorized future boundary activates new schema and all verifiers understand mandatory fields -> accept.

### D. Tombstone/reintroduction — 8 cases

25. delete primary + leave stale positive cache -> stale cache cannot authorize/read;
26. delete primary + restore pre-delete snapshot -> tombstone replay suppresses restored object;
27. replica disconnected during deletion rejoins with older live copy -> tombstone wins;
28. async retry job recreates deleted row with predecessor generation -> reject;
29. derived deterministic index still points to deleted principal -> lookup fails closed;
30. tombstone GC attempted while an archive/backup domain can still restore predecessor -> reject GC;
31. deletion propagated everywhere, negative cache lost -> stale predecessor still cannot return;
32. explicit authorized re-create uses a strictly new object/generation lineage and cannot masquerade as predecessor resurrection.

### E. PQ/TLS resumption DR — 8 cases

33. ticket decrypts in old and new region but spend ownership ambiguous -> consequential 0-RTT reject/fallback;
34. old region fenced, spend authority transferred to new generation -> exactly one region accepts;
35. partition duplicates independent replay caches -> policy detects weaker mode and disables consequential 0-RTT;
36. fresh DR process starts with anti-replay recording-window gap -> reject 0-RTT during overlap;
37. K1 compromised then K2 rotated; old K1 ticket presented -> reject new consequential use;
38. pre-upgrade classical ticket reaches node after PQ/hybrid floor activation -> full compliant handshake or reject;
39. mixed-version old node cannot evaluate current policy epoch -> reject/fallback, never grandfather;
40. ordinary non-0RTT resumption remains possible only if current identity, lifetime, ticket generation and crypto policy all revalidate.

## Implementation consequences for AI Runtime Lab

This design should not be implemented as five isolated ad-hoc flags. Future RED/GREEN work should reuse three shared primitives where possible:

1. **Generation-bound protected sink** — monotonic floor + restore generation + transition authorization;
2. **Canonical semantic verifier** — strict parse, critical-field handling, canonical projection digest, dual-verifier equality;
3. **Deletion/resumption ownership ledger** — explicit successor generations for tombstone GC and ticket-spend authority migration.

A future implementation must first prove whether existing LAB-090..100 surfaces already contain sufficient generation/lineage primitives before adding new tables or authority stores.

## Security audit of this freeze

- No claim here substitutes for LAB-086 exact executable gates.
- Snapshot integrity, valid signatures, parser success, cache absence, ticket decryption, and regional availability are each explicitly separated from current authorization.
- Every recovery path has an anti-rollback or fail-closed rule.
- No low-level Git ref/tree manipulation or background worker dependency is introduced.
- The test matrix contains both fail-closed negatives and legitimate recovery positives to avoid designing a system that only survives by permanently refusing service.

## Next distinct evidence slice if exact execution remains unavailable

Investigate and freeze: **fence-floor authority compromise/recovery; semantic-projection hash algorithm migration and verifier quorum independence; schema registry equivocation/split-view; tombstone GC witness/backup discovery completeness; PQ ticket-policy state under client-side ticket caching, server identity rollover, and cross-service SNI/ALPN rebinding**.
