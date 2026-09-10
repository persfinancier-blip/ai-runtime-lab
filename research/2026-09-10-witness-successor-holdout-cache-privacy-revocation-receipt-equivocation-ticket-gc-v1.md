# Witness successor / holdout-cache / privacy-revocation / external-receipt / ticket-GC contract v1

Date: 2026-09-10
Status: FROZEN DESIGN EVIDENCE; executable RED/GREEN pending
Contract: `WITNESS_SUCCESSOR_HOLDOUT_CACHE_PRIVACY_REVOCATION_RECEIPT_EQUIVOCATION_TICKET_GC_V1_FROZEN`

## Scope

This slice extends LAB-093 follow-up evidence while LAB-086 exact execution remains blocked by lack of a supported byte-exact connector-to-local-filesystem materializer. It does **not** substitute for LAB-086 executable validation.

## Sources / donors

- RFC 9162 (Certificate Transparency v2): append-only consistency, signed tree heads/checkpoints, inclusion/consistency proofs, and the explicit limitation that global view consistency requires comparing observations across entities.
- Dwork et al., *Generalization in Adaptive Data Analysis and Holdout Reuse* (2015): repeated adaptive disclosure can overfit a holdout; validation mechanisms must bound information flow.
- NIST SP 800-226 / NIST privacy-budget glossary: privacy budget is an upper bound on cumulative privacy loss across analyses on a dataset.
- RFC 8446 / RFC 9846 TLS 1.3: 0-RTT replay limitations; resumption tickets can otherwise extend ancestry of original keying material and implementations should bound total lifetime.
- RFC 9325: ticket-encryption keys must rotate regularly and old keys must be destroyed after validity.

## Frozen boundaries

### 1. Witness successor authorization under partial predecessor compromise

`SUCCESSOR_QUORUM_VALID != SUCCESSOR_LINEAGE_AUTHORIZED`

A new witness set is accepted only when the transition proves continuity from the last non-disputed predecessor state and does not allow the compromised minority to silently disappear evidence.

Required transition tuple:

`(log_id, predecessor_membership_epoch, predecessor_checkpoint, predecessor_conflict_digest, successor_membership_epoch, successor_member_lineages, threshold, independent_domain_floor, transition_nonce)`.

Rules:
- successor authorization requires the configured recovery rule over predecessor authority plus any independent recovery/witness-root rule;
- removed or expired predecessor witnesses lose future voting power but their previously authenticated conflict/checkpoint evidence remains durable;
- re-keying or renaming an operator does not create a new independent failure domain;
- partial predecessor compromise cannot lower the recovery threshold by authorizing a transition under the same compromised authority alone;
- if the last uncontested checkpoint cannot be established, enter `WITNESS_RECOVERY_QUARANTINE` rather than selecting a convenient branch.

### 2. Cross-log checkpoint retention / GC proof

`CHECKPOINT_COMPACTED != CHECKPOINT_HISTORY_DISPENSABLE`

A compact root may replace raw checkpoints only after proving that all authority-relevant predecessor intervals are covered.

Minimum compact-root commitments:
- log identity;
- first/last covered tree size;
- first/last checkpoint hash;
- membership epochs crossed;
- digest of conflict/equivocation evidence;
- successor compact-root generation;
- predecessor compact-root hash;
- retention cutoff policy version.

GC is forbidden while any unresolved split-view/conflict interval intersects the candidate range. A Merkle inclusion proof only proves membership in one authenticated tree; it does not prove that no conflicting authenticated tree was served elsewhere.

### 3. Holdout correlation through shared feature / embedding caches

`DISTINCT_DATASET_ROWS != INDEPENDENT_HOLDOUT_INFORMATION`

If candidate generation, scoring, training, or analyst tooling can read embeddings/features/statistics computed from the holdout, that cache is part of the disclosure channel even when raw holdout rows are inaccessible.

Rules:
- holdout provenance records derived feature/embedding/cache lineage;
- feature stores computed from holdout data inherit the same disclosure ancestry and exposure budget;
- cache snapshots, approximate-nearest-neighbor indexes, learned normalizers, label statistics, ranks, and score histograms count as derived disclosures when they can influence adaptive candidate choice;
- deleting raw holdout rows does not reset exposure if derived artifacts remain;
- changing analyst/account/model IDs does not create fresh budget when the same adaptive controller or shared derived cache persists.

### 4. Privacy disjointness proof revocation after identity-graph merge

`DISJOINTNESS_PROOF_VALID_AT_T0 != DISJOINTNESS_PROOF_VALID_AFTER_GRAPH_MERGE`

A proof that two privacy scopes were disjoint is versioned evidence, not permanent truth.

Bind proof to:
`(subject_set_versions, resolver/model version, identity_graph_epoch, evidence_cutoff, proof_expiry, uncertainty_bound)`.

Rules:
- identity-graph merge/link events revoke affected disjointness proofs;
- stale proofs may remain historical evidence but cannot authorize new independent-budget accounting;
- spend already charged under previously separate scopes is reconciled conservatively after a merge; no budget is refunded merely because historical accounting used different scope IDs;
- negative resolver output is not proof of disjointness;
- unresolved linkage uncertainty carries forward as overlap uncertainty until superseded by fresher evidence.

### 5. External receipt-provider equivocation and bounded compensation loops

`VALID_PROVIDER_RECEIPT != UNIQUE_PROVIDER_EFFECT_HISTORY`

A provider can issue two individually authentic but mutually inconsistent receipts. Receipt verification therefore needs an authenticated provider-effect sequence/fence, not signature validity alone.

Receipt tuple should bind:
`(provider_id, provider_key_epoch, logical_operation_id, semantic_idempotency_digest, provider_effect_id, effect_sequence, predecessor_effect_digest, effect_kind, result_digest, timestamp_or_epoch)`.

Rules:
- conflicting receipts for the same logical operation enter `PROVIDER_EQUIVOCATION` and stop blind retries;
- compensation is a new effect referencing the original effect; it does not erase the original event;
- compensation-of-compensation must carry a monotonically increasing compensation generation and bounded policy limit;
- reaching the loop bound requires human or policy-authorized reconciliation, not automatic oscillation;
- multi-provider workflows remain `EFFECT_UNKNOWN/PARTIAL` until every provider effect is either confirmed, explicitly reversed by a separately confirmed compensation, or fenced from future execution.

### 6. Ticket security-epoch GC only after predecessor authority extinction

`TICKET_EXPIRED_LOCALLY != PREDECESSOR_AUTHORITY_EXTINCT_GLOBALLY`

A ticket security epoch may be garbage-collected only after all ways to spend or resurrect predecessor authority are proved extinct.

Required extinction evidence covers:
- maximum ticket lifetime and bounded ancestry lifetime;
- active and retired ticket-encryption keys;
- KMS/HSM wrapped copies;
- backup/DR snapshots and restore inventories;
- regions/replicas that can still decrypt or validate predecessor tickets;
- replay-window state needed for 0-RTT;
- certificate/DC/PQ/ECH policy generations that constrain admissibility;
- recovery credentials capable of restoring old ticket keys.

Rules:
- restoring a snapshot with a lower `ticket_security_epoch` never lowers the monotonic floor;
- a stale/restored region remains `RESUMPTION_QUARANTINED` until it proves current epoch and revocation floors;
- fresh full-auth 1-RTT may be enabled before PSK resumption when identity/authentication is current;
- PSK 1-RTT requires ticket/key/policy ancestry convergence;
- 0-RTT additionally requires replay-state continuity or expiration of the overlapping replay window;
- epoch GC requires durable acknowledgements from every eligible spend/recovery domain or explicit removal plus proof that removed authority is unspendable;
- cryptographic erasure claims are insufficient if recoverable wrapped/backup copies remain.

## RED-first matrix

1. predecessor quorum healthy -> authorized successor accepted.
2. compromised minority alone proposes successor -> reject.
3. successor renames compromised operator as new member -> does not increase independent-domain count.
4. removed witness had prior conflict evidence -> evidence retained after transition.
5. no uncontested predecessor checkpoint -> recovery quarantine.
6. compact root covers clean checkpoint interval -> eligible for GC.
7. compact root omits a membership epoch -> reject completeness.
8. unresolved split-view intersects GC range -> prohibit GC.
9. valid inclusion proof exists only for one conflicting view -> does not establish global consistency.
10. compact-root rollback to lower generation -> reject.
11. raw holdout inaccessible but shared embedding index influences candidate search -> charge same disclosure lineage.
12. derived feature cache copied under new dataset ID -> exposure ancestry preserved.
13. raw holdout deleted while derived score histogram remains -> budget not reset.
14. new analyst account uses same adaptive controller/cache -> no fresh budget.
15. truly independent holdout with independent controller/cache lineage -> may receive fresh budget under policy.
16. disjointness proof matches current graph epoch -> usable until expiry.
17. identity graph merges two prior subjects -> affected proof revoked.
18. resolver negative result only -> insufficient for independent scope accounting.
19. stale proof after graph epoch advance -> reject for new spend.
20. scope merge after prior independent charges -> preserve conservative cumulative spend.
21. one provider signs two contradictory terminal receipts -> provider equivocation.
22. timeout after possible external effect -> `EFFECT_UNKNOWN`, no blind retry.
23. confirmed compensation -> original receipt remains in history; net state may reconcile.
24. compensation loop exceeds configured generation bound -> stop automatic compensation.
25. one of three providers remains unknown -> global operation remains partial/unknown.
26. local ticket expiry reached but DR snapshot can restore key -> epoch not GC-safe.
27. all tickets expired but wrapped predecessor key remains recoverable -> epoch not GC-safe.
28. stale region rejoins below security epoch -> resumption quarantine.
29. PSK ancestry converged but replay state lost -> 1-RTT resumption may be policy-eligible; 0-RTT stays disabled.
30. all spend/recovery domains acknowledge extinction and ancestry lifetime elapsed -> epoch may be GC-eligible.
31. restored backup carries lower monotonic epoch -> floor remains current, old tickets rejected.
32. cert/DC/PQ identity rotated but old ticket key still spendable -> predecessor epoch remains live.
33. region removed from membership but retains usable ticket key -> removal alone is not extinction proof.
34. old receipt key retired -> old receipts remain verifiable evidence, cannot authorize fresh effects.
35. provider rotates receipt key during unresolved operation -> reconciliation spans both key epochs.
36. conflict evidence itself is compacted -> successor digest must authenticate exact retained evidence set/range.
37. feature cache regenerated deterministically from same exposed holdout -> not fresh independence.
38. privacy graph split after earlier merge -> historical merged cumulative spend is not refunded.
39. recovery credentials can recreate destroyed ticket key -> erasure not yet complete.
40. all predecessor authorities extinct but proof inventory missing one recovery domain -> fail closed pending reconciliation.

## Implementation direction

When exact execution becomes available, implement RED tests before production changes. Prefer monotonic generations, authenticated predecessor digests, explicit quarantine states, and resource/provider-side fencing over caller-asserted booleans. Avoid self-hashes stored only beside the mutable evidence they claim to authenticate.

## Current blocker observation

Current run probe: `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`. Connector reads/writes remain available. No new LAB-086 executable PASS is claimed.
