# Witness membership, correlated holdout operators, privacy proof freshness, external receipts, and ticket cutoff — v1

Date: 2026-09-10
Status: `WITNESS_MEMBERSHIP_HOLDOUT_CORRELATION_PRIVACY_PROOF_FRESHNESS_EXTERNAL_RECEIPTS_TICKET_CUTOFF_V1_FROZEN`
Parent: LAB-093/#178 architecture evidence; does not supersede LAB-086 executable priority.

## Scope and evidence boundary

This is a design/evidence freeze only. No repository behavioral PASS is claimed. The current runtime could not byte-exactly materialize the LAB-086 executable closure: direct git transport failed before repository execution because `github.com` could not be resolved. GitHub connector reads/writes remained available, but model-visible connector payloads are intentionally not substituted for the retained exact-byte execution gate.

Primary donors consulted:
- RFC 9162, Certificate Transparency Version 2.0: append-only consistency, inclusion/consistency proofs, and the fact that consistency of views presented to all entities requires sharing observations beyond a single log response. https://www.rfc-editor.org/rfc/rfc9162.html
- Dwork et al., *Generalization in Adaptive Data Analysis and Holdout Reuse* (2015): repeated adaptive reuse can overfit the holdout. https://arxiv.org/abs/1506.02629
- Nakkiran & Blasiok, *The Generic Holdout* (2018): statistical validity depends on separated exploration/holdout data plus deliberately limited information disclosure. https://arxiv.org/abs/1809.05596
- NIST SP 800-226 / NIST differential-privacy guidance: DP claims quantify privacy risk and must be evaluated against the actual mechanism/composition assumptions, not administrative labels. https://www.nist.gov/news-events/news/2025/03/nist-finalizes-guidelines-evaluating-differential-privacy-guarantees-de
- RFC 8446 TLS 1.3: 0-RTT has weaker replay guarantees; after fresh startup, implementations should reject 0-RTT while the recording window overlaps startup; distributed anti-replay designs need an authoritative zone or accept weaker per-zone replay bounds. https://www.rfc-editor.org/rfc/rfc8446.html
- RFC 9325: ticket-encryption keys should rotate regularly and old ticket-encryption keys must be destroyed after their validity period. https://www.rfc-editor.org/rfc/rfc9325.html
- RFC 9149: ticket reuse is a security/privacy concern; clients must not cache tickets beyond seven days. https://www.rfc-editor.org/rfc/rfc9149.html

## Frozen distinctions

### 1. Transparency witness membership and cross-log recovery

`CURRENT_WITNESS_SET_SIGNED != WITNESS_MEMBERSHIP_HISTORY_CONTINUOUS`.

A recovery root must not be accepted merely because the currently configured witness quorum signs it. The verifier needs an authenticated membership lineage that binds predecessor membership epoch, successor membership epoch, admissions/removals, effective cutoff, and retained conflict evidence. A rollback to an older but correctly signed witness-set descriptor is a rollback attack unless a newer authenticated membership state explicitly authorizes it.

`EACH_LOG_INTERNALLY_CONSISTENT != CROSS_LOG_RECOVERY_CONSISTENT`.

When two transparency domains/logs mutually witness or reference recovery state, each log can be locally append-only while the pair disagrees about the recovery root, membership epoch, or declared conflict cutoff. Cross-log recovery therefore needs a canonical tuple such as `(log_id, tree_size, root_hash, recovery_epoch, membership_epoch, conflict_digest)` and consistency evidence over the same tuple. Absence of a conflict in one log is not proof that the other log never observed one.

Membership removal never erases evidence already produced by the removed witness. A removed/expired witness loses future voting authority but its previously authenticated observations remain part of recovery history.

### 2. Holdout independence under correlated operators/data planes

`DISTINCT_WITNESS_IDS != INDEPENDENT_HOLDOUT_WITNESSES`.

Holdout witnesses/operators are independent only if their failure/learning channels are independent enough for the stated guarantee. Separate service accounts, keys, pods, regions, or legal entities are insufficient if they share the same operator, adaptive controller, raw scoring store, hidden labels, feature cache, or analyst feedback channel.

`SEPARATE_HOLDOUT_TABLES != INDEPENDENT_DATA`.

Derived, sampled, duplicated, synthetically perturbed, or deterministically transformed datasets inherit provenance from their source population. A fresh identifier or physical table does not reset disclosure/adaptivity history. Correlated holdout families must carry one exposure lineage unless there is positive provenance evidence supporting independence.

A reusable-holdout state therefore needs at least: dataset lineage root, generator lineage, operator/controller lineage, disclosure mechanism, exposure counter/budget, and predecessor compact root. Threshold changes or witness rotation preserve the maximum prior exposure floor.

### 3. Privacy identity-proof freshness and negative-disjointness evidence

`IDENTITY_PROOF_VALID_ONCE != IDENTITY_PROOF_CURRENT`.

An identity/disjointness proof is scoped to a subject-set version, resolver policy/model version, evidence cutoff, and expiry/freshness window. Reusing an old proof after data ingestion, resolver changes, account linking, identifier reassignment, or subject-set expansion is unsafe.

`NO_MATCH_FOUND != PROOF_OF_DISJOINTNESS`.

Negative search evidence is weaker than positive identity evidence. Resolver failure, stale indexes, incomplete coverage, probabilistic thresholds, or adversarial poisoning can all produce false disjointness. Privacy accounting therefore treats unresolved overlap conservatively. A claim that two scopes are disjoint requires explicit evidence with known coverage and freshness, not merely `resolver_result = none`.

If independent resolvers disagree, the system must not choose the result that yields more budget. It carries the overlap uncertainty forward, composes spend conservatively, and requires fresh reconciliation before reducing the uncertainty floor.

### 4. External-effect receipt rotation, compensation, and multi-provider reconciliation

`RECEIPT_SIGNATURE_VALID != RECEIPT_AUTHORITY_CURRENT`.

External-effect receipts must bind provider identity, operation semantic id, target/resource identity, effect kind, request digest, provider result/effect position when available, receipt key id/epoch, issuance time, and predecessor key lineage. Receipt-key rotation needs an authenticated successor relation; old receipts remain verifiable evidence but an old key must not authorize a new effect after its retirement cutoff.

`COMPENSATED != REVERSED`.

A compensation is a new business effect intended to offset an earlier effect; it is not cryptographic or semantic proof that the earlier effect never happened. Reconciliation state must preserve both effects and their order. Examples include refund after charge, restoring a deleted replica from another copy, or issuing a counter-order. Only a provider-defined true reversal with authenticated semantics may be represented as reversal, and even then the original effect remains historical evidence.

`PROVIDER_A_CONFIRMED != GLOBAL_MULTI_PROVIDER_COMPLETE`.

A logical destructive operation spanning providers stays unresolved until every provider-side sub-effect is confirmed absent, confirmed applied, or fenced from future application. Timeout/unknown at any provider prevents blind global retry under a new semantic id. Retries use the same logical operation identity and provider-specific idempotency/fence lineage where supported.

### 5. Ticket cutoff after KMS/backup restore, stale regional caches, and replay epoch rollover

`ACTIVE_KMS_KEY_RETIRED != ALL_OLD_TICKET_AUTHORITY_UNSPENDABLE`.

A ticket-key cutoff must account for live KMS, wrapped exports, HSM replicas, backups, DR snapshots, restored regions, and cached ticket-admission state. Restoring an old KMS/backup image cannot restore ticket authority past the globally committed cutoff.

Define a monotonic `ticket_security_epoch`. Ticket acceptance requires both cryptographic decryption and admission of the ticket's epoch under current certificate/DC/PQ/ECH/service-equivalence/revocation policy. Key restore alone cannot lower the minimum accepted epoch.

`REGION_REJOINED != REGION_RESUMPTION_READY`.

A stale region is quarantined for resumption until it proves current ticket cutoff and policy epoch. Full fresh-auth 1-RTT may be enabled under current credentials before PSK resumption. 0-RTT additionally requires replay-window state whose epoch/cutoff is current. If replay state was lost or rolled back, 0-RTT remains disabled for at least the overlapping recording window; this follows the TLS 1.3 startup/replay guidance.

`NEW_REPLAY_EPOCH != OLD_WINDOW_SAFE_TO_FORGET`.

Replay-window epoch rollover must preserve a predecessor rejection floor until all tickets that could have been admitted under the old replay state are expired or explicitly fenced. A new empty replay cache is not proof that old 0-RTT data was never observed.

## Required state shape

A future implementation should be able to derive or persist the following monotonic evidence without introducing a second mutable authority source:

- `witness_membership_epoch`, predecessor digest, admissions/removals, minimum independent-domain rule;
- cross-log recovery tuple and retained conflict digest;
- holdout provenance root, operator/controller lineage, disclosure mechanism and cumulative exposure floor;
- privacy subject-set version, resolver/evidence version, proof cutoff/expiry, overlap uncertainty floor;
- external logical operation id plus per-provider effect/receipt/key epochs and reconciliation status;
- ticket security epoch, minimum accepted epoch, ticket-key retirement evidence, region admission epoch, replay-window epoch and replay cutoff.

All successor transitions must be authenticated and monotonic. Administrative renaming, key rotation, membership churn, process restart, region replacement, backup restore, or compaction must not silently reset predecessor security state.

## RED-first matrix (40 cases)

### Witness membership / cross-log recovery
1. Roll witness-set descriptor back one epoch while preserving valid signatures -> reject.
2. Replace two witnesses with new keys controlled by same failure domain -> do not count as two independent admissions.
3. Remove witness after it reported conflict -> retain its conflict evidence.
4. Current quorum signs recovery root omitting predecessor membership digest -> reject.
5. Log A and B each internally consistent but bind different recovery roots at same recovery epoch -> fail closed.
6. Cross-log tuple matches root but differs on conflict digest -> fail closed.
7. Recovery root is included in one log but absent/unproven in required peer log -> recovery incomplete.
8. Emergency membership transition expires; old emergency signer attempts future vote -> reject while retaining old evidence.

### Holdout correlation / witness independence
9. Two holdout witnesses share one scoring database -> count correlated, not independent.
10. Two services use different keys but one adaptive controller -> preserve one controller lineage.
11. Synthetic holdout generated deterministically from exposed holdout -> inherit exposure.
12. Random subsample from same exposed population with overlapping rows -> no fresh independence claim without quantified contract.
13. Dataset copied to another region/name -> exposure unchanged.
14. Witness threshold increases after prior disclosures -> cumulative exposure floor unchanged.
15. Operator rotates service account -> operator lineage unchanged.
16. Compact provenance root omits a predecessor disclosure range -> reject compaction/GC.

### Privacy proof freshness / disjointness
17. Valid disjointness proof used after subject-set ingestion cutoff advances -> stale/reject for budget separation.
18. Resolver model/policy changes after proof -> require fresh proof.
19. `no match` from resolver with incomplete index -> unresolved overlap, not disjoint.
20. Resolver A says distinct, resolver B says same subject -> compose conservatively.
21. Two resolvers share same poisoned upstream graph -> not independent evidence.
22. Identifier is reassigned after proof expiry -> old proof cannot authorize separate budget.
23. Negative evidence expires while positive spend remains -> keep spend, restore overlap uncertainty.
24. Scope split uses stale disjointness proof to duplicate remaining budget -> reject.

### External receipts / compensation / multi-provider
25. Old receipt key verifies old receipt after rotation -> evidence remains valid.
26. Old retired receipt key signs a new effect after cutoff -> reject authority.
27. Receipt omits semantic request digest -> insufficient for exactly-once reconciliation.
28. Provider times out after request send -> mark `EFFECT_UNKNOWN`; no blind new-id retry.
29. Charge confirmed then refund confirmed -> record compensation, not erase charge.
30. Provider claims reversal but receipt schema does not define reversal semantics -> treat as compensation/unknown, not history deletion.
31. Provider A applied; provider B unknown -> logical operation unresolved.
32. Provider A applied; B fenced absent; C applied -> reconcile exact per-provider terminal states before declaring global completion.

### Ticket cutoff / KMS restore / regional replay
33. Restore backup containing retired ticket key below minimum security epoch -> ticket remains rejected.
34. Rejoined region has stale ticket-admission cache -> resumption quarantined.
35. Fresh full-auth credentials current but resumption epoch stale -> allow fresh 1-RTT only.
36. PSK 1-RTT admission converged but replay cache lost -> keep 0-RTT disabled.
37. Replay-window epoch increments with empty cache while predecessor tickets still valid -> reject 0-RTT until predecessor window fenced/expired.
38. DR HSM replica exposes old wrapped key after global cutoff -> old tickets remain below admission floor.
39. Regional ticket cache accepts old epoch despite KMS key deletion -> reject at admission-policy layer.
40. All old tickets expired, all spend authorities acknowledge cutoff, replay overlap elapsed -> permit retirement of predecessor rejection metadata subject to durable proof/GC contract.

## Implementation guidance

Do not implement these as five isolated boolean flags. The common mechanism is an authenticated monotonic lineage with explicit scope and predecessor evidence. Prefer one small reusable transition envelope/digest helper where existing architecture permits, while keeping domain-specific semantic verification separate. Tests should prove rollback, correlated-independence, stale-proof, partial-effect, and region-rejoin failures before production refactors.

## Audit result

No contradiction found with the retained LAB-086/090/092 boundaries. These contracts tighten evidence semantics; they do not authorize mutation or merge of any current draft. The principal unresolved engineering blocker remains exact local execution of the pinned LAB-086 closure.