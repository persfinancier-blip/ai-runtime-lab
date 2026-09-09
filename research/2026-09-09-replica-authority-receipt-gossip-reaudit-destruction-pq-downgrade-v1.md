# Replica authority, receipt-log survivability, confidential re-audit, destruction inventory, and PQ downgrade — V1

Date: 2026-09-09
Status: `REPLICA_AUTHORITY_RECEIPT_GOSSIP_REAUDIT_DESTRUCTION_PQ_DOWNGRADE_V1_FROZEN`
Scope: design/evidence freeze only. This does **not** substitute for executable RED/GREEN validation on LAB-086 or LAB-093..100.

## Why this exists

The previous evidence freezes established that replica labels do not prove failure-domain independence, receipt omission requires positive evidence, confidential corpus re-audit must preserve committed population, destruction assertions do not prove all copies unrecoverable, and PQ hybrid semantics must be explicit.

This follow-up closes five remaining authority/lifecycle gaps:

1. who is trusted to audit replica-domain independence when that audit authority itself rolls over or is compromised;
2. how challenge transcripts avoid replay and how accepted receipt promises survive receipt-log retirement through witness/gossip evidence;
3. how confidential semantic re-audit remains independent and challenge-secret when part of the auditor set is compromised;
4. how a destruction inventory proves completeness across backup/snapshot/replica domains instead of proving only deletion from enumerated locations;
5. how archived hybrid/PQ evidence prevents verifier monoculture, algorithm-policy rollback, and downgrade reinterpretation after migration.

## Primary donors

- RFC 9162, Certificate Transparency v2: append-only Merkle logs, signed tree heads/checkpoints, consistency proofs, SCT acceptance promises, MMD-bounded inclusion, and detection of conflicting views. https://www.rfc-editor.org/rfc/rfc9162.html
- NIST SP 800-57 Part 1 Rev. 5: compromise response, replacement of affected keying material, backup/archive lifecycle, separation of operational and archival material, multiple physically separate archive copies, and destruction of traces when material is no longer required. https://doi.org/10.6028/NIST.SP.800-57pt1r5
- NIST FIPS 203/204/205 and NIST PQC migration material: ML-KEM, ML-DSA and SLH-DSA are standardized PQ primitives; migration is an explicit lifecycle rather than a silent verifier reinterpretation. https://csrc.nist.gov/projects/post-quantum-cryptography
- NIST IR 8547 initial public draft: transition/deprecation planning for quantum-vulnerable algorithms, including explicit future disallow dates rather than implicit algorithm switching. https://doi.org/10.6028/NIST.IR.8547.ipd
- NIST CSWP 39, Considerations for Achieving Crypto Agility: algorithm replacement must preserve security and ongoing operations and requires operational mechanisms/policy, not merely support for more algorithms. https://doi.org/10.6028/NIST.CSWP.39

## 1. Replica-audit authority compromise and rollover

### Frozen boundary

`REPLICA_AUDIT_SIGNED != REPLICA_INDEPENDENCE_TRUE`

Replica independence is an authenticated topology assertion for a bounded interval. The audit authority is itself part of the trust chain and cannot be treated as an oracle whose signature permanently establishes topology truth.

### ReplicaAuditAuthorityEpoch

Every audit result MUST bind:

- `authority_id`;
- `authority_key_epoch`;
- exact authority policy/version;
- audited replica identities;
- claimed destructive/control-domain labels;
- evidence manifest digest;
- challenge transcript root;
- `valid_from` / `valid_until` or equivalent authenticated interval;
- predecessor authority epoch, if any;
- successor authorization path where rollover applies.

Normal rollover MUST create a successor authority epoch. It MUST NOT rewrite old audit generations or silently replace the verifier key used for historical decisions.

### Compromise semantics

If an authority epoch is later proven compromised:

- audits issued after the authenticated compromise-effective boundary are `AUTHORITY_COMPROMISED_REAUDIT_REQUIRED`;
- audits provably before the boundary may remain historical evidence under the frozen policy in force at that time;
- if the effective boundary is unknown, consequential current reliance fails closed for the ambiguous interval;
- a successor clean audit can restore **future** replica eligibility but cannot erase a historical interval in which false independence was proven or compromise was unresolved.

The compromised authority MUST NOT be the sole authority that selects its own compromise-effective boundary.

### Challenge anti-replay

A fresh possession/topology challenge MUST include at least:

- unpredictable nonce with sufficient entropy;
- verifier/auditor identity and key epoch;
- exact replica identity;
- challenge purpose/domain;
- issue time interval and expiry/deadline;
- predecessor audit generation or topology root;
- policy version.

A response MUST bind the entire challenge. Reuse of an old response against a new nonce, new replica, new authority epoch, new policy, or new time window is `REPLAY_REJECTED`.

Possession response proves only the protocol-defined property for that challenge. It does not by itself prove destructive-domain independence.

## 2. Receipt-log witness quorum, gossip, and promise survivability

RFC 9162 gives a useful donor model: acceptance creates a signed promise (SCT), and monitors/auditors check append-only evolution and promise fulfillment against later authenticated tree state. The design here generalizes that pattern to consequential ingress receipts.

### ReceiptAcceptancePromise

An accepted challenge/request MUST yield a signed receipt that commits to:

- exact request/challenge digest;
- nonce;
- ingress identity and key epoch;
- acceptance time interval;
- inclusion deadline / MMD-equivalent;
- target receipt-log identity and key epoch;
- canonical leaf identity or derivation;
- policy/version.

`SEND_ATTEMPT != ACCEPTANCE_PROMISE`

Without a valid acceptance receipt, later absence is `DELIVERY_NOT_PROVEN`, not positive censorship/omission evidence.

### Receipt-log checkpoints

Consequential receipt logs MUST expose authenticated checkpoints sufficient to prove:

- exact log identity/key epoch;
- tree size/root;
- append-only ancestry through consistency proof material;
- the checkpoint time/freshness relation required by the promise deadline.

Same-size/different-root checkpoints are positive equivocation evidence.

### Witness quorum

A receipt-log checkpoint may be relied on as a witnessed state only under a predeclared witness population/denominator/threshold for that witness-policy epoch.

Historical quorum MUST be evaluated against the historical denominator. Later witness retirement, partition, replacement, or denominator reduction cannot retroactively turn an under-quorum checkpoint into a quorum checkpoint.

Witnesses SHOULD persist their last accepted checkpoint/frontier and reject incompatible successor views.

### Gossip

Gossip transports signed checkpoints/receipts between independently governed observers so split views can be compared. Gossip delivery itself is not consensus; its security value comes from making incompatible signed views jointly observable.

The evidence model therefore distinguishes:

- `CHECKPOINT_SIGNED`;
- `CHECKPOINT_WITNESSED_QUORUM`;
- `GOSSIP_CORROBORATED`;
- `EQUIVOCATION_PROVEN`.

### Log retirement

Retiring a receipt log does not cancel outstanding acceptance promises.

Before retirement, the system MUST either:

1. fulfill every outstanding promise and archive the required inclusion/consistency evidence; or
2. produce an authenticated migration/supersession record that explicitly preserves the original promise, target lineage, deadline semantics, and verification path.

A successor log MUST NOT be treated as if it had always been the original target unless that cross-log supersession was authenticated before the old verification path became unavailable.

`LOG_RETIRED != PROMISE_EXTINGUISHED`

## 3. Confidential re-audit independence under compromised auditor sets

### Frozen boundary

`MORE_AUDITOR_SIGNATURES != MORE_INDEPENDENT_REEXECUTIONS`

A re-audit counts toward semantic assurance only when it is an independently executed evaluation over the authenticated committed population under a distinct qualifying control/provenance domain.

### ReAuditGeneration

Each re-audit generation MUST bind:

- predecessor audit generation;
- exact corpus/population commitment/root;
- hidden-case commitment set;
- evaluator code/circuit/parser version;
- challenge-generation policy/version;
- auditor-set membership/denominator/threshold epoch;
- each auditor's qualifying independence domain;
- result commitment before reveal where anti-copy matters;
- reveal/decryption evidence where confidentiality is used;
- decision/verdict and evidence manifest.

### Compromised auditor set

If k auditors are controlled by the same compromised domain, they count as one compromised domain for independence purposes, not k independent votes.

Auditor membership/denominator MUST be frozen before challenge/result observation. Dropping an inconvenient or compromised auditor after results are known cannot silently reduce the historical denominator.

If the remaining independent set no longer satisfies policy, the generation is `AUDITOR_INDEPENDENCE_QUORUM_LOST` even if the raw signature count still exceeds threshold.

### Challenge secrecy

When challenge secrecy is required to prevent copying or overfitting:

- challenge population is committed before evaluator access;
- challenge plaintext is hidden from non-authorized auditors/evaluators until the protocol-defined phase;
- result commitments occur before reveal;
- access to challenge plaintext is auditable and bound to auditor/evaluator identity and epoch;
- compromise of enough challenge custodians to reconstruct hidden challenges before the anti-copy deadline yields `CHALLENGE_SECRECY_COMPROMISED` even if no public leak is observed.

A later clean re-audit can establish a new assurance generation. It does not erase the compromised predecessor generation.

## 4. Destruction inventory anti-omission and backup-domain discovery

NIST SP 800-57 distinguishes operational, backup, and archive storage and requires destruction of traces when protected keying material is no longer required. That lifecycle implies a critical evidence distinction: proving deletion from known locations is weaker than proving that the inventory of locations was complete.

### Frozen boundary

`ALL_ENUMERATED_COPIES_DESTROYED != ALL_COPY_DOMAINS_ACCOUNTED_FOR`

### DestructionInventoryGeneration

Before claiming complete disposal, bind an authenticated inventory generation containing at least:

- secret/material identity or irreversible tokenized identifier;
- creation/provisioning lineage;
- every known operational store;
- every backup system and backup policy that could have captured the material;
- snapshots/checkpoints/images;
- replicas/caches;
- disaster-recovery/archive domains;
- removable/offline media domains where policy permits them;
- HSM/secure-element wrap/export history where applicable;
- cloud/provider managed backup classes where applicable;
- retention/expiry policy for each domain;
- inventory discovery method/version;
- discovery frontier / completeness evidence;
- destruction/sanitization evidence per domain.

### Anti-omission proof

Positive `ALL_COPY_DOMAINS_ACCOUNTED_FOR` requires evidence from the systems that generate/capture copies, not merely a human-maintained list.

Examples of qualifying mechanisms include authenticated enumeration of backup policies/jobs, snapshot catalogs, replica membership, archive manifests, export/wrap logs, and configuration histories covering the material's lifetime.

An empty query result without a proven complete source frontier is `NO_COPY_FOUND`, not `NO_COPY_EXISTS`.

If a new previously unknown backup domain is discovered later, prior all-copy destruction claims become `INVENTORY_INCOMPLETE_DISCOVERED` for the affected interval. Destroying the newly discovered copy restores future state but cannot make the old completeness claim retrospectively true.

### Privacy/minimization

Destruction evidence SHOULD retain only the minimum authenticated metadata needed to prove lifecycle actions and completeness. It MUST NOT retain the destroyed secret/plaintext solely to make the audit easier.

## 5. PQ migration-attestation verifier diversity, rollback protection, and archived downgrade defense

NIST has standardized ML-KEM, ML-DSA, and SLH-DSA and separately treats migration/deprecation as an explicit lifecycle. Therefore verifier behavior must be policy-versioned and time/epoch-bound; merely adding PQ support is insufficient.

### MigrationAttestation

Every migration/renewal attestation MUST bind:

- exact semantic payload/evidence object being protected;
- predecessor crypto policy and algorithm set;
- successor crypto policy and algorithm set;
- hybrid combiner semantics;
- migration reason and effective boundary;
- predecessor evidence degradation state;
- verifier implementation identity/version;
- verifier-policy version;
- independent verification results/attestations required by policy.

### Verifier diversity

`N_VERIFIERS != N_INDEPENDENT_VERIFIER_IMPLEMENTATIONS`

Multiple verifier processes count as diverse only if policy-defined independence is satisfied. Shared parser/library/provider/runtime defects must be modeled as correlated failure domains.

For high-consequence migration evidence, policy SHOULD require at least two independently implemented verification paths where operationally feasible, especially during algorithm/proof-system transitions.

### Rollback protection

Once an authenticated policy epoch raises the minimum accepted algorithm/combiner level, a later verifier MUST NOT silently accept an older/weaker policy simply because archived evidence contains a valid old signature.

Required comparison inputs include:

- evidence creation/effective time interval;
- policy epoch active for the claimed decision;
- deprecation/disallow boundary;
- renewal/migration lineage;
- whether the requested operation is historical verification or new consequential reliance.

Historical verification may legitimately verify an old algorithm as evidence of what happened then. New consequential authorization after a disallow boundary MUST satisfy the current policy.

This distinction prevents two opposite failures:

- `RETROACTIVE_INVALIDATION`: incorrectly pretending old evidence never existed because its algorithm is now deprecated;
- `POLICY_ROLLBACK`: using an old archived signature to authorize a new action under a weaker retired policy.

### Hybrid/composite downgrade

Hybrid evidence MUST encode the combiner, e.g. `BOTH_REQUIRED`, `PQ_REQUIRED_CLASSICAL_OPTIONAL`, or another explicit policy. A verifier MUST NOT reinterpret `BOTH_REQUIRED` archived evidence as `EITHER_ACCEPTED` merely because one component remains verifiable.

If a required component becomes unverifiable or cryptographically broken, the evidence is downgraded according to the exact frozen combiner policy. A surviving component may preserve partial historical evidence, but it does not silently promote the object to the original assurance class.

### Renewal

`NEW_PQ_SIGNATURE != FULL_RENEWAL`

Full renewal requires rebinding the original authenticated semantic payload plus predecessor lineage, degradation state, current policy, and migration attestation. A new PQ signature over a summary that omits predecessor caveats is downgrade laundering.

## 6. Frozen RED-first matrix

The following cases are implementation obligations for future executable work.

### A. Replica authority / anti-replay (8)

1. fresh nonce, current authority epoch, exact replica -> accept;
2. replay old response under new nonce -> reject;
3. replay response for replica A as replica B -> reject;
4. replay predecessor-authority response after rollover -> reject for new audit generation;
5. authority compromised after provably earlier audit -> preserve historical audit under frozen policy;
6. audit in ambiguous compromise interval -> fail closed for consequential reliance;
7. successor audit restores future eligibility -> accept future only;
8. later false-independence evidence -> historical affected interval marked degraded, denominator not rewritten.

### B. Receipt log / witness / retirement (8)

9. signed acceptance + inclusion before deadline + valid ancestry -> fulfilled;
10. send attempt without acceptance -> omission not proven;
11. accepted promise + sufficiently late authenticated checkpoint + canonical non-inclusion -> omission proven;
12. same-size/different-root checkpoint -> equivocation proven;
13. checkpoint below historical witness quorum -> not quorum even after later denominator shrink;
14. gossip exposes two incompatible signed views -> equivocation evidence retained;
15. log retired with outstanding promise and no migrated verification path -> retirement invalid/incomplete;
16. successor log with pre-retirement authenticated supersession preserving promise lineage -> verifiable migration.

### C. Confidential re-audit (8)

17. independent qualifying auditor domains re-execute exact committed population -> count;
18. three signatures from one compromised control domain -> count as one independence domain;
19. drop dissenting auditor after results -> denominator laundering reject;
20. hidden-case commitment omitted from successor re-audit -> incomplete population reject;
21. result copied after observing another reveal without prior commitment -> anti-copy reject;
22. threshold challenge custodians compromised before reveal deadline -> secrecy compromised;
23. clean successor re-audit after predecessor compromise -> new assurance generation only;
24. new auditors merely re-sign predecessor verdict without re-execution -> not re-audit.

### D. Destruction inventory (8)

25. all enumerated stores sanitized but backup discovery frontier incomplete -> no all-copy claim;
26. authenticated backup/snapshot/archive enumeration covers full lifetime and all domains sanitized -> all-copy claim eligible;
27. empty backup lookup without completeness proof -> no-copy-found only;
28. later discovery of forgotten snapshot -> prior completeness claim degraded;
29. destroy discovered snapshot -> future state restored, prior claim not rewritten;
30. destruction attestation retains plaintext secret -> privacy/minimization violation;
31. crypto-erasure proven but surviving wrapped key copy exists -> disposal incomplete;
32. logical delete only -> classify lower assurance, not physical/cryptographic destruction.

### E. PQ migration / downgrade (8)

33. archived old signature verified only for historical event before deprecation -> allowed historical verification;
34. archived old signature reused to authorize new post-disallow action -> rollback reject;
35. `BOTH_REQUIRED` hybrid with classical valid/PQ invalid -> reject original assurance;
36. `PQ_REQUIRED_CLASSICAL_OPTIONAL` with PQ valid/classical unavailable -> accept only if exact policy permits;
37. verifier update attempts to reinterpret old combiner as weaker -> reject;
38. multiple verifier processes sharing same implementation counted as diverse -> reject diversity claim;
39. new PQ signature over payload that drops predecessor degradation -> renewal reject;
40. full renewal binds original payload, lineage, degradation, current policy, and independently checked migration attestation -> eligible successor evidence.

## 7. Implementation notes for LAB-093+ follow-up

The frozen schemas above should be introduced only through tests-first work on exact source. Recommended object families:

- `ReplicaAuditAuthorityEpoch`, `ReplicaAuditGeneration`, `ReplicaChallengeTranscript`;
- `ReceiptAcceptancePromise`, `ReceiptLogCheckpoint`, `ReceiptWitnessPolicyEpoch`, `ReceiptLogRetirementRecord`;
- `ConfidentialReAuditGeneration`, `AuditorIndependenceDomain`, `ChallengeSecrecyState`;
- `DestructionInventoryGeneration`, `CopyDomainEvidence`, `InventoryCompletenessProof`;
- `MigrationAttestation`, `CryptoPolicyEpoch`, `HybridCombinerPolicy`, `VerifierIndependenceDomain`.

Do not collapse these into unsigned mutable runtime structs. Historical verifier decisions must remain reproducible from immutable/authenticated evidence plus the exact historical policy epoch.

## 8. Security audit of this freeze

No claim here depends on GitHub Actions or unexecuted repository code. The design intentionally distinguishes positive proof from absence, historical validity from new consequential authorization, raw signature count from independence, and copy deletion from inventory completeness.

The largest unresolved implementation risks are denominator laundering, time/effective-boundary ambiguity, circular authority recovery, and accidental treatment of mutable indexes/configuration as truth. Those remain RED-first obligations.

## 9. Decision

Freeze `REPLICA_AUTHORITY_RECEIPT_GOSSIP_REAUDIT_DESTRUCTION_PQ_DOWNGRADE_V1_FROZEN`.

This evidence task is complete at the design/research level only. LAB-086 remains the top engineering priority; when exact-source execution becomes available, return immediately to the complete real-ledger LAB-080→086 gate, unsafe expected-failure seed, compileall, security reconciliation, and branch/main conflict audit before changing PR #165 draft/merge status.
