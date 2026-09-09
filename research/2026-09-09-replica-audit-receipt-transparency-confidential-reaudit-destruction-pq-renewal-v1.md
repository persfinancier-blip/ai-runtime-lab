# Replica audit freshness, receipt transparency, confidential re-audit, destruction evidence, and PQ renewal

Date: 2026-09-09
Status: FROZEN DESIGN / RED-first contract
Contract id: `REPLICA_AUDIT_RECEIPT_TRANSPARENCY_CONFIDENTIAL_REAUDIT_DESTRUCTION_PQ_RENEWAL_V1_FROZEN`

## Scope

This follow-up extends the LAB-093..100 evidence architecture without claiming executable closure. It addresses five unresolved boundaries: (1) replica-domain challenge/audit freshness and revocation of false independence, (2) transparent ingress receipts and positive non-inclusion proof, (3) confidential semantic-corpus auditor compromise and re-audit generations, (4) retention of destruction evidence without retaining unnecessary secrets, and (5) explicit PQ hybrid-combiner/deprecation/renewal semantics.

LAB-086 remains the execution priority. This document is a fallback evidence freeze only because exact repository execution is unavailable in the current runtime.

## Primary donors and facts

### RFC 9162 / Certificate Transparency
RFC 9162 defines an append-only Merkle log, a signed acceptance promise (SCT), a fixed Maximum Merge Delay, signed tree heads, inclusion proofs, and consistency proofs. A client can audit an SCT against a sufficiently late tree and obtain signed evidence of misbehavior when a promised entry is not included within the committed MMD. The protocol also treats inconsistent log views as misbehavior. We reuse the mechanism, not the certificate-specific object model.

### NIST crypto agility and PQ transition
NIST's PQ standards finalized ML-KEM (FIPS 203), ML-DSA (FIPS 204), and SLH-DSA (FIPS 205) in August 2024. NIST's transition and crypto-agility guidance treats algorithm replacement as a lifecycle/migration problem rather than an implicit reinterpretation of old signatures. Current NIST guidance also supports maintaining explicit algorithm-policy and transition state.

### NIST SP 800-57 key lifecycle
Key-management guidance separates active use, archival retention, cryptoperiods, compromise, and destruction. Long-lived integrity evidence may need renewal under successor keys/algorithms; destroying keying material does not imply deleting all non-secret audit metadata needed to prove what occurred.

## Frozen invariants

### 1. Replica-domain audit freshness

`REPLICA_LABELS_PRESENT != REPLICA_INDEPENDENCE_CURRENTLY_PROVEN`.

A historical independence attestation is valid only for its exact topology/audit epoch. Consequential current reliance requires a freshness policy with an authenticated `valid_from`, `valid_until` or equivalent challenge interval.

A replica-domain audit record must bind at minimum:
- logical replica id;
- physical/destructive-domain claim;
- controlling administrative/security domain claim;
- storage/provider/account identity where policy allows disclosure;
- audit/challenge epoch;
- evidence digests and authority identities;
- freshness interval;
- predecessor topology epoch.

If later evidence proves two replicas shared a destructive/control domain during an earlier epoch, the old independence assertion becomes `FALSE_INDEPENDENCE_PROVEN` for that interval. Historical quorum/evidence is re-evaluated under the original denominator with the affected replicas collapsed according to the frozen policy; the system MUST NOT silently relabel the replicas and preserve the old count.

Revocation is monotone evidence. A later clean audit may restore future eligibility but cannot erase a proved historical co-failure domain.

### 2. Challenge-based freshness

A freshness challenge must be bound to a nonce, exact replica/domain claim, deadline, audit authority epoch, and required response material. A successful response proves possession/control only relative to the stated challenge semantics; it does not by itself prove independent destructive domains.

`FRESH_CHALLENGE_PASS != INDEPENDENCE_PASS`.

Independence requires corroborating topology/control evidence from authority that is not solely controlled by the replica being audited.

### 3. Transparent ingress receipts

An ingress acceptance receipt is itself consequential evidence and must be transparently logged or cross-logged under an authenticated receipt-log identity.

Receipt record binds:
- receipt id;
- exact request/challenge digest;
- nonce;
- destination/source identity;
- accepted-at authenticated time evidence;
- deadline/MMD-like inclusion commitment;
- receipt-log/key epoch.

`RECEIPT_ISSUED != RECEIPT_PUBLICLY_AUDITABLE`.

The log must provide an append-only checkpoint and inclusion proof. If the receipt promise commits to inclusion by deadline D, positive omission proof requires:
1. authentic receipt/promise;
2. authenticated sufficiently-late checkpoint(s) under the promised log epoch;
3. canonical non-inclusion/exhaustive monitor evidence appropriate to the frozen log construction;
4. consistency evidence from the receipt's predecessor checkpoint to the audit checkpoint.

A 404, timeout, failed lookup, or absence from a partial mirror remains `NONINCLUSION_NOT_PROVEN`.

Two incompatible receipt-log checkpoints at the same logical tree position/generation are positive equivocation evidence.

### 4. Collector collusion boundary

Receipt transparency does not prove collector completeness. Source-withholding attribution requires the precommitted observation denominator plus independently authenticated collector outputs.

If all collectors share one control domain, the evidence class is `SINGLE_CONTROL_DOMAIN_OBSERVATION` even when there are many signatures.

### 5. Confidential semantic-corpus auditor compromise

Each confidential corpus audit is an immutable `AuditGeneration` binding:
- corpus generation/root and exact committed population;
- disclosed/hidden case commitment set;
- audit predicate/policy version;
- auditor population, threshold, independence policy and key epochs;
- ZK/selective-disclosure circuit/verifier parameters where used;
- result and coverage manifest;
- predecessor audit generation.

If an auditor key/control domain is later proved compromised with effective time intersecting an audit generation, that generation is not silently edited. It becomes one of:
- `AUDIT_ASSURANCE_UNAFFECTED`;
- `AUDIT_ASSURANCE_DEGRADED`;
- `AUDIT_REAUDIT_REQUIRED`;
- `AUDIT_INVALIDATED`.

The exact mapping is policy-defined and depends on threshold remaining after collapsing compromised/non-independent auditors.

A successor re-audit creates a new generation. It MUST bind the same exact corpus population (or an explicitly versioned successor corpus) and must not omit previously committed hidden cases. Re-audit result may supersede current reliance but does not delete predecessor evidence.

`REAUDIT_PASS != PREDECESSOR_NEVER_COMPROMISED`.

### 6. Anti-omission for confidential re-audit

For a same-corpus re-audit, the new case-commitment manifest must equal the predecessor authenticated population unless a separately authorized corpus migration declares exact additions/removals and rationale.

A hidden case can remain hidden, but its commitment cannot disappear merely because an auditor was replaced.

### 7. Destruction evidence versus secrets minimization

`DESTRUCTION_EVIDENCE_RETAINED != SECRET_MATERIAL_RETAINED`.

A system may retain non-secret, authenticated destruction evidence while deleting key/share/plaintext material. The retained destruction record should bind only what is needed for audit:
- object/share/key identifier or one-way commitment;
- exact epoch/branch;
- destruction/sanitization method class;
- device/storage scope where available;
- actor/authority identities;
- authenticated time evidence;
- result/status;
- independent verification evidence if policy requires it;
- predecessor/fork adjudication id.

It SHOULD NOT retain recoverable shares, plaintext secret values, raw backup material, or unnecessary sensitive device metadata.

A signed destruction assertion is not proof that all copies are unrecoverable. Assurance classes must be explicit, e.g. `LOGICAL_DELETE_ATTESTED`, `DEVICE_SANITIZATION_VERIFIED`, `KEY_CRYPTO_ERASURE_VERIFIED`, `ALL_COPY_DOMAINS_ACCOUNTED_FOR`. The strongest class requires authenticated inventory closure over policy-required copy/backup domains.

### 8. Retention lifecycle for destruction records

Destruction records themselves have retention/deprecation policy. Deleting them requires a positive dependency/retention-closure proof; otherwise evidence needed for fork or compromise adjudication may be lost.

Privacy minimization is achieved by narrowing the record schema and using commitments/pseudonymous identifiers, not by deleting consequential evidence before its retention obligations expire.

### 9. PQ hybrid combiner semantics

A hybrid signature/migration attestation MUST declare its combiner semantics before signing/verifying. At minimum distinguish:
- `BOTH_REQUIRED`: classical and PQ signatures must both verify;
- `PQ_REQUIRED_CLASSICAL_OPTIONAL`: PQ is authoritative; classical is compatibility evidence;
- `CLASSICAL_REQUIRED_PQ_OPTIONAL`: temporary pre-migration mode only;
- `EITHER_ACCEPTED`: explicitly weaker and generally unsuitable for consequential renewal because compromise of either scheme may suffice.

The verifier policy, algorithm ids, parameter sets, signer key epochs, signed payload, and combiner mode are part of the authenticated statement.

`HYBRID_PRESENT != HYBRID_STRONG`.

### 10. Algorithm deprecation effective time

Algorithm deprecation is an authenticated policy event with:
- algorithm/parameter id;
- deprecation reason/class;
- `effective_from` time evidence;
- grace/verification-only interval where applicable;
- successor algorithm policy;
- policy authority epoch.

A later policy MUST NOT reinterpret an old signature as having used a different combiner mode.

For consequential current reliance:
- evidence generated before deprecation may remain historically verifiable under frozen policy;
- new evidence after `effective_from` must satisfy successor policy;
- if compromise is believed to predate publication, the compromise effective boundary controls, not publication time;
- ambiguous effective-time ordering fails closed for consequential promotion/authorization.

### 11. Long-term renewal of migration attestations

Renewal creates a successor attestation over the exact predecessor statement/evidence digest plus the current canonical semantic payload, policy id, algorithm suite, and provenance lineage.

A successor signature that only signs the predecessor signature bytes does not repair a predecessor semantic/provenance failure.

Full renewal requires:
1. predecessor evidence remains independently verifiable under its historical policy or is explicitly marked degraded;
2. original authenticated semantic payload/source evidence is available;
3. successor verifier confirms semantic equivalence/canonicalization under current schema;
4. successor attestation uses current non-deprecated policy;
5. lineage binds predecessor id and reason for renewal;
6. any degradation/compromise state is propagated monotonically.

`RENEWED_CRYPTO_BINDING != REPAIRED_SEMANTIC_TRUTH`.

## RED-first regression matrix

### Replica audit / revocation
1. Two labels on same physical/control domain must not count as two independent replicas.
2. Fresh challenge to both labels with shared controller must not prove independence.
3. Expired topology audit must not authorize consequential current quorum.
4. Later proof of shared domain must mark affected historical interval false-independent.
5. Later clean audit may restore future eligibility but must not erase historical false-independence.
6. Same-generation conflicting topology mappings must surface equivocation.
7. Concurrent successor topology epochs must surface split-brain.
8. Historical denominator must not be rewritten by later relabel/retirement.

### Receipt transparency / non-inclusion
9. Accepted challenge with valid receipt and timely inclusion passes.
10. Receipt without transparent inclusion remains incomplete until the committed deadline/audit state exists.
11. 404 after deadline without exhaustive authenticated state must not prove omission.
12. Valid receipt + sufficiently late authenticated complete checkpoint + canonical non-inclusion evidence proves omission.
13. Stale checkpoint must not prove omission.
14. Partial mirror/collector absence must not prove omission.
15. Same-position conflicting receipt-log roots surface equivocation.
16. Log rollover without authenticated continuity must not inherit old receipt promises.

### Confidential corpus re-audit
17. Auditor compromise after audit but outside effective interval follows policy-defined historical status, not automatic deletion.
18. Compromise overlapping audit threshold can trigger re-audit/invalidation.
19. Re-audit must bind exact predecessor corpus population for same-generation audit.
20. Hidden committed case silently omitted on re-audit fails.
21. New auditor signatures over old result without independent re-execution do not count as re-audit.
22. Re-audit pass does not erase predecessor compromise evidence.
23. Auditor replacement cannot alter predecessor denominator retroactively.
24. Re-audit under new ZK circuit must bind exact successor circuit/verifier policy.

### Destruction evidence / minimization
25. Retain authenticated destruction record while raw share is absent.
26. Destruction record containing recoverable secret bytes fails minimization policy.
27. Signed deletion assertion alone cannot satisfy strongest all-copies-unrecoverable class.
28. Missing backup-domain inventory prevents `ALL_COPY_DOMAINS_ACCOUNTED_FOR`.
29. Crypto-erasure verification can satisfy its declared class without claiming physical media destruction.
30. Losing fork disposal must retain fork/adjudication linkage.
31. Privacy-driven deletion of still-required destruction evidence fails retention closure.
32. Expired retention with positive dependency closure permits deletion of non-required audit detail under policy.

### PQ hybrid / deprecation / renewal
33. `BOTH_REQUIRED` rejects if either classical or PQ signature fails.
34. `EITHER_ACCEPTED` is not silently upgraded to both-required assurance.
35. Verifier must reject unknown/implicit combiner mode for consequential evidence.
36. Deprecated algorithm cannot create new consequential evidence after effective boundary when policy forbids it.
37. Pre-boundary historical evidence remains labeled under historical policy rather than re-signed in place.
38. Ambiguous compromise/deprecation ordering fails closed for consequential renewal.
39. PQ wrapper over semantically invalid predecessor does not repair truth.
40. Full renewal under current algorithm must bind original semantic payload, predecessor lineage, current policy and propagated degradation state.

## Implementation consequences for LAB-093..100

Future executable work should model these as explicit immutable records/epochs rather than booleans or mutable labels. Verification APIs should return typed states such as `FRESH`, `STALE`, `EQUIVOCATED`, `FALSE_INDEPENDENCE_PROVEN`, `NONINCLUSION_PROVEN`, `NONINCLUSION_NOT_PROVEN`, `AUDIT_REAUDIT_REQUIRED`, `DESTRUCTION_ASSURANCE_<CLASS>`, `ALGORITHM_DEPRECATED`, and `RENEWAL_DEGRADED`.

No production refactor is authorized by this design document alone. RED tests must be implemented first on exact source, then minimal production changes, then full supported-surface/security regressions.

## Sources

- RFC 9162, Certificate Transparency Version 2.0: append-only Merkle logs, SCT acceptance promise/MMD, signed tree heads, inclusion/consistency auditing, signed evidence of log misbehavior.
- NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA), finalized 2024.
- NIST IR 8547 transition guidance and NIST CSWP 39 crypto-agility guidance: explicit algorithm migration/transition lifecycle.
- NIST SP 800-57 Part 1: cryptoperiod, archival keying material, compromise and destruction lifecycle.
