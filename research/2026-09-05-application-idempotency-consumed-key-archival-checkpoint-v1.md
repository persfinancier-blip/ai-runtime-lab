# Application idempotency consumed-key archival/checkpoint contract V1

Status: `APPLICATION_IDEMPOTENCY_CONSUMED_KEY_ARCHIVAL_CHECKPOINT_V1_FROZEN`

Date: 2026-09-05

Scope: LAB-093 / #178 follow-up to the durable worker request/effect registry, cross-session application idempotency, authenticated installation/retention, and bounded-growth/resource-exhaustion contracts.

## Question

Can the application-idempotency subsystem compact historical consumed keys while preserving the V1 safety property that a key which has ever authorized an effect can never later become `MISS` and authorize a second effect?

## Executive decision

Yes, but only under a deliberately asymmetric correctness contract:

1. **False negatives are forbidden.** A historically consumed key MUST never be classified as definitely unseen.
2. **False positives may be admitted only as availability loss.** An unseen key may be conservatively classified `MAYBE_CONSUMED` and rejected/routed to exact archival lookup; it must never be allowed to execute merely because compact state is uncertain.
3. **A bounded probabilistic summary cannot preserve useful availability forever for an unbounded stream.** A fixed-size Bloom-style summary can retain the no-false-negative safety direction, but its false-positive rate tends toward 1 as inserted cardinality grows. Therefore V1 does not claim infinite admission with fixed active storage.
4. **Compaction is not deletion of authority evidence.** Exact historical evidence must remain recoverable from an authenticated archival tier, or the active tier must fail closed on every positive/uncertain query. A digest/checkpoint alone is not an exact membership oracle.
5. **No archive/checkpoint operation can make a consumed key reusable.** Epoch rotation, compaction, filter rebuild, archive loss, retention, restore, and policy change all preserve a monotonic consumed-key namespace.

The preferred V1 architecture is therefore a two-tier authenticated design:

- a small active exact registry for recent/live `BOUND`, `PREPARED`, `UNKNOWN`, `COMMITTED`, and recently tombstoned keys;
- immutable sealed archival epochs containing exact consumed-key records (or an exact queryable representation), each committed by an authenticated checkpoint in the global provenance chain;
- an optional false-positive-only approximate membership summary over sealed epochs as a *negative accelerator*, never as sole positive authority.

If exact archival lookup is unavailable, `MAYBE_CONSUMED` fails closed. The system may lose availability, but it must not create a second effect.

## Why exact bounded storage is impossible for arbitrary unbounded keys

For an unbounded namespace of arbitrary application keys, exact membership in an ever-growing consumed set carries monotonically increasing information. A fixed finite state machine has finitely many internal states, while the number of possible historical consumed sets grows without bound. Eventually distinct histories must map to the same compact state; an exact query cannot distinguish them. Therefore a permanently bounded exact representation cannot provide both:

- zero false negatives for every consumed key; and
- zero false positives for every never-consumed key;

for an unbounded insertion stream.

V1 therefore makes the safety/availability asymmetry explicit instead of hiding it behind retention.

## Donor mechanisms and evidence

### Bloom filters

Bloom filters are a canonical approximate-membership structure: they are compact, may produce false positives, and in their ordinary insertion-only form do not produce false negatives. That direction is exactly the only probabilistic error V1 can safely tolerate.

Primary/technical references:

- NIST publication: Ken Christensen, Allen Roginsky, Miguel Jimeno, *A New Analysis of the False-Positive Rate of a Bloom Filter* — https://www.nist.gov/publications/new-analysis-false-positive-rate-bloom-filter
- Kirsch & Mitzenmacher, *Less Hashing, Same Performance: Building a Better Bloom Filter* — https://doi.org/10.1002/rsa.20208

Important limitation: for fixed `m` bits and increasing inserted cardinality `n`, the false-positive probability rises; a saturated filter eventually answers positive for essentially everything. This preserves no-false-negative safety but destroys useful admission availability.

### Counting/deletable filters

Counting Bloom filters and cuckoo-filter families support deletion, but deletion is not a safe primitive for the permanent consumed-key safety set unless an independently authenticated exact record proves that the key remains consumed elsewhere. Accidental/unauthorized deletion could create a false negative and therefore a duplicate side effect.

V1 consequently forbids using approximate-filter deletion as retention authority.

### Authenticated checkpoints / Merkle-style commitments

A cryptographic root can authenticate a large immutable archive and make tampering detectable, but a root alone does not answer arbitrary membership queries. Exact membership still requires the archived data, an authenticated index, or a supplied membership proof. A checkpoint is therefore an integrity anchor, not a substitute for the historical membership information itself.

The lab's existing parent-linked authenticated provenance chain is the natural authority surface for archive-epoch checkpoints; V1 must not introduce an independent locally valid history island.

## Data model

### 1. Active exact registry

Contains all nonterminal operations and a bounded recent terminal window. At minimum:

- canonical application namespace/principal;
- canonical application key digest;
- canonical operation identity digest;
- status: `BOUND | PREPARED | UNKNOWN | COMMITTED | TOMBSTONED`;
- exact LAB-080 request binding when effectful;
- exact provenance transition binding;
- immutable result digest / result-retention state where applicable;
- archive epoch id once sealed.

`PREPARED` and `UNKNOWN` MUST NOT be archived away from the recovery executor's exact lookup surface.

### 2. Sealed exact archive epoch

An epoch is immutable after seal. Canonical epoch identity commits to at least:

- `archive_epoch_id`;
- logical database/history identity;
- application-idempotency registry schema/version;
- first and last canonical record ordering keys;
- exact record count;
- digest/root of exact canonical records;
- previous archive checkpoint digest;
- capacity/retention policy version;
- creation/seal provenance parent;
- optional approximate-summary digest and parameters.

The exact archive can live outside the hot SQLite rows, but startup/recovery must know how to authenticate and query it. Archive location is not authority; the authenticated checkpoint/root is.

### 3. Approximate historical summary

Optional. It is an optimization only.

Allowed response classes:

- `DEFINITELY_NOT_IN_SUMMARY`: safe only if the summary construction/version is authenticated, complete for all sealed epochs it claims, and the queried key is also absent from active exact state;
- `MAYBE_CONSUMED`: never authorizes a new effect. Perform exact archive lookup or fail closed.

There is deliberately no `DEFINITELY_CONSUMED` claim based solely on a probabilistic filter; positive results may be false positives.

## Canonical query algorithm

Given `(principal, namespace, application_key, operation_identity)`:

1. Authenticate startup state, registry installation provenance, current archive checkpoint chain, and active exact registry.
2. Query active exact registry first.
   - Exact same key + same operation: converge to its current/terminal state.
   - Exact same key + different operation: `APPLICATION_KEY_CONFLICT`.
3. If absent active, evaluate every authenticated compact summary that claims coverage of sealed history, or a canonical merged summary whose checkpoint proves complete coverage.
4. If any summary says `MAYBE_CONSUMED`, perform authenticated exact archive lookup.
   - exact same operation -> historical convergence/result semantics;
   - different operation -> conflict;
   - no exact match after authenticated complete lookup -> false positive; admission may continue only after the lookup's snapshot/preconditions are revalidated.
5. Only if active exact state is absent **and** the authenticated historical mechanism proves absence under the configured safety contract may a new `BOUND` be admitted.
6. Revalidate the absence proof/preconditions inside the final broker-authorized admission transaction before binding the key.

If archive lookup or checkpoint authentication is unavailable/UNKNOWN, return a retryable/fatal fail-closed classification; never degrade to `MISS`.

## Compaction protocol

Compaction is a broker-admin operation, not worker authority.

1. Select only terminal records eligible under authenticated policy. `BOUND`, `PREPARED`, and `UNKNOWN` are ineligible.
2. Under sole-writer authorization, canonicalize selected exact records and construct a new immutable archive epoch.
3. Compute the exact archive root/digest and optional approximate summary from the same canonical record set.
4. Verify locally that every selected key tests non-negative in the candidate summary. This is a construction check, not proof of future integrity.
5. Durably install/archive the exact epoch and obtain its authenticated storage identity if the archive tier requires one.
6. Append a parent-linked `APPLICATION_IDEMPOTENCY_ARCHIVE_EPOCH_SEALED` transition to the existing global provenance chain. The transition binds the archive root, record count/range, previous checkpoint, summary digest/parameters, policy version, and logical DB/history identity.
7. Re-authenticate the newly appended checkpoint and exact archive before deleting hot terminal payload/rows.
8. Replace hot terminal rows only with the minimum exact metadata needed by the active registry/checkpoint accounting. A key cannot become unrepresented between archive seal and hot-row reclamation.
9. On any crash before authenticated seal, retain/reconstruct the original hot exact records; do not infer that archive installation succeeded merely from files being present.
10. On crash after seal but before hot cleanup, duplicates across hot/archive are benign and must converge by exact identity.

The authority ordering is **archive exact data -> authenticated checkpoint -> re-authentication -> hot cleanup**, never cleanup first.

## Checkpoint chaining and rollback resistance

Each archive checkpoint is parent-linked into the same global provenance chain already frozen for LAB-090/LAB-092/LAB-097..100 work. Startup verifies:

- checkpoint chain continuity;
- monotonic epoch numbering;
- non-overlapping/canonical record ranges or another unambiguous coverage scheme;
- cumulative record count/accounting;
- logical database/history identity;
- policy/schema versions;
- exact archive root availability/integrity where required;
- approximate summary digest and parameters;
- no unexplained disappearance of an epoch previously authenticated.

Deleting the newest checkpoint, substituting an older checkpoint set, or rebuilding a smaller filter from a subset of history is rollback/tamper and fails closed.

## False-positive-only structures: allowed and forbidden uses

### Allowed

- negative acceleration before exact archival lookup;
- conservative duplicate suppression where a false positive merely rejects/delays a genuinely new operation;
- sealed immutable insertion-only summaries whose completeness is authenticated;
- multiple immutable epoch summaries, provided all required epochs remain covered and query logic cannot skip one.

### Forbidden

- treating a probabilistic positive as proof of the exact historical operation/result without exact evidence;
- deleting elements from the safety summary because a result payload was tombstoned;
- rebuilding from a lossy subset and treating negatives as authoritative;
- resetting/salting hash parameters without an authenticated full rebuild from exact history;
- allowing summary corruption/unavailability to fall back to `MISS`;
- using an adaptive/deletable filter where query-driven mutation can remove a genuine consumed-key indication;
- accepting a filter's claimed `n`, bitset, hash seed, or epoch coverage as self-authenticating.

## Saturation and bounded active storage

A fixed Bloom-style summary has bounded bytes but not bounded useful lifetime. V1 defines authenticated saturation thresholds:

- each summary has immutable parameters and an admitted maximum inserted cardinality/estimated false-positive ceiling;
- once a summary reaches its policy ceiling, no further keys are inserted into that summary;
- a new sealed epoch/summary may be created only if policy permits another archive object;
- if total allowed archive summaries/checkpoints or exact archive capacity is exhausted, unseen-key admission stops fail-closed;
- merging summaries is allowed only by rebuilding from authenticated exact union data and producing a new parent-linked checkpoint; bitwise tricks that are not proven equivalent to the canonical construction are not authority operations.

Thus compaction can bound **hot** storage and reclaim result bytes, but cannot magically provide infinite useful idempotency capacity in fixed total storage.

## Archive availability modes

V1 permits three deployment modes, each explicit in policy:

### A. Exact archive online

Approximate summary negative -> continue; positive -> exact lookup. Best availability.

### B. Exact archive cold/offline but retrievable

Positive/uncertain -> `PENDING_ARCHIVE_LOOKUP`; no effect until exact authenticated lookup completes. Higher latency, same safety.

### C. Summary-only emergency mode

Negative may authorize further admission only if the summary is authenticated, proven complete for its checkpoint coverage, and active exact state is clean. Positive always rejects. Availability degrades according to false-positive rate; no exact historical result redelivery is possible. This mode must be explicitly policy-authorized and cannot pretend a positive identifies a specific prior operation.

If summary integrity/completeness itself is uncertain, all unseen admissions fail closed.

## Crash consistency

Required crash windows:

1. archive bytes written, no checkpoint -> hot rows remain authority;
2. checkpoint PREPARED/UNKNOWN -> broker recovery owns exact transition; no cleanup;
3. checkpoint COMMITTED, hot cleanup not started -> duplicate exact representation accepted;
4. partial hot cleanup -> startup authenticates checkpoint/archive and deterministically resumes cleanup; never reconstructs `MISS` from missing hot rows alone;
5. approximate summary written but exact archive/root mismatch -> fail closed;
6. exact archive available but summary missing/corrupt -> exact lookup may preserve availability if policy allows; never silently rebuild without authenticated transition;
7. restored DB with older active rows/checkpoint head -> provenance rollback detection before admission.

## Security considerations

### Adversarial false-positive amplification

An attacker may deliberately search for keys that collide in an approximate filter, turning safety-preserving false positives into denial of service. Therefore:

- filter parameters/seeds are broker-private or otherwise not unnecessarily exposed;
- per-principal/namespace admission quotas from the bounded-growth contract remain in force;
- false-positive rate is telemetry, not a correctness assumption;
- a positive never causes an effect, only lookup/rejection;
- repeated false-positive pressure cannot authorize filter deletion/reset.

### Hash collision vs application-key identity

Approximate-filter hashes are not the canonical application-key identity. Exact archive records bind a cryptographic canonical key digest and operation identity. Filter collisions therefore affect only availability.

### Archive substitution

Archive object names/paths are locators, not trust anchors. Root/digest, epoch identity, logical DB identity and parent-linked provenance are authoritative.

## RED-first matrix

Before production implementation, at minimum execute the following categories against exact source.

### Basic archival
1. terminal COMMITTED key archives and remains consumed;
2. TOMBSTONED key archives and remains consumed;
3. same key/same operation converges after hot-row deletion;
4. same key/different operation conflicts after hot-row deletion;
5. never-seen key remains admissible after authenticated negative proof.

### No false negatives
6. delete one bit / corrupt summary -> fail closed, not MISS;
7. rebuild summary omitting one consumed key -> startup rejects via checkpoint/digest;
8. omit one archive epoch from query coverage -> startup/query rejects;
9. rollback to older summary/checkpoint -> rejected;
10. change hash seed/parameters without authenticated rebuild -> rejected.

### False positives
11. deliberately generate summary false positive -> no effect before exact lookup;
12. exact archive disproves false positive -> admission may resume after revalidation;
13. archive offline on false positive -> fail closed/PENDING, no effect;
14. summary-only mode false positive -> reject new work, no effect;
15. repeated false positives cannot mutate/reset summary.

### Ineligible states
16. BOUND cannot archive;
17. PREPARED cannot archive;
18. UNKNOWN cannot archive;
19. recovery-owned request cannot be detached from exact LAB-080 binding;
20. concurrent completion during compaction causes stale-plan rejection/replan.

### Crash windows
21. crash before archive durable -> hot state intact;
22. crash after archive write before checkpoint -> hot authority intact;
23. UNKNOWN checkpoint append -> no cleanup;
24. committed checkpoint before cleanup -> duplicate representation converges;
25. partial cleanup -> restart re-authenticates and completes without MISS.

### Tamper/deletion
26. delete exact archive with checkpoint present -> fail closed for affected queries/startup according to policy;
27. substitute archive contents under same locator -> digest mismatch;
28. delete checkpoint but leave archive -> rollback/unproven archive rejected;
29. delete hot rows before checkpoint -> provenance/accounting mismatch;
30. alter epoch record count/range -> rejected.

### Saturation/capacity
31. summary below ceiling accepts seal;
32. summary at ceiling rejects further insertion to same epoch;
33. new epoch allocation obeys authenticated capacity policy;
34. total archive capacity exhaustion rejects unseen keys before BOUND;
35. existing-key retry still converges at exhaustion;
36. saturation cannot trigger historical key eviction;
37. tombstoning result bytes does not refund consumed-key membership.

### Concurrency
38. two compactors race -> one authenticated parent wins; loser stale;
39. compactor vs new admission -> exact boundary prevents skipped key;
40. compactor vs terminal transition -> only stable canonical record version archives;
41. two brokers reading different snapshots cannot each seal conflicting epoch under same parent.

### Cross-session/application semantics
42. new worker session discovers archived COMMITTED result only after current disclosure authorization;
43. old session is not resurrected by archive lookup;
44. archived UNKNOWN remains impossible because UNKNOWN is ineligible;
45. archived result redelivery performs no provider call/new LAB-080 request/provenance effect transition.

### Authority
46. worker cannot invoke compaction;
47. storage pressure alone cannot invoke compaction authority;
48. stale retention/capacity policy cannot seal epoch;
49. logical DB/history mismatch rejects imported archive;
50. independent locally-valid archive chain is rejected.

### Exactness/audit
51. canonical serialization round-trip is byte-stable;
52. archive root covers exact key+operation+terminal identity fields;
53. approximate-summary digest covers exact parameters/seed/version;
54. exact archive lookup distinguishes filter collision from true membership;
55. filter positive cannot fabricate result payload;
56. filter negative is never trusted when checkpoint coverage is incomplete;
57. restored older DB cannot skip newer archived epochs;
58. archive index corruption cannot return false absence without authenticated detection;
59. process/sole-writer boundary prevents direct archive mutation by workers;
60. full restart reconstructs active + sealed coverage before delegation.

## V1 non-goals

- No claim of infinite exact idempotency in fixed total storage.
- No production approximate-filter implementation before executable RED/GREEN is available.
- No requirement to use Bloom filters specifically; any structure must satisfy the one-sided error and authenticated-completeness contract.
- No deletion/reuse of historical application keys.
- No independent archive provenance chain.
- No weakening of LAB-080 exact request identity, broker recovery ownership, LAB-087 sole-writer boundary, LAB-090/LAB-100 activation authority, or LAB-093 session/effect-boundary checks.

## Decision summary

`APPLICATION_IDEMPOTENCY_CONSUMED_KEY_ARCHIVAL_CHECKPOINT_V1_FROZEN`:

- compaction may reduce hot exact state and result payload bytes;
- exact consumed-key history remains logically monotonic forever;
- authenticated approximate summaries may have false positives but MUST have no false negatives for the history they claim to cover;
- positives never authorize effects; they trigger exact lookup or fail closed;
- checkpoint/root authenticates archive integrity but is not itself an exact membership oracle;
- fixed bounded summaries eventually saturate, so bounded total storage implies eventual admission exhaustion rather than unsafe key reuse;
- archive sealing is parent-linked into the existing global provenance chain and must complete before hot cleanup;
- archive loss, filter corruption, rollback, incomplete coverage, or UNKNOWN can reduce availability but can never turn a historical consumed key into `MISS`.

## Exact next research question

If LAB-086 executable composition remains unavailable, freeze the **archive object identity/availability and authenticated retrieval protocol**: locator-vs-authority semantics, exact archive manifest/index format, multi-copy/remote retrieval, proof of complete negative lookup, archive-loss classifications, restore/rebuild authority, and how cold archival availability composes with startup/delegation without allowing an unavailable epoch to be silently skipped.
