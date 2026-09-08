# Witness partition recovery, cross-log obligation completeness, beacon liveness, semantic-attester independence, and provenance compromise effective-time

Date: 2026-09-08
Status: `WITNESS_PARTITION_CROSSLOG_OBLIGATION_BEACON_LIVENESS_SEMANTIC_ATTESTER_PROVENANCE_EFFECTIVE_TIME_V1_FROZEN`
Parent: LAB-093 / #178

## Scope

This freeze extends the LAB-093 transparency/freshness evidence line while LAB-086 exact source execution is unavailable. It is a design contract and RED-first test specification, **not executable proof**.

The contract addresses five failure classes that remain after the previous transparency/witness freeze:

1. a witness or verifier rejoins after a long partition and is offered a selectively truncated but internally consistent history;
2. a required cross-log anchor is promised but never published;
3. a threshold randomness round does not complete and observers must distinguish availability loss from attributable withholding without inventing evidence;
4. several semantic repair attesters return the same result but may have copied one another rather than independently reproducing it;
5. a provenance-authority key is later declared compromised and old attestations need deterministic pre/post-compromise treatment.

## Primary donors

### RFC 9162 / Certificate Transparency v2

Useful mechanism: an SCT is an authenticated promise to include an accepted submission within a fixed Maximum Merge Delay (MMD). After the MMD, an inclusion check against a sufficiently recent authenticated tree can yield positive evidence of log misbehavior. RFC 9162 also separates append-only consistency from leaf semantics and notes that split-view detection requires comparing authenticated tree views.

Adopted mechanism: **promise-before-deadline + independently retained promise + authenticated post-deadline state + canonical inclusion/non-inclusion check**.

Not adopted blindly: CT does not define the generic witness-gossip protocol or make absence of a newer checkpoint proof of latestness.

### transparency.dev witness model

Useful mechanism: a witness cosigns only checkpoints that are consistent with the checkpoint it previously accepted. Multiple witnesses can reduce split-view risk; witnesses validate append-only consistency, not semantic correctness of leaves.

Adopted mechanism: each witness retains its accepted frontier and must prove monotonic reconciliation from that frontier after partition.

### drand protocol/security model

Useful mechanism: a threshold beacon is produced from at least the configured threshold of verifiable partial signatures; a node's partial signature is bound to the round (and, in chained mode, the previous signature), and catch-up advances deterministic rounds after an outage.

Adopted mechanism: signed/verified partial contributions are positive evidence of participation; absence of a contribution is not automatically proof that a specific member maliciously withheld it unless an independently verifiable participation obligation existed for that round and the observation surface is complete enough to establish non-participation.

### in-toto / SLSA

Useful mechanism: owner-defined authorized functionaries, signed step metadata, and reproducible/independent executions can corroborate a result. SLSA explicitly warns that nominally multiple rebuilders are not independent if they share one vulnerable pipeline implementation.

Adopted mechanism: semantic-attester quorum counts **independent reproductions**, not signatures, processes, endpoints, or copied outputs.

### Sigstore threat/security model

Useful mechanism: transparency/monitoring detects misuse, while TUF-managed trust material supplies rotation/revocation; Sigstore explicitly models compromise time so legitimate signatures from before compromise can remain verifiable while later use of the compromised material is rejected.

Adopted mechanism: revocation is versioned and contains an authenticated effective-time / effective-sequence boundary. The boundary changes current reliance but does not erase historical evidence.

## Frozen invariants

### A. Witness partition recovery

`VALID_CHECKPOINT != COMPLETE_HISTORY`

`CONSISTENT_WITH_LOCAL_FRONTIER != LATEST_KNOWN_GLOBALLY`

A witness/verifier that rejoins after partition MUST begin from its last independently retained accepted checkpoint/frontier. It MUST NOT discard that frontier merely because the remote endpoint presents a newer-looking checkpoint.

For the same log lineage:

- same tree size + different authenticated root => `EQUIVOCATION_CONFLICT`;
- larger tree size + valid consistency proof from retained frontier => monotonic candidate advancement;
- larger tree size without required consistency proof => `HISTORY_CONTINUITY_UNKNOWN`;
- smaller tree size than retained frontier => stale/truncated view, never current;
- no newer checkpoint observed => **not** proof that no newer checkpoint exists.

A long partition MAY be reconciled through an independently retained witness/cross-log checkpoint that dominates the local frontier, but every hop must be authenticated and consistency-verifiable. “Jump to the freshest mirror” is forbidden.

If two independently authenticated post-partition branches cannot be proven consistent, rejoin fails closed with explicit conflict. LWW/newest timestamp/fastest mirror is forbidden.

### B. Cross-log anchor obligation completeness

`NO_ANCHOR_OBSERVED != ANCHOR_OMISSION_PROVEN`

A mandatory cross-log anchor is only omission-provable if there was a durable authenticated obligation **before** the deadline.

Define `CrossLogAnchorPromiseV1` with at minimum:

- source log lineage + source checkpoint digest/tree size;
- destination log lineage;
- canonical anchor statement digest;
- promise id;
- deadline rule / max publication delay;
- promise authority + generation;
- required destination inclusion evidence profile;
- cancellation/supersession policy, if any.

Positive `CROSSLOG_ANCHOR_OMISSION_PROVEN` requires all of:

1. valid independently retained promise;
2. deadline proven elapsed using accepted time policy;
3. authenticated destination state after the deadline;
4. a canonical exhaustive or compact non-inclusion proof over the promised anchor key/statement;
5. no valid predecessor-authorized cancellation/supersession that became effective before the deadline.

A destination 404, timeout, empty query, or unavailable monitor is never positive omission evidence.

Late publication after the deadline does not erase the historical omission violation; it changes availability/current state only.

### C. Threshold-beacon liveness evidence

`ROUND_DID_NOT_COMPLETE != MEMBER_WITHHOLDING_PROVEN`

`MISSING_PARTIAL != MALICIOUS_WITHHOLDING_PROVEN`

For each challenge/randomness round, freeze before values are knowable:

- group generation;
- eligible members and public-share identities;
- threshold;
- round/epoch;
- chained predecessor, if applicable;
- contribution deadline;
- observation/collector quorum;
- fallback policy.

Define `BeaconParticipationReceiptV1` for positive participation evidence: member id, group generation, round, predecessor digest, partial-signature digest/signature, collector id, observation time evidence.

Define `BeaconLivenessStatementV1` for a collector/witness to state which valid partials it observed for the exact frozen round.

A round can be classified:

- `BEACON_COMPLETE`: threshold final signature verifies;
- `BEACON_INCOMPLETE_ATTRIBUTION_UNKNOWN`: insufficient partials; observation surface incomplete or no prior participation obligation;
- `BEACON_INCOMPLETE_MEMBER_NONPARTICIPATION_PROVEN`: prior member obligation + post-deadline independently authenticated observation set is complete enough to prove no valid contribution from that member;
- `BEACON_EQUIVOCATION_CONFLICT`: one member produces incompatible valid contributions where the scheme/policy allows only one;
- `BEACON_OBSERVATION_CONFLICT`: independent collectors disagree and completeness cannot be reconciled.

Even positive non-participation evidence does not by itself prove malicious intent; it proves protocol non-participation under the frozen obligation.

Fallback to another beacon/group is permitted only if fallback order and composition were frozen before observing the primary outcome. Same-round adaptive reselection remains forbidden.

### D. Semantic-attester independence challenge

`N_ATTESTATIONS != N_INDEPENDENT_REPRODUCTIONS`

`MATCHING_OUTPUTS != INDEPENDENCE_PROVEN`

A semantic repair attester must commit before challenge to a versioned provenance descriptor:

- implementation/source lineage;
- parser/canonicalizer id;
- crypto/library family;
- build/toolchain provenance;
- runtime/control domain;
- input acquisition path/archive identity;
- attester authority generation.

The challenge is revealed only after the eligible attester set and provenance commitments are frozen. It binds:

- exact repair manifest/predecessor;
- canonical source/archive checkpoint;
- deterministic reconstruction policy;
- a fresh nonce and challenge id;
- requested intermediate commitment set, e.g. canonical-input digest, reconstructed-prefix digest, per-stage digests, final semantic result.

Each attester returns `SemanticReproductionAttestationV1` signed over the challenge and all required digests.

Quorum counting uses an `IndependencePolicyV1`, not raw signatures. Attesters that share a disallowed common control/build/runtime/source dependency collapse into one effective failure domain.

A copied final output without independently derived intermediate commitments cannot increase semantic quorum. Divergent deterministic outputs are explicit conflict and require fail-closed adjudication; majority vote must not silently bless one implementation family.

Challenge scheduling must avoid giving one attester another attester's response before its own commitment/response is fixed.

### E. Provenance-authority compromise effective-time semantics

`KEY_REVOKED_NOW != ALL_HISTORICAL_ATTESTATIONS_INVALID`

`PRE_COMPROMISE_TIMESTAMP != PRE_COMPROMISE_AUTHENTICITY` unless the time/sequence evidence itself is independently trusted.

Define `AuthorityCompromiseStatementV1`:

- authority id + key id;
- authority lineage/generation;
- compromise knowledge publication sequence/time;
- `effective_from` expressed using an accepted authenticated time and/or monotonic transparency sequence boundary;
- statement issuer/recovery authority;
- reason/classification;
- superseded key/material identifiers;
- policy version.

Verification categories:

1. `CREATED_BEFORE_EFFECTIVE_BOUNDARY_WITH_TRUSTED_TIME`: historical evidence may remain usable under the policy active at creation, subject to all other validity checks.
2. `CREATED_AT_OR_AFTER_EFFECTIVE_BOUNDARY`: reject current reliance on the compromised authority/key.
3. `CREATION_TIME_OR_SEQUENCE_UNKNOWN`: fail closed for consequential current decisions; historical bytes remain evidence but assurance is unresolved.
4. `BOUNDARY_EQUIVOCATION_CONFLICT`: two authenticated compromise statements for same authority lineage establish incompatible effective boundaries without valid supersession; fail closed.

A compromise statement published late MAY set an earlier effective boundary if that boundary is itself independently authenticated/adjudicated. Publication time is not automatically compromise time.

Revocation/compromise is append-only evidence. Later recovery does not erase that the old key was compromised; it establishes a successor trust lineage.

For high-assurance archival verification, prefer a monotonic transparency sequence/checkpoint bound plus authenticated time rather than wall-clock time alone.

## Composite state machine

A consequential repair/randomness/latestness decision is allowed only when all required layers are simultaneously acceptable:

`AUTHORITY_VALID`
`AND HISTORY_CONTINUITY_PROVEN`
`AND REQUIRED_PUBLICATION_OBLIGATIONS_SATISFIED_OR_NOT_DUE`
`AND RANDOMNESS_POLICY_NOT_ADAPTIVELY_DOWNGRADED`
`AND SEMANTIC_QUORUM_COUNTS_INDEPENDENT_REPRODUCTIONS`
`AND PROVENANCE_AUTHORITIES_VALID_FOR_THE_EVIDENCE_EFFECTIVE_BOUNDARY`.

Any `UNKNOWN` in a required layer remains `UNKNOWN`; signatures from another layer do not launder it into `VALID`.

## RED-first matrix

Freeze at least the following 64 cases before implementation. The list below defines the mandatory dimensions; implementation may split them into more tests.

### Witness/partition — 16

1. retained g10/checkpoint 100, server offers checkpoint 90 -> stale reject;
2. retained size 100/root A, server same size/root B -> equivocation;
3. size 120 with valid 100->120 consistency -> candidate advance;
4. size 120 without proof -> unknown;
5. malformed proof -> reject;
6. valid proof from wrong lineage -> reject;
7. newer cross-log checkpoint proves local mirror stale;
8. no newer cross-log checkpoint -> latestness remains unknown;
9. partition rejoins through witness whose retained frontier predates local one -> no rollback;
10. witness forgets frontier after restart -> fail closed unless authenticated recovery state exists;
11. two witness quorums cosign conflicting same-size roots -> conflict;
12. witness membership rotated during partition without predecessor authorization -> reject;
13. authorized membership rotation with continuity proof -> accept new membership prospectively;
14. truncated checkpoint chain with individually valid signatures -> continuity unknown;
15. destination anchor survives source outage -> existence evidence retained;
16. source recovery cannot retroactively rewrite retained cross-log anchor.

### Cross-log obligation — 12

17. promise + timely inclusion -> satisfied;
18. promise + post-deadline canonical non-inclusion -> omission proven;
19. no promise + no anchor -> unknown, not omission;
20. promise only stored at source then source disappears -> insufficient unless retention policy allowed it;
21. destination timeout -> unknown;
22. empty search API result -> unknown;
23. valid exhaustive destination prefix after deadline with zero canonical matches -> omission proven;
24. late anchor after proven omission -> historical violation retained;
25. cancellation after deadline -> cannot erase violation;
26. predecessor-authorized cancellation before deadline -> obligation cancelled prospectively;
27. self-cancellation by compromised promise authority without required recovery authorization -> reject;
28. same promise id rebound to another source checkpoint -> equivocation/reject.

### Beacon liveness — 12

29. threshold final signature verifies -> complete;
30. t-1 valid partials only, incomplete observation -> attribution unknown;
31. t-1 partials plus complete signed observation surface and prior member obligation -> member non-participation proven;
32. missing partial with no prior obligation -> not attributable;
33. valid member partial observed by one collector but omitted by another -> observation conflict, not member withholding;
34. collector fabricates partial digest without valid partial -> reject;
35. member sends incompatible valid partials where deterministic scheme permits one -> equivocation;
36. round incomplete then adaptive local-PRNG fallback not predeclared -> reject;
37. predeclared secondary beacon fallback after objective liveness condition -> allowed prospectively;
38. scheduler changes eligible group after seeing primary partials -> reject;
39. catch-up emits deterministic missed rounds in order -> continuity accept when signatures verify;
40. skip directly to current round where chained policy requires predecessor continuity -> reject.

### Semantic attester independence — 12

41. three signatures, same process/output copied -> effective quorum 1;
42. three processes, same control/runtime domain disallowed by policy -> collapse domain;
43. independent implementations reproduce exact canonical digests/result -> quorum counts;
44. same final result, divergent intermediate canonical-input digest -> conflict/ineligible;
45. attester sees peer response before committing -> ineligible for independence quorum;
46. challenge nonce replay -> reject;
47. response bound to wrong manifest/predecessor -> reject;
48. response uses stale provenance generation -> reject/current reliance unknown per policy;
49. two implementations share parser bug and policy marks parser family common-mode -> collapse;
50. deterministic divergence 2-vs-1 -> fail closed, no majority semantic truth;
51. independently rebuilt identical binary but shared source semantics -> build independence does not imply semantic independence;
52. one attester unavailable -> quorum recalculated only according to frozen denominator policy, never denominator laundering.

### Provenance compromise effective time — 12

53. attestation creation sequence provably before compromise boundary -> historical use allowed by frozen policy;
54. creation sequence after boundary -> reject;
55. wall-clock says before but transparency sequence says after -> conflict/fail closed;
56. creation time unknown -> consequential current use fails closed;
57. compromise statement published late with independently adjudicated earlier effective boundary -> apply earlier boundary;
58. publication timestamp used as effective boundary without policy authority -> reject;
59. recovery successor valid after compromised key -> accept successor prospectively;
60. old compromised key signs successor alone -> reject;
61. conflicting compromise effective boundaries same generation -> equivocation;
62. valid predecessor/recovery-authorized supersession narrows/clarifies boundary -> apply versioned rule, retain old statement historically;
63. compromise of timestamp/time authority reopens classifications that depended solely on it;
64. evidence also bound to independently retained monotonic log sequence survives wall-clock authority compromise when policy permits.

## Security conclusions

1. Partition recovery is a monotonic reconciliation problem, not a freshness-by-timestamp problem.
2. Mandatory publication only becomes positively omission-provable when the system first creates an independently retained, deadline-bearing obligation.
3. A failed threshold-beacon round proves availability failure; attribution to a member requires stronger retained obligations and observation-completeness evidence.
4. Semantic attestation quorum must count independent reproductions under explicit provenance policy; signatures are not independence.
5. Key-compromise handling needs an authenticated effective boundary. Current revocation must not erase legitimate historical evidence, while uncertain evidence at/after the boundary must not remain trusted by default.
6. Every layer preserves `UNKNOWN` rather than laundering missing evidence through another valid signature layer.

## Implementation handoff

When executable source is available, LAB-086 remains priority #1. For this frozen contract, implementation should be regression-first and split into small types/state machines rather than one monolithic verifier:

- witness retained-frontier reconciliation;
- `CrossLogAnchorPromiseV1` + omission verifier;
- beacon participation/liveness evidence classifier;
- semantic reproduction challenge + independence-policy evaluator;
- provenance compromise effective-boundary classifier.

No production refactor should precede the corresponding RED cases.