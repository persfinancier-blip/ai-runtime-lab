# Publication-promise fulfillment / verifiable non-inclusion / subject-index completeness — v1 frozen

Status: `PUBLICATION_PROMISE_FULFILLMENT_VERIFIABLE_NON_INCLUSION_SUBJECT_INDEX_COMPLETENESS_V1_FROZEN`

Date: 2026-09-06

Scope: LAB-093 trust-frontier/monitoring follow-up. Design and RED contract only; no production subject index, map, prover, or behavioral PASS is claimed.

## Problem

The prior omission contract allows `OMISSION_PROVEN` when a signed publication promise reaches its deadline and a later authenticated state proves the promised subject was still absent. That statement is only sound if the data structure used by the proof can actually prove non-membership or completeness for the promised subject.

A conventional append-only Certificate Transparency-style Merkle log proves:

- inclusion of a particular leaf at a particular tree size; and
- consistency/append-only extension between tree sizes.

It does **not**, from a failed inclusion lookup alone, prove that an arbitrary semantic subject key never appears in the committed tree. Failure to obtain a proof can mean transport loss, incomplete search, alternate canonicalization, duplicate encodings, indexing defects, or a malicious query service.

Therefore LAB-093 must not convert `missing inclusion proof` into `OMISSION_PROVEN` unless the promise is bound to a verifiable subject-index/completeness commitment whose proof semantics make non-membership decidable at the relevant authenticated frontier.

## Primary donor mechanisms

### RFC 9162 — Certificate Transparency v2

RFC 9162 defines dense append-only Merkle trees, inclusion proofs, consistency proofs, signed tree heads, and SCT/MMD publication promises. Its inclusion proof proves that a known leaf hash exists in a particular committed tree; consistency proves append-only evolution. CT detects violated SCT promises by combining authenticated promises with sufficiently new tree state and monitor/auditor evidence, not by treating an ordinary failed lookup as a generic Merkle non-membership proof.

Reference: https://www.rfc-editor.org/rfc/rfc9162.html

### Trillian verifiable maps / sparse Merkle trees

Trillian's map design assigns each logical key to a deterministic leaf index derived from the key hash in a fixed-depth sparse Merkle tree. Empty subtrees have committed empty hashes distinct from set leaves. A proof for the canonical key path can therefore demonstrate that the corresponding committed leaf is empty at a particular signed map root.

References:
- https://transparency.dev/verifiable-data-structures/
- https://github.com/google/trillian/blob/master/docs/MapHashers.md

### Ordered/range commitments

For some subject models, an ordered authenticated set or namespaced/range tree can prove completeness over a subject interval by committing to ordering/range metadata. This is useful when the question is not merely “is exact key K absent?” but “did the log include every event for subject S / namespace N through frontier F?”. A range proof must itself be committed by the authenticated root; a database index or API result set is not sufficient.

## Frozen decisions

### 1. Dense append-only log absence is not generic non-membership evidence

For a CT-style dense log, the following are insufficient alone for `OMISSION_PROVEN`:

- `get-proof-by-hash` returns not found;
- no monitor happened to find the subject;
- a query index returns zero rows;
- an API returns 404;
- enumerating only part of the log fails to find the subject;
- the log refuses or times out on a proof request.

A dense log can still support promise-violation proof if the promised exact leaf bytes/hash are known and an independently complete monitor has reconstructed and authenticated the entire committed leaf sequence for a post-deadline tree. That is a completeness proof by full reconstruction, not a native non-membership proof from the dense Merkle tree.

### 2. Every consequential publication promise binds a canonical subject key

A promise capable of later proving omission binds:

- `subject_key_scheme_generation`;
- canonical subject type/domain;
- canonical subject bytes or digest;
- canonical leaf/event encoding generation;
- duplicate/retry semantics;
- destination commitment class (`DENSE_LOG`, `SPARSE_MAP`, `ORDERED_SET`, `LOG_DERIVED_MAP`, or explicitly versioned equivalent);
- source promise generation and deadline;
- required frontier/checkpoint generation;
- hash/domain-separation generation;
- policy generation.

A promise over a human-readable identifier that can map to multiple canonical keys cannot authorize a proven-omission verdict.

### 3. Promise-to-leaf binding is explicit and deterministic

The promise commits either:

1. the exact leaf bytes/hash expected to appear in the append-only log; or
2. a deterministic canonical transformation from promise subject to leaf commitment whose generator/version is itself bound.

Retries must not silently produce semantically different leaf identities. If timestamps/nonces are part of the leaf, the promise must bind the exact accepted leaf instance or a separately committed request identifier whose index completeness semantics cover all allowed leaf realizations.

### 4. Sparse-map non-membership requires a committed empty leaf/path

For a fixed-depth sparse Merkle map:

- key `K` maps deterministically to index `I = H(domain || canonical_key)`;
- a signed/authenticated map root commits the leaf value or canonical empty value at `I`;
- the proof path is verified against that exact root and map/hash generation;
- empty-never-set is distinct from an application value whose payload is empty/null;
- a non-membership verdict is valid only if the authenticated path proves the canonical empty state for `I`.

An application-level `None`, missing SQL row, or API 404 is not a sparse-Merkle non-membership proof.

### 5. Hash-key collisions are protocol events, not impossible assumptions

The subject-key scheme must define collision behavior. A collision between two canonical subjects under a finite key hash cannot be resolved by silently overwriting one map leaf.

Allowed designs include collision buckets whose contents are themselves canonically committed, a collision-resistant secondary authenticated structure, or fail-closed admission requiring explicit migration. The proof bundle records the key scheme and any collision-bucket generation.

### 6. Ordered-set/range completeness requires ordering commitments

If the system uses a sorted authenticated set, range tree, or namespace tree, a completeness proof for subject interval `[a,b]` must establish that:

- all committed leaves are in canonical order under the bound comparator generation;
- predecessor/successor boundaries around the requested interval are authenticated;
- the proof includes every committed leaf whose canonical key falls in the interval, or proves an authenticated empty range;
- duplicates are handled under explicit multiset/set semantics;
- comparator/canonicalization changes create a new structure generation and cannot reinterpret historical roots.

### 7. Subject index and append-only evidence log are distinct commitments

A practical design may maintain:

- an append-only event log for global history; and
- a sparse/ordered subject index for efficient membership/non-membership/completeness proofs.

These cannot be independent authority islands. Each subject-index root must be cryptographically bound to the exact log frontier it indexes, and the binding must be authenticated in the same trust-frontier lineage.

A newer index root over an older log frontier is stale; a newer log frontier with no corresponding required index root is incomplete for omission adjudication.

### 8. Log-derived map updates are deterministic and complete

For `LOG_DERIVED_MAP`, an index revision `M_n` is authoritative for log frontier `L_n` only if a verifier can prove or independently replay that every eligible log leaf through `L_n` was mapped exactly once according to the bound mapper generation.

The mapper commits:

- accepted source leaf schema generations;
- canonical subject extraction rules;
- duplicate/retry handling;
- tombstone/revocation semantics;
- collision handling;
- deterministic update order;
- map hash generation.

A signed map root without proof of derivation completeness cannot prove that an omitted source leaf was not simply skipped by the mapper.

### 9. Promise fulfillment is checked against the first eligible post-deadline frontier

A promise with deadline `D` is evaluated against an authenticated frontier whose effective publication time is provably after `D + allowed_skew` and whose subject-index revision is bound to that frontier.

Later eventual inclusion does not erase a proven missed-deadline event. The proof bundle retains both the violating frontier and any later recovery inclusion.

### 10. Duplicate and retry semantics are frozen

For each promise class the policy declares one of:

- `EXACTLY_ONE_LEAF` — the exact accepted leaf instance must appear;
- `AT_LEAST_ONE_CANONICAL_SUBJECT` — at least one leaf/index value bound to the promised subject must appear;
- `ALL_ACCEPTED_INSTANCES` — every separately acknowledged accepted instance must appear;
- `STATE_BY_DEADLINE` — the subject index must reflect a specified state/value by the deadline frontier.

The verifier cannot switch semantics after observing the result.

### 11. Tombstones/deletions cannot masquerade as never-published

If the subject-index data model supports deletion, tombstone, revocation, supersession, or compaction, historical non-membership must distinguish:

- `NEVER_PRESENT_AT_FRONTIER`;
- `PRESENT_VALUE`;
- `TOMBSTONED_AFTER_PRIOR_PRESENCE`;
- `SUPERSEDED`;
- `UNKNOWN_UNPROVABLE`.

A current empty leaf does not prove the subject was absent at an earlier promised frontier unless historical map revisions are retained/authenticated.

### 12. Historical proof verification is generation-pinned

All non-membership/completeness proof bundles bind the exact:

- log root/frontier;
- map/set root and revision;
- subject-key scheme;
- canonicalizer/comparator;
- hash functions/domain separators;
- mapper generation;
- collision semantics;
- promise policy;
- verifier generation.

A rehash, canonicalization migration, or comparator change creates a new generation. Historical proofs are not reinterpreted under current rules.

### 13. Migration/rehash requires dual-frontier linkage

When moving from index generation A to B, the migration bundle must prove:

- source authenticated root/frontier A;
- target authenticated root/frontier B;
- exact migration mapper/canonicalization generation;
- complete coverage of every live/tombstoned subject required by policy;
- explicit treatment of collisions and duplicates;
- linkage to the same or a monotonic successor log frontier;
- no authority gap where neither generation can prove subject status.

A freshly rebuilt map from mutable database state is not historical proof.

### 14. Full-log monitor reconstruction is an allowed but expensive proof class

A dense log monitor may establish absence of exact promised leaf `X` at tree size `N` only when it has:

- all `N` leaf inputs/entries;
- independently recomputed the tree root equal to the authenticated root;
- applied exact bound canonical/leaf encoding rules;
- searched the full reconstructed set for the exact promise binding;
- preserved enough evidence for independent replay.

This proof class is valid for exact-leaf absence, but it does not automatically prove semantic subject absence if multiple leaf encodings can represent the subject.

### 15. Query indexes are acceleration only

SQL indexes, search services, Bloom filters, caches, and API query layers may accelerate discovery but never constitute authority for non-membership unless their state is itself authenticated by the committed proof structure.

False positives in probabilistic indexes may trigger extra work; false negatives must never authorize omission verdicts.

### 16. `OMISSION_PROVEN` requires a proof class declared by policy

A promise-violation verdict requires:

1. valid signed publication promise;
2. eligible post-deadline authenticated frontier;
3. a policy-approved completeness/non-membership proof for the exact subject/leaf semantics;
4. proof that the index/root is bound to that frontier;
5. independent verification of all generation/collision/duplicate semantics;
6. retained transcript sufficient for reproducible adjudication.

If any element is missing, the strongest allowed state is `OMISSION_SUSPECTED` or `UNKNOWN_UNPROVABLE`, not `OMISSION_PROVEN`.

## Recommended composite architecture

For LAB-093, prefer a **log + derived sparse subject map** when exact-key non-membership is important:

- append-only log remains the durable global event/history sequence;
- each accepted publication promise binds an exact event leaf and canonical subject key;
- a deterministic mapper consumes every committed log leaf through frontier `N` and emits subject-map revision `N`;
- the authenticated checkpoint binds `(log_root_N, tree_size_N, subject_map_root_N, mapper_generation, subject_key_generation)`;
- inclusion of the event is proven against the log;
- subject membership/non-membership is proven against the sparse map;
- mapper-completeness evidence prevents a malicious map from silently dropping log events.

For interval/namespace completeness, use an ordered/range authenticated structure instead of pretending a hash-indexed map proves ordered ranges.

## Canonical proof bundle

A non-inclusion/completeness adjudication bundle contains at least:

- signed publication promise bytes/signature;
- canonical promised subject and exact leaf binding;
- deadline/skew/time-source policy;
- pre-deadline retained checkpoint if relevant;
- first eligible post-deadline authenticated checkpoint;
- log root/tree size;
- subject-index root/revision;
- log→index binding artifact;
- map/set proof path or full-log reconstruction manifest;
- subject-key/canonicalizer/comparator/hash generations;
- mapper generation and completeness evidence;
- duplicate/retry/collision/tombstone policy;
- verifier/adjudicator generations;
- verdict reason code;
- later recovery inclusion if one occurs.

## 80-case RED-first matrix

### A. Dense-log non-membership boundary (1–10)
1. `get-proof` not-found alone cannot prove omission;
2. HTTP 404 alone cannot prove omission;
3. timeout alone cannot prove omission;
4. partial log scan cannot prove absence;
5. complete N-leaf reconstruction with wrong root rejected;
6. complete reconstruction matching authenticated root can prove exact-leaf absence;
7. exact-leaf absence cannot prove semantic-subject absence when alternate encodings exist;
8. query DB zero rows is non-authoritative;
9. Bloom-filter negative is non-authoritative unless cryptographically bound with zero false-negatives by contract;
10. consistency proof alone cannot prove subject absence.

### B. Canonical subject / leaf binding (11–20)
11. promise missing subject-key generation rejected for proven omission;
12. alternate Unicode normalization yields distinct key unless canonicalizer says otherwise;
13. case-folding change cannot reinterpret historical promise;
14. promise subject digest altered => signature failure;
15. leaf encoder generation altered => proof mismatch;
16. timestamped retry producing distinct leaf requires declared retry semantics;
17. `EXACTLY_ONE_LEAF` cannot be silently evaluated as `AT_LEAST_ONE_CANONICAL_SUBJECT`;
18. human-readable alias mapping to two subjects => unprovable until disambiguated;
19. wrong domain separator rejects key proof;
20. subject extraction failure from accepted leaf fails closed.

### C. Sparse-map non-membership (21–30)
21. wrong key index proof rejected;
22. wrong map root rejected;
23. wrong revision rejected;
24. empty-never-set distinguished from explicit empty value;
25. application `None` without Merkle path is insufficient;
26. truncated path rejected;
27. forged empty-subtree marker rejected;
28. stale map root cannot adjudicate newer promise;
29. valid empty-leaf proof at eligible frontier establishes exact-key non-membership;
30. map key hash collision cannot overwrite silently.

### D. Collision / duplicate / retry semantics (31–40)
31. two subjects colliding under index trigger collision policy;
32. collision bucket proof commits all bucket entries;
33. duplicate exact leaf under `EXACTLY_ONE_LEAF` remains fulfillment;
34. multiple accepted instances under `ALL_ACCEPTED_INSTANCES` require all promised ids;
35. retry after transport UNKNOWN cannot invent a new promise identity silently;
36. deduplication by subject must be policy-bound;
37. duplicate ordering cannot change root nondeterministically;
38. collision-policy generation rollback rejected;
39. bucket overflow cannot silently evict old subject;
40. hash algorithm migration requires explicit generation transition.

### E. Ordered/range completeness (41–50)
41. unordered map cannot prove ordered interval completeness by assertion;
42. wrong comparator generation rejected;
43. predecessor boundary omitted => incomplete proof;
44. successor boundary omitted => incomplete proof;
45. missing in-range leaf detected by root mismatch/proof failure;
46. duplicate-key multiset semantics preserved;
47. empty interval proof requires authenticated neighboring boundaries or empty subtree/range commitment;
48. namespace proof cannot cover adjacent namespace accidentally;
49. reordered leaves invalidate authenticated root;
50. comparator migration cannot reuse old range proof.

### F. Log-derived index completeness (51–60)
51. map root not bound to log frontier rejected;
52. map revision behind log frontier => stale/unusable for proven omission;
53. mapper silently skips one eligible leaf => completeness failure;
54. mapper applies same leaf twice => completeness failure unless idempotent rule proves equivalence;
55. wrong subject extraction generation rejected;
56. mapper nondeterministic update order yielding different root rejected;
57. unsigned mapper generation metadata insufficient;
58. source log leaf schema unknown => fail closed;
59. map checkpoint newer than source log without valid binding rejected;
60. mapper replay from full log reproduces committed map root.

### G. Deadline / historical status / tombstones (61–70)
61. pre-deadline empty proof cannot prove missed deadline;
62. first eligible post-deadline empty proof can satisfy absence condition;
63. later inclusion does not erase prior proven deadline miss;
64. current empty leaf cannot prove historical never-presence after deletion;
65. tombstone records prior presence distinctly;
66. supersession preserves historical fulfillment evidence;
67. archive restore cannot replace promised historical revision with latest-only state;
68. clock uncertainty blocks deadline proof;
69. wrong frontier timestamp/time-source generation rejected;
70. promise fulfilled exactly at permitted skew boundary handled deterministically.

### H. Migration / reproducibility / authority (71–80)
71. rehash without dual-frontier linkage invalidates omission authority;
72. canonicalizer migration missing collision report fails closed;
73. rebuilt map from mutable current DB cannot stand in for historical root;
74. proof bundle missing map/log binding fails adjudication;
75. proof bundle missing duplicate/collision policy fails adjudication;
76. independent verifier reproduces non-membership verdict from retained bundle;
77. verifier disagreement => fail closed / revalidation required;
78. revoked verifier signature cannot grant current admission;
79. forked log/map checkpoints route to `FORK`, not simple omission;
80. no supported proof class => `UNKNOWN_UNPROVABLE`/`OMISSION_SUSPECTED`, never fabricated `OMISSION_PROVEN`.

## Integration constraints

- Compose with the frozen publication-promise/challenge-response, monitor-completeness, witness/split-view, proof reproducibility, and adjudicator trust-frontier contracts.
- Do not create a second mutable subject-index authority disconnected from the append-only global frontier.
- Historical proofs remain pinned to original key/canonicalizer/hash/mapper generations.
- Exact executable RED tests must demonstrate that a failed dense-log lookup cannot produce `OMISSION_PROVEN`, while a valid post-deadline sparse-map empty proof or complete reconstructed-log proof under the correct promise semantics can.

## Result

Frozen design contract only. The central safety boundary is explicit: **a missing lookup result is not a non-membership proof. `OMISSION_PROVEN` requires an authenticated post-deadline frontier plus a data-structure-specific proof that is actually capable of proving exact subject/leaf absence or completeness under generation-pinned semantics.**
