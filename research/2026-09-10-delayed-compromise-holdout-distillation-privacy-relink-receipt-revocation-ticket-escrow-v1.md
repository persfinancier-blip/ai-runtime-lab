# Delayed compromise, derived holdout lineage, privacy relink, receipt revocation, and ticket escrow — v1

Date: 2026-09-10
Status: FROZEN design contract; RED-first executable proof pending exact-source runtime
Contract: `DELAYED_COMPROMISE_HOLDOUT_DISTILLATION_PRIVACY_RELINK_RECEIPT_REVOCATION_TICKET_ESCROW_V1_FROZEN`

## Scope

This slice extends LAB-093/#178 without substituting for LAB-086 executable evidence. It targets six delayed-discovery failure classes that remain after the prior recovery-root/GC/receipt/ticket contracts:

1. successor recovery quorum authorization when a predecessor member is discovered compromised only after transition;
2. compact-root reconstruction when retained witness attestations rotate or expire;
3. reusable-holdout exposure continuity through distillation, lossy compression, embeddings and approximate indexes;
4. privacy-spend reconciliation when an identity is tombstoned/deleted and later relinked;
5. provider-effect reconciliation across receipt-key compromise/revocation and reordered delayed receipts;
6. ticket-security-epoch authority discovery through external KMS import/replication and cross-region credential escrow.

## Primary evidence / donors

- RFC 9162 Certificate Transparency v2: signed tree heads authenticate states, while Merkle consistency proofs establish append-only continuity between states; auditing must also consider consistency of views presented to different entities. Donor mechanism: predecessor-bound continuity evidence and explicit equivocation rather than accepting isolated valid signatures.
- Dwork et al., *Generalization in Adaptive Data Analysis and Holdout Reuse* (2015): adaptive reuse can overfit a holdout because information revealed by prior analyses feeds later choices. Donor mechanism: exposure follows information flow, not storage/object identity.
- Jagielski et al., *Students Parrot Their Teachers: Membership Inference on Model Distillation* (2023): distillation alone provides limited privacy and membership leakage can survive indirect teacher influence. Donor mechanism: a student/derived model is not a fresh independent holdout boundary.
- Liu et al., *Mitigating Privacy Risks in LLM Embeddings from Embedding Inversion* (2024): stored embeddings can leak information about source text. Donor mechanism: vectorization is a transformation, not proof of information erasure.
- NIST SP 800-226 / NIST privacy-budget definition: privacy budget is an upper bound on cumulative privacy loss across analyses of the same data. Donor mechanism: deletion/relink/name changes cannot refund already incurred privacy loss.
- TLS 1.3 (RFC 8446; current successor RFC 9846 preserves the relevant resumption guidance): repeatedly issued tickets can extend ancestry of original keying material; implementations should bound total lifetime. Donor mechanism: ticket authority follows ancestry, not only current encryption key name.
- NIST SP 800-88 Rev. 2: sanitization/cryptographic erase depends on making access infeasible and explicitly addresses externally managed keys. Donor mechanism: removing local active references does not prove extinction of imported, replicated, escrowed, wrapped, backup, or externally managed authority.

## Frozen invariants

### A. Delayed predecessor compromise

`SUCCESSOR_QUORUM_VALID_AT_T0 != SUCCESSOR_AUTHORITY_SAFE_AFTER_DELAYED_COMPROMISE_DISCOVERY`.

Every recovery transition records a canonical predecessor-member set, stable failure-domain/issuer lineage, threshold rule, signed transition payload, evidence cutoff, and successor root. If a member is later proven compromised with a compromise interval intersecting the transition authorization window, the transition is reclassified against the remaining independently valid predecessor authority.

- If the uncompromised predecessor subset still satisfies the frozen transition rule, continuity remains valid and the new compromise evidence is appended.
- If it does not, authority enters `DELAYED_AUTHORIZATION_UNCERTAIN`; no new destructive/recovery authority may be derived from that successor until a higher/root recovery path resolves it.
- A later key rotation, member rename, or membership removal cannot erase the compromised signer from the historical authorization calculation.
- Overlapping old/new quorum signatures cannot be threshold-shopped after the fact.

### B. Rotating/expiring witness attestations

`WITNESS_ATTESTATION_EXPIRED != HISTORICAL_EVIDENCE_INVALID` and `NEW_WITNESS_KEY != NEW_INDEPENDENT_WITNESS`.

Compact-root GC must retain enough authenticated lineage to validate historical attestations after online verification keys rotate or expire. A historical attestation remains evidence if its signature and authority were valid at its signed evidence cutoff and its lineage has not been revoked for that interval.

GC may discard bulky predecessor material only when the compact successor commits to: predecessor root/range, witness stable identity/failure domain, signing-key epoch, validity interval, revocation cutoff, quorum rule, conflict set, and a completeness commitment sufficient to reconstruct the authority decision.

Late revocation whose effective interval intersects an attestation reopens the compact-root authority proof; it must never silently convert the old attestation into absent history.

### C. Holdout lineage through distillation/compression/indexes

`LOSSY_TRANSFORM != INFORMATION_INDEPENDENCE`.

A holdout-derived artifact inherits the holdout exposure lineage when an adaptive controller can obtain useful information from it, including through:

- distilled/student models trained on teacher outputs influenced by the holdout;
- quantized/compressed models preserving relevant behavior;
- embeddings, centroids, feature stores, statistics and cached scores;
- approximate-nearest-neighbor indexes or sketches that preserve retrieval/neighborhood information;
- synthetic examples selected/generated using holdout feedback.

Deletion of raw holdout rows does not reset exposure while reachable derivatives remain. A derived artifact can become an independent evaluation resource only through a separately justified statistical/privacy contract; a new object hash/model ID is insufficient.

### D. Privacy identity tombstone and relink

`IDENTITY_TOMBSTONED != PRIVACY_LINEAGE_ERASED`.

Privacy accounting retains a non-identifying monotonic lineage token sufficient to reconcile prior spend/reservations/unknown loss without retaining unnecessary deleted profile data. If later evidence relinks a new identity node to that lineage, the effective spend floor is the conservative composition of all compatible predecessor lineages.

Split/delete/recreate/relink oscillation cannot mint budget. Ambiguous relink enters `IDENTITY_RECONCILIATION_UNCERTAIN` and blocks budget expansion until resolved; negative resolver output alone is not proof of disjointness.

### E. Receipt-key compromise/revocation and delayed ordering

`RECEIPT_SIGNATURE_VALID != RECEIPT_AUTHORITY_VALID_FOR_EVENT_TIME`.

Every provider receipt binds provider stable identity, operation semantic identity, effect generation, provider sequence/position when available, receipt-key epoch, event time/evidence cutoff, and predecessor receipt/effect reference.

- Revocation is interval-aware: receipts signed after effective compromise/revocation are untrusted for authority, while earlier receipts may remain historical evidence if the compromise interval excludes them.
- A late-arriving older receipt is inserted into reconciliation order by provider sequence/event evidence, not arrival time.
- Two incompatible valid receipts whose authority intervals overlap create `PROVIDER_EQUIVOCATION`.
- Compensation is a new bounded-generation effect; it never erases the original effect or allows an unbounded compensate/retry loop.
- Timeout after dispatch remains `EFFECT_UNKNOWN` until authentic provider evidence or an independently fenced reconciliation proves the outcome.

### F. External KMS replication/import and credential escrow

`LOCAL_KMS_KEY_ABSENT != TICKET_PREDECESSOR_AUTHORITY_EXTINCT`.

Ticket-security-epoch GC tracks every authority domain capable of recovering or spending predecessor resumption authority: active KMS/HSM replicas, imported/wrapped key copies, backup/DR sets, cross-region replication, escrow/recovery credentials, offline restore packages, and replay-state epochs relevant to 0-RTT.

A late-discovered external replica/import/escrow path reopens extinction proof but never lowers the monotonic `ticket_security_epoch_floor`. Affected restore/spend domains remain `RESUMPTION_QUARANTINED` until they prove current epoch convergence and predecessor non-spendability.

Fresh certificate-authenticated 1-RTT may recover independently; PSK resumption requires ticket-authority convergence; 0-RTT additionally requires anti-replay epoch convergence. Old-key deletion from active configuration is not erasure evidence by itself.

## RED-first matrix (40 cases)

### Delayed predecessor compromise
1. successor transition signed by 3-of-5; one signer later compromised outside authorization interval -> remains valid.
2. same compromise interval overlaps transition but remaining 2-of-4 independent valid signers still satisfy frozen rule -> valid with appended evidence.
3. delayed compromise leaves fewer than required independent predecessor signers -> `DELAYED_AUTHORIZATION_UNCERTAIN`.
4. compromised signer re-keyed after transition -> historical contribution still re-evaluated.
5. compromised signer removed from current membership -> historical contribution still re-evaluated.
6. two signer IDs share one later-proven failure domain -> recount independence, no double count.
7. old/new overlapping quorum permits two conflicting successors -> explicit equivocation.

### Witness rotation/expiry and compact-root reconstruction
8. historical witness key expires after valid attestation cutoff -> attestation remains evidence.
9. key rotates with stable witness identity -> no new independence credit.
10. revocation effective after attestation cutoff -> earlier attestation retained.
11. revocation effective before attestation cutoff -> compact proof reopens/fails authority.
12. compact root omits witness-key epoch -> reconstruction fails closed.
13. compact root omits predecessor conflict set -> completeness fails closed.
14. witness online service disappears but retained lineage/proof is complete -> historical reconstruction still succeeds.

### Holdout transformation lineage
15. raw holdout deleted; teacher-distilled student retained -> exposure floor retained.
16. student re-quantized/new model ID -> no exposure reset.
17. embeddings derived from holdout retained -> exposure retained.
18. ANN index retains neighborhoods after source vectors deleted -> exposure retained.
19. lossy sketch still changes adaptive selection -> exposure retained.
20. synthetic examples selected using holdout scores -> inherit disclosure lineage.
21. truly fresh independently sampled evaluation dataset with no derivative path -> may receive separate budget after proof.

### Privacy tombstone/relink
22. identity tombstoned then recreated under new ID -> no automatic fresh budget.
23. later strong relink to predecessor -> compose predecessor spend floor.
24. ambiguous relink to two predecessor identities -> conservative union/uncertainty floor.
25. graph split after prior merge -> no spend refund.
26. negative resolver result without current proof -> no disjointness assertion.
27. relink proof expires -> block budget expansion, retain existing spend.
28. deletion removes profile attributes while monotonic opaque lineage token remains -> accounting still reconciles without profile resurrection.

### Receipt compromise/reordering
29. receipt valid before compromise interval -> historical evidence retained.
30. receipt signed inside proven compromised interval -> authority rejected.
31. delayed receipt arrives after successor-key receipt but has lower provider sequence -> order by provider evidence, not arrival.
32. conflicting receipts across key epochs claim incompatible outcomes for one semantic operation -> equivocation.
33. key revocation followed by same semantic retry without reconciliation -> blocked.
34. compensation receipt references original effect and increments bounded generation -> accepted as new effect.
35. compensation loop exceeds configured generation bound -> fail closed/escalate reconciliation.

### Ticket external authority discovery
36. local key deleted but replicated KMS key remains -> extinction proof fails.
37. replica discovered after GC acknowledgement -> reopen proof, keep security epoch floor, quarantine replica domain.
38. escrow credential can restore wrapped predecessor ticket key -> predecessor authority not extinct.
39. region proves current ticket epoch but lost 0-RTT replay state -> fresh 1-RTT allowed, 0-RTT quarantined.
40. all active/backup/escrow/import domains prove predecessor non-spendability and bounded ancestry lifetime elapsed -> predecessor epoch eligible for final GC.

## Implementation shape for future RED/GREEN

Introduce no production abstraction until exact executable source is available. Tests should first model canonical records for `RecoveryTransition`, `WitnessAttestationLineage`, `HoldoutDerivativeLineage`, `PrivacySubjectLineage`, `ProviderEffectReceipt`, and `TicketAuthorityDomain`. All monotonic floors must be persisted/authenticated through the existing durable authority graph rather than a new self-asserted mutable side table.

The executable acceptance bar remains: RED demonstrates each unsafe normalization/rebind/refund/revival; GREEN fails closed without mutating predecessor evidence; restart reproduces the same authority decision; compileall and full supported downstream gates pass; branch/main conflict audit is clean.

## Decision

Freeze `DELAYED_COMPROMISE_HOLDOUT_DISTILLATION_PRIVACY_RELINK_RECEIPT_REVOCATION_TICKET_ESCROW_V1_FROZEN` as LAB-093 architecture evidence. It is design evidence only and does not change draft status of LAB-086/#165 or any other executable PR.
