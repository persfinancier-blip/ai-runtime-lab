# Observer emergency admission, reusable-holdout identity, privacy spend-witness recovery, retention lease fencing, and PQ/ECH split-brain

Date: 2026-09-10
Status: DESIGN FROZEN / RED-FIRST CONTRACT
Parent: LAB-093/#178 and follow-on LAB-094..100

## Run capability observation

LAB-086 remained priority #1. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`. GitHub connector reads/writes remain available, but no supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed in this run. Therefore this note does **not** claim any new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, or conflict PASS.

## Frozen contract

`OBSERVER_EMERGENCY_HOLDOUT_IDENTITY_PRIVACY_WITNESS_RETENTION_LEASE_PQ_SPLITBRAIN_V1_FROZEN`

### 1. Observer recovery-root compromise and emergency admission

Primary donor: RFC 9162 Certificate Transparency v2.0.

RFC 9162 requires auditors/monitors to check append-only behavior and consistency of the log view presented to query sources; inconsistent authenticated views are signed evidence of misbehavior. Sharing views is an additional system mechanism rather than an automatic property of one valid signature set.

Freeze:

- `VALID_CURRENT_OBSERVER_SIGNATURES != OBSERVER_CONTROL_PLANE_UNCOMPROMISED`.
- `EMERGENCY_ADMISSION != THRESHOLD_SELF_REDUCTION`.
- Compromise of the observer recovery root puts the affected observer-set epoch into a degraded/recovery state. The same root cannot authorize a silent reduction of signer count, independent failure-domain floor, or conflict-evidence obligations and thereby declare itself recovered.
- Emergency admission requires a separately defined recovery authority that binds: predecessor observer-set epoch, last uncontested checkpoint, all known conflicting heads, degraded interval, admitted observer identity and failure domain, emergency reason, expiry, and successor threshold policy.
- Emergency observers are not retroactive witnesses. Their signatures establish successor visibility only after admission.
- Temporary emergency membership expires or is explicitly promoted through a normal successor transition; expiry cannot remove already observed conflict evidence.
- Lowering minimum independent-domain coverage is a distinct high-risk transition and must not be an implicit consequence of unavailable observers.

### 2. Reusable holdout: correlated datasets, analyst identity transfer, and exposure-ledger rollback

Primary donors: Dwork et al., *Generalization in Adaptive Data Analysis and Holdout Reuse* (2015); Nakkiran/Błasiok, *The Generic Holdout* (2018).

The literature's reusable-holdout guarantees depend on the exact mechanism and on controlling information leaked from the holdout. Adaptive reuse can itself overfit the holdout; Generic Holdout's simple strong case deliberately reveals only a limited yes/no result rather than a score/ranking.

Freeze:

- `NEW_DATASET_ID != INDEPENDENT_HOLDOUT`.
- `NEW_ANALYST_ID != FRESH_ADAPTIVITY_BUDGET`.
- `EXPOSURE_LEDGER_RESTORED_FROM_BACKUP != EXPOSURE_ERASED`.
- Dataset independence is semantic/provenance based: overlapping samples, deterministic transforms, shared labels/features, leakage through cached model artifacts, or common upstream collection can correlate supposedly separate holdouts.
- Analyst/controller identity follows transferred state, not login/account name. A new analyst process that receives prior scores, rankings, selected candidates, gradients, prompts, or controller checkpoints inherits the relevant exposure history.
- Holdout exposure accounting is monotonic across snapshot restore, failover, credential rotation, analyst transfer, and candidate-family renaming.
- A mechanism-specific disclosure budget must record mechanism/version, holdout lineage, analyst/controller lineage, disclosure type, query/candidate identity, and outcome visibility.
- If rollback makes prior exposure uncertain, default is `EXPOSURE_UNKNOWN` and fresh independent confirmation data/mechanism, not zero exposure.

### 3. Privacy spend-witness compromise, freshness, and uncertainty-floor succession

Primary donor: NIST SP 800-226 / NIST privacy-budget definition: privacy budget is an upper bound on allowable cumulative privacy loss across analyses on a dataset.

Freeze:

- `SPEND_WITNESS_SIGNATURE_VALID != SPEND_WITNESS_CURRENT`.
- `NEW_SPEND_WITNESS_KEY != CUMULATIVE_SPEND_RESET`.
- `UNKNOWN_SPEND != ZERO_SPEND`.
- Spend-continuity witnesses carry a monotonic witness generation, freshness/recovery counter, subject/dataset/purpose scope, cumulative committed floor, unresolved reservation/transfer floor, and source provenance.
- Witness compromise creates a degraded interval. Successor recovery must carry forward the maximum uncontested cumulative floor plus unresolved/possibly disclosed reservations; it may increase uncertainty but never decrease the already established floor.
- A new witness key without an authenticated predecessor/successor bridge cannot re-authorize lower spend.
- Conflicting valid spend-witness statements at the same logical generation are equivocation evidence. Reconciliation cannot choose the lower statement because it is cheaper.
- Freshness is checked against authenticated monotonic state; wall-clock recency alone is insufficient after rollback/restore.

### 4. Retention revocation acknowledgement equivocation, lease expiry, and resource-side fencing

Freeze:

- `REVOCATION_ACK_RECEIVED != CAPABILITY_UNSPENDABLE`.
- `LEASE_EXPIRED_IN_CONTROL_PLANE != RESOURCE_FENCED`.
- `TWO_VALID_ACKS != CONSISTENT_ACK_HISTORY`.
- Every destructive-capable worker/resource pair has an authenticated revocation/policy/hold floor and a bounded lease generation.
- A revocation acknowledgement binds worker identity, resource scope, capability/delegation generation, revocation floor, lease generation/expiry, and monotonic receipt sequence.
- Conflicting acknowledgements from one worker/resource authority are equivocation evidence and put that authority into destructive quarantine.
- Lease expiry blocks new destructive execution even if queued/offline work was authorized earlier. Execution-time reauthorization is mandatory.
- Resource-side fencing is the final safety boundary: storage/API/resource authority must reject destructive operations whose capability generation, revocation floor, or lease is stale, even if the worker/control plane is partitioned.
- Rejoining workers cannot self-certify freshness; they must obtain current floor/lease state before destructive execution.

### 5. PQ/ECH cross-SNI service-equivalence split-brain, DC expiry, and regional ticket admission convergence

Primary donors: RFC 9846 (current TLS 1.3 publication) and RFC 9345 (Delegated Credentials).

RFC 9846 permits resumption with a different SNI only under certificate validity constraints and recommends same-SNI resumption unless external knowledge indicates the servers can accept each other's tickets. RFC 9345 says cached delegated credentials should be revalidated during resumption because otherwise a connection can resume after the DC expired; DC compromise has no independent early-revocation mechanism apart from parent-certificate revocation and short lifetime.

Freeze:

- `CERTIFICATE_COVERS_BOTH_SNIS != SERVICES_CURRENTLY_EQUIVALENT`.
- `REGION_A_EQUIVALENCE_CURRENT != REGION_B_EQUIVALENCE_CURRENT`.
- `TICKET_DECRYPTS != TICKET_ADMISSIBLE`.
- `DC_VALID_AT_ISSUE != DC_VALID_AT_RESUME`.
- Cross-SNI resumption requires a current authenticated service-equivalence policy generation shared by issuer and admitting region, plus current certificate/DC/PQ/ECH/backend/revocation/replay floors.
- If regions disagree on equivalence-policy generation, the safe state is resumption quarantine for the disputed cross-SNI relationship; 1-RTT with full current authentication may remain available.
- Ticket ancestry records the DC/certificate identity and expiry/revocation generations relevant at issuance. On resumption, a cached DC is revalidated when the implementation relies on cached authentication state.
- Parent-certificate reissue or DC expiry does not silently sanitize descendant tickets.
- Regional ticket admission requires convergence on a minimum revocation/admission floor. A late region must not accept tickets solely because local ticket keys still decrypt them.
- Re-enabling cross-SNI resumption after split-brain is an explicit successor transition; convergence observation alone is not retroactive authorization for tickets issued/admitted under the disputed interval.

## RED-first matrix (40 cases)

### Observer emergency/recovery (O1-O8)
1. O1 — recovery root compromised; same root lowers threshold and signs recovery => reject.
2. O2 — emergency observer admitted without predecessor epoch binding => reject.
3. O3 — admission omits known conflicting head => reject.
4. O4 — emergency member counted retroactively for predecessor quorum => reject.
5. O5 — expired emergency membership still counted => reject.
6. O6 — observer removal deletes prior conflict evidence => reject.
7. O7 — domain floor lowered implicitly because one domain unavailable => reject.
8. O8 — valid successor recovery with independent recovery authority, full conflict set, bounded emergency membership, unchanged-or-stronger domain floor => accept.

### Holdout identity/exposure (H1-H8)
9. H1 — same samples under new dataset UUID => exposure carries forward.
10. H2 — deterministic transformed clone used as 'fresh' holdout => not independent.
11. H3 — new analyst account receives prior score history => exposure carries forward.
12. H4 — controller checkpoint transferred to new process => same analyst/controller lineage.
13. H5 — exposure ledger restored to older snapshot => fail closed `EXPOSURE_UNKNOWN`.
14. H6 — candidate family renamed after holdout feedback => no exposure reset.
15. H7 — one-bit mechanism starts returning scores without budget/mechanism transition => reject guarantee claim.
16. H8 — genuinely disjoint fresh holdout + fresh exposure ledger/root + predeclared mechanism => fresh confirmation allowed.

### Privacy spend witness (P1-P8)
17. P1 — old signed witness with lower cumulative spend replayed => reject.
18. P2 — witness key rotated with no predecessor bridge => cannot lower/reauthorize spend.
19. P3 — two valid same-generation witnesses disagree => mark equivocation/degraded.
20. P4 — recovery chooses lower conflicting spend floor => reject.
21. P5 — possible disclosure during compromised interval unresolved => charged/unknown floor retained.
22. P6 — wall clock newer but monotonic recovery counter older => stale.
23. P7 — snapshot restore loses unresolved reservation => successor must restore uncertainty floor.
24. P8 — independent successor witness quorum carries max uncontested floor + unresolved reservations => accept.

### Retention revocation/lease fencing (R1-R8)
25. R1 — worker ACKs revocation but resource still accepts stale capability => revocation incomplete.
26. R2 — worker emits conflicting ACK floors => destructive quarantine.
27. R3 — queued delete executes after lease expiry without reauth => reject.
28. R4 — offline worker uses pre-revocation capability after reconnect => reject.
29. R5 — control plane renewed lease but resource has older revocation floor => reject at resource.
30. R6 — resource accepts unsigned/local-only lease generation => reject.
31. R7 — worker cannot obtain current floor during partition => no destructive execution.
32. R8 — current bounded lease + current revocation/hold/policy floor acknowledged at worker and enforced at resource => accept.

### PQ/ECH cross-SNI/DC/regional convergence (T1-T8)
33. T1 — certificate covers A/B but service-equivalence policy absent => no cross-SNI resumption.
34. T2 — region A says equivalent, region B has older generation => B quarantines cross-SNI resumption.
35. T3 — ticket decrypts after DC expiry; cached DC not revalidated => reject.
36. T4 — parent certificate revoked/reissued; descendant ticket presented under old ancestry => reject/fence per current policy.
37. T5 — region rejoins with stale revocation/admission floor but valid ticket key => quarantine.
38. T6 — ECH/backend/PQ generation changed incompatibly while ticket remains decryptable => reject resumption.
39. T7 — split-brain interval ends but old disputed-interval ticket is accepted retroactively => reject.
40. T8 — full-auth 1-RTT succeeds under current identity while resumption remains quarantined until explicit converged successor admission => accept staged recovery.

## Audit / scope

This is a design/evidence freeze, not an implementation PASS. It extends LAB-093's capability-boundary family and should become executable tests only when exact source execution is available. It does not change LAB-086 priority and does not authorize merging any current draft PR.

## Primary sources

- RFC 9162, Certificate Transparency Version 2.0: https://www.rfc-editor.org/rfc/rfc9162
- Dwork et al., Generalization in Adaptive Data Analysis and Holdout Reuse: https://arxiv.org/abs/1506.02629
- Nakkiran & Błasiok, The Generic Holdout: https://arxiv.org/abs/1809.05596
- NIST privacy budget glossary / SP 800-226: https://csrc.nist.gov/glossary/term/privacy_budget
- RFC 9345, Delegated Credentials for TLS and DTLS: https://www.rfc-editor.org/rfc/rfc9345
- RFC 9846, TLS 1.3: https://www.rfc-editor.org/rfc/rfc9846
