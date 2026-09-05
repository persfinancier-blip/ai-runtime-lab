# Observer evidence durability / bounded queue / recovery-journal contract v1

Status: `OBSERVER_EVIDENCE_DURABILITY_BOUNDED_QUEUE_RECOVERY_JOURNAL_V1_FROZEN`

Date: 2026-09-05

Scope: LAB-093 follow-up under #178. This is a design/evidence contract only. No production observer implementation or behavioral PASS is claimed.

## Problem

The prior transport-observer contract requires a durable `SINK_ENTERED` fact to be committed before the first forwarding-capable transport sink and requires all SQL locks/transactions to be released before network I/O. That closes the crash-after-I/O-before-observation gap, but it creates a harder durability problem:

- SQLite can be busy because there is only one writer at a time;
- the disk can be full or return an I/O error;
- a process can crash between enqueue, journal append, SQLite commit, callback and checkpoint;
- multiple processes can attempt to record evidence concurrently;
- an in-memory queue can overflow;
- a post-call observer callback must not block or deadlock the provider path;
- evidence loss must never be reinterpreted as evidence that no I/O occurred.

The contract below separates the **pre-I/O authority barrier** from best-effort post-I/O enrichment and makes loss/ambiguity monotone: missing evidence can only reduce certainty, never increase permission.

## Frozen invariants

### I1. `SINK_ENTERED` is a synchronous durable barrier, not an asynchronous queue event

Before entering a forwarding-capable sink, the process must synchronously establish a durable append for the exact transport attempt:

`attempt_id -> SINK_ENTERED(sequence, authority_generation, request_digest, observer_profile, process_instance)`

The external I/O call is forbidden until that append has returned a committed/durable result according to the admitted persistence profile.

A queue may be used for later observations, but **not** to defer `SINK_ENTERED` durability. If the barrier cannot be made durable within the bounded admission budget, the attempt fails closed **before** I/O.

### I2. No SQL transaction or provider/pool lock spans network I/O

The persistence barrier transaction must commit and release all DB locks before the provider call. Observer callbacks must not synchronously reacquire adapter/pool locks or wait on a queue consumer that may itself require those locks.

This prevents a safety mechanism from creating a provider-path deadlock.

### I3. SQLite profile is explicit and admission-bound

The admitted local durable profile is:

- same-host local filesystem only for WAL mode;
- `journal_mode=WAL` where supported and proven for the deployment filesystem;
- `synchronous=FULL` for evidence whose survival across OS/power failure is part of the claimed guarantee;
- explicit bounded busy handling;
- a separately controlled checkpoint policy;
- startup verification of actual pragmas/VFS/topology before authority is admitted.

`WAL + synchronous=NORMAL` is not sufficient for a claim that the newest evidence transaction survives power loss. SQLite documents that FULL in WAL adds a WAL sync after each commit and provides ACID durability, while NORMAL may lose recent transactions after power loss. WAL also allows only one writer at a time and requires all clients to be on the same host because the wal-index uses shared memory.

### I4. `SQLITE_BUSY` is not retried without bound

Contention is handled by a finite observer-barrier budget. A busy handler/timeout may sleep and retry only up to that configured bound.

If `SINK_ENTERED` cannot commit inside the budget, the network attempt is not started. The caller receives a local `EVIDENCE_BARRIER_UNAVAILABLE` / `FAILED_BEFORE_IO` class whose proof includes that sink entry never happened.

Post-I/O enrichment may use an independent bounded retry/queue policy, but exhaustion cannot downgrade an already-started attempt from `UNKNOWN`.

### I5. Disk-full / I/O error is fail-closed before sink entry

`SQLITE_FULL`, `SQLITE_IOERR`, failed fsync/xSync, journal corruption, or inability to extend the durable evidence store before `SINK_ENTERED` are authority failures. The provider call is forbidden.

No fallback to volatile memory is allowed for the pre-I/O barrier. "We put it in RAM" is not equivalent evidence.

### I6. Post-call observations are monotone enrichment

Evidence after `SINK_ENTERED`—partial write observations, protocol reset, authenticated not-processed proof, response headers/body, completion—is appended as immutable child records.

If a post-I/O event cannot be persisted because of crash, disk-full, contention or queue overflow, the durable state remains at least `SINK_ENTERED`, hence `UNKNOWN` unless an already durable protocol-certified non-processing proof exists.

Loss of enrichment must never produce `FAILED_BEFORE_IO`.

### I7. Bounded queue is permitted only after the durable barrier

A bounded MPSC queue may decouple network callbacks from durable enrichment writes. Each item carries exact attempt identity and a monotonically increasing local observation ordinal.

Queue overflow behavior is fixed:

- never block while holding transport/provider locks;
- never evict or overwrite an earlier record silently;
- append/mark an explicit durable `OBSERVATION_GAP` when possible;
- if that gap marker itself cannot be persisted, startup/recovery treats the attempt as having incomplete evidence and remains `UNKNOWN`;
- overflow can trigger quarantine/admission shutdown for new consequential sends, but cannot rewrite prior evidence.

### I8. Recovery journal is append-only and independently framed

If a dedicated recovery journal is used ahead of SQLite, every record has:

- magic/version/domain separator;
- attempt id;
- record type;
- monotonic sequence/ordinal;
- exact payload length;
- payload digest;
- previous-record digest or segment-chain link;
- checksum/MAC/signature as required by the retained authority design;
- commit marker/framing sufficient to distinguish complete from torn tail records.

Recovery scans only through the last fully validated record. A torn or incomplete tail is discarded as an incomplete tail, never interpreted as a committed negative fact.

A recovery journal does **not** create an independent authority island. Its accepted records must bind into the same global provenance/authority generations frozen for LAB-090..100.

### I9. Journal-to-SQL replay is idempotent

Each evidence record has a stable content identity, e.g. `(attempt_id, record_type, ordinal, digest)`. Replaying an already materialized record is a no-op after equality verification. A conflicting same-identity/different-content record is corruption and fails closed.

Recovery order is:

1. validate store/provenance/profile;
2. parse journal to last valid committed frame;
3. replay missing records idempotently into SQL;
4. verify SQL/journal agreement for overlapping identities;
5. classify incomplete attempts conservatively;
6. only then consider admitting new consequential authority.

### I10. Multi-process writers must serialize the pre-I/O barrier explicitly

SQLite WAL still has a single writer. Multiple worker processes therefore need either:

- a short SQLite transaction with finite busy handling and no outer process-global critical section spanning I/O; or
- an admitted single local evidence-writer service/process with a durable request/ack protocol whose ACK means the record itself is durable, not merely queued.

If a writer daemon is used, process death after receipt but before durable append must not emit an ACK. Clients that lose the writer connection without an ACK fail closed before I/O.

### I11. ACK semantics are precise

For `SINK_ENTERED`, ACK means: the exact framed record has crossed the configured durability boundary and can be recovered after the failure classes claimed by the profile.

ACK must not mean:

- accepted into an in-memory queue;
- copied into a userspace buffer;
- submitted to another thread;
- SQLite statement stepped but transaction not committed;
- WAL commit returned under a weaker-than-declared synchronous mode;
- journal write returned without required sync when power-loss durability is claimed.

### I12. Checkpointing cannot weaken commit semantics

WAL checkpoint scheduling is a performance/recovery concern, not the definition of whether the latest `SINK_ENTERED` commit exists. Automatic checkpoints may be disabled or moved off the provider thread to avoid latency spikes, but WAL growth must be bounded and monitored.

If checkpoint starvation, disk pressure or WAL growth threatens the configured reserve required for future durable barriers, new consequential sends are quarantined before reserve exhaustion.

### I13. Capacity reserve is safety state

The evidence subsystem maintains a minimum reserved capacity budget sufficient for at least:

- one `SINK_ENTERED` barrier;
- one ambiguity/gap marker;
- one shutdown/quarantine marker;
- recovery metadata.

Crossing a high-water threshold disables admission of new consequential sends while allowing read-only recovery/reconciliation. The system must not wait until ENOSPC to discover that it can no longer record safety evidence.

### I14. Recovery cannot manufacture certainty from absence

On restart:

- durable `SINK_ENTERED` with no terminal evidence => `UNKNOWN`;
- journal tail corruption after a valid `SINK_ENTERED` => `UNKNOWN`;
- queue loss suspected after `SINK_ENTERED` => `UNKNOWN`;
- process died before durable `SINK_ENTERED` ACK and admission code proves sink call was not reached => `FAILED_BEFORE_IO`;
- absence of post-call evidence alone is never proof of no I/O.

### I15. Evidence store failure propagates to authority admission

The observer evidence subsystem is part of the effective-authority dependency manifest. If startup cannot prove its durability profile, schema/version, journal continuity, free-space reserve, writer topology or recovery completion, affected `SEND/MUTATE/RESUME/TOKEN_MINT` authority is withheld.

Read-only reconciliation may remain available if independently safe.

## State machine

Minimum durable states for one transport attempt:

`ALLOCATED`

→ `SINK_ENTERED_DURABLE`

→ zero or more `OBSERVED_*`

→ one of:

- `CERTIFIED_NOT_PROCESSED`
- `PROVIDER_CONFIRMED`
- `FAILED_AFTER_SINK_UNKNOWN`
- `EVIDENCE_GAP_UNKNOWN`

A separate pre-sink terminal state is permitted:

`EVIDENCE_BARRIER_UNAVAILABLE_FAILED_BEFORE_IO`

There is no transition from any durable post-`SINK_ENTERED` state back to `FAILED_BEFORE_IO`.

## Bounded queue design

Suggested implementation boundary for later RED/GREEN work:

- network callback performs only fixed-size allocation/copy of already-bounded metadata, non-blocking enqueue, and return;
- queue capacity is fixed and observable;
- a dedicated evidence consumer persists batches outside provider locks;
- batch transactions are bounded by record count/time;
- queue depth/high-water marks feed new-send admission;
- consumer failure trips quarantine for new sends;
- overflow records are explicit ambiguity evidence, not silently dropped metrics.

Large provider bodies must not be copied into this queue. Store digests, bounded status metadata and references to already-authenticated artifacts instead.

## Recovery-journal choice

Two safe implementation profiles remain admissible for later experimentation:

### Profile A — SQLite-only pre-I/O barrier

Use a minimal `BEGIN IMMEDIATE`/insert/commit transaction for `SINK_ENTERED`, WAL+FULL on a proven local filesystem, finite busy timeout, then release the connection/transaction before network I/O. Post-call observations may be queued.

Advantages: one durable store, simplest reconciliation.

Risk: writer contention and fsync latency occur on the pre-I/O path.

### Profile B — dedicated append-only journal + asynchronous SQL materialization

The pre-I/O barrier appends and synchronizes one framed record to a local append-only journal, then releases the journal lock before network I/O. SQLite is a materialized index/view rebuilt/reconciled from the journal.

Advantages: short sequential critical section; avoids SQLite writer contention on the absolute barrier.

Risks: requires exact torn-write framing, fsync semantics, segment rotation, free-space reservation, journal/SQL reconciliation and global-provenance binding. It must be proven, not assumed, to be safer/faster.

No profile is selected for production until the fault matrix is executable.

## RED-first fault matrix

Freeze at least the following 64 cases before implementation is admitted.

### A. Barrier ordering and lock discipline (8)
1. sink call cannot execute before durable barrier ACK;
2. exception before barrier => no `SINK_ENTERED`;
3. DB transaction is closed before sink call;
4. provider/pool lock is not held while waiting for DB durability;
5. crash immediately after barrier commit before sink => restart classifies conservatively, not as provider-confirmed;
6. crash on first instruction inside sink => `SINK_ENTERED` survives;
7. callback cannot recursively enter provider send;
8. observer failure cannot bypass authority gate.

### B. SQLite contention (8)
9. one competing writer clears inside budget;
10. contention exceeds budget => fail before I/O;
11. multi-process simultaneous barriers serialize correctly;
12. busy handler is finite;
13. no busy-spin CPU loop;
14. writer crash releases lock and surviving writer recovers;
15. long reader under WAL does not invalidate barrier semantics;
16. checkpoint contention cannot silently drop a barrier.

### C. Disk / fsync / corruption (8)
17. ENOSPC before barrier => no I/O;
18. ENOSPC after barrier during enrichment => UNKNOWN;
19. injected xSync/fsync failure => no barrier ACK;
20. SQLite IOERR before barrier => no I/O;
21. corrupted WAL/journal on restart => fail closed;
22. torn final journal frame ignored as incomplete tail;
23. complete prior frame survives torn successor;
24. low-space reserve triggers preemptive quarantine.

### D. Queue semantics (8)
25. normal enqueue/drain preserves order per attempt;
26. queue full does not block under transport lock;
27. overflow never overwrites unconsumed evidence silently;
28. overflow after `SINK_ENTERED` => UNKNOWN/gap;
29. consumer crash leaves durable barrier intact;
30. consumer restart replays idempotently;
31. duplicate queued record is no-op after equality check;
32. conflicting duplicate is corruption.

### E. Multi-process / writer service (8)
33. two workers same attempt cannot create conflicting ordinals;
34. writer daemon ACK only after durable append;
35. daemon dies before append => no ACK/no I/O;
36. daemon dies after append before ACK => caller fails closed; restart recovers durable barrier;
37. duplicate client retry of barrier request is idempotent;
38. stale process generation cannot append to new epoch;
39. socket/IPC reconnect does not imply durable ACK;
40. writer service cannot initiate provider I/O.

### F. Recovery journal (8)
41. clean replay into empty SQL;
42. partial replay resumes idempotently;
43. SQL has matching record => no-op;
44. SQL same identity/different digest => fail closed;
45. broken prev-digest chain => fail closed;
46. segment rotation preserves chain/provenance;
47. missing middle segment => fail closed;
48. journal from wrong authority epoch rejected.

### G. Restart classification (8)
49. no barrier + proven pre-sink crash => FAILED_BEFORE_IO;
50. barrier only => UNKNOWN;
51. barrier + partial-write evidence => UNKNOWN;
52. barrier + certified-not-processed => eligible for that narrow classification;
53. barrier + provider-confirmed => committed/confirmed;
54. missing callback after barrier => UNKNOWN;
55. evidence gap after barrier => UNKNOWN;
56. restart never infers negative evidence from missing rows alone.

### H. Admission / capacity / topology (8)
57. WAL on unsupported/network filesystem rejected;
58. synchronous mode drift rejected;
59. schema/profile version drift rejected;
60. insufficient free-space reserve rejects new sends;
61. queue high-water can quarantine new sends while reads continue;
62. observer profile mismatch rejects consequential authority;
63. recovery incomplete rejects new sends;
64. full clean recovery + profile proof permits only the authority otherwise allowed by the parent contracts.

## Donors / evidence

Primary sources consulted on 2026-09-05:

1. SQLite WAL documentation: WAL appends commit records; readers and a writer may coexist, but there is only one writer at a time; WAL requires same-host shared memory; FULL synchronous adds a WAL sync after every transaction commit, while NORMAL may lose recent transactions after power loss. https://sqlite.org/wal.html
2. SQLite PRAGMA synchronous documentation: FULL/EXTRA durability properties and the distinction between WAL FULL and WAL NORMAL. https://sqlite.org/pragma.html#pragma_synchronous
3. SQLite `sqlite3_busy_timeout`: the busy handler sleeps/retries only for a bounded accumulated interval, then returns SQLITE_BUSY. https://sqlite.org/c3ref/busy_timeout.html
4. SQLite atomic-commit design notes: recovery must distinguish complete journal state from incomplete/torn state and relies on sync/order assumptions of the VFS/filesystem. https://sqlite.org/atomiccommit.html

## Decision

Freeze `OBSERVER_EVIDENCE_DURABILITY_BOUNDED_QUEUE_RECOVERY_JOURNAL_V1_FROZEN`.

The most important safety boundary is now explicit: **pre-I/O `SINK_ENTERED` durability is synchronous and mandatory; post-I/O observation durability may be decoupled, but any loss only increases ambiguity.** Queueing, lock contention, disk pressure and process failure are therefore availability concerns until they threaten evidence durability, at which point consequential authority is removed rather than silently weakened.

## Next distinct evidence task

If LAB-086 exact execution remains unavailable, freeze a **durable evidence-store capacity reservation / compaction / archival continuity contract**: segment/checkpoint/compaction rules, retention versus replay needs, authenticated archival and restore, disk-reserve accounting, safe deletion proofs, WAL/journal truncation, evidence pinning for unresolved UNKNOWN/manual-resolution cases, and a RED-first crash/space-amplification matrix. Production observer code remains blocked on executable RED/GREEN.