# Log-to-subject-index derivation completeness / skipped-leaf fraud-proof / mapper checkpoint — v1 frozen

Status: `LOG_TO_SUBJECT_INDEX_DERIVATION_COMPLETENESS_SKIPPED_LEAF_FRAUD_PROOF_MAPPER_CHECKPOINT_V1_FROZEN`

Date: 2026-09-06

Scope: LAB-093 trust-frontier/non-inclusion follow-up. Design and RED contract only; no production mapper/prover/index implementation or behavioral compatibility PASS is claimed.

## Problem

The prior `PUBLICATION_PROMISE_FULFILLMENT_VERIFIABLE_NON_INCLUSION_SUBJECT_INDEX_COMPLETENESS_V1_FROZEN` contract correctly requires a derived subject index to be cryptographically bound to the append-only source-log frontier. That is necessary but not sufficient.

A malicious or defective mapper can consume source log frontier `L_N`, silently omit one eligible source leaf, produce a perfectly valid sparse-map root `M_N`, sign the pair `(L_N, M_N)`, and later return a valid sparse-map non-inclusion proof for the omitted subject. Every individual Merkle proof can verify while the derived index is incomplete.

Therefore the authority question is not merely whether `M_N` is signed and linked to `L_N`; it is whether a verifier can establish that **every eligible source leaf in the exact append-only interval was interpreted exactly once under the bound mapper semantics and that the resulting deterministic state transition produced `M_N`**.

This contract freezes that derivation-completeness boundary.

## Primary donor mechanisms

### IETF Key Transparency combined tree and auditor updates

The July 2026 Key Transparency protocol draft combines a searchable prefix tree with an append-only log tree. Each prefix-tree change yields a new root which is stored in the log tree. Its auditor protocol receives explicit `added` / `removed` sets plus proofs against the previous prefix-tree state and verifies ordering and transition semantics rather than trusting a fresh root in isolation.

Reference: https://datatracker.ietf.org/doc/draft-ietf-keytrans-protocol/

The June 2026 architecture draft explicitly describes third-party auditors as authenticating that a tree was constructed correctly; asynchronous auditor signatures may lag, but their admissible lag is configuration-bound.

Reference: https://datatracker.ietf.org/doc/draft-ietf-keytrans-architecture/

### Google Key Transparency

Google Key Transparency separates a sparse Merkle map from an append-only log of map roots. Client verification covers the sparse-tree proof, signed map head, append-only log tree head/consistency, and inclusion of the signed map head in the log. This is a useful donor for binding searchable state revisions into append-only history, while this LAB contract adds an explicit requirement to prove source-leaf-to-map derivation completeness.

References:
- https://github.com/google/keytransparency
- https://github.com/google/keytransparency/blob/master/docs/design.md

### Trillian / transparency ecosystem

Trillian distinguishes append-only Log mode from sparse Map semantics and requires application-specific personalities for admission/canonicalization. The Trillian examples repository includes independent log cloning/auditing patterns (for example SumDB verification) that reinforce the rule that an auditor may independently consume authenticated source history instead of trusting a derived service's claims.

References:
- https://github.com/google/trillian
- https://github.com/google/trillian-examples

## Frozen decisions

### 1. A signed `(log_root, map_root)` pair is not derivation-completeness evidence

A mapper checkpoint signature proves only that the signer asserted the pair. It does not prove that all eligible source leaves were processed, that no leaf was processed twice, or that the correct mapper generation was used.

Consequential non-inclusion/omission adjudication therefore rejects checkpoints that lack policy-approved derivation evidence.

### 2. Source intervals are explicit and contiguous

Each mapper transition is defined over a half-open source interval:

`(source_from_size, source_to_size]`

and binds:

- previous authenticated source-log checkpoint;
- target authenticated source-log checkpoint;
- exact source tree sizes/roots;
- previous derived-map revision/root;
- target derived-map revision/root;
- mapper generation;
- source schema/admission generation set;
- subject canonicalizer/key generation;
- duplicate/retry/collision/tombstone policy;
- deterministic update-order rule;
- hash/domain-separation generations.

A mapper cannot claim `source_to_size = N` after reading a non-contiguous subset of leaves.

### 3. Every source position receives a deterministic disposition

For every source leaf position in the committed interval the mapper emits exactly one canonical disposition:

- `APPLY(subject_key, operation_digest)`;
- `NOOP_DUPLICATE(canonical_event_id)`;
- `NOOP_POLICY_IRRELEVANT(reason_code)`;
- `REJECT_UNSUPPORTED_SCHEMA(schema_generation)`;
- `TOMBSTONE(subject_key, operation_digest)`;
- another explicitly versioned policy-approved disposition.

There is no implicit `ignored` state.

A consequential checkpoint cannot become authoritative while an interval contains `UNCLASSIFIED`, `UNKNOWN_SCHEMA`, parse failure, or missing source positions.

### 4. The interval disposition stream is itself committed

Each transition includes a canonical ordered commitment over the per-position dispositions, for example a Merkle root or domain-separated streaming accumulator whose semantics are frozen by generation.

The commitment binds source position + source leaf digest + disposition + derived operation digest. It prevents the mapper from later changing why a leaf was included/excluded without changing the checkpoint evidence.

### 5. Exact-once is about source positions, not merely event IDs

The completeness obligation is: every authenticated source **position** in the interval is accounted for exactly once.

Application event IDs may intentionally deduplicate retries, but two log positions with the same event ID still require two dispositions. One may be `APPLY` and the other `NOOP_DUPLICATE`; neither may disappear from the derivation transcript.

### 6. Batch roots require positional coverage proofs

A batch mapper may process many source leaves together, but a batch receipt must commit to:

- first and last source position;
- count;
- source leaf digest sequence commitment;
- disposition sequence commitment;
- previous derived root;
- resulting derived root;
- mapper generation.

Overlapping batches, gaps, duplicate position coverage, and reordered positional ranges are invalid unless an explicit parallel-shard protocol proves disjoint exhaustive coverage and deterministic merge semantics.

### 7. Compact skipped-leaf fraud proof

A verifier can prove a mapper skipped source position `i` when it can present:

1. authenticated source-log inclusion proof for leaf `i` at the mapper's claimed target source frontier;
2. mapper checkpoint claiming complete coverage through that frontier;
3. derivation transcript/coverage proof showing no committed disposition for `i`, or showing a range commitment whose positional count/boundaries exclude `i`;
4. checkpoint signature/authority evidence.

This is sufficient fraud evidence against the mapper checkpoint without reconstructing every subject-map leaf.

If the transcript commitment format cannot demonstrate whether position `i` was accounted for, that format is not sufficient for consequential completeness authority.

### 8. Compact duplicated-leaf fraud proof

A duplicated-source-position violation is proven by two authenticated mapper receipts/disposition leaves that both claim source position `i` under the same transition lineage, unless the protocol explicitly defines one as a superseding correction whose old checkpoint is revoked and no longer authoritative.

Deduplicated semantic effects do not erase duplicated source accounting.

### 9. Misclassification fraud requires deterministic re-execution evidence

For a source leaf whose committed disposition is wrong rather than missing, fraud evidence includes:

- authenticated source leaf bytes/digest and inclusion proof;
- exact mapper/schema/canonicalizer policy generations;
- committed mapper disposition;
- independently reproducible deterministic classification showing a conflicting mandatory disposition.

If classification depends on ambient mutable state, network responses, wall clock, locale, database contents, or current policy, the mapper contract is invalid for historical proof unless those inputs are separately content-addressed and bound.

### 10. Derived-root transition proof is separate from coverage proof

A complete coverage transcript is necessary but does not prove that `M_prev -> M_next` was computed correctly.

The authority bundle therefore proves both:

- **coverage:** every source position has exactly one valid disposition;
- **execution:** applying all effectful dispositions under the frozen deterministic mapper to `M_prev` yields `M_next`.

These may be proven by independent replay, authenticated incremental update proofs, a succinct proof system approved by policy, or another independently verifiable mechanism. A signature alone is not execution proof.

### 11. Independent full replay is the reference fallback

The slow but simple reference verifier is allowed to:

1. obtain every source leaf in `(from,to]` with authenticated positional inclusion/consistency evidence;
2. independently parse/classify each leaf using the pinned mapper generation;
3. apply dispositions deterministically to the prior authenticated subject-map state;
4. recompute disposition commitment and target map root;
5. require exact equality with the published mapper checkpoint.

This provides a high-assurance fallback when compact proofs are unavailable.

### 12. Checkpoints form a monotonic mapper lineage

Every mapper checkpoint commits to the hash/identity of the exact previous authoritative mapper checkpoint, except genesis.

A valid next checkpoint must have:

- `source_from_size == previous.source_to_size`;
- target source checkpoint that is append-only consistent with the previous target source checkpoint;
- `map_prev_root == previous.map_next_root`;
- monotonically advancing mapper checkpoint sequence/revision;
- approved mapper/schema migration if generation changes.

Forked mapper checkpoint children are equivocation evidence unless a policy-approved recovery transition explicitly records the fork/replacement.

### 13. Mapper code/schema evolution cannot reinterpret old intervals

Changing source schemas, canonicalization, collision handling, duplicate rules, tombstone semantics, or mapper implementation creates a new generation.

Historical transitions remain verified under their original generations. New generations begin at an explicit source frontier and bind the predecessor state plus migration evidence.

A newer mapper may not replay old source leaves under new semantics and silently replace an old authoritative map root.

### 14. Unknown/new source schemas fail closed for authority

If a source leaf is authenticated but the active mapper generation does not understand its schema/admission generation, the interval may be stored/observed but cannot be declared derivation-complete.

It transitions to `MAPPER_UPGRADE_REQUIRED` / `DERIVATION_BLOCKED`, not `NOOP_POLICY_IRRELEVANT` by default.

### 15. Parallel mapping requires deterministic exhaustive partitioning

Parallel workers are allowed only when the checkpoint proves:

- a deterministic partition function bound by generation;
- disjoint position/subrange assignments;
- exhaustive union equal to the complete source interval;
- per-partition coverage/disposition commitments;
- deterministic merge/reduction ordering;
- no result acceptance before all required partitions are complete.

Worker timeout or missing shard cannot be silently omitted from the final root.

### 16. Crash/restart resumes from durable receipts, not guessed progress

Mapper progress is durable only after an authenticated/checksummed transition receipt binds its exact source subrange and prior/next derived state.

On restart, uncommitted work is replayed. A local cursor saying `processed=N` without corresponding committed derivation evidence cannot advance authoritative coverage.

### 17. Mapper checkpoint time is not source completeness

Timestamp freshness cannot substitute for source coverage. A checkpoint produced after the source frontier time is still incomplete if it omitted positions.

Likewise, a high map revision number is not proof that the mapper consumed the corresponding log size.

### 18. External auditor signatures bind the exact derivation statement

An independent auditor/adjudicator signs a canonical statement containing at least:

- source checkpoint identity/range;
- previous/next mapper checkpoint identity;
- coverage/disposition commitment;
- target map root;
- mapper/schema/canonicalizer generations;
- verification method (`FULL_REPLAY`, `INCREMENTAL_PROOF`, etc.);
- verifier generation and trust frontier.

A generic signature over `map_root` alone does not attest derivation completeness.

### 19. Fraud evidence revokes checkpoint authority monotonically

Once a valid skipped/duplicated/misclassified-leaf fraud proof is admitted under the authenticated trust frontier:

- the affected mapper checkpoint becomes `FRAUD_PROVEN`;
- descendants depending on it become `REVALIDATION_REQUIRED` or invalid according to policy;
- omission/non-membership verdicts derived from those checkpoints lose admission authority;
- the old checkpoint remains preserved as evidence and cannot be made authoritative again by rollback.

### 20. Recovery creates a new lineage transition; it does not erase the bad one

Recovery from mapper fraud records:

- last known-good source and map checkpoints;
- fraudulent checkpoint(s) and fraud proof;
- exact replay/correction interval;
- corrected mapper generation;
- reconstructed target map root;
- independent verification/adjudication evidence;
- trust-frontier authorization for re-admission.

The repaired root is a new checkpoint generation. Historical bad checkpoints remain immutable evidence.

## Recommended composite checkpoint

For each derived-map transition publish a canonical content-addressed `MapperCheckpoint` equivalent to:

```text
mapper_checkpoint_generation
previous_mapper_checkpoint_digest
source_from {size, root, checkpoint_digest}
source_to   {size, root, checkpoint_digest}
map_from    {revision, root}
map_to      {revision, root}
mapper_generation
source_schema_generation_set
subject_key_generation
policy_generation
partition_generation
coverage_commitment
position_count
applied_count
noop_count
rejected_count
execution_proof_kind
execution_proof_digest
created_time_source_generation
```

The signed/authenticated checkpoint is authority only when its coverage/execution proof class is accepted by the current trust policy.

## Fraud-proof classes

### `SKIPPED_POSITION`
Authenticated source position exists inside claimed complete interval but lacks exactly one committed disposition.

### `DUPLICATED_POSITION`
Same source position is committed more than once in one authoritative derivation transition/partition union.

### `WRONG_SOURCE_BINDING`
Committed disposition references bytes/digest not equal to the authenticated source leaf at that position.

### `MISCLASSIFIED_POSITION`
Committed disposition conflicts with deterministic classification under the bound generations.

### `WRONG_EFFECT`
Coverage/classification is correct but the committed target map root does not equal deterministic execution over the prior map root.

### `GAP_OR_OVERLAP`
Batch/partition ranges are not a disjoint exhaustive cover of `(from,to]`.

### `GENERATION_REINTERPRETATION`
Checkpoint claims old source interval under a mapper/schema generation that was not authorized for that interval.

## 80-case RED-first matrix

### A. Source frontier and contiguous interval (1–10)
1. source target root not authenticated => reject;
2. source target size smaller than start => reject;
3. source consistency proof missing => reject;
4. claimed interval `(10,20]` but mapper receives positions 11..19 only => incomplete;
5. position 20 present but 17 missing => incomplete;
6. source positions reordered in transcript => reject unless canonical order is restored by proof;
7. source root correct but leaf bytes at position i wrong => reject;
8. same source root with wrong tree size => reject;
9. mapper checkpoint target source frontier stale relative to policy => not omission-authoritative;
10. valid contiguous complete interval => coverage stage may proceed.

### B. Exactly-one disposition per source position (11–20)
11. one source position has no disposition => skipped fraud;
12. one position has two APPLY dispositions => duplicate fraud;
13. one position has APPLY + NOOP => duplicate fraud;
14. duplicate event id at two positions still requires two dispositions;
15. explicit NOOP duplicate is accepted only with canonical original event binding;
16. unknown schema classified as irrelevant => reject;
17. parse failure silently skipped => reject;
18. policy-irrelevant reason code changed after checkpoint => digest mismatch;
19. source digest not bound into disposition => proof class rejected;
20. all positions map to exactly one canonical disposition => pass coverage cardinality.

### C. Batch / partition completeness (21–30)
21. batches `[1,10]` + `[12,20]` => gap detected;
22. batches `[1,10]` + `[10,20]` => overlap detected under closed-boundary encoding;
23. duplicate shard receipt => reject duplicate coverage;
24. missing final shard => no authoritative checkpoint;
25. worker timeout cannot be converted to empty shard;
26. partition function generation mismatch => reject;
27. partition union exhaustive but merge order nondeterministic => reject execution authority;
28. count commitment differs from interval cardinality => reject;
29. ranges exhaustive but one receipt references wrong source checkpoint => reject;
30. disjoint exhaustive deterministic partition set => coverage may proceed.

### D. Skipped/duplicate compact fraud evidence (31–40)
31. authenticated leaf at i + checkpoint complete claim + absent committed position => `SKIPPED_POSITION`;
32. non-authenticated alleged source leaf cannot prove fraud;
33. position outside claimed interval cannot prove skip against that checkpoint;
34. two receipts both binding i => `DUPLICATED_POSITION`;
35. duplicate semantic event at different positions is not duplicate-position fraud;
36. forged mapper receipt signature rejected;
37. stale superseded non-authoritative checkpoint does not invalidate current lineage unless policy says descendant depends on it;
38. valid fraud proof persists after service restart;
39. deleting local fraud record cannot restore authority if trust frontier retains it;
40. bad checkpoint descendant enters revalidation/invalid state.

### E. Deterministic classification / source-schema evolution (41–50)
41. mapper generation not pinned => reject;
42. source schema generation unsupported => block interval;
43. canonicalizer version differs => reject historical replay;
44. locale affects classification => nondeterministic/reject;
45. wall clock affects relevance without bound time input => reject;
46. external network lookup affects classification without captured content => reject;
47. duplicate policy changed mid-interval without transition => reject;
48. tombstone interpretation changed without generation transition => reject;
49. independent replay derives different disposition => misclassification disagreement;
50. exact captured inputs + generation reproduce disposition commitment.

### F. Execution proof / target derived root (51–60)
51. complete dispositions but wrong prior map root => reject;
52. complete dispositions but wrong target map root => `WRONG_EFFECT`;
53. APPLY operation omitted during state execution => root mismatch;
54. NOOP incorrectly mutates map => root mismatch;
55. same operations applied in nondeterministic order produce different root => protocol invalid unless order canonicalized;
56. sparse-map collision policy violation => execution failure;
57. independent full replay equals target root => execution proof accepted;
58. compact proof accepted only for approved proof generation;
59. generic mapper signature cannot replace execution proof;
60. execution proof digest must be bound into mapper checkpoint.

### G. Checkpoint lineage / crash / restart (61–70)
61. previous checkpoint digest mismatch => fork/reject;
62. source_from size differs from predecessor source_to => gap/overlap reject;
63. map_from root differs from predecessor map_to => reject;
64. mapper revision rollback => reject;
65. crash after local cursor advance but before durable receipt => replay range;
66. crash after durable receipt before aggregate checkpoint => reuse verified receipt idempotently;
67. restart silently trusts mutable processed counter => reject;
68. two competing children from same predecessor => equivocation evidence;
69. recovery checkpoint records last-good + bad checkpoint + correction evidence;
70. rollback to pre-fraud trust state cannot restore bad checkpoint authority.

### H. Auditor / omission composition / migrations (71–80)
71. auditor signature over map root only => insufficient derivation attestation;
72. auditor signature binds wrong source interval => reject;
73. auditor beyond allowed lag => not current admission authority;
74. sparse-map non-inclusion proof from unverified mapper checkpoint => cannot yield `OMISSION_PROVEN`;
75. mapper completeness verified but promise deadline frontier too early => no omission verdict;
76. mapper generation migration without explicit boundary => reject;
77. historical checkpoint reinterpreted under new schema => reject;
78. corrected replay produces new root but erases old fraud evidence => reject recovery;
79. independent full replay reproduces coverage commitment + target root => admissible derivation evidence;
80. promise + eligible frontier + verified mapper derivation + valid map non-inclusion proof => omission adjudication may proceed to remaining policy/trust checks.

## Implementation order when exact execution is available

1. Implement data-only canonical mapper checkpoint/disposition/receipt schemas and hashing/domain separation.
2. Add RED tests for interval gaps, duplicate positions, unknown schemas, wrong target root and stale lineage before production mapper behavior.
3. Implement a reference full-replay verifier first; use it as the correctness oracle for later compact-proof optimizations.
4. Implement mapper transition execution with deterministic per-position dispositions.
5. Add batch/parallel receipts only after single-threaded exhaustive coverage is proven.
6. Add compact skipped/duplicate fraud proof verification.
7. Compose checkpoint authority into the existing trust-frontier/adjudicator contracts.
8. Only then allow a derived-map non-inclusion proof to participate in `OMISSION_PROVEN`.

## Audit conclusions

- Append-only source authenticity and sparse-map proof validity do not jointly imply derivation completeness.
- Every source position needs an explicit committed disposition; there is no safe implicit ignore path.
- Coverage and correct state execution are separate proof obligations.
- A full independent replay is the reference safe fallback and should exist even if compact proofs are later introduced.
- Compact fraud evidence must be able to identify skipped/duplicated source positions against the mapper's own claimed complete interval.
- Mapper/schema/canonicalizer migrations are generation transitions, not reinterpretations of old checkpoints.
- Proven mapper fraud monotonically removes checkpoint authority and triggers descendant revalidation; recovery preserves the fraud history.

No production code was changed in this research step and no behavioral PASS is claimed.