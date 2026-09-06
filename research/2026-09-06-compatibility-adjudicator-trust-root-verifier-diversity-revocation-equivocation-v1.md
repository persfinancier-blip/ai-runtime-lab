# Compatibility adjudicator trust-root, verifier-diversity, revocation and proof-equivocation — V1 frozen contract

Date: 2026-09-06
Status: `COMPATIBILITY_ADJUDICATOR_TRUST_ROOT_VERIFIER_DIVERSITY_REVOCATION_EQUIVOCATION_V1_FROZEN`
Scope: LAB-093 design follow-up; no production implementation or behavioral PASS is claimed.

## 1. Why this contract exists

The preceding compatibility-proof work froze deterministic proof bundles and independent adjudication. That is insufficient unless the runtime can answer four additional questions without circular trust:

1. **Who is allowed to adjudicate a consequential compatibility edge?**
2. **What does “independent verifier” mean when two implementations may share the same parser, canonicalizer, semantic-diff engine, oracle library, dependency graph, maintainer lineage, build root, or signing key?**
3. **What happens to already-issued PASS attestations after a verifier key, implementation, dependency, or oracle lineage is compromised or found unsound?**
4. **How is equivocation detected when an apparently valid adjudicator signs contradictory verdicts for the same proof state?**

The answer is not “count signatures.” Thresholds improve key compromise tolerance only when the admitted signers and semantic implementations are themselves independently authorized and their trust state is monotonic.

This document therefore freezes a trust plane for compatibility adjudication. It is deliberately stricter than ordinary signature validation: cryptographic validity proves who signed a statement, not that the signer was currently authorized, semantically independent, uncompromised, non-revoked, or consistent with its own prior statements.

## 2. Primary donor mechanisms

### 2.1 The Update Framework (TUF)

TUF is the donor for threshold trust roots, signed root rotation, and rollback resistance. Its root role delegates keys/thresholds for other roles, and a root update must be authorized by both the old and new root thresholds while advancing the root version. This is the right shape for verifier-trust-root rotation: a new trust root cannot self-authorize and an older internally valid root cannot silently regain authority.

Primary source:
- https://theupdateframework.github.io/specification/draft/

Relevant mechanisms adopted as donors:
- threshold-authorized trust metadata;
- old-root + new-root authorization for trust-root transition;
- monotonic version/frontier checks;
- explicit revocation through subsequent trusted metadata;
- fail-closed handling of rollback.

LAB does **not** inherit TUF's software-update semantics wholesale. The trust object here is adjudication authority over compatibility proof bundles, with semantic-lineage and equivocation constraints that TUF does not define.

### 2.2 Sigstore trust roots and transparency

Sigstore is the donor for separating artifact/proof signatures from the trust roots used to validate signer identities and transparency-log evidence. Sigstore documents TrustRoot objects containing certificate authorities, transparency-log keys and timestamp authorities, and its Rekor security model emphasizes append-only third-party-verifiable history whose long-term value depends on monitoring.

Primary sources:
- https://docs.sigstore.dev/about/security/
- https://docs.sigstore.dev/policy-controller/overview/

Relevant mechanisms adopted as donors:
- explicit trusted identities/roots rather than accepting any valid signature;
- separation of signing identity from transparency evidence;
- append-only public/auditable attestations;
- monitoring as a requirement for detecting inconsistent behavior.

LAB adds a stronger rule: transparency inclusion authenticates existence/history but cannot by itself establish semantic correctness of a compatibility verdict.

### 2.3 RFC 9162 Certificate Transparency

RFC 9162 is the donor for the split-view/equivocation threat. It explicitly recognizes a log presenting conflicting Merkle-tree views to different parties and notes that comparing signed tree heads (gossip) is a way to detect append-only violations/split views.

Primary source:
- https://www.rfc-editor.org/rfc/rfc9162.html

Relevant mechanism adopted as donor:
- contradictory signed views are durable evidence of misbehavior;
- independent comparison of authenticated views is necessary because a single verifier talking to a single authority may see a coherent but false split view.

LAB applies the same shape to adjudicator attestations and verifier-trust metadata.

### 2.4 SLSA provenance verification

SLSA is the donor for verifying provenance against a configured root of trust and for rejecting unrecognized external parameters rather than treating signed but unexpected statements as acceptable.

Primary source:
- https://slsa.dev/spec/v1.0-rc2/verifying-artifacts

LAB extends this principle: every adjudicator capability, semantic lineage, toolchain generation, and dependency commitment must be recognized by current verifier-trust metadata. A cryptographically valid attestation carrying an unrecognized or out-of-scope capability fails closed.

## 3. Trust objects and identities

Every consequential adjudication is bound to the following immutable identities.

### 3.1 `verifier_trust_root_generation`

Content-addressed canonical trust metadata containing:

- trust-root generation/version;
- predecessor trust-root digest, except genesis;
- effective frontier;
- root-authority public keys and threshold;
- authorized adjudicator identities;
- each adjudicator's capability scope;
- semantic-lineage declaration;
- build/toolchain/dependency commitments;
- allowed proof-bundle schema generations;
- allowed oracle/fixture/mutant generations;
- revocations and quarantine records;
- minimum diversity policy;
- expiry/freshness bounds where applicable;
- transition signatures from old and new root authority for non-genesis rotation.

The digest of this object is the trust-root identity. Human-readable names are metadata only.

### 3.2 `adjudicator_generation`

An adjudicator identity is not merely a public key. It is a tuple committing to:

- signing identity/key generation;
- implementation source digest;
- build provenance/build recipe identity;
- semantic parser/canonicalizer lineage;
- semantic-diff engine lineage;
- fixture synthesizer lineage;
- oracle/metamorphic-relation lineage;
- critical transitive dependency closure;
- supported proof-bundle generations;
- declared capability scope;
- independence-domain labels.

Any change in an authority-relevant component creates a new `adjudicator_generation` even if the product name and signing key remain the same.

### 3.3 Capability scope

Trust metadata grants explicit scopes such as:

- `VERIFY_BUNDLE_INTEGRITY`
- `RECONSTRUCT_OBLIGATIONS`
- `EXECUTE_MUTANT_SUITE`
- `EVALUATE_METAMORPHIC_RELATIONS`
- `ADJUDICATE_REQUEST_EFFECT`
- `ADJUDICATE_HISTORICAL_REPLAY`
- `ADJUDICATE_EVIDENCE`
- `ADJUDICATE_RECONCILIATION`
- `ADJUDICATE_DISCLOSURE`

A signer authorized only for bundle-integrity verification cannot satisfy semantic adjudication threshold.

## 4. Monotonic verifier-trust frontier

Every verifier-trust decision is evaluated at an authenticated monotonic frontier `F`.

An admissible compatibility attestation binds:

`(bundle_id, compatibility_edge_id, verdict, obligation_root, trust_root_generation, trust_frontier, adjudicator_generation, capability_scope, semantic_lineage_root, toolchain_root, timestamp/sequence, attestation_id)`

Rules:

1. An attestation issued under trust frontier `F_old` may remain archival evidence after `F_new > F_old`, but it does not automatically retain admission authority.
2. Admission at the current frontier requires either:
   - the attestation's adjudicator generation remains explicitly valid under current trust metadata; or
   - a current revalidation statement explicitly carries the prior result forward after checking all revocations/quarantines and proof-bundle compatibility.
3. A restored backup containing an older, internally valid trust root cannot lower the externally authenticated/global frontier.
4. Trust-root rotation follows old+new authorization analogous to TUF root rotation. The new root cannot self-authorize.
5. Missing intermediate trust-root generations fail closed unless an explicitly defined and independently authenticated recovery transition exists.

## 5. Diversity is semantic, not process-count diversity

Two processes, containers, binaries, hosts, regions, keys, or vendors do **not** automatically constitute two independent verifiers.

### 5.1 Diversity graph

Each adjudicator generation declares a content-addressed dependency/lineage graph. Nodes include at minimum:

- parser/model loader;
- canonicalizer/normalizer;
- semantic-diff engine;
- compatibility rule set;
- fixture synthesizer;
- mutant generator;
- oracle/metamorphic engine;
- proof-bundle decoder;
- critical crypto verification library;
- generated schema/DTO compiler where semantically relevant;
- build pipeline/toolchain root;
- critical third-party semantic dependencies.

Edges identify derivation/use relationships.

### 5.2 Independence classes

For each consequential verdict dimension, trust policy declares which lineage classes must differ. Example:

- request-effect adjudication: independent semantic parser/canonicalizer **and** independent request-effect oracle lineage;
- historical replay: independent replay adapter/oracle lineage;
- signing-scope semantics: independent signing canonicalizer/expected-string construction lineage;
- model compatibility: independent semantic-diff implementation or an independently derived metamorphic oracle able to distinguish the disputed delta.

### 5.3 Common-mode dependency collapse

If two adjudicators share any dependency marked `COMMON_MODE_CRITICAL` for the disputed obligation, they count as one diversity domain for that obligation unless there is a separate proof that the shared dependency cannot influence the verdict.

A shared library hidden behind different wrappers, a fork with no semantic changes, the same generated code, or the same test oracle copied into two repositories is not diversity.

### 5.4 Independence evidence is obligation-specific

Diversity is evaluated against the exact obligation/semantic delta, not globally. Two verifiers may be independent for protobuf enum semantics but not for signing canonicalization if both reuse the same signing library.

## 6. Admission threshold

For a consequential PASS, the current trust policy requires:

1. complete deterministic proof bundle valid at current registry/model/policy frontier;
2. at least the configured threshold of currently authorized adjudicators;
3. each signer possesses the required capability scope;
4. diversity graph satisfies the obligation-specific independence policy;
5. all required adjudicators reproduce the same obligation root;
6. all required adjudicators agree on the verdict and relevant semantic witness roots;
7. no signer is revoked, quarantined, stale, or outside allowed toolchain/schema generations;
8. no unresolved equivocation exists for the same adjudicator generation and adjudication key;
9. no current trust-root rule marks the proof bundle or affected lineage as `REVALIDATION_REQUIRED`.

Threshold arithmetic is performed **after** capability, freshness, revocation, and diversity collapse. Three signatures from one collapsed common-mode domain count as one domain, not three.

## 7. Revocation and quarantine

Revocation and quarantine are distinct.

### 7.1 Revocation

`REVOKED` means the adjudicator generation or key is no longer trusted for new admission. Reasons include:

- signing-key compromise;
- malicious implementation;
- proven semantic unsoundness affecting all outputs in scope;
- untraceable build/provenance compromise;
- unauthorized capability expansion.

Revocation is monotonic at the trust frontier. Reusing the same key or generation identifier is forbidden.

### 7.2 Quarantine

`QUARANTINED` means admission is suspended while impact is bounded. Reasons include:

- newly discovered common-mode oracle defect;
- unresolved dependency vulnerability that could affect verdicts;
- unexplained nondeterminism;
- contradictory attestation awaiting adjudication;
- provenance gap;
- discovered misdeclared diversity relationship.

Quarantined attestations remain evidence but cannot satisfy a new PASS threshold.

### 7.3 Blast-radius index

Every attestation index must support reverse lookup by:

- adjudicator generation;
- signing key generation;
- semantic-lineage node;
- dependency digest;
- oracle generation;
- toolchain/build root;
- trust-root generation;
- proof-bundle schema generation.

A revocation/quarantine therefore computes an explicit affected-edge set. “Re-run everything” may be conservative but is not sufficient as the only recovery specification.

### 7.4 Historical PASS after revocation

Historical PASS does not become false merely because a key rotates. Admission status is derived from revocation reason and effective interval:

- routine key retirement: historical attestations can remain acceptable if signed while valid and no semantic compromise exists;
- key compromise with unknown start: all attestations from the bounded/unknown compromise interval become `REVALIDATION_REQUIRED`;
- semantic verifier defect introduced at generation G: all edges whose obligation cone intersects the defective lineage at G+ become `REVALIDATION_REQUIRED` regardless of signature validity;
- malicious equivocation: affected scope is quarantined at least from the earliest provable contradictory statement, with policy allowed to widen conservatively.

## 8. Equivocation definition

An adjudicator equivocates when it produces two cryptographically valid, authority-relevant attestations that cannot both be true under the same adjudication key.

Canonical adjudication key:

`K = (bundle_id, compatibility_edge_id, trust_frontier, adjudicator_generation, obligation_root)`

Examples of contradiction:

- `PASS` and `FAIL` for the same K;
- two different obligation roots while claiming complete reconstruction for the same bundle/edge/frontier/generation;
- same verdict but incompatible witness roots when both are declared complete/canonical;
- two different semantic-lineage roots while reusing the same adjudicator-generation identifier;
- same attestation sequence number bound to different content.

Benign revision is not represented by overwriting/re-signing under the same K. A legitimate correction must advance an explicit adjudication revision/sequence and state that it supersedes a prior attestation; current policy then determines whether the prior event itself requires quarantine.

## 9. Equivocation evidence and response

### 9.1 Durable equivocation proof

An equivocation proof contains both complete signed attestations plus the trust-root evidence showing each was authorized at issuance. The proof is content-addressed and append-only.

### 9.2 Immediate response

Upon a valid equivocation proof:

1. mark the adjudicator generation `QUARANTINED_EQUIVOCATION` at the next authenticated trust frontier;
2. remove its attestations from threshold counts for new admissions;
3. identify every currently admitted compatibility edge that depended on that adjudicator beyond the remaining threshold/diversity margin;
4. move those edges to `REVALIDATION_REQUIRED` or stricter state;
5. preserve the contradictory attestations as evidence;
6. forbid “pick the PASS,” “pick the latest,” majority voting between the two statements, or deleting the unfavorable statement.

### 9.3 Split-view trust metadata

Contradictory valid trust-root/frontier views are themselves a trust-plane equivocation. Clients/verifiers compare authenticated frontier/checkpoint statements through an independent/global continuity channel. Until the split view is resolved, consequential admission fails closed.

This adopts the RFC 9162 lesson: a locally coherent signed view is insufficient protection against an authority presenting different views to different parties.

## 10. Key and implementation rotation

### 10.1 Routine key rotation

Routine key rotation produces a new key generation under the same semantic adjudicator generation only when implementation/toolchain/lineage are unchanged and this fact is authenticated by trust-root transition metadata.

### 10.2 Implementation/toolchain rotation

Any authority-relevant implementation, oracle, semantic dependency, compiler/codegen, build root, or policy change creates a new `adjudicator_generation` and requires fresh diversity evaluation.

### 10.3 Compromise recovery

After key/toolchain compromise:

1. advance trust root with old+new threshold if old threshold remains trustworthy;
2. otherwise use the separately defined out-of-band/root-recovery authority — never a self-signed replacement;
3. revoke/quarantine compromised generations;
4. calculate affected proof edges from blast-radius index;
5. re-adjudicate affected edges with currently authorized independent generations;
6. append revalidation attestations at the new frontier;
7. never delete old compromised/equivocating evidence merely to make history look clean.

### 10.4 Re-admission

A previously revoked generation is never “unrevoked.” A fixed implementation is a new generation. Re-admission requires normal root authorization and diversity evaluation from scratch.

## 11. Threshold degradation

If revocation or quarantine reduces the available authorized/diverse set below policy threshold:

- consequential compatibility admission stops;
- existing admitted edges whose historical threshold remains sound may continue only if current policy explicitly permits grandfathered operation and no affected semantic compromise exists;
- edges depending on affected adjudicators enter `REVALIDATION_REQUIRED`;
- threshold is **not** automatically lowered to restore availability;
- emergency threshold changes are trust-root policy changes and require the normal high-authority transition path.

Availability pressure is not authority to weaken the proof threshold.

## 12. Archive, backup and restore semantics

Every archived proof bundle/attestation set includes the trust-root generation and authenticated frontier at which it was evaluated.

Restore rules:

1. restored trust metadata may be used as archival evidence;
2. it cannot lower a newer externally/global authenticated trust frontier;
3. restored attestations from revoked/quarantined generations are re-evaluated under current revocation history;
4. an archive missing a required revocation/equivocation segment is incomplete, not evidence that the revocation never happened;
5. cryptographic validity of an old root does not restore current admission authority.

## 13. Canonical records

### 13.1 Trust-root record

```text
VerifierTrustRootV1 {
  version
  predecessor_root_digest
  effective_frontier
  root_keys[]
  root_threshold
  adjudicators[] {
    adjudicator_generation
    signing_key_generations[]
    capability_scopes[]
    semantic_lineage_root
    dependency_root
    toolchain_root
    independence_domains[]
    valid_from_frontier
    valid_until_frontier?
    status
  }
  diversity_policy_root
  revocations[]
  quarantines[]
  accepted_bundle_schema_generations[]
  transition_authorizations[]
}
```

### 13.2 Adjudication attestation

```text
CompatibilityAdjudicationV1 {
  bundle_id
  compatibility_edge_id
  verdict
  obligation_root
  witness_root
  trust_root_generation
  trust_frontier
  adjudicator_generation
  signing_key_generation
  capability_scope
  semantic_lineage_root
  dependency_root
  toolchain_root
  adjudication_sequence
  issued_at_evidence
}
```

### 13.3 Equivocation record

```text
EquivocationProofV1 {
  adjudication_key
  attestation_a_digest
  attestation_b_digest
  contradiction_class
  authorization_evidence_root
  detection_frontier
}
```

## 14. Fail-closed states

At minimum the implementation must distinguish:

- `TRUST_ROOT_UNKNOWN`
- `TRUST_ROOT_ROLLBACK`
- `TRUST_ROOT_SPLIT_VIEW`
- `ADJUDICATOR_UNAUTHORIZED`
- `ADJUDICATOR_SCOPE_MISMATCH`
- `ADJUDICATOR_REVOKED`
- `ADJUDICATOR_QUARANTINED`
- `ADJUDICATOR_STALE`
- `DIVERSITY_INSUFFICIENT`
- `COMMON_MODE_DEPENDENCY`
- `THRESHOLD_DEGRADED`
- `EQUIVOCATION_DETECTED`
- `REVALIDATION_REQUIRED`
- `ATTESTATION_FRONTIER_STALE`
- `ATTESTATION_LINEAGE_MISMATCH`

None of these may silently downgrade to PASS.

## 15. Explicit RED-first matrix — 80 cases

The production implementation must begin by making the following cases executable RED tests. Group labels are part of the frozen contract.

### A. Trust-root identity and rotation (A01–A08)
1. A01 — valid attestation under an unknown trust-root generation is rejected.
2. A02 — older internally valid root cannot replace newer authenticated frontier.
3. A03 — new root signed only by new-root keys is rejected.
4. A04 — new root signed only by old-root threshold but not new-root threshold is rejected.
5. A05 — skipped intermediate root generation is rejected without explicit recovery proof.
6. A06 — root metadata with same version but different bytes is split-view/equivocation evidence.
7. A07 — expired/stale root beyond policy freshness cannot authorize new PASS.
8. A08 — restored archive root cannot lower global frontier.

### B. Adjudicator identity and scope (B01–B08)
9. B01 — valid signature from unregistered key is rejected.
10. B02 — registered key with wrong adjudicator generation is rejected.
11. B03 — `VERIFY_BUNDLE_INTEGRITY` signer cannot satisfy semantic adjudication.
12. B04 — attestation claiming undeclared capability scope is rejected.
13. B05 — source digest drift under reused generation identifier is rejected.
14. B06 — toolchain root drift under reused generation identifier is rejected.
15. B07 — dependency root drift under reused generation identifier is rejected.
16. B08 — same product name/new key without trust-root authorization is rejected.

### C. Diversity/common-mode collapse (C01–C08)
17. C01 — two processes running identical binary count as one domain.
18. C02 — two containers with same semantic lineage count as one domain.
19. C03 — two wrappers around same oracle library count as one for oracle-dependent obligation.
20. C04 — fork with cosmetic changes only does not create independence.
21. C05 — shared generated canonicalizer marked critical collapses signing-semantics diversity.
22. C06 — shared parser is allowed only when proof establishes parser cannot affect disputed obligation.
23. C07 — independence for enum semantics does not imply independence for signing semantics.
24. C08 — hidden transitive common-mode dependency discovered after admission forces revalidation.

### D. Threshold arithmetic (D01–D08)
25. D01 — three signatures from one collapsed diversity domain do not satisfy 2-domain policy.
26. D02 — revoked signer is removed before threshold count.
27. D03 — quarantined signer is removed before threshold count.
28. D04 — stale signer generation is removed before threshold count.
29. D05 — capability-mismatched signer is removed before threshold count.
30. D06 — duplicate signature/key counts once.
31. D07 — threshold loss after revocation does not auto-lower policy.
32. D08 — mixed PASS/FAIL cannot be converted to PASS by majority vote.

### E. Revocation blast radius (E01–E08)
33. E01 — routine key retirement preserves sound pre-retirement history when policy allows.
34. E02 — key compromise with known start marks interval edges for revalidation.
35. E03 — key compromise with unknown start conservatively widens affected interval.
36. E04 — semantic defect affects all edges whose obligation cone intersects defective lineage.
37. E05 — unrelated edges outside proven blast radius remain distinguishable.
38. E06 — missing reverse dependency index fails closed rather than claiming unaffected state.
39. E07 — revoked generation cannot be unrevoked by later metadata.
40. E08 — fixed implementation with same human name must use new generation identity.

### F. Equivocation (F01–F08)
41. F01 — PASS and FAIL for same adjudication key produce equivocation proof.
42. F02 — two complete but different obligation roots for same key produce equivocation proof.
43. F03 — same sequence number/different contents produce equivocation proof.
44. F04 — same generation identifier/different semantic-lineage roots produce equivocation proof.
45. F05 — verifier cannot discard the unfavorable contradictory attestation.
46. F06 — “latest wins” cannot resolve contradictory same-key attestations.
47. F07 — equivocation quarantines signer for new admission before investigation completes.
48. F08 — every admitted edge relying on lost threshold/diversity margin enters revalidation.

### G. Split view and monitoring (G01–G08)
49. G01 — two clients receive different valid root views at same frontier; admission stops.
50. G02 — two clients receive contradictory authorized status for same adjudicator generation; admission stops.
51. G03 — single-client local consistency is insufficient after external split-view evidence appears.
52. G04 — stale monitor checkpoint cannot overwrite newer checkpoint.
53. G05 — missing consistency/continuity evidence at required boundary fails closed.
54. G06 — transparency inclusion without semantic authorization cannot satisfy PASS.
55. G07 — signed timestamp without current trust-root authorization cannot revive revoked signer.
56. G08 — monitor compromise does not grant adjudication capability.

### H. Rotation/recovery (H01–H08)
57. H01 — routine key rotation with unchanged lineage succeeds only through authorized trust transition.
58. H02 — implementation change under key-only rotation is rejected.
59. H03 — compiler/codegen semantic change creates new adjudicator generation.
60. H04 — compromised old root below threshold can be rotated normally.
61. H05 — threshold root compromise requires separate recovery authority, not self-signed replacement.
62. H06 — recovered signer cannot reuse revoked generation ID.
63. H07 — post-recovery re-admission requires fresh diversity evaluation.
64. H08 — recovery cannot delete compromise/equivocation history.

### I. Historical proof/frontier (I01–I08)
65. I01 — old proof bundle remains archival but loses new-admission authority after frontier advance when not carried forward.
66. I02 — current revalidation can explicitly carry forward sound old proof.
67. I03 — revalidation under revoked signer is rejected.
68. I04 — restored backup missing later revocation is incomplete, not clean history.
69. I05 — restored backup missing later equivocation proof cannot erase quarantine.
70. I06 — archived attestation with valid signature but stale trust root cannot satisfy current threshold.
71. I07 — historical PASS affected by semantic defect becomes `REVALIDATION_REQUIRED`.
72. I08 — unrelated historical PASS remains valid only with explicit blast-radius proof/current policy.

### J. Downgrade/substitution and operational pressure (J01–J08)
73. J01 — verifier toolchain downgrade under same generation ID is rejected.
74. J02 — fallback verifier with different key but undeclared lineage is rejected.
75. J03 — emergency outage does not permit threshold lowering without root-authorized policy change.
76. J04 — unavailable second diversity domain yields `DIVERSITY_INSUFFICIENT`, not one-verifier PASS.
77. J05 — nondeterministic adjudicator is quarantined rather than repeatedly retried until favorable output.
78. J06 — dependency substitution after build invalidates toolchain/dependency commitment.
79. J07 — proof schema widening unknown to trust root is rejected.
80. J08 — an old, valid, favorable attestation cannot override a newer fail-closed revalidation requirement.

## 16. Implementation order when executable source is available

1. Implement canonical trust-root/adjudicator/attestation/equivocation DTOs and hashing.
2. Implement append-only trust frontier with rollback/split-view checks.
3. Implement capability-scoped adjudicator registry.
4. Implement dependency/lineage graph and obligation-specific diversity collapse.
5. Implement threshold evaluation after diversity/revocation filtering.
6. Implement revocation/quarantine blast-radius index.
7. Implement equivocation detector and durable proof record.
8. Implement revalidation state machine.
9. Execute all 80 RED cases; demonstrate meaningful pre-fix failures.
10. Implement production behavior until matrix GREEN.
11. Run cross-generation archive/restore and root-rotation tests.
12. Audit that no compatibility PASS path bypasses current trust frontier, diversity, revocation, or equivocation checks.

## 17. Frozen decisions

`COMPATIBILITY_ADJUDICATOR_TRUST_ROOT_VERIFIER_DIVERSITY_REVOCATION_EQUIVOCATION_V1_FROZEN` means:

- A valid signature is necessary but insufficient for semantic adjudication authority.
- Trust authority is content-addressed, capability-scoped, generation-bound and evaluated at a monotonic authenticated frontier.
- Root rotation is dual-authorized by old and new roots; rollback fails closed.
- Verifier diversity is based on obligation-specific semantic lineage/dependency independence, not process/container/key/vendor count.
- Threshold arithmetic happens after diversity collapse and revocation/quarantine/scope filtering.
- Revocation and quarantine preserve evidence and remove admission authority; fixed implementations receive new generations rather than being “unrevoked.”
- Contradictory valid attestations for the same canonical adjudication key are equivocation evidence and trigger immediate quarantine/revalidation, not favorable-verdict selection or majority voting.
- Split-view trust metadata is a trust-plane failure; locally coherent signed views are not enough.
- Historical proof authority is re-evaluated under current trust/revocation frontier; archive restore cannot roll trust state backward.
- Production implementation remains blocked on executable exact-source RED/GREEN. No behavioral PASS is claimed by this design freeze.

## 18. Next distinct research seam

If exact source execution remains unavailable after this freeze, the next non-duplicative evidence task is:

**compatibility trust-frontier witness / split-view gossip / checkpoint-consistency contract** — define how independent witnesses exchange and persist verifier-trust checkpoints, how consistency/ancestry is proven across frontier advances, how clients detect withheld or forked trust metadata without trusting one distribution channel, witness quorum/diversity semantics, witness compromise/revocation, offline/air-gapped catch-up, and RED cases for freeze attacks, forked checkpoints, witness common-mode failure, stale gossip, partial network partition, archive replay and recovery after split-view detection.
