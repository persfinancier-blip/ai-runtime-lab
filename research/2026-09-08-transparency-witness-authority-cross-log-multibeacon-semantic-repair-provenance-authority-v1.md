# Transparency/witness authority lifecycle, cross-log anchoring, multi-beacon anti-bias, semantic repair quorum, verifier-provenance authority

Date: 2026-09-08
Status: design freeze / executable RED-GREEN pending
Contract: `TRANSPARENCY_WITNESS_CROSSLOG_MULTIBEACON_SEMANTIC_REPAIR_PROVENANCE_AUTHORITY_V1_FROZEN`

## Context

LAB-086 exact execution remains blocked in this runtime before repository code executes (`git clone --no-checkout` fails on DNS resolution for `github.com`). Per `AGENTS.md`, this note advances the recorded distinct evidence fallback without claiming executable proof.

This extends the LAB-093 design chain. The target failure modes are recursive trust in transparency/witness infrastructure, cross-log suppression/equivocation, selective withholding in randomness fallback, semantic false-positive repair attestations, and self-certified verifier provenance.

## Primary donors

1. RFC 9162, Certificate Transparency v2 — append-only Merkle logs, consistency proofs, MMD, signed tree heads and signed evidence of log misbehavior:
   https://www.rfc-editor.org/rfc/rfc9162.html
2. transparency.dev Witness Network — a witness cosigns only checkpoints consistent with the checkpoint history it previously accepted; witness quorum is split-view resistance, not semantic validation of leaf contents:
   https://blog.transparency.dev/can-i-get-a-witness-network
3. transparency.dev transparent keyserver design — witness cosignatures protect non-equivocation for clients while semantic monitoring remains a separate role:
   https://blog.transparency.dev/building-a-transparent-keyserver
4. drand documentation — threshold/publicly-verifiable randomness and group resharing; useful for separating beacon cryptographic continuity from operator/control-domain continuity:
   https://docs.drand.love/
5. in-toto specification — project-owner-controlled layouts designate authorized functionaries and may require threshold matching link metadata for a step; verification checks both signer authorization and reported materials/products:
   https://github.com/in-toto/specification/blob/master/in-toto-spec.md
6. Sigstore security/threat model — transparency makes issuance/signatures auditable but does not make an artifact semantically good; TUF trust root supplies service-key revocation; monitoring is required for compromise detection:
   https://docs.sigstore.dev/about/security/
   https://docs.sigstore.dev/about/threat-model/
7. SLSA provenance concepts — provenance is an attestation about build inputs/process/identity; provenance validity is distinct from whether the resulting artifact is correct or safe:
   https://slsa.dev/spec/v1.0/provenance

## Frozen distinctions

The following implications are forbidden:

```text
VALID_LOG_SIGNATURE != CURRENT_LOG_AUTHORITY
VALID_WITNESS_SIGNATURE != CURRENT_WITNESS_MEMBERSHIP
WITNESSED_CHECKPOINT != SEMANTICALLY_TRUE_LEAVES
CROSS_LOG_INCLUSION != GLOBAL_LATESTNESS
MULTIPLE_LOGS != MULTIPLE_INDEPENDENT_CONTROL_DOMAINS
MULTIPLE_BEACON_OUTPUTS != UNBIASED_COMPOSITION
MULTIPLE_REPAIR_SIGNATURES != INDEPENDENT_SEMANTIC_REPRODUCTION
VALID_PROVENANCE_ATTESTATION != VERIFIER_INDEPENDENCE_PROVEN
VERIFIER_SELF_ATTESTATION != INDEPENDENCE_EVIDENCE
REVOCATION != HISTORICAL_EVIDENCE_ERASURE
```

## 1. Transparency-log authority lifecycle without circular self-trust

### 1.1 `TransparencyLogAuthorityV1`

Each accepted log authority generation is externally authenticated and contains at minimum:

- `lineage_id`
- `generation`
- `log_id`
- `log_public_key`
- `predecessor_digest`
- `not_before` / `not_after` or equivalent freshness policy reference
- `witness_policy_generation`
- `cross_log_policy_generation`
- `recovery_authority_reference`
- canonical digest/signatures

A log cannot make a new log key authoritative merely by placing that key in its own log. Self-inclusion can be evidence of publication only after an independently trusted authority transition already exists.

### 1.2 Rotation

Normal rotation requires predecessor continuity plus the current externally trusted authority policy. A later generation is accepted only after:

1. predecessor-authorized transition verifies;
2. transition is independently retained outside the rotating log;
3. configured transparency publication profile is satisfied;
4. required witness/cross-log observations are satisfied;
5. no same-lineage/same-generation conflicting digest exists.

Same lineage + generation + different authenticated digest is `LOG_AUTHORITY_EQUIVOCATION_CONFLICT`; newest timestamp/LWW/fastest mirror must not resolve it.

### 1.3 Compromise recovery

If the threshold controlling the current log authority is compromised, that authority cannot alone bless its successor. Recovery must chain from an independently retained recovery authority, higher root, or explicitly new lineage established out of band.

This mirrors the already frozen TUF-derived rule: a fully compromised trust root cannot safely repair itself by issuing one more signed root.

### 1.4 Witness authority lifecycle

`WitnessSetAuthorityV1` is a separate versioned object containing witness identities/keys, threshold, independence constraints, predecessor digest and recovery authority.

A witness set cannot certify its own membership generation solely by cosigning the membership document. Membership rotation must be authorized by the predecessor witness-set authority/recovery chain and published outside the affected witness set.

`WITNESS_KEY_ROTATION != NEW_INDEPENDENT_WITNESS` remains mandatory.

## 2. Cross-log anchoring: what it proves and what it does not

Define `CrossLogAnchorV1` over an exact source-log checkpoint digest, source log identity, source tree size, source checkpoint timestamp, destination log identity and destination inclusion proof/receipt.

### 2.1 Positive evidence obtained

Cross-log anchoring can provide positive evidence for:

- existence of a specific source checkpoint no later than the destination log's authenticated inclusion time;
- later source equivocation if the source presents an incompatible checkpoint for the same size/generation;
- suppression against a relying party when an independently retained destination anchor proves a newer source checkpoint existed than the source/mirror is presenting;
- survivability when one log becomes unavailable but another independent log has retained the anchor.

### 2.2 Not proven

Cross-log anchoring does **not** by itself prove:

- semantic correctness of source-log leaves;
- that no newer source checkpoint exists;
- that source and destination are independently controlled;
- that all mandatory events were admitted into the source log;
- that destination inclusion happened before an untrusted local clock time;
- that two logs under one operator/cloud/account are two independent failure domains.

Therefore:

```text
CROSS_LOG_ANCHORED_CHECKPOINT + INCOMPATIBLE_SOURCE_VIEW
    -> POSITIVE_STALENESS_OR_EQUIVOCATION_EVIDENCE

NO_NEWER_CROSS_LOG_ANCHOR_OBSERVED
    -> UNKNOWN, not proof of latestness
```

## 3. Multi-beacon anti-bias composition under partial compromise

### 3.1 Threat model

Some beacon contributors/operators may:

- know their own output before honest parties learn it;
- selectively withhold after observing other outputs;
- control multiple nominal endpoints;
- delay delivery to chosen verifiers;
- force a fallback path after seeing an unfavorable value.

A simple `XOR(all outputs received before timeout)` is not safe against adaptive withholding if an adversary can choose whether its already-known contribution participates after seeing honest outputs. That gives a last-revealer selection channel.

### 3.2 Frozen safe profiles

#### Profile B0 — one threshold beacon

Use one cryptographically threshold-produced beacon whose output cannot be chosen by a single participant and is publicly verifiable. Loss of threshold is availability failure; do not silently weaken to local PRNG.

#### Profile B1 — precommitted ordered fallback

Before any round output is known, freeze:

- eligible beacon set;
- independence/control-domain classification;
- exact ordered fallback list;
- timeout policy;
- combination rule;
- epoch/population commitment.

If primary output is unavailable by the predeclared deadline, advance exactly to the predeclared fallback. Never select among available outputs based on their values.

This is primarily availability-diversity, not simultaneous-composition security.

#### Profile B2 — commit/reveal contributions

For simultaneously combined independent contributors, each contributor commits to its contribution before any contribution is revealed. Reveals are checked against commitments. The final output is derived only under a predeclared completion rule.

If a committed contributor withholds after reveal begins, the round must either:

- fail closed; or
- use a protocol where the missing committed contribution is recoverable from threshold/VSS shares without letting the contributor choose participation after seeing others.

Do **not** simply drop the missing contribution and recompute.

#### Profile B3 — combine independently finalized beacon outputs

If each component beacon finalizes its output independently of the challenge scheduler and before the scheduler can decide inclusion, freeze exact component epochs and derive:

```text
R = H(domain || policy_generation || epoch || beacon_id_1 || output_1 || ... || beacon_id_n || output_n)
```

All required component outputs are mandatory. Missing required output yields `RANDOMNESS_QUORUM_UNAVAILABLE`, unless the precommitted policy specified a fallback *before* any component values became available.

### 3.3 Common-control denominator

Beacon key count, endpoint count and geographic region count do not define independence. Record operator, trust root, key ceremony, cloud/account, implementation and upstream randomness dependencies. Multiple components with one effective controller collapse to one control domain for anti-collusion assurance.

## 4. Semantic repair-attestation quorum

Witnessing a repair manifest only proves that the manifest was published consistently. It does not prove that the repair reconstructs the intended archive or restores independence.

Define `SemanticRepairAttestationV1` over:

- immutable repair-manifest digest;
- exact predecessor manifest/checkpoint;
- reconstructed canonical prefix/root;
- erasure reconstruction result;
- fragment hashes and required `k`;
- destination destructive-domain registry generation;
- observed destructive-domain provenance;
- parser/canonicalizer/verification algorithm versions;
- verifier provenance digest;
- result and explicit failure class.

### 4.1 Reproduction rule

An attester must independently obtain/reconstruct the evidence required by the semantic policy. Merely reading another attester's result and cosigning it is not a second semantic attestation.

For a policy requiring threshold `t`, the verifier counts only attestations that:

1. are authorized by the current semantic-attester policy;
2. bind the exact same manifest/predecessor/result digest;
3. come from sufficiently independent verification provenance domains;
4. report matching canonical outputs;
5. were produced without sharing an untrusted intermediate result as the sole source of truth.

### 4.2 Divergence

If authorized independent attesters disagree on canonical reconstruction/root or independence classification, the result is `SEMANTIC_REPAIR_ATTESTATION_CONFLICT`, not majority-LWW.

A threshold may establish a policy-defined assurance level only after conflicts are resolved or explicitly adjudicated under a separate adjudication authority. Quorum cannot make contradictory deterministic outputs simultaneously true.

### 4.3 Relationship to in-toto

in-toto is a useful donor because a project owner defines authorized functionaries and threshold, and threshold link metadata is expected to report matching step products. The lab extension is stricter for repair: the policy additionally classifies verifier implementation/control independence and treats deterministic-output divergence as a conflict requiring adjudication.

## 5. Verifier-provenance attestation authority and revocation

### 5.1 Separate roles

Use distinct objects/roles:

- `VerifierIdentityAuthorityV1`: who may operate a verifier identity/key;
- `VerifierProvenanceAttestationAuthorityV1`: who may attest source/build/runtime/control provenance about a verifier;
- `VerifierIndependencePolicyV1`: how provenance dimensions map to effective independence;
- `VerifierProvenanceRevocationV1`: compromise/revocation notice;
- `VerifierProvenanceAdjudicationV1`: resolution of conflicting provenance claims.

A verifier must not be the sole authority allowed to certify its own independence. Self-reported metadata is evidence input, not independence proof.

### 5.2 Provenance dimensions

At minimum bind:

- source repository/commit/lineage;
- parser/canonicalizer implementation;
- cryptographic implementation/library;
- compiler/toolchain and build recipe;
- builder/build-control domain;
- binary digest/reproducibility evidence;
- runtime image/host/control domain;
- key custody/signing domain;
- operator/administrative domain;
- relevant shared upstream dependencies.

### 5.3 Revocation semantics

Revocation is append-only evidence about current reliance. It does not erase historical attestations.

Distinguish:

- identity-key compromise;
- attestation-authority compromise;
- provenance fact later shown false;
- shared dependency newly discovered;
- implementation vulnerability;
- algorithm compromise.

Each can reduce current effective independence differently.

If the provenance-attestation authority itself is compromised, its post-compromise attestations cannot bootstrap a trusted successor. Recovery requires independent recovery authority / higher trust root / new lineage, and independently retained transparency evidence.

### 5.4 Sigstore/TUF lesson

Sigstore's threat model is a useful boundary: transparency enables detection/auditability of compromised issuance and TUF supplies service trust-root revocation, but signed/transparency-logged evidence still does not prove that the artifact is good. The lab therefore treats provenance attestations as authenticated claims whose semantic truth and independence remain policy/audit subjects.

## 6. State machine additions

Recommended explicit states:

```text
LOG_AUTHORITY_CURRENT
LOG_AUTHORITY_LATESTNESS_UNKNOWN
LOG_AUTHORITY_STALE_PROVEN
LOG_AUTHORITY_EQUIVOCATION_CONFLICT

WITNESS_SET_CURRENT
WITNESS_SET_QUORUM_DEGRADED
WITNESS_SET_EQUIVOCATION_CONFLICT

CROSS_LOG_ANCHOR_VALID
CROSS_LOG_SOURCE_STALE_PROVEN
CROSS_LOG_INDEPENDENCE_UNKNOWN

RANDOMNESS_READY
RANDOMNESS_QUORUM_UNAVAILABLE
RANDOMNESS_FALLBACK_USED_PRECOMMITTED
RANDOMNESS_POLICY_VIOLATION_ADAPTIVE_SELECTION

SEMANTIC_REPAIR_ATTESTED
SEMANTIC_REPAIR_ATTESTATION_CONFLICT
SEMANTIC_REPAIR_ASSURANCE_INSUFFICIENT

VERIFIER_PROVENANCE_CURRENT
VERIFIER_PROVENANCE_CONFLICT
VERIFIER_PROVENANCE_REVOKED_CURRENT_RELIANCE
VERIFIER_INDEPENDENCE_DEGRADED
```

## 7. RED-first matrix

Executable tests remain pending. Minimum cases to implement before production refactor:

### A. Log/witness authority lifecycle
1. predecessor-authorized log-key rotation accepted;
2. self-logged unexternally-authorized log key rejected;
3. same generation/different log-key digest -> conflict;
4. compromised current log authority cannot self-recover;
5. independently authorized recovery generation accepted;
6. witness key rotation preserves witness identity, not independence count;
7. witness set cannot self-authorize membership solely through its own quorum;
8. removed witness remains historical denominator for old checkpoint policy;
9. stale but valid witness-set generation cannot authorize new checkpoint after proven newer generation;
10. witness-set same-generation conflicting membership -> conflict;
11. log authority valid but latestness unknown -> consequential mutation blocked;
12. witness quorum degraded after late compromise -> current assurance downgraded, historical cosignatures retained.

### B. Cross-log anchoring
13. source checkpoint anchored in independent destination verifies existence;
14. source later serves incompatible same-size root -> positive equivocation evidence;
15. source serves older checkpoint while destination retained newer source checkpoint -> stale proven;
16. absence of newer destination anchor does not prove source latestness;
17. source+destination under same control domain collapse independence count;
18. destination receipt without source checkpoint binding rejected;
19. cross-log anchor proves publication but not leaf semantic truth;
20. destination unavailable but retained inclusion proof/checkpoint still verifies historical anchor;
21. destination log later equivocates -> anchor reliance re-appraised;
22. cross-log cycle A->B->A does not manufacture independent trust.

### C. Multi-beacon anti-bias
23. primary threshold beacon success accepted;
24. threshold unavailable -> no silent local PRNG fallback;
25. ordered fallback declared pre-round and used after primary timeout accepted;
26. scheduler selects fallback after seeing primary value -> policy violation;
27. XOR of reveal-now/drop-later malicious contribution -> rejected/fail closed;
28. commit/reveal with all commitments revealed accepted;
29. committed contribution withheld after reveals -> fail closed unless protocol recovers exact committed contribution;
30. dropping missing committed contributor and recomputing rejected;
31. independently finalized required beacon set all present -> hash-composition accepted;
32. one required finalized beacon missing -> unavailable unless precommitted fallback applies;
33. two beacon endpoints same operator/key ceremony collapse independence;
34. beacon replay from wrong epoch rejected;
35. beacon value valid but population commitment created after value known rejected;
36. fallback policy generation changed mid-round rejected.

### D. Semantic repair attestations
37. two independent reproductions same canonical prefix/root count toward quorum;
38. two signatures over one copied reproduction do not count as independent semantic reproduction;
39. same manifest, different reconstructed root -> conflict;
40. matching root but insufficient destructive-domain independence -> assurance insufficient;
41. matching erasure `k` but stale registry generation -> rejected;
42. attestation over wrong predecessor manifest rejected;
43. witnessed manifest without semantic attestations not considered semantically repaired;
44. semantic quorum without transparency publication does not create authoritative repair history if policy requires publication;
45. attester later compromised -> current reliance re-appraised, historical evidence retained;
46. deterministic divergence cannot be resolved by newest timestamp;
47. parser-version mismatch outside allowed policy -> non-comparable/conflict;
48. exact independent replay by third verifier reproduces accepted result.

### E. Verifier provenance authority/revocation
49. verifier self-attestation alone does not establish independence;
50. authorized external provenance attestation accepted as claim evidence;
51. same verifier/generation conflicting provenance -> conflict;
52. provenance authority compromise revokes current reliance on affected claims;
53. compromised provenance authority cannot self-recover successor;
54. independently authorized successor accepted with continuity evidence;
55. two binaries from same source/toolchain/build account are not automatically independent;
56. reproducible byte equality corroborates build inputs but not semantic correctness;
57. two verifiers share parser library -> parser-family independence collapses;
58. two verifiers share crypto library -> crypto-implementation independence collapses;
59. separate parser+crypto+builder but same runtime/admin control -> operational independence degraded;
60. late disclosure of shared upstream dependency re-appraises current quorum;
61. revocation does not delete historical attestations;
62. expired/stale provenance generation cannot support new consequential decision;
63. attestation-authority key rotation does not create a new independent attestation authority;
64. conflicting provenance claims require adjudication/fail closed, not majority metadata overwrite.

## 8. Audit conclusions

1. Transparency and witnesses solve authenticated history/non-equivocation dimensions, not semantic truth.
2. Cross-log anchoring is strongest when it provides independently retained positive evidence of an incompatible/newer source view; lack of an anchor remains absence of evidence.
3. Multi-beacon fallback is safe only when selection semantics are frozen before values are knowable. Adaptive post-value fallback/reselection is a bias channel.
4. Semantic repair quorum must count independent reproductions, not cosignatures over one producer's result.
5. Verifier provenance authority must be external to the verifier for independence claims, versioned/revocable, and itself recoverable without circular self-trust.
6. Late compromise or common-mode disclosure changes current reliance; historical receipts and attestations remain evidence and are never rewritten.

## 9. Implementation direction

Do not implement production refactors from this design freeze until exact source execution returns. First add RED tests corresponding to the matrix above, then introduce the smallest versioned policy/state objects needed to make them GREEN. Keep LAB-086 priority #1 and its draft gate unchanged.

## Next distinct evidence task if exact execution is still unavailable

Freeze **witness-gossip partition recovery / cross-log anchor obligation completeness + threshold-beacon liveness certificates / semantic-attester independence challenge protocol / provenance-authority transparency and key-compromise effective-time semantics**. In particular: define how a long network partition rejoins without accepting a selectively truncated witness history; how mandatory cross-log anchoring can produce positive omission evidence when an anchor is promised but withheld; how to distinguish beacon unavailability from malicious withholding with signed liveness evidence; how to challenge semantic attesters for independent reconstruction rather than copied outputs; and how revocation effective-time interacts with artifacts/attestations created before versus after a provenance-authority key compromise.