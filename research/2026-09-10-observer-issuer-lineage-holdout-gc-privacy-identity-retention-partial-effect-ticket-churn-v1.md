# Observer issuer-lineage recovery, holdout GC completeness, probabilistic privacy identity, retention partial-effect reconciliation, and ticket-retirement churn

Date: 2026-09-10
Status: FROZEN DESIGN / RED-FIRST CONTRACT
Contract: `OBSERVER_ISSUER_LINEAGE_HOLDOUT_GC_PRIVACY_IDENTITY_RETENTION_PARTIAL_EFFECT_TICKET_CHURN_V1_FROZEN`

## Why this slice exists

LAB-086 remains the executable priority. This run re-probed direct exact-source checkout and `git clone --no-checkout` again failed before repository execution with `Could not resolve host: github.com`. The GitHub connector can read/write repository state, but no supported non-model connector-to-local-filesystem byte-exact materializer is exposed. Therefore this document advances only the next distinct evidence task recorded in `state/CURRENT.md`; it is not an executable PASS for LAB-086 or LAB-093..100.

## Primary donors

- RFC 9162, Certificate Transparency v2: authenticated tree heads, inclusion/consistency proofs, and conflicting views as evidence of misbehavior. https://www.rfc-editor.org/rfc/rfc9162
- Nakkiran & Blasiok, The Generic Holdout: adaptive safety depends on controlling the information disclosed from the holdout, not merely renaming data or trials. https://arxiv.org/abs/1809.05596
- Dwork et al., Generalization in Adaptive Data Analysis and Holdout Reuse: repeated adaptive reuse can overfit evaluation data. https://arxiv.org/abs/1506.02629
- NIST SP 800-226: differential-privacy loss is cumulative and must compose across analyses that touch the same protected subjects/data. https://doi.org/10.6028/NIST.SP.800-226
- RFC 8446, TLS 1.3: session tickets are resumable PSK authority; ticket lifetime is bounded and chained ticket issuance can extend original keying-material ancestry unless separately limited. https://www.rfc-editor.org/rfc/rfc8446
- RFC 9345, Delegated Credentials: DCs are short-lived, cannot be independently early-revoked, and cached DCs should be revalidated on resumption. https://www.rfc-editor.org/rfc/rfc9345
- RFC 9325 plus NIST SP 800-88r2: old ticket/cryptographic keys require explicit retirement/destruction semantics; cryptographic erase depends on sanitizing the actual confidentiality keys across the relevant recovery universe. https://www.rfc-editor.org/rfc/rfc9325 and https://doi.org/10.6028/NIST.SP.800-88r2

## 1. Observer attestation issuer compromise, cross-signing, and lineage merge

### Boundary

`ATTESTATION_CROSS_SIGNED != FAILURE_DOMAIN_INDEPENDENT`

A domain claim signed by multiple issuers is not automatically stronger when those issuers share a compromised root, operator, control plane, recovery authority, or issuance pipeline. Quorum independence must be computed over authenticated issuer/authority lineage, not signature count.

Canonical domain-attestation evidence should bind:
- subject observer/member key;
- stable observer authority-lineage id;
- asserted failure-domain dimensions;
- issuer lineage id and issuer-root generation;
- cross-signing parents and their lineage ids;
- validity interval and revocation generation;
- predecessor attestation digest;
- compromise/degraded flags inherited from predecessor issuer generations.

### Cross-signing rule

`MULTIPLE_SIGNATURES != MULTIPLE_FAILURE_DOMAINS`

If issuer A and issuer B are descendants of the same compromised root or share the same required failure domain, their signatures count once for that dimension. Cross-signing can prove continuity during rotation, but it cannot manufacture independence.

### Lineage merge rule

If two previously separate issuer lineages are merged operationally or cryptographically, the successor must inherit the union of unresolved compromise flags and the stricter independence interpretation until a recovery transition proves a new independent authority set. A merge cannot erase a predecessor compromise merely by assigning a new lineage id.

### Recovery-root compromise

`NEW_ISSUER_ROOT != CLEAN_ISSUER_HISTORY`

After compromise, a successor issuer root must commit to the last uncontested root, all known conflicting/forged attestations, predecessor issuer-set digest, new threshold policy, and degraded interval. Old conflicting signed objects remain evidence. RFC 9162 is the donor for preserving authenticated conflicting views instead of allowing a preferred later view to overwrite the existence of equivocation.

## 2. Authenticated compact holdout-root completeness, GC proof, and restoration

### Boundary

`COMPACT_ROOT_AUTHENTIC != COMPACT_ROOT_COMPLETE`

A compact provenance root can be correctly signed while omitting a disclosure edge, generator dependency, analyst/controller lineage, or candidate-family interaction. Authenticity proves who committed the root; it does not prove the root summarizes every required predecessor fact.

A GC-eligible compact root therefore needs a deterministic coverage manifest over the predecessor provenance epoch:
- predecessor root digest;
- canonical node-count / event-sequence range;
- ordered or Merkle-committed set of provenance event digests;
- disclosure-class cumulative counters;
- dataset/generator/controller/candidate-family lineage roots;
- unresolved/missing-node bitmap or explicit zero-gap proof;
- successor root generation.

RFC 9162 inclusion/consistency proofs are a useful donor pattern: compaction should prove that the successor commitment includes the complete authenticated predecessor event prefix required by policy, not merely a hand-picked subset.

### GC rule

Raw provenance nodes may be deleted only after:
1. successor compact root is durably committed;
2. coverage proof verifies every required predecessor event/range;
3. independent recovery copy or equivalent authenticated witness for the successor root exists;
4. no unresolved provenance gaps remain.

`RAW_NODE_GCED != DISCLOSURE_ANCESTRY_GONE`.

### Lost provenance restoration

If raw nodes are later lost, restoration from the compact root may recover authorization/accounting state only to the fidelity actually committed by the root. Unknown omitted details stay `PROVENANCE_INCOMPLETE`; they do not default to zero disclosure. A stale backup restored before a later disclosure root is fenced by the monotonic successor generation.

## 3. Privacy-scope equivalence under probabilistic identity resolution and subject migration

### Boundary

`IDENTITY_MATCH_PROBABILITY_BELOW_ONE != SUBJECTS_DISJOINT`

Probabilistic entity resolution changes certainty, not the cumulative privacy-loss obligation. Two records/scopes with a non-zero credible probability of representing the same protected subject cannot be treated as certainly disjoint solely because the resolver has not crossed a match threshold.

Recommended scope accounting carries:
- stable record/data lineage;
- candidate subject-identity set or equivalence-class reference;
- confidence/evidence band used by the resolver;
- resolver/model/version lineage;
- migration/split/merge predecessor ids;
- charged/reserved/unknown privacy floors.

### Conservative overlap rule

For authority decisions, classify relationships as:
- `PROVEN_SAME`;
- `PROVEN_DISJOINT` under an accepted deterministic proof;
- `POSSIBLE_OVERLAP`;
- `UNKNOWN`.

Only `PROVEN_DISJOINT` permits independent budget capacity. `POSSIBLE_OVERLAP` and `UNKNOWN` carry conservative composed loss until evidence resolves them. This follows the NIST SP 800-226 donor principle that privacy loss composes across repeated analyses of the same protected data/subjects.

### Subject migration

A subject moving tenants, regions, account ids, household/group identities, or pseudonyms does not create a fresh privacy budget. Successor scopes inherit the maximum relevant cumulative spend plus unresolved reservations/possible disclosures from all predecessor identities that may map to the same subject.

`NEW_PSEUDONYM != NEW_PRIVACY_SUBJECT`.

Resolver rollback or retraining cannot lower historical spend merely by lowering a current match probability.

## 4. Multi-replica destructive effect reconciliation after partial success

### Boundary

`SOME_REPLICAS_ACKED != GLOBAL_EFFECT_COMPLETE`

A destructive request may succeed on a subset of replicas before timeout/partition. Retrying the same logical request as a fresh destructive generation can duplicate effects, race tombstone/version semantics, or violate retention holds.

Each destructive operation should therefore bind:
- immutable logical operation id;
- policy/delegation/operation generation;
- canonical replica-set membership epoch;
- per-replica resource-fence generation;
- effect token / precondition version where the backend supports it;
- per-replica outcome: `NOT_ATTEMPTED`, `NO_EFFECT`, `EFFECT_CONFIRMED`, `EFFECT_UNKNOWN`, `REJECTED_STALE_FENCE`;
- reconciliation generation.

### Reconciliation rule

After partial success, the coordinator must not mint a new logical destructive operation until every destructive-capable member from the original membership epoch is either:
1. reconciled to a definite predecessor effect/no-effect outcome, or
2. fenced beyond the predecessor operation so it can no longer execute it.

A retry should reuse the immutable logical operation id / idempotency token where supported and must carry a monotonic fence. A late replica receiving the predecessor after successor completion must reject it by resource fence.

### Membership churn

Removing a replica from current membership does not erase its possible predecessor effect. The successor membership transition must either present a final reconciliation result for the removed replica or a durable proof that it is fenced/unreachable as a destructive authority for the relevant resource generation.

`MEMBER_REMOVED != PREDECESSOR_EFFECT_IMPOSSIBLE`.

## 5. PQ/ECH/DC ticket-retirement quorum changes during region membership churn

### Boundary

`CURRENT_REGION_QUORUM_ACKED != ALL_PREDECESSOR_TICKET_SPEND_AUTHORITY_RETIRED`

A region removed from the current membership set may still possess old ticket-encryption keys, cached session state, delegated credentials, replay state, or routable infrastructure. Retirement quorum therefore must be evaluated over every predecessor spend authority that could still accept the affected ticket ancestry, not only the current region list.

Canonical retirement epoch should commit to:
- ticket-generation ancestry root;
- certificate/DC/PQ/ECH/backend identity floors;
- ticket-key generation and retirement deadline;
- predecessor and successor region-spend-authority inventories;
- per-authority rejection/fence acknowledgement;
- replay-state floor for 0-RTT;
- erasure/zeroization evidence state for retired secrets;
- maximum ancestry expiry bound.

### Old-key erasure evidence

`KEY_REMOVED_FROM_ACTIVE_CONFIG != KEY_UNRECOVERABLE`

Old ticket keys are not considered erased merely because a current process no longer loads them. Backups, DR stores, offline recovery systems, HSM replicas, and externally managed copies belong to the erasure evidence boundary when they can restore ticket-decryption authority. NIST SP 800-88r2 is the donor for cryptographic erase requiring sanitization of the confidentiality keys and validation of the sanitization process.

### Bounded ancestry lifetime

RFC 8446 warns that repeatedly issuing successor tickets can indefinitely extend keying material derived from the original authenticated handshake. Therefore the runtime must track an ancestry birth/floor independent of the current ticket ciphertext/key generation and impose a maximum total ancestry lifetime. Re-encryption, region handoff, DC replacement, ECH/PQ rotation, or successor ticket issuance cannot reset that clock.

### Regional churn rule

A removed/rejoining region remains `RESUMPTION_QUARANTINED` until it proves:
- predecessor ticket generations rejected/fenced;
- current identity/PQ/ECH/DC/revocation floors installed;
- replay floor current if 0-RTT is enabled;
- old recoverable ticket keys are erased or cryptographically fenced by a stronger monotonic admission floor;
- its acknowledgement is bound to current regional authority lineage.

Full-auth 1-RTT may be restored earlier when current identity checks pass; PSK resumption and especially 0-RTT remain separately gated.

## 40-case RED-first matrix

### Observer issuer lineage / cross-signing
1. Two cross-signatures from issuers sharing one root -> count as one root domain.
2. Different issuer ids backed by one control plane -> no new control-plane independence.
3. Issuer root rotates normally with predecessor cross-sign -> continuity preserved, no extra independence minted.
4. Compromised issuer cross-signs fresh child -> child inherits compromise flag.
5. Two formerly independent issuers merge -> successor inherits union of unresolved compromise flags.
6. New lineage id after merge omits predecessor links -> reject successor attestation.
7. Recovery root omits known forged/conflicting attestation -> fail closed.
8. Stale but valid issuer-root generation after recovery -> reject for current quorum.

### Holdout compact-root completeness / GC
9. Signed compact root with complete predecessor event prefix -> eligible for coverage verification.
10. Signed compact root omits one disclosure event -> incomplete, no GC.
11. Node count matches but event digest set differs -> reject coverage proof.
12. Disclosure counters match but generator lineage omitted -> incomplete.
13. Raw nodes deleted before successor root durable commit -> recovery failure, fail closed.
14. Raw nodes deleted after valid coverage + durable successor -> restore accounting from compact root.
15. Backup restores pre-disclosure compact root -> stale by successor-generation floor.
16. Lost raw node was never covered by compact root -> mark `PROVENANCE_INCOMPLETE`, never assume zero exposure.

### Probabilistic privacy identity / subject migration
17. Resolver says 0.8 probability same subject -> `POSSIBLE_OVERLAP`, compose conservatively.
18. Resolver says 0.2 probability but non-zero credible overlap -> still not `PROVEN_DISJOINT`.
19. Deterministic authenticated evidence proves disjoint -> independent allocator may split capacity.
20. Two pseudonyms later resolve to same subject -> merge cumulative spend/reservations/unknown floors.
21. Same subject migrates region/tenant -> successor inherits predecessor spend.
22. Resolver-model rollback lowers match probability -> historical spend does not decrease.
23. Split identity later re-merged -> no duplicated remaining budget.
24. Deleted identifier disappears from current graph after prior disclosure -> charged ancestry remains.

### Retention partial effect / anti-replay
25. Delete confirmed on replica A, timeout on B -> logical operation remains unresolved.
26. Fresh operation id issued after partial timeout -> reject while predecessor can still execute.
27. Retry with same immutable op id and current fence -> backend idempotency/reconciliation path only.
28. Late predecessor reaches stale replica after fence advance -> reject before effect.
29. Removed replica has `EFFECT_UNKNOWN` and no fence proof -> membership change cannot claim global completion.
30. Removed replica presents durable fence beyond predecessor -> predecessor no longer spendable there.
31. Replica snapshot rollback forgets completed op but retains old queue -> resource-fence floor blocks replay.
32. All original replicas reconciled/fenced -> successor destructive generation may proceed.

### Ticket retirement / membership churn / erasure
33. Current regions ack retirement but removed predecessor region still has spend authority -> incomplete retirement.
34. Removed region is network-isolated but retains recoverable old key -> not erasure proof; maintain fence/quarantine.
35. Active config drops old ticket key but DR backup can restore it -> key not globally unrecoverable.
36. Valid sanitization evidence covers active+backup/HSM recovery domains -> mark erasure confirmed for that inventory epoch.
37. Re-encrypt old ticket under new regional key -> ancestry birth unchanged.
38. Successor ticket after certificate/DC/PQ/ECH rotation -> unresolved compromised ancestry remains fenced.
39. Ticket ciphertext lifetime valid but total ancestry lifetime exceeded -> reject resumption.
40. Rejoining region has current cert/PQ/ECH but stale replay floor -> eligible policy may allow full-auth 1-RTT; keep 0-RTT disabled and PSK subject to retirement floor.

## Audit notes

- These contracts intentionally distinguish cryptographic authenticity from completeness, freshness, independence, and effect reconciliation.
- Conservative `UNKNOWN` states are required where omission cannot be disproved; absence of evidence is not converted into positive safety evidence.
- Cross-signing, compaction, identity resolution, replica churn, and ticket re-encryption are all successor transformations. None may reset unresolved predecessor authority/evidence floors.
- No production code was changed in this slice because the owning executable branches remain behind the exact-source materialization gate.

## Decision

Freeze `OBSERVER_ISSUER_LINEAGE_HOLDOUT_GC_PRIVACY_IDENTITY_RETENTION_PARTIAL_EFFECT_TICKET_CHURN_V1_FROZEN` for future RED-first implementation. It composes with LAB-093..100 and the preceding observer/holdout/privacy/retention/TLS design freezes, but does not change their READY/draft status and does not substitute for LAB-086 executable validation.