# HISTORICAL_REATTESTATION_SCHEDULING_CRYPTOGRAPHIC_SUNSET_EVIDENCE_REFRESH_COMPLETENESS_V1_FROZEN

Date: 2026-09-06
Status: FROZEN DESIGN / RED-FIRST
Scope: LAB-093 retained-authority / long-lived evidence safety. This does not supersede LAB-086 priority or claim executable production completion.

## Question

How can a system retire a cryptographic carrier, verifier generation, trust root, timestamp authority, or proof system without discovering after the sunset that some still-live E2/E3/E4 evidence depended on the retired mechanism and can no longer be safely refreshed, replayed, or adjudicated?

## Donor evidence

1. NIST CSWP 39upd1 (2026-06-29) defines crypto agility as the ability to replace/adapt cryptography while preserving security and ongoing operations. Its operational implication for this project is that migration is an inventory-and-transition problem, not merely an algorithm-selection event.
2. NIST NCCoE's Migration to PQC project makes cryptographic discovery/inventory a first migration step and explicitly connects inventory to risk management and prioritization.
3. RFC 4998 Evidence Record Syntax requires evidence renewal before the currently relied-on cryptographic mechanism becomes unreliable. It distinguishes:
   - timestamp renewal, when the old timestamp/signature carrier is aging or its certificate/key is at risk but the underlying hash tree remains trustworthy;
   - hash-tree renewal, when the hash used for the archived object commitment is itself becoming insecure, which requires access to the underlying archived objects/evidence, not just the previous timestamp.
   RFC 6283 carries the same distinction for XML evidence records.
4. ETSI TS 119 511 long-term preservation explicitly treats algorithm/key/hash obsolescence, key compromise, and loss of validation capability as long-term preservation concerns.

## Core decision

A cryptographic sunset MAY become destructive only after a proof-carrying refresh campaign establishes complete coverage of every still-live object whose accepted authority, verification, recovery, or retention semantics depend on the retiring carrier.

`deadline reached` is never equivalent to `safe to forget old evidence`.

The system must distinguish:

- **acceptance sunset**: old carrier cannot authorize new consequential statements;
- **verification sunset**: old carrier is no longer accepted as a standalone basis for current verification;
- **destructive-retention sunset**: originals/old proofs may be removed only after all live obligations have been refreshed or explicitly failed closed;
- **emergency rejection**: immediate compromise may force rejection before planned refresh completes; affected obligations become quarantined/revalidation-required, not silently trusted or deleted.

These frontiers can occur at different times.

## Canonical objects

### `CryptoSunsetPlanV1`

Authenticated statement containing at minimum:

- `plan_id`
- carrier identity: algorithm / key generation / verifier generation / proof-system generation / trust-root generation
- reason: scheduled deprecation, certificate expiry, policy removal, compromise, cryptanalytic event, implementation bug, verifier semantic change
- `no_new_authority_after`
- `historical_verify_until` when such a window is policy-allowed
- `refresh_must_complete_before`
- `destructive_gc_not_before`
- dependency classes affected: E1/E2/E3/E4
- required successor carriers/verifiers
- required refresh modes
- inventory namespace/schema generations
- archive/offline handling policy
- signer/threshold/policy frontier

### `RefreshInventoryCheckpointV1`

Authenticated inventory snapshot of the candidate universe. It binds:

- exact repository/evidence/log/map/checkpoint frontiers scanned;
- schema/extractor generations used to identify carrier dependencies;
- complete key/range/partition coverage manifests;
- explicit scan gaps and unreachable archives;
- object counts and Merkle/content commitments for candidate sets;
- supersession/repair frontier used when calculating liveness;
- challenge/revocation/appeal/GC frontiers.

An inventory checkpoint with a gap is not complete and grants no destructive authority for the affected range.

### `RefreshObligationV1`

One obligation per still-live dependency on the retiring carrier. Required fields include:

- immutable original object/evidence identity;
- dependency class E1/E2/E3/E4;
- retiring carrier identity;
- exact reason the dependency is material;
- root obligation set / supported observation namespace;
- original availability location(s);
- allowed refresh outcomes;
- deadline and urgency class;
- campaign generation.

Exactly-one disposition is required for every obligation.

### Allowed dispositions

- `DIRECT_REATTESTED`: retained original was directly replayed/reverified and a successor-carrier certificate now covers the same semantic statement and obligations.
- `LOSSLESS_REENCODED_AND_REATTESTED`: byte representation changed losslessly and both old/new identity relation plus semantic statement were independently verified.
- `SUBSUMED`: an independently verified successor proof/certificate demonstrably subsumes the complete root obligation set.
- `ARCHIVE_RETRIEVED_AND_REFRESHED`: offline object was restored, verified, then refreshed.
- `NO_LONGER_LIVE_WITH_AUTHENTICATED_PROOF`: dependency became genuinely unreachable from all authority-sensitive retention roots before the sunset; requires the normal GC/reachability proof, not campaign convenience.
- `QUARANTINED_UNREFRESHABLE`: still-live evidence could not be refreshed; it remains retained and all guarantees depending on it degrade/fail closed.
- `REJECTED_AS_INVALID`: source evidence itself is invalid; dependent verdicts/authorities are re-adjudicated, never silently refreshed.

There is no `IGNORED`, `BEST_EFFORT`, `TIMED_OUT_SO_ASSUME_DEAD`, or `NOT_FOUND_SO_DONE` disposition.

## Refresh mode selection

The system must choose the refresh mode based on which cryptographic layer is expiring.

### Carrier-only renewal

Permitted only when the semantic/object commitment beneath the retiring carrier remains secure and independently verifiable. Analogous to RFC 4998 timestamp renewal: successor evidence may bind the previous accepted evidence record without touching every original payload.

### Commitment/hash renewal

Required when the retiring primitive participates in content identity, Merkle/hash-tree commitments, subject-index keys, proof public inputs, or any other layer whose collision/preimage security is material. Analogous to RFC 4998 hash-tree renewal: underlying objects/evidence must be available and re-committed under the successor primitive.

A new outer signature over an old weak hash does not refresh the underlying commitment.

### Verifier-semantic renewal

Required when verifier generation changes what observations are material. Old `PASS` cannot simply be resigned. The retained original evidence must be replayed under the successor verifier or be covered by an independently justified observation-subsumption proof.

### Trust-root/key compromise renewal

If compromise occurred before a trustworthy successor bridge was established, the old key/root cannot self-authorize its own rescue. Recovery requires a pre-authorized independent recovery root/quorum/checkpoint. Objects whose only authority chain passes through the compromised carrier become revalidation-required.

## Completeness model

A refresh campaign is complete only if all four properties hold:

1. **Universe completeness** — every storage/log/map/archive namespace that may contain a live dependency was included or explicitly marked as a blocking gap.
2. **Classification completeness** — every candidate object was evaluated under the authenticated dependency schema plus all historical repair edges and materiality adjudications.
3. **Disposition completeness** — every resulting live obligation has exactly one terminal disposition.
4. **Successor-coverage completeness** — every disposition claiming preservation has a successor proof that preserves the full required obligation set for the dependency class.

Completeness must be reproducible by an independent verifier from the inventory checkpoint, manifests, obligation set, dispositions, and successor proof references.

## Campaign state machine

`PLANNED -> INVENTORY_FROZEN -> REFRESHING -> VERIFYING_COVERAGE -> COMPLETE | BLOCKED | COMPROMISED_ABORT`

Rules:

- Sunset planning may start while writes continue, but inventory must bind a precise frontier.
- New objects created after the frozen frontier that use the retiring carrier are forbidden once `no_new_authority_after` is reached.
- Objects entering liveness after the inventory frontier through revocation, appeal, dependency-repair, fork recovery, or schema reinterpretation create delta obligations and invalidate a previously computed terminal completeness proof until processed.
- Physical deletion of old evidence is forbidden until campaign `COMPLETE`, destructive-GC horizon elapsed, and the GC mark is recomputed against the successor dependency graph.
- A late compromise during the campaign invalidates any disposition whose proof depended on post-compromise use of the retiring carrier beyond its accepted effective frontier.

## Priority scheduling

Refresh order is risk-weighted, not FIFO.

Highest priority:

1. irreplaceable E4 authority-continuity evidence;
2. E3 recovery evidence needed only during rollback/fork/disaster paths;
3. E2 consequential verification evidence with no independent duplicate;
4. offline/archive-only originals with long retrieval lead time;
5. evidence whose current carrier has the nearest security/expiry horizon;
6. evidence with large downstream dependency blast radius;
7. E1 reproducibility-only evidence;
8. audit provenance that is not authority-sensitive.

Campaign scheduling must reserve time for failed archive retrieval, independent replay, disagreement adjudication, and a final completeness audit before the cryptographic deadline. Finishing on the deadline is an unsafe plan.

## Archive/offline semantics

An archived object is not considered refreshable merely because an archive manifest exists.

Before destructive sunset for a dependency requiring underlying bytes, the campaign must either:

- retrieve the object, verify its content address/provenance, and perform the required refresh; or
- retain the old evidence and mark the dependent guarantee `QUARANTINED_UNREFRESHABLE`.

Late-joining/offline verifiers must receive the successor evidence plus authenticated handoff chain and the campaign checkpoint needed to show the refresh predated rejection of the old carrier.

## GC interlock

While a sunset campaign is active:

- every discovered live obligation is an explicit GC root;
- unresolved candidate ranges are temporary GC roots;
- originals needed for commitment/hash or verifier-semantic renewal cannot be substituted away by a prior compact substitute unless the substitute is already proven sufficient for the new refresh mode;
- campaign `COMPLETE` does not itself authorize deletion; normal proof-carrying GC still applies using the successor dependency graph;
- if campaign completeness or successor certificate is later revoked, affected historical closures reactivate as GC roots.

## Mixed-algorithm / hybrid evidence

For objects protected by multiple carriers, safety is evaluated against the exact policy semantics:

- if policy requires all carriers, sunset of one requires refresh of that component;
- if policy accepts an authenticated threshold/OR construction, surviving independent carriers may preserve authority only if the historical policy already authorized that semantics;
- a migration cannot retroactively reinterpret `AND` as `OR` or lower a threshold to claim refresh completeness.

Hybrid cryptography is not a blanket excuse to skip inventory.

## Deadline semantics

Deadlines are authenticated policy inputs, not wall-clock guesses.

The verifier must distinguish:

- planned policy deadline;
- certificate/key validity horizon;
- external cryptanalytic/revocation event effective time;
- local observation time;
- trusted timestamp/checkpoint frontier.

Clock skew or a local scheduler miss cannot extend the authority of a carrier past an authenticated rejection frontier.

If `refresh_must_complete_before` passes with unresolved live obligations, the campaign becomes `BLOCKED_EXPIRED`; the system must retain evidence and degrade affected guarantees. It must not auto-mark unresolved objects as refreshed.

## Proof of complete campaign

`RefreshCampaignCompletionProofV1` binds:

- sunset plan digest;
- inventory checkpoint digest;
- candidate universe commitment;
- obligation-set commitment;
- disposition-set commitment;
- successor-proof commitment;
- unresolved-gap count = 0;
- unresolved-live-obligation count = 0;
- dependency schema/repair/materiality frontiers;
- trust/verifier/policy frontiers;
- independent verifier identities/results;
- completion timestamp/checkpoint authenticated by a carrier already acceptable after the sunset;
- exact GC-not-before frontier.

The proof is invalid if any referenced inventory partition, disposition, successor proof, or verifier lineage is missing or later revoked without successful re-adjudication.

## Common-mode independence

For E2/E3/E4, inventory/classification and preservation verification cannot rely exclusively on the same buggy extractor/verifier lineage that could have omitted the dependency originally.

At least one independent validation domain is required for consequential campaign completion. Independence may be implementation, operator, code lineage, proof system, or separately generated inventory, depending on the failure model.

## Failure semantics

- Missed certificate discovered before sunset: add obligation, invalidate old coverage checkpoint, refresh normally.
- Missed certificate discovered after sunset while original still exists: quarantine, perform successor-only direct replay if possible, record that previous completeness proof was false, compute blast radius, re-adjudicate deletions/verdicts that relied on it.
- Missed certificate discovered after sunset after original was deleted: do not fabricate recovery; downgrade/fail affected guarantees and open a durable safety incident.
- Original unavailable before required hash/verifier renewal: `QUARANTINED_UNREFRESHABLE`; no destructive GC.
- Successor verifier disagreement: `REFRESH_DISAGREEMENT`; retain both original and candidate successor evidence until adjudication.
- Late revocation of successor: reopen affected obligations and campaign closure.

## 80-case RED-first matrix

### A. Inventory / universe (1-10)
1. Single live E2 certificate discovered.
2. Live E3 certificate in cold archive discovered.
3. Live E4 chain reachable only through recovery root discovered.
4. Dead E1 object excluded only with authenticated reachability proof.
5. Object in second storage namespace is not silently omitted.
6. Partition gap blocks completeness.
7. Stale inventory schema cannot claim full universe.
8. Duplicate inventory rows collapse to one canonical object identity without losing references.
9. Content-address alias does not hide second dependency class.
10. New namespace introduced during campaign creates a delta coverage requirement.

### B. Classification / materiality (11-20)
11. E2 dependency on retiring signature key classified.
12. E3-only recovery bytes remain material despite normal verifier not reading them.
13. E4 root-continuity object cannot be downgraded due to age.
14. E1 provenance-only dependency does not gain destructive authority accidentally.
15. Historical repair edge adds a previously missing dependency.
16. Materiality disagreement blocks destructive completion.
17. Revoked classifier causes revalidation of its campaign slice.
18. Same-producer classifier alone is insufficient for consequential completion.
19. Schema migration cannot reinterpret old object without historical decoder.
20. Cyclic repair edges do not self-create liveness.

### C. Carrier-only renewal (21-30)
21. Expiring timestamp with secure underlying hash renews by successor timestamp.
22. Expiring signing certificate with secure retained commitment renews without payload replay only when semantics permit.
23. New outer signature over already-rejected inner signature is not laundering.
24. Renewal timestamp must predate old carrier rejection frontier.
25. Post-compromise self-signing cannot rescue old root.
26. Successor proof binds exact original evidence identity.
27. Wrong policy/context cannot be reused across refresh.
28. Old evidence remains historically verifiable but cannot authorize new refresh after acceptance sunset.
29. Replay of old renewal response is rejected by campaign/object identity binding.
30. Two independent successor carriers satisfy only historically authorized threshold semantics.

### D. Hash/commitment renewal (31-40)
31. Retiring Merkle hash forces original object retrieval.
32. Outer timestamp renewal alone fails for weak content hash.
33. Every archived object in the old commitment is rehashed or explicitly excluded by authenticated liveness proof.
34. Missing leaf blocks commitment renewal completeness.
35. Duplicate semantic object at distinct authenticated positions remains exactly accounted for.
36. Canonicalization drift cannot silently change object meaning during rehash.
37. New hash collision policy is bound to new commitment generation.
38. Subject-index key hash renewal preserves subject mapping semantics.
39. Proof public-input hash migration preserves original statement identity.
40. Recommitment root is independently reproducible.

### E. Verifier/proof-system renewal (41-50)
41. V1 PASS is not simply resigned by V2.
42. Direct replay under V2 preserves full root obligation set.
43. Observation-subsumption proof explicitly covers every material V1 observation.
44. New V2 material observation makes old compact substitute insufficient.
45. Recursive proof upgrade preserves all logical ancestors.
46. Retired verifier embedded in new circuit gains no new authority.
47. Successor verifier disagreement blocks completion.
48. Common-mode V1/V2 implementation lineage cannot serve as sole independence proof.
49. V2 bug revocation reopens affected refresh obligations.
50. Recovery verifier version is tracked separately from normal verification version.

### F. Scheduling / deadlines (51-60)
51. E4 object with nearest deadline is prioritized over bulk E1.
52. Archive retrieval lead time affects priority.
53. Campaign begins with safety margin before rejection deadline.
54. Scheduler crash resumes from authenticated campaign state.
55. Wall-clock rollback cannot extend old authority.
56. Deadline expiry with one unresolved E2 produces BLOCKED_EXPIRED.
57. Emergency compromise causes immediate authority rejection and quarantine.
58. Planned acceptance sunset can precede historical-verification sunset.
59. Destructive GC horizon cannot precede successful refresh completion.
60. New late-live obligation invalidates prior completion until processed.

### G. Archive / offline / availability (61-68)
61. Archive manifest without retrieval proof is insufficient for hash renewal.
62. Retrieved object digest mismatch blocks refresh.
63. One lost archive replica succeeds through independently verified second replica.
64. All replicas lost => quarantine, not fabricated completion.
65. Offline verifier catches up through authenticated successor handoff.
66. Offline verifier cannot self-bootstrap from newest root alone.
67. Archive restored after deadline can support re-adjudication but cannot retroactively prove timely refresh.
68. Compacted hot copy remains until archive write-read-verify succeeds.

### H. GC / races / recovery (69-80)
69. Active campaign obligation roots original against GC.
70. Unscanned range roots the affected namespace against destructive GC.
71. GC mark before late revocation becomes stale.
72. Refresh completion followed by dependency repair triggers delta obligations.
73. Original cannot be deleted before successor proof is independently verified.
74. Existing semantic substitute is rejected if insufficient for required new hash/verifier renewal.
75. Crash after successor proof write but before disposition commit is idempotently recovered.
76. Crash after disposition commit but before completion checkpoint does not double-count.
77. Missed object found post-sunset with original retained triggers incident + successful re-adjudication path.
78. Missed object found post-sunset after original deletion forces guarantee downgrade and records unsafe prior GC.
79. Disaster recovery rebuilds campaign state from authenticated inventory/obligation/disposition commitments.
80. Independent verifier reproduces zero-gap, zero-unresolved completion and exact successor coverage before destructive retirement is authorized.

## Acceptance bar before implementation

Do not wire production sunset/refresh authority until executable RED tests exist for at least:

- missed live certificate;
- weak-hash requiring original retrieval;
- outer-signature laundering attempt;
- offline/archive unavailable original;
- late revocation reopening campaign;
- deadline expiry with unresolved E2/E3/E4;
- GC race with late obligation;
- false completeness from inventory gap;
- verifier-generation drift;
- independent completion proof replay.

## Decision

Freeze this contract as `HISTORICAL_REATTESTATION_SCHEDULING_CRYPTOGRAPHIC_SUNSET_EVIDENCE_REFRESH_COMPLETENESS_V1_FROZEN`.

No current implementation or PASS is claimed. LAB-086 remains the first execution priority whenever exact source execution or a safe byte-preserving publication path becomes available.

## Next distinct evidence question

**Refresh-campaign inventory attestation / delta-capture / completeness-under-concurrent-mutation semantics**: define a practical authenticated snapshot+delta protocol that proves the refresh universe remained complete while evidence, revocations, appeals, repair edges, liveness roots, and archive locations changed concurrently; determine whether source logs/checkpoints can give a compact cut without globally stopping writers, and freeze RED cases for phantom obligations, double-counted moves, archive relocation, snapshot/delta gaps, rollback, and campaign-finalization races.
