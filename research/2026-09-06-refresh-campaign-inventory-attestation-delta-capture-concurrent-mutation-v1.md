# Refresh-campaign inventory attestation / delta capture / completeness under concurrent mutation v1

Status: `REFRESH_CAMPAIGN_INVENTORY_ATTESTATION_DELTA_CAPTURE_CONCURRENT_MUTATION_V1_FROZEN`

Date: 2026-09-06

## Scope

This note extends the frozen historical re-attestation / cryptographic-sunset contract. It answers one question: how can a refresh campaign prove that it found every still-live E1/E2/E3/E4 obligation while evidence, roots, revocations, appeals, dependency repairs, archive locations, verifier policy and object liveness continue to mutate, without globally stopping writers?

This is a design contract, not a claim of production integration or behavioral PASS.

## Primary-source donors

1. PostgreSQL logical replication exported snapshots: creation of a logical replication slot returns a `consistent_point` and an exported `snapshot_name`; the snapshot represents database state after which subsequent changes are available in the change stream. Mechanism reused: bind baseline snapshot and ordered delta stream to the same cut, rather than independently sampling state and log. Source: https://www.postgresql.org/docs/17/protocol-replication.html and https://www.postgresql.org/docs/16/logicaldecoding-explanation.html
2. Debezium incremental snapshots: concurrent table snapshots use explicit snapshot windows/watermarks and reconcile snapshot READs against streamed UPDATE/DELETE events for the same primary key. Mechanism reused: bounded overlap window plus deterministic dedup/supersession, not an assumed pause in writers. Source: https://debezium.io/documentation/reference/stable/connectors/postgresql.html
3. CockroachDB changefeeds: resolved timestamps are promises that no later event will arrive at or below the resolved frontier. Mechanism reused: campaign finalization requires an authenticated resolved-through frontier, not merely "stream currently empty". Source: https://www.cockroachlabs.com/blog/change-data-capture/
4. Kafka transactional offset handling: consumed offsets can be committed atomically with produced records; producer fencing prevents a stale transactional producer from continuing as authority. Mechanism reused: atomically bind processing progress to emitted campaign dispositions where the substrate supports it; do not separately checkpoint input and output and infer exact-once. Source: https://kafka.apache.org/10/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html

## Threat model

During a long-running crypto/evidence refresh campaign, any of the following may happen concurrently:

- a new evidence object is published;
- an E1 object becomes E2/E3 due to a newly discovered dependency;
- a live root is added or removed;
- a revocation, appeal, fraud finding or dependency-repair edge reactivates historical closure;
- an archive object moves between locations;
- a previously archived object becomes unavailable;
- a verifier/policy/trust-root generation changes;
- an object is superseded or tombstoned;
- GC marks or deletes objects;
- workers crash and resume;
- two refresh workers observe overlapping ranges;
- a delayed event becomes visible after the baseline snapshot scan has already passed its object.

A naive `scan all rows, then process new rows` protocol can miss exactly the objects that mutate across the scan boundary.

## Core decision

A refresh campaign universe is not "whatever the scanner saw". It is an authenticated **snapshot-plus-delta interval** with an explicit start frontier and a resolved final frontier.

Canonical campaign coverage statement:

`Universe(C) = BaselineSnapshot(F0) ⊕ CanonicalDeltas(F0, F1]`

where:

- `F0` is the authenticated opening frontier;
- `BaselineSnapshot(F0)` is a repeatable snapshot logically bound to `F0`;
- `CanonicalDeltas(F0, F1]` contains every authority-relevant committed mutation after `F0` through `F1`;
- `F1` is not accepted until every contributing source proves `RESOLVED_THROUGH(F1)`;
- `⊕` is deterministic replay with explicit object identity, causality and supersession rules.

An empty poll is not a final frontier.

## Source domains and frontiers

The minimum refresh-completeness frontier covers these authority domains:

1. object/evidence registry;
2. semantic dependency and repair-edge registry;
3. liveness/GC-root registry;
4. revocation / appeal / fraud / adjudication registry;
5. archive-location + availability registry;
6. verifier / policy / trust-root / crypto-sunset generation registry;
7. substitution / supersession / tombstone registry.

### Preferred single-log form

If all material mutations can commit into one append-only authenticated source log, `F0` and `F1` are single monotonically increasing positions. Baseline snapshot is exported at the same consistent point from which delta consumption begins.

### Federated form

If domains cannot share one transaction/log, use an authenticated vector frontier:

`F = {domain_i: (generation_i, position_i, root_i)}`

A vector component cannot silently disappear or be replaced by another domain. Domain membership itself is versioned and authenticated.

Federated completion additionally requires either:

- atomic cross-domain transaction IDs visible in every affected source; or
- causal parent IDs that let the verifier prove all consequences of a mutation are included before finalization.

Without either mechanism, "all streams individually caught up" does not prove cross-domain semantic completeness.

## Opening protocol

1. Authenticate the campaign policy, source-domain set and accepted schema/trust generations.
2. Establish `F0` from authoritative source checkpoints.
3. Start/retain delta capture from `F0` **before** releasing any source retention needed to replay `(F0, ...]`.
4. Export/read a repeatable baseline snapshot bound to `F0`.
5. Record an authenticated `CampaignOpenV1` containing campaign id, source-domain manifest, `F0`, snapshot identity/root, schemas, trust generations and delta-retention leases.
6. Only then parallelize baseline scanning.

Opening in the opposite order (scan, then begin change capture) is invalid because mutations can fall into the gap.

## Baseline identity and exact-one disposition

Each baseline object is keyed by immutable content/object identity plus authority namespace, not mutable archive pathname or current rowid.

For each object material at `F1`, the final campaign manifest must contain exactly one terminal disposition:

- `REFRESHED_SUCCESSOR_BOUND`
- `ALREADY_STRONG_ENOUGH`
- `QUARANTINED_UNREFRESHABLE`
- `NO_LONGER_LIVE_PROVEN`
- `SUPERSEDED_WITH_VALID_WITNESS`
- `OUT_OF_SCOPE_PROVEN`

Intermediate states such as `SEEN`, `MOVED`, `RETRYING`, `PENDING_APPEAL` or `WAITING_ARCHIVE` are not completion dispositions.

Exact-once applies to **obligation identity + generation**, not to physical row observations. Duplicate observations caused by snapshot/delta overlap are expected and must deterministically collapse.

## Delta semantics

Every authority-relevant mutation after `F0` is represented as a canonical event with:

- source domain + monotonic position;
- transaction/causal id;
- subject/object id;
- precondition generation or predecessor digest;
- event kind;
- authority-relevant payload digest;
- commit frontier/time where meaningful;
- source authentication proof.

Required event kinds include at least:

`OBJECT_PUBLISHED`, `LIVE_ROOT_ADD`, `LIVE_ROOT_REMOVE`, `DEPENDENCY_ADD`, `DEPENDENCY_REPAIR`, `REVOCATION`, `APPEAL_OPEN`, `APPEAL_RESOLVE`, `ARCHIVE_LOCATION_ADD`, `ARCHIVE_LOCATION_RETIRE`, `AVAILABILITY_FAIL`, `POLICY_GENERATION_ADVANCE`, `TRUST_GENERATION_ADVANCE`, `SUPERSEDE`, `TOMBSTONE`, `GC_DELETE_COMMIT`.

Unknown event kinds or undecodable generations keep the affected frontier unresolved; they are never treated as no-ops.

## Deduplication and supersession

Snapshot/delta overlap is normal. A baseline object and a later mutation for that object do not count twice.

Rules:

- deltas replay in authenticated source order;
- a delta may supersede baseline state only with matching object identity and valid predecessor/generation relation;
- delete/tombstone does not erase historical refresh obligation if another live root, appeal, revocation, E2/E3/E4 dependency or retention hold still reaches the object;
- archive relocation is modeled as `ADD(new_location, verified_content)` followed later by `RETIRE(old_location)`; a move is never an unauthenticated pathname rewrite;
- if content identity changes during relocation, this is replacement/substitution and requires the frozen substitution witness contract.

## Finalization barrier

A campaign cannot finalize merely because all workers report idle.

Finalization uses a two-cut barrier:

1. choose candidate `F1` after baseline scan and ordinary deltas are drained;
2. require every source domain to authenticate `RESOLVED_THROUGH(F1_component)` — no future event committed at or below that component may appear later;
3. ingest and replay all deltas through `F1`;
4. recompute obligation set and exact-one terminal dispositions at `F1`;
5. re-check campaign source-domain membership, schema/trust generations and retention leases;
6. publish `CampaignCompletionV1` binding `F0`, `F1`, snapshot root, delta-log roots, disposition-manifest root, unresolved/quarantine set, validator set and policy generation;
7. independent verifier replays snapshot+delta commitments and verifies complete disposition coverage.

If a new material mutation commits after `F1`, it belongs to a later delta campaign. If it is causally rooted at or before `F1` but was omitted from the source's resolved claim, the source has equivocated/failed its completeness contract.

## Delta-on-finalization race

For federated sources, events can cross while `F1` is being assembled. Therefore a simple "read latest position from each source once" vector is unsafe.

Allowed mechanisms:

- global coordinator transaction that freezes only the frontier metadata, not writers;
- barrier epoch: each domain acknowledges the same campaign-finalization epoch only after publishing all prior causal work;
- repeated vector stabilization: capture V1, wait for all domains resolved-through V1, then prove no cross-domain transaction with commit/order <= V1 remains partially represented.

If none is supported, completion remains `PARTIAL_UNRESOLVED`; do not fabricate global completeness from per-source liveness.

## Liveness changes during campaign

The target set is evaluated at `F1`, but history since `F0` remains relevant.

- object live at F0 and dead by F1 may use `NO_LONGER_LIVE_PROVEN` only if the removal is authenticated and no higher-class dependency/appeal/revocation/hold remains;
- object dead at F0 but reactivated before/equal F1 becomes an obligation;
- object published after F0 and live by F1 becomes an obligation even if the baseline scan never saw it;
- transient reactivation that triggers an irreversible consequential action cannot be erased merely because it is dead again at F1; the action/evidence dependency is separately retained.

## Archive relocation and availability

Location is not identity.

Campaign processing must bind archive content digest + provenance and retrieve/verify bytes whenever the refresh operation requires original bytes. A relocation event cannot satisfy refresh. `ARCHIVE_LOCATION_RETIRE` is valid only after the replacement location has a verified content/provenance receipt and required availability policy.

If the only known copy disappears before refresh, terminal state is `QUARANTINED_UNREFRESHABLE`, not `NO_LONGER_LIVE`.

## GC interlock

While campaign C is open:

- baseline snapshot roots, delta-retention leases, unresolved obligation closures and originals needed for hash/semantic renewal are temporary GC roots;
- GC proof must bind a campaign frontier at least as new as the refresh campaign's current acknowledged frontier;
- GC cannot delete an original merely because one worker emitted `REFRESHED_SUCCESSOR_BOUND`; deletion authority requires accepted campaign disposition + substitution/successor witness + challenge/revocation conditions from the frozen GC contracts;
- if GC observes a newer revocation/repair/liveness frontier than the campaign completion proof, that completion is stale for deletion authority.

## Crash / restart

Durable campaign progress consists of authenticated source frontiers and idempotent dispositions, not worker-local cursors.

After crash:

- resume delta capture from the last durable acknowledged source position;
- re-read any uncommitted baseline chunk;
- duplicate snapshot/delta observations collapse by obligation identity/generation;
- never skip ahead based only on a worker's last in-memory primary key;
- if retained source history required to bridge the durable frontier has expired, campaign becomes `GAP_UNRECOVERABLE` and cannot complete.

## Proof bundle

`RefreshCampaignCompletenessProofV1` must include or commit to:

- campaign policy and source-domain manifest;
- `F0` and `F1`;
- baseline snapshot identity/root and F0 binding;
- per-domain delta roots/ranges and resolved-through attestations;
- schema/trust/policy generations;
- cross-domain causal/barrier evidence where applicable;
- canonical replay algorithm/version;
- final obligation-set root;
- terminal-disposition manifest root;
- quarantine/unresolved set;
- independent validation attestations required by dependency class;
- all source-retention gap checks;
- proof that every obligation in final universe has exactly one terminal disposition.

A verifier must be able to distinguish `COMPLETE`, `PARTIAL_UNRESOLVED`, `GAP_UNRECOVERABLE`, `SOURCE_EQUIVOCATION`, and `INVALID`.

## Explicit non-claims

This contract does **not** claim:

- that per-row timestamps alone prove completeness;
- that Kafka-like exactly-once transport proves application-semantic exact-once;
- that an archive manifest proves bytes remain retrievable;
- that a source's current high-water mark proves no older event will arrive later;
- that snapshot isolation across independent databases creates a global consistent snapshot;
- that campaign completion itself authorizes GC deletion.

## 80-case RED-first matrix

### A. Opening cut / snapshot binding (10)
1. delta capture begins after baseline scan starts -> reject gap-prone opening;
2. snapshot not bound to F0 -> reject;
3. F0 root mismatch -> reject;
4. source-domain omitted from manifest -> reject;
5. source-domain added after open without authenticated manifest generation -> reject;
6. retention lease starts after F0 -> reject;
7. snapshot identity reused across incompatible policy generation -> reject;
8. snapshot taken before F0 but claimed at F0 -> reject;
9. federated vector component rollback -> reject;
10. unknown snapshot schema generation -> unresolved/reject.

### B. Snapshot/delta overlap and dedup (10)
11. same object in baseline + update delta -> one obligation;
12. baseline + delete delta while still rooted -> retain obligation;
13. baseline + delete delta with no remaining root -> `NO_LONGER_LIVE_PROVEN`;
14. baseline old generation + two ordered updates -> final generation exactly once;
15. duplicate delta delivery -> idempotent;
16. same event id with different payload -> source equivocation;
17. delta predecessor mismatch -> reject;
18. late baseline chunk after newer delta -> newer delta wins deterministically;
19. mutable rowid reused for different content -> distinct identity, reject collapse;
20. content duplicate at two locations -> one content obligation, multiple location facts.

### C. Concurrent liveness/dependency changes (10)
21. dead at F0, root added before F1 -> obligation;
22. live at F0, root removed before F1 -> prove no remaining dependency before discharge;
23. E1 upgraded to E3 before F1 -> E3 refresh requirements;
24. repair edge discovered after object scanned -> reopen obligation;
25. revocation reactivates historical closure -> reopen all affected obligations;
26. appeal opens then remains unresolved at F1 -> rooted/unresolved;
27. appeal resolves before F1 -> apply authenticated resolution, preserve consequential evidence;
28. tombstone plus live E4 authority path -> no discharge;
29. supersession without valid witness -> original remains live;
30. new object published before F1 but never in baseline -> delta creates obligation.

### D. Archive/location mutation (10)
31. verified add-new then retire-old -> valid relocation;
32. retire-old before new retrieval verification -> reject;
33. pathname changes without content binding -> reject;
34. replacement bytes hash mismatch -> quarantine;
35. archive manifest present but retrieval fails -> quarantine;
36. location duplicated across archives -> dedup identity, preserve provenance;
37. relocation races hash renewal -> retain original until renewal result committed;
38. archive generation rollback -> reject;
39. location event arrives after claimed resolved frontier with older position -> source failure;
40. last copy lost during campaign -> `QUARANTINED_UNREFRESHABLE`.

### E. Final frontier / resolved-through semantics (10)
41. all workers idle but no resolved frontier -> no completion;
42. one source lacks resolved-through F1 -> partial unresolved;
43. source later emits <=F1 event after resolved claim -> source equivocation/failure;
44. F1 vector built from incompatible barrier epochs -> reject;
45. cross-domain transaction represented in only one source -> unresolved/reject;
46. causal parent <=F1, child required but >F1 due ingestion delay -> barrier must capture child or fail;
47. source membership changes while finalizing -> restart/stabilize frontier;
48. policy generation changes while finalizing -> stale completion;
49. trust generation changes while finalizing -> revalidate obligations;
50. finalized delta range has an authenticated position gap -> invalid.

### F. Exact-one dispositions / processing (10)
51. obligation missing disposition -> incomplete;
52. obligation has two terminal dispositions -> invalid;
53. retry creates duplicate successor but same obligation -> deterministic winner/explicit conflict;
54. `REFRESHED_SUCCESSOR_BOUND` without successor witness -> invalid;
55. `ALREADY_STRONG_ENOUGH` under wrong sunset policy -> invalid;
56. `OUT_OF_SCOPE_PROVEN` without policy authority -> invalid;
57. `NO_LONGER_LIVE_PROVEN` ignores E3 edge -> invalid;
58. quarantined object silently omitted from completion root -> invalid;
59. worker claims success but output commit absent -> pending, not complete;
60. input checkpoint advances independently of disposition output -> detect/replay, no silent skip.

### G. Crash, rollback and retention gaps (10)
61. crash after snapshot read before disposition commit -> replay chunk;
62. crash after disposition commit before cursor advance -> idempotent duplicate;
63. crash after cursor advance before disposition commit -> forbidden/checkpoint rollback;
64. delta source truncates required range -> `GAP_UNRECOVERABLE`;
65. worker resumes from unauthenticated local cursor -> reject;
66. source checkpoint rollback after restart -> reject;
67. stale producer/worker continues writing dispositions -> fence/reject generation;
68. partial campaign completion record after crash -> verify/recover or discard, never assume complete;
69. baseline snapshot unavailable after crash but scan incomplete -> gap/incomplete;
70. retained source history available -> deterministic resume from durable frontier.

### H. GC, adversarial races and independent verification (10)
71. GC deletes original while refresh unresolved -> fail closed/audit violation;
72. GC uses completion proof older than revocation frontier -> stale/reject;
73. GC uses newer campaign proof but older repair frontier -> stale/reject;
74. malicious source omits event and advances without authenticated resolved semantics -> no completion authority;
75. source equivocates two delta roots for same range -> source equivocation;
76. independent verifier recomputes different obligation root -> invalid;
77. independent verifier finds terminal disposition count != obligation count -> invalid;
78. compressed proof omits source-domain manifest -> invalid;
79. campaign completion proves coverage but not successor semantic validity -> no destructive authority;
80. full snapshot+delta replay reproduces F1 obligation/disposition roots -> PASS for completeness layer only.

## Frozen acceptance contract

`REFRESH_CAMPAIGN_INVENTORY_ATTESTATION_DELTA_CAPTURE_CONCURRENT_MUTATION_V1_FROZEN` means:

1. baseline and deltas share an authenticated opening cut;
2. every material source is part of an authenticated source-domain manifest;
3. finalization requires resolved-through evidence, never an empty queue/poll;
4. snapshot/delta overlap is explicitly deduplicated by immutable obligation identity and ordered mutation semantics;
5. cross-domain completion requires atomic transaction identity, causal closure or an equivalent authenticated barrier;
6. liveness/revocation/appeal/repair/archive/trust changes through F1 can create or reopen obligations;
7. archive relocation cannot erase content identity or byte-availability requirements;
8. active campaign inputs and unresolved closures interlock with GC;
9. crash recovery resumes from durable authenticated frontiers and fails closed on source-history gaps;
10. independent replay must reproduce the final obligation-set and terminal-disposition commitments.

## Audit finding

The protocol deliberately prefers `PARTIAL_UNRESOLVED` over a false global `COMPLETE`. The largest residual risk is federated finalization: without a shared transaction/log or explicit causal/barrier protocol, independent resolved positions do not prove that every cross-domain consequence has become visible. That boundary must remain visible in implementation rather than being hidden behind a generic `latest_checkpoint()` abstraction.

## Next distinct evidence task

**Federated finalization barrier / causal-closure attestation / cross-domain partial-transaction detection semantics**: define the minimum authenticated protocol that lets independent evidence, revocation, repair, liveness and archive domains publish a common `F1` without a globally serializable database; determine how barrier epochs, causal transaction manifests and timeout/UNKNOWN states compose with source equivocation, offline domains and GC authority; freeze executable RED cases for split transactions and delayed consequences.
