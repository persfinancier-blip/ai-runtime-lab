# Checkpoint archival, time-authority recovery, proof-closure semantic migration, escrow epoch concurrency, and ZK parameter renewal

Date: 2026-09-09
Status: design freeze / RED-first contract
Contract ID: `CHECKPOINT_TIME_PROOFCLOSURE_ESCROW_ZK_RENEWAL_V1_FROZEN`
Owner context: LAB-093/#178 design follow-up while LAB-086 exact executable gate remains blocked by per-run transport limits.

## Scope

This note closes the next evidence gap recorded in `state/CURRENT.md`:

1. checkpoint-package archival denominator and positive anti-GC proof;
2. Byzantine time-source membership recovery after authority compromise;
3. proof-closure semantic-diff attestation and canonical corpus versioning;
4. escrow refresh concurrency and epoch-fork adjudication;
5. ZK ceremony transcript availability, contributor-independence evidence, and proof renewal across parameter deprecation.

This is architecture evidence only. It does **not** substitute for LAB-086 exact executable RED/GREEN proof.

## Primary donors

- RFC 9162, Certificate Transparency Version 2.0 — append-only Merkle trees, signed tree heads, inclusion and consistency proofs, promise-to-include / MMD semantics, signed evidence of log misbehavior: https://www.rfc-editor.org/rfc/rfc9162.html
- IETF Roughtime draft-ietf-ntp-roughtime-19 — nonce-bound signed time responses, radius/interval semantics, multi-server inconsistency evidence, delegated signing keys with validity intervals: https://datatracker.ietf.org/doc/html/draft-ietf-ntp-roughtime
- SLSA build provenance / FAQ — reproducibility proves build relation, not semantic correctness; independent rebuilders must actually be independent: https://slsa.dev/spec/draft/faq and https://slsa.dev/spec/v1.2-rc2/build-provenance
- Ethereum KZG Ceremony / EF wrap-up — public transcript, independently verifiable contribution chain, final transcript hash, and explicit warning that contribution count/identities are not a strong independence/Sybil signal: https://ceremony.ethereum.org/ and https://blog.ethereum.org/2024/01/23/kzg-wrap
- NIST Multi-Party Threshold Cryptography project — threshold operations and distributed secret handling as the base model for share refresh/reconfiguration: https://csrc.nist.gov/projects/threshold-cryptography

## 1. Historical checkpoint package: denominator is part of the proof

### Decision

A historical checkpoint claim is evaluated under the exact witness/log policy epoch that governed it when issued. The archival package must retain enough material to reproduce that evaluation later.

Minimum `CheckpointArchivePackage`:

- exact signed checkpoint bytes;
- log identity and log signing-key epoch;
- exact witness membership epoch and denominator;
- threshold/quorum policy bytes, not only a policy hash;
- witness signatures/cosignatures that were actually counted;
- predecessor checkpoint(s) or retained consistency-proof ancestry sufficient to re-prove append-only continuity from a trusted retained frontier;
- hash/signature algorithm identifiers and parameter epochs;
- authenticated time evidence used for any deadline/effective-time decision;
- package manifest/version and canonical encoding identifier.

### Frozen invariants

`WITNESS_LOSS_LATER != HISTORICAL_DENOMINATOR_SHRINK`.

`CHECKPOINT_DIGEST_RETAINED != CHECKPOINT_PROOF_RETAINED`.

`CURRENT_POLICY_AVAILABLE != HISTORICAL_POLICY_AVAILABLE`.

A later witness retirement, key rollover, compromise, or quorum reduction cannot retroactively recalculate an old checkpoint against the smaller current denominator.

RFC 9162 supports the core distinction: append-only claims are verified from signed tree heads plus Merkle consistency material. A retained root hash by itself is not enough to reconstruct the relationship to another historical tree state.

### Positive anti-GC rule

A historical checkpoint package may be garbage-collected only after a **positive dependency-closure proof**, not because no current reader happened to reference it.

`CheckpointGCAuthorization` must bind:

- exact package digest;
- authenticated complete dependency-event frontier;
- dependency-index version;
- proof that every still-relied-upon descendant/claim is self-sufficient without this package or has been renewed into an independently sufficient successor package;
- GC policy epoch;
- authorizing quorum and effective time.

`EMPTY_DEPENDENCY_LOOKUP != NO_DEPENDENCIES`.

If the dependency frontier cannot be exhaustively reproduced, the package is `GC_BLOCKED_FRONTIER_INCOMPLETE`.

## 2. Time-source membership recovery after compromise

### Decision

Time evidence is a set of authenticated intervals/order claims from a precommitted authority population, not a scalar timestamp selected after observation.

`TimeAuthorityEpoch` binds:

- authority IDs and key epochs;
- independence/control-domain metadata;
- threshold/denominator;
- aggregation rule;
- maximum accepted radius/uncertainty;
- validity interval;
- predecessor/successor authorization;
- recovery authority.

Roughtime is a useful donor because a client nonce is incorporated into signed responses, establishing that the response was generated after the nonce, and multi-server mode is explicitly intended to expose inconsistent servers. Delegated response keys also have bounded validity intervals.

### Recovery invariants

`AUTHORITY_COMPROMISED != REMOVE_FROM_OLD_DENOMINATOR`.

A compromised member remains part of the historical denominator for epochs in which it was eligible; evidence from that epoch may be downgraded/reopened, but the denominator is not rewritten.

`RECOVERY_EPOCH != RETROACTIVE_REINTERPRETATION`.

A successor authority set starts a new epoch. It may establish new current time evidence, but it does not silently re-sign or reinterpret old timestamps.

`POST_OBSERVATION_MEMBER_DROP == DENOMINATOR_LAUNDERING` unless the drop condition was committed in advance and independently evidenced.

### Compromise handling

If compromise effective time is known and independently adjudicated:

- responses provably before the boundary may retain historical validity under the frozen old policy;
- responses provably after the boundary fail current reliance;
- responses whose authenticated intervals overlap the boundary are `TIME_AUTHORITY_BOUNDARY_AMBIGUOUS`.

If effective time is unknown, consequential decisions requiring that authority fail closed or require an independent successor evidence path.

## 3. Proof-closure semantic-diff attestation and canonical corpus

### Problem

A new parser/generator can deterministically rebuild a proof closure while changing semantics. Reproducibility demonstrates a build/output relation, not that two versions interpret the evidence identically. SLSA explicitly makes this distinction and requires genuinely independent rebuilders for reproducibility to add assurance.

### Decision

Every proof-closure parser/generator version has an immutable `SemanticInterpreterEpoch`:

- source/version digest;
- parser grammar/canonicalization version;
- generator algorithm version;
- build provenance/toolchain;
- accepted input schema;
- canonical output schema;
- canonical conformance corpus version;
- semantic-diff policy;
- predecessor/successor relationship.

A migration from interpreter A to B creates a **new proof generation**. It never overwrites A's output.

### Canonical corpus

The corpus is itself versioned evidence and contains:

- positive canonical vectors;
- invalid/rejected vectors;
- ambiguity vectors;
- boundary/overflow/Unicode/canonicalization vectors where relevant;
- historical real evidence snapshots stripped of secrets when necessary;
- expected semantic claim graph, not merely expected serialized bytes.

A candidate successor must execute the exact corpus independently. Differences are classified:

- `BYTE_DIFF_SEMANTIC_EQUIVALENT`;
- `SEMANTIC_DIFF_INTENDED_POLICY_CHANGE`;
- `SEMANTIC_DIFF_UNEXPLAINED`;
- `PARSER_ACCEPTANCE_SURFACE_EXPANDED`;
- `PARSER_ACCEPTANCE_SURFACE_REDUCED`.

Only the first two may proceed, and an intended policy change must create a new policy epoch rather than pretending equivalence.

### Attestation quorum

Semantic-equivalence attestations must bind exact A/B versions, corpus version, source frontier, result digests, and independent provenance. Multiple signatures over the same single execution count as one reproduction domain.

`REPRODUCIBLE_BYTES != SEMANTIC_EQUIVALENCE`.

## 4. Escrow refresh concurrency and epoch-fork adjudication

### Decision

Share refresh is an epoch transition with a single canonical predecessor. Concurrent refreshes from the same predecessor are conflicting successors unless the scheme explicitly defines composable refresh deltas and the implementation proves that property.

`EscrowEpoch` binds:

- predecessor epoch digest;
- participant membership/denominator;
- threshold;
- public commitment to the protected secret/key identity;
- refresh transcript/commitments required by the scheme;
- activation state;
- compromise state;
- retirement state.

### Atomic activation

A new refresh epoch is not active until the required threshold of participants has completed the protocol and an authenticated epoch-activation record is committed.

Partial refresh produces `REFRESH_INCOMPLETE`; old and new shares must not be mixed unless the underlying scheme explicitly proves cross-epoch compatibility.

### Fork rule

Two different activated candidates with the same predecessor are `ESCROW_EPOCH_FORK`.

Resolution must not use last-write-wins. Adjudication requires:

- exact transcripts for both candidates;
- participant/control-domain evidence;
- compromise/exposure evidence;
- independently authorized choice of one successor or full reconstitution into a new recovery epoch.

The rejected fork remains archived as evidence.

### Rollback/offline rules

- runtime/database rollback cannot resurrect retired shares;
- an offline member does not justify lowering threshold after the refresh protocol has begun;
- membership/threshold reconfiguration is a distinct operation from refresh;
- a refresh after a recorded threshold compromise may restore future confidentiality, but cannot erase the historical compromise event.

## 5. ZK ceremony transcript survivability and parameter renewal

### Ceremony transcript

Ethereum's KZG ceremony is a strong donor for transcript survivability: the final transcript has a public hash and can be independently verified. It also gives an important negative lesson: a large contribution count does **not** imply that contributors are independent identities; the EF explicitly warns that linked addresses/entities made multiple contributions.

Therefore:

`MANY_CONTRIBUTIONS != MANY_INDEPENDENT_CONTROL_DOMAINS`.

A `ZKParameterArchivePackage` must retain:

- exact ceremony/final transcript or content-addressed retrievable chunks plus manifest;
- final transcript digest;
- proof-system/curve/domain parameters;
- contribution verification rules/tool versions;
- setup assumption statement (for example, "at least one contribution secret destroyed");
- parameter activation epoch;
- circuit/predicate versions that depend on the parameter set;
- any independently collected contributor-control-domain evidence, labeled by confidence.

### Transcript availability

A digest without retrievable transcript bytes permits identity checking only if a copy appears; it does not permit independent verification after all copies are lost.

`TRANSCRIPT_HASH_RETAINED != TRANSCRIPT_VERIFYABILITY_RETAINED`.

Archive policy should therefore require multiple independently governed storage domains and periodic retrieval/verification challenges.

### Contributor independence

For ceremonies whose safety assumption only needs one honest entropy contribution, Sybil multiplicity does not necessarily break soundness, but it also does not justify stronger claims such as "N independent contributors". Independence claims require separate evidence (organizational/control domain, build/runtime diversity, custody evidence, etc.).

### Parameter deprecation / compromise

When an SRS/parameter epoch is deprecated or compromised:

- existing proofs remain immutable historical objects;
- current consequential reliance is re-evaluated according to the compromise/deprecation policy;
- a successor parameter set protects successor proofs only;
- old proofs can be renewed/re-proved only if the underlying authenticated witness/source evidence still exists and the successor circuit/predicate is semantically equivalent or an explicit policy migration authorizes the semantic change.

`NEW_SRS != OLD_PROOF_REHABILITATED`.

### Recursive proof renewal

A recursive wrapper around an old proof does not remove the old proof's assumptions if the new proof merely asserts "old verifier accepted". The renewal package must state whether it proves:

1. the original statement directly from retained witness under the successor system; or
2. only the validity of an old proof under the old verifier.

Case (2) inherits the deprecated old parameter/proof-system assumption and cannot be labeled full cryptographic renewal.

`PROOF_OF_OLD_PROOF_VALIDITY != REPROOF_OF_ORIGINAL_STATEMENT`.

## RED-first matrix (40 cases)

### A. Checkpoint archival / anti-GC

A01 historical 3-of-5 checkpoint remains 3-of-5 after two witnesses retire -> historical denominator unchanged.
A02 same checkpoint evaluated as 3-of-3 after retirement -> reject denominator laundering.
A03 signed checkpoint retained, historical policy bytes missing -> archival proof incomplete.
A04 checkpoint + policy retained, consistency ancestry missing -> append-only relationship not independently reproducible.
A05 GC requested after empty materialized dependency lookup but source frontier unavailable -> block GC.
A06 authenticated complete frontier proves zero dependents -> GC may proceed under policy.
A07 all dependents renewed into self-sufficient packages -> GC may proceed only with exact renewal linkage.
A08 concurrent new dependency appears between census and GC commit -> CAS/version mismatch, abort GC.

### B. Time authority recovery

B01 2-of-3 population fixed before query, one server gives inconvenient interval -> cannot drop it post-observation.
B02 compromised member removed only in successor epoch -> old denominator retained.
B03 old and successor authority epochs overlap -> exact epoch/key validity determines eligible evidence.
B04 response interval fully before independently adjudicated compromise boundary -> historical policy may accept.
B05 interval crosses compromise boundary -> ambiguous/fail closed for consequential use.
B06 successor set re-signs old scalar time with no old evidence -> not historical rehabilitation.
B07 two servers share one operator/KMS -> two responses but one independence domain.
B08 nonce-bound Roughtime response proves response-after-nonce, not absolute correctness of server clock.

### C. Proof-closure semantic migration

C01 A/B emit byte-identical output on corpus but share same vulnerable parser library -> reproducibility not independent semantic proof.
C02 independent implementations produce same claim graph for all canonical vectors -> positive equivalence evidence.
C03 B accepts formerly invalid ambiguous encoding -> acceptance-surface expansion requires explicit review.
C04 B rejects formerly canonical historical vector -> migration blocked unless policy intentionally changes.
C05 output bytes differ only in canonical serialization while claim graph identical -> classify byte-diff semantic-equivalent.
C06 claim graph differs -> never auto-classify equivalent.
C07 corpus changes during attestation -> version mismatch, rerun.
C08 old proof generation overwritten by B output -> reject; immutable successor generation required.

### D. Escrow refresh concurrency

D01 refresh R1 and R2 start from same predecessor -> concurrent candidates recorded.
D02 both candidates reach activation independently -> epoch fork, no LWW.
D03 only R1 activates; R2 partial shares survive -> R2 remains non-active and must be destroyed/retired per policy.
D04 runtime rollback presents retired predecessor as current -> reject using external/independent epoch evidence.
D05 offline member after protocol start -> no threshold reduction.
D06 explicit membership reconfiguration before new refresh -> allowed as separate authenticated transition.
D07 prior threshold compromise then successful refresh -> future assurance may recover; historical compromise remains recorded.
D08 shares from predecessor and successor mixed without scheme proof -> reject.

### E. ZK ceremony / renewal

E01 transcript digest valid but transcript bytes unavailable anywhere -> independent transcript verification unavailable.
E02 transcript replicated across independent storage domains and periodically verified -> survivability evidence positive.
E03 100 contributions from linked identities -> do not claim 100 independent contributors.
E04 one honest contribution suffices by scheme assumption -> Sybil multiplicity alone does not invalidate final SRS.
E05 setup compromise established -> current reliance on affected old proofs downgraded/rejected per policy.
E06 new SRS created but historical witness unavailable -> cannot re-prove original statement.
E07 recursive successor proof only verifies old proof under old verifier -> inherits old assumptions.
E08 successor proof directly re-proves original statement from retained authenticated witness under semantically equivalent predicate -> full renewal candidate.

## Security / correctness audit

- No rule above treats availability evidence as proof of malicious attribution.
- No membership retirement changes a historical denominator.
- No rebuild/reproducibility claim is promoted to semantic correctness without independent interpretation evidence.
- No share refresh is allowed to erase previous compromise evidence or silently perform membership/threshold reconfiguration.
- No ZK parameter migration rehabilitates an old proof unless the original statement is actually re-established under successor assumptions.
- Every destructive GC transition requires positive, authenticated closure evidence rather than absence-of-observation.

## Implementation consequence

When exact executable source becomes available, these contracts should be implemented test-first as immutable epoch/package state machines rather than ad-hoc booleans. Until then, this note is the frozen design input for LAB-093/#178 and future RED matrices; LAB-086 remains priority #1.
