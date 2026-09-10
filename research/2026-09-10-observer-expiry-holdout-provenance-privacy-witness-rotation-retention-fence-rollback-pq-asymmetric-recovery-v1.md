# Observer emergency expiry, holdout provenance, privacy witness rotation, retention fence rollback, and PQ/ECH asymmetric recovery

Date: 2026-09-10
Status: DESIGN FROZEN / RED-FIRST CONTRACT
Parent: LAB-093/#178 and follow-on LAB-094..100

## Run capability observation

LAB-086 remained priority #1. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`. GitHub connector reads/writes remain available, but no supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed in this run. Therefore this note does **not** claim any new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, or conflict PASS; PR #165 remains draft.

## Frozen contract

`OBSERVER_EXPIRY_HOLDOUT_PROVENANCE_PRIVACY_WITNESS_ROTATION_RETENTION_FENCE_ROLLBACK_PQ_ASYMMETRIC_RECOVERY_V1_FROZEN`

### 1. Observer emergency-admission expiry/replacement under partial recovery-authority compromise

Primary donor: RFC 9162 Certificate Transparency v2.0.

RFC 9162 gives authenticated tree heads and consistency/inclusion proofs, but one valid signed view does not prove that no conflicting view exists elsewhere. Recovery therefore cannot treat emergency membership merely as an expiring ACL entry; the replacement transition must preserve what the emergency member observed and the exact trust state under which it was admitted.

Freeze:

- `EMERGENCY_MEMBER_EXPIRED != EMERGENCY_EVIDENCE_EXPIRED`.
- `RECOVERY_AUTHORITY_QUORUM_REACHED != RECOVERY_AUTHORITY_UNCOMPROMISED`.
- Emergency admission records bind predecessor observer epoch, recovery-authority generation, admitted observer identity/failure domain, last uncontested checkpoint, known conflict set, admission reason, start, expiry, and allowed role.
- If part of the recovery authority is later suspected or proven compromised, every emergency admission it helped authorize is classified by overlap with the compromised signer/domain set. Admissions are not silently grandfathered.
- Expiry removes future quorum/admission power but never deletes checkpoint/conflict evidence already produced by the emergency member.
- Replacement requires a successor transition that explicitly references the expiring admission and carries forward all evidence; a replacement observer is not a retroactive signer for the predecessor interval.
- A recovery transition signed by a quorum that still satisfies numeric threshold but whose independent-domain floor falls below policy is `DEGRADED`, not recovered.
- Unknown compromise interval or incomplete signer provenance fails closed for claims of unique observer history; observation/audit may continue, but authoritative conflict adjudication waits for a clean successor authority.

### 2. Correlated holdout provenance through derived/synthetic datasets and disclosure-budget composition

Primary donors: Dwork et al., *Generalization in Adaptive Data Analysis and Holdout Reuse*; Nakkiran/Błasiok, *The Generic Holdout*.

Adaptive validity depends on limiting information leaked by the holdout. A derived or synthetic dataset is not automatically independent merely because row ids and raw values differ; if generation used holdout samples, labels, scores, gradients, accepted/rejected hypotheses, or a model trained with holdout feedback, the new data inherits exposure lineage.

Freeze:

- `SYNTHETIC != INDEPENDENT`.
- `DISJOINT_ROWS != DISJOINT_INFORMATION`.
- Dataset provenance is a DAG, not a UUID. Each holdout records source datasets, transforms/generators, model checkpoints, analyst/controller lineage, and whether holdout-derived outputs influenced generation.
- Synthetic data generated from a model that consumed holdout feedback inherits that holdout's exposure lineage unless a separately justified mechanism provides a quantified independence/privacy guarantee.
- Candidate validation across correlated holdouts composes disclosure budgets; renaming or sharding a family cannot reset exposure.
- Generic-Holdout-style one-bit answers and score/ranking disclosures are separate mechanisms with separate budgets. A mechanism upgrade to richer disclosure cannot reuse the old accounting as if information release were unchanged.
- If provenance is incomplete, the safe classification is `CORRELATION_UNKNOWN`; use fresh independently collected confirmation data rather than infer independence from missing edges.

### 3. Privacy spend-witness quorum overlap, rotation, and stale-witness eviction

Primary donor: NIST SP 800-226 privacy-budget model, where privacy budget bounds cumulative privacy loss across analyses on a dataset.

Freeze:

- `WITNESS_ROTATED != SPEND_FLOOR_ROTATED_AWAY`.
- `STALE_WITNESS_EVICTED != STALE_STATEMENT_INVALIDATED_RETROACTIVELY`.
- Witness-set rotation binds predecessor/successor generation, subject/dataset/purpose scope, maximum uncontested cumulative spend floor, unresolved reservation/transfer uncertainty floor, signer membership, independent failure domains, and a monotonic recovery counter.
- A successor witness quorum must overlap the predecessor trust chain through an authenticated handoff or an independently authorized recovery bridge; a fresh key set alone cannot authorize a lower floor.
- During rotation, the accepted spend floor is the maximum authenticated non-superseded floor plus unresolved uncertainty, never the minimum among quorums.
- Stale witness eviction removes future voting authority. Its old signed statements remain evidence and can still expose equivocation or a higher historical floor.
- Same-generation conflicting spend statements are equivocation; rotation does not erase the degraded interval.
- If quorum overlap is insufficient because too many predecessor witnesses are compromised/unavailable, recovery uses dual control: independent recovery authority + spend-continuity evidence. Unknown spend stays charged/fenced.

### 4. Retention resource-fence generation rollback/recovery and offline destructive-job replay

Freeze:

- `CONTROL_PLANE_FENCE_CURRENT != RESOURCE_FENCE_CURRENT`.
- `JOB_AUTHORIZED_ONCE != JOB_AUTHORIZED_AT_EXECUTION`.
- Every destructive operation presents a resource-verifiable tuple: resource id, capability/delegation generation, revocation floor, hold/policy floor, execution-lease generation, job id/attempt id, and monotonic resource-fence generation.
- Resource authorities persist the highest accepted fence generation in rollback-resistant state appropriate to the deployment. A restored older resource snapshot cannot lower this floor.
- If a resource detects fence rollback/unknown monotonic state, destructive operations enter quarantine until a successor recovery transition proves a nondecreasing floor.
- Offline/queued jobs never carry durable destructive authority. On each attempt they reacquire current authorization and are rejected if their job/capability/fence generation predates revocation or recovery.
- Retry after ambiguous execution uses an idempotent operation/attempt identity or explicit reconciliation; timeout is not proof that deletion did not happen.
- Rejoining workers/resources cannot self-assert that their cached lease or fence is current.

### 5. PQ/ECH cross-SNI equivalence-policy rollback, DC replacement ancestry, and ticket admission after asymmetric regional recovery

Primary donors: RFC 9846 (TLS 1.3) and RFC 9345 (Delegated Credentials).

RFC 9846 permits different-SNI resumption only when the new SNI is valid for the original certificate and recommends same-SNI resumption unless external knowledge establishes that the servers can accept each other's tickets. It also requires consistent state for strong 0-RTT anti-replay in distributed deployments. RFC 9345 requires delegated credentials to be revalidated when cached for resumption because a DC can expire while tickets remain decryptable.

Freeze:

- `EQUIVALENCE_POLICY_RESTORED != OLD_EQUIVALENCE_POLICY_CURRENT`.
- `DC_REPLACED != OLD_TICKET_ANCESTRY_SANITIZED`.
- `REGION_RECOVERED_FOR_1RTT != REGION_RECOVERED_FOR_RESUMPTION_OR_0RTT`.
- Cross-SNI service-equivalence policy carries a monotonic generation and binds service identities, accepted certificate/DC lineage, PQ/ECH/backend generations, ticket-key generation, revocation floor, and replay/admission policy.
- Snapshot rollback of equivalence policy cannot authorize older cross-SNI relationships. A lower generation is stale even if cryptographic material still decrypts tickets.
- Replacing an expired/compromised DC creates new ancestry. Tickets descended from the old DC remain bound to the old ancestry and are rejected when current policy says that ancestry is no longer admissible.
- Regional recovery is staged: current full-auth 1-RTT may be enabled once identity/current crypto state is verified; PSK resumption waits for ticket-admission/revocation convergence; 0-RTT additionally waits for replay-authority convergence.
- If region A has recovered to generation `g+1` while B remains at `g`, B must not accept tickets whose safety depends on `g+1`, and A must not treat B's stale acceptance as global convergence.
- A late region rejoins in resumption quarantine and proves current equivalence, ticket-key, revocation, replay, ECH/PQ, backend and ancestry floors before admission.

## RED-first matrix (40 cases)

### Observer emergency expiry/replacement (O1-O8)
1. O1 — emergency member expires; implementation deletes its prior conflict evidence => reject.
2. O2 — replacement observer counted retroactively for predecessor interval => reject.
3. O3 — recovery authority numeric threshold passes but independent-domain floor is lost => degraded/reject recovery claim.
4. O4 — later compromise overlaps signers of an emergency admission; admission silently grandfathered => reject.
5. O5 — replacement transition omits predecessor admission id/evidence => reject.
6. O6 — expired member still votes on new authoritative checkpoint => reject.
7. O7 — compromise interval unknown but unique-history claim proceeds => reject.
8. O8 — bounded expiry + evidence preservation + explicit successor replacement under clean domain threshold => accept.

### Holdout provenance/composition (H1-H8)
9. H1 — synthetic holdout generated by model trained using prior holdout scores => correlated lineage.
10. H2 — row-disjoint derived dataset shares labels/features generated from holdout feedback => not independent.
11. H3 — new dataset UUID with same upstream collection slice => exposure carries forward.
12. H4 — Generic-Holdout one-bit mechanism silently starts returning ranking => reject unchanged-budget claim.
13. H5 — two correlated holdouts each under local budget but combined disclosure exceeds composed policy => reject.
14. H6 — controller/model checkpoint transferred to another analyst identity => lineage/exposure carries forward.
15. H7 — provenance edge missing after rollback => `CORRELATION_UNKNOWN`, not independent.
16. H8 — independently collected confirmation set with clean provenance and predeclared disclosure mechanism => fresh confirmation allowed.

### Privacy spend-witness rotation (P1-P8)
17. P1 — successor keys valid but no predecessor handoff/recovery bridge => cannot lower/reauthorize floor.
18. P2 — predecessor reports 7 units, successor starts at 5 => reject.
19. P3 — stale witness removed; its historical higher signed floor ignored => reject.
20. P4 — same-generation witnesses sign 8 and 11 units => equivocation; floor at least 11/unknown as policy dictates.
21. P5 — rotation loses unresolved reservation => reject.
22. P6 — snapshot restores older witness generation with valid signatures => stale.
23. P7 — insufficient overlap; recovery chooses zero because old quorum unavailable => reject.
24. P8 — authenticated handoff/dual-control recovery carries max floor + uncertainty and evicts stale future authority => accept.

### Retention fence rollback/offline replay (R1-R8)
25. R1 — resource restored to older fence generation and accepts delete => reject.
26. R2 — control plane current but resource revocation floor stale => resource rejects.
27. R3 — queued delete authorized before revocation executes later without reauth => reject.
28. R4 — offline job retries same ambiguous deletion with new attempt id and no reconciliation => reject unsafe duplicate authority.
29. R5 — resource monotonic state unknown after restore => destructive quarantine.
30. R6 — worker presents cached valid lease but stale fence generation => reject.
31. R7 — successor recovery proves nondecreasing fence/revocation/hold floors and resource installs them before delete => accept.
32. R8 — timeout after possible deletion is treated as no-op and capacity/history rolled back => reject; reconcile first.

### PQ/ECH asymmetric regional recovery (T1-T8)
33. T1 — equivalence-policy store rolls back to older generation; old cross-SNI ticket accepted => reject.
34. T2 — DC replaced after compromise; descendant ticket from old DC decrypts => reject if old ancestry fenced.
35. T3 — region A current, B stale; A declares global resumption convergence => reject.
36. T4 — recovered region enables 1-RTT full auth while keeping resumption quarantined => accept staged recovery.
37. T5 — 0-RTT enabled before replay-authority convergence after restart => reject.
38. T6 — late region has current ticket key but stale revocation/equivalence floor => quarantine.
39. T7 — cross-SNI certificate coverage valid but current equivalence policy absent => no cross-SNI resumption.
40. T8 — all regions attest current equivalence/ticket-key/revocation/replay/ECH/PQ/backend/DC ancestry floors, then explicit successor admission enables resumption/0-RTT according to policy => accept.

## Audit / scope

This is a design/evidence freeze, not executable proof. It extends the LAB-093 family without changing LAB-086 priority, and it does not authorize ready/merge status for any draft PR. The matrix must become concrete RED tests before production refactoring once exact source execution is available.

## Primary sources

- RFC 9162, Certificate Transparency Version 2.0: https://www.rfc-editor.org/rfc/rfc9162
- Dwork et al., Generalization in Adaptive Data Analysis and Holdout Reuse: https://arxiv.org/abs/1506.02629
- Nakkiran & Błasiok, The Generic Holdout: https://arxiv.org/abs/1809.05596
- NIST SP 800-226 / privacy budget glossary: https://csrc.nist.gov/glossary/term/privacy_budget
- RFC 9345, Delegated Credentials for TLS and DTLS: https://www.rfc-editor.org/rfc/rfc9345
- RFC 9846, TLS 1.3: https://www.rfc-editor.org/rfc/rfc9846
