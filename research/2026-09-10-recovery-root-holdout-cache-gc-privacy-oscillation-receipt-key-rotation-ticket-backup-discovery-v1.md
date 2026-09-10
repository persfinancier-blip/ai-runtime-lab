# Recovery-root rollback / holdout-cache GC / privacy oscillation / receipt-key rotation / delayed ticket-authority discovery v1

Date: 2026-09-10
Status: FROZEN DESIGN EVIDENCE; executable RED/GREEN pending
Contract: `RECOVERY_ROOT_ROLLBACK_HOLDOUT_CACHE_GC_PRIVACY_OSCILLATION_RECEIPT_KEY_ROTATION_TICKET_DELAYED_AUTHORITY_V1_FROZEN`

## Scope

This is the next distinct evidence slice recorded in `state/CURRENT.md` while LAB-086 exact execution remains blocked by the absence of a supported byte-exact connector-to-local-filesystem materializer. It does not substitute for LAB-086 executable validation.

## Sources / donors

- RFC 9162, Certificate Transparency v2: append-only consistency proofs and the explicit distinction between validating one authenticated tree and establishing consistency of views served to all query sources.
- Dwork et al., *Generalization in Adaptive Data Analysis and Holdout Reuse* (2015): repeated adaptive disclosure can overfit a holdout; independence cannot be inferred from renaming/copying data artifacts.
- NIST SP 800-226: privacy budget is an upper bound on cumulative privacy loss across analyses of the same data.
- RFC 9325: ticket-encryption keys must rotate regularly and old keys must be destroyed after their validity period.
- NIST SP 800-88 Rev. 2: cryptographic erase/sanitization claims require attention to key copies, externally managed keys, and validation of the sanitization result.

## Frozen boundaries

### 1. Successor recovery-root rollback and overlapping old/new quorum ambiguity

`SUCCESSOR_ROOT_PRESENT != SUCCESSOR_ROOT_MONOTONICALLY_AUTHORIZED`

A successor recovery root is authoritative only if its transition is authenticated from the last uncontested predecessor state and its membership epoch is monotonic. Restoring an older root snapshot or presenting overlapping old/new quorums cannot select authority by whichever quorum is easiest to satisfy.

Required transition tuple:
`(log_id, predecessor_root_epoch, predecessor_root_digest, predecessor_membership_epoch, last_uncontested_checkpoint, conflict_digest, successor_root_epoch, successor_root_digest, successor_membership_epoch, transition_policy_version, transition_nonce)`.

Rules:
- root epoch must strictly increase;
- predecessor and successor quorums may overlap, but independence is counted by stable authority/failure-domain lineage, not member IDs or re-keyed identities;
- when both predecessor and successor quorums can produce valid but mutually incompatible transitions, enter `RECOVERY_ROOT_EQUIVOCATION`;
- rollback to an older validly signed root never lowers the monotonic root floor;
- removal of compromised predecessors does not erase their already-authenticated conflict evidence.

### 2. Cross-log compact-root reconstruction after witness loss

`COMPACT_ROOT_SIGNATURE_VALID != COMPACT_ROOT_RECONSTRUCTABLE`

A compacted checkpoint history may be garbage-collected only if retained evidence is sufficient to reconstruct the authority-relevant chain across membership epochs and conflict intervals after one or more witnesses disappear.

Minimum retained commitments:
- covered log/tree-size range;
- predecessor compact-root digest;
- all membership-epoch boundaries in range;
- conflict/equivocation interval digest;
- witness-set lineage digest;
- reconstruction proof version;
- minimum surviving independent-witness threshold.

If witness loss drops the surviving reconstruction set below the frozen threshold, raw evidence is retained or the log enters `COMPACTION_RECOVERY_QUARANTINE`; a locally valid inclusion proof is not enough to prove absence of a conflicting view elsewhere.

### 3. Revocation / GC of holdout-derived feature caches with exposure-floor continuity

`CACHE_OBJECT_DELETED != HOLDOUT_EXPOSURE_REVOKED`

Deleting one embedding/index/statistics object does not restore a fresh holdout budget when equivalent or downstream derivatives remain usable by the adaptive controller.

Each derived artifact records:
`(holdout_lineage_id, parent_artifact_digests, derivation_kind, controller_lineage, disclosure_class, exposure_floor, creation_epoch, revocation_epoch)`.

Rules:
- GC is allowed only after every reachable derivative is either deleted/fenced or explicitly carries the predecessor exposure floor forward;
- regenerated deterministic embeddings/features remain in the same exposure lineage;
- copied caches under new dataset/model/account IDs do not create independence;
- revocation blocks future use but does not refund prior exposure;
- incomplete derivative inventory requires conservative retention of the exposure floor.

### 4. Privacy identity-graph split/merge oscillation and monotonic spend reconciliation

`GRAPH_SPLIT_AFTER_MERGE != PRIVACY_SPEND_REFUND`

Identity-graph topology may oscillate as new linkage evidence arrives. Accounting therefore uses a monotonic spend floor over authenticated subject-lineage history rather than the current graph partition alone.

Rules:
- a merge invalidates incompatible prior disjointness proofs and reconciles cumulative spend conservatively;
- a later split may affect future routing, but cannot refund spend previously composed while overlap was plausible/authenticated;
- proof freshness binds `identity_graph_epoch`, resolver/model version, subject-set versions, evidence cutoff, expiry and uncertainty bound;
- repeated merge/split cycles cannot mint new budget;
- unresolved historical overlap keeps the maximum relevant cumulative spend/unknown-loss floor until superseded by stronger evidence.

### 5. Provider receipt equivocation across key rotation and partial compensation

`RECEIPT_KEY_ROTATED != RECEIPT_HISTORY_LINEARIZED`

Provider receipt-key rotation changes verification authority for new receipts, but unresolved operations may span key epochs. Conflicting valid receipts before/after rotation therefore require one provider-effect sequence, not per-key histories.

Receipt continuity binds:
`(provider_id, logical_operation_id, semantic_idempotency_digest, provider_effect_id, effect_sequence, predecessor_effect_digest, receipt_key_epoch, effect_kind, result_digest)`.

Rules:
- key rotation cannot erase or supersede earlier valid receipts for the same logical operation;
- two valid incompatible terminal receipts across key epochs trigger `PROVIDER_EQUIVOCATION`;
- partial compensation is a new sequenced effect referencing the original effect; it does not make the original receipt disappear;
- retries are fenced while any provider effect is `UNKNOWN`, equivocated or partially compensated;
- provider-key compromise may invalidate authorization for new receipts while historical receipts remain evidence tagged with their trust status.

### 6. Ticket-security-epoch GC under delayed backup discovery and recovery-credential rotation

`GC_ACK_QUORUM_COMPLETE_AT_T0 != PREDECESSOR_AUTHORITY_EXTINCT_AFTER_LATE_DISCOVERY`

Ticket epoch GC is safe only if no still-usable predecessor decryption/recovery authority can later reappear. A backup, wrapped key, regional cache or recovery credential discovered after the initial GC decision reopens the extinction proof and forces resumption quarantine for affected domains.

Rules:
- maintain a monotonic `ticket_security_epoch_floor` outside rollback-prone restored state;
- inventory active, retired, wrapped, backed-up and externally managed ticket keys plus recovery credentials capable of recreating them;
- recovery-credential rotation does not prove old credential extinction until old credentials and every restoration path are fenced or sanitized;
- late discovery of a predecessor key/credential does not lower the floor: old tickets remain rejected and affected regions enter `RESUMPTION_QUARANTINED`;
- full-auth 1-RTT may recover before PSK resumption when current identity/authentication is sound;
- 0-RTT additionally requires replay-state continuity or expiry of the overlapping replay window;
- GC evidence remains an auditable historical decision but is superseded by a later `AUTHORITY_DISCOVERED` event, never silently rewritten.

## RED-first matrix

1. valid successor root chained from uncontested predecessor -> accept.
2. valid older root restored from backup -> reject rollback.
3. overlapping old/new quorums sign same transition -> accept if lineage threshold and policy satisfy.
4. overlapping quorums sign incompatible successors -> `RECOVERY_ROOT_EQUIVOCATION`.
5. re-keyed compromised operator counted as new independent domain -> reject independence inflation.
6. predecessor conflict evidence survives member removal -> retained.
7. compact root covers all membership epochs and conflict intervals -> reconstruction eligible.
8. compact root omits one membership transition -> reject GC.
9. one witness is lost but surviving independent threshold remains -> reconstruct succeeds.
10. witness loss drops below reconstruction threshold -> retain raw evidence/quarantine.
11. one authenticated inclusion proof exists while conflicting view evidence exists elsewhere -> no global consistency claim.
12. compact-root generation rollback -> reject.
13. delete raw holdout-derived embedding but ANN index remains -> exposure floor retained.
14. delete ANN index but downstream learned normalizer remains -> exposure floor retained.
15. regenerate deterministic feature cache under new ID -> same lineage.
16. revoke every reachable derivative with complete inventory -> future use fenced; prior exposure not refunded.
17. derivative inventory incomplete -> conservative exposure floor retained.
18. genuinely independent holdout/controller/cache lineage -> policy may allocate fresh budget.
19. identity graph merges previously separate subjects -> reconcile spend upward/conservatively.
20. graph later splits same subjects -> no refund of historical composed spend.
21. repeated split/merge oscillation -> no budget minting.
22. stale disjointness proof from old graph epoch -> reject for new spend.
23. fresh proof with bounded uncertainty -> usable only within expiry/policy.
24. unresolved overlap after split -> keep maximum relevant spend/unknown-loss floor.
25. provider receipt key rotates during unresolved operation -> reconciliation spans both key epochs.
26. old-key SUCCESS and new-key FAILURE for same effect sequence -> provider equivocation.
27. key rotation alone followed by consistent successor receipt -> sequence continues.
28. partial compensation confirmed for one provider effect -> original effect remains in history.
29. compensation result UNKNOWN -> operation remains unresolved; no blind retry.
30. compromised old receipt key -> historical evidence retained with downgraded trust; no fresh authorization.
31. ticket epoch declared GC-safe, then forgotten backup is discovered -> extinction proof reopened; old tickets still rejected.
32. late backup contains old ticket key -> affected restore domain quarantined from resumption.
33. recovery credential rotates but old credential remains in escrow -> predecessor authority not extinct.
34. old key removed from active KMS but wrapped copy remains -> not GC-safe.
35. sanitization/erasure evidence covers all known copies and validity/ancestry windows elapsed -> GC eligible.
36. restored region reports lower ticket epoch -> monotonic floor wins; region quarantined.
37. current certificate/auth identity valid but PSK ancestry stale -> full-auth 1-RTT allowed, PSK disabled.
38. PSK ancestry current but replay state lost -> 1-RTT resumption may recover, 0-RTT disabled.
39. delayed authority discovery occurs after previous GC acknowledgement -> append `AUTHORITY_DISCOVERED`; never rewrite old decision.
40. all predecessor spend/recovery paths proven extinct after late-discovery reconciliation -> successor epoch may return to GC-safe.

## Implementation direction

When exact executable source becomes available, write RED tests first. Prefer authenticated predecessor digests, monotonic epoch floors, explicit equivocation/quarantine states, complete derivative/authority inventories and append-only reconciliation events. Do not use mutable self-hashes or caller-asserted booleans as the sole proof of continuity/extinction.

## Current blocker observation

Current-run probe executed `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` and failed before repository execution with `Could not resolve host: github.com`. GitHub connector reads/writes are available, but no supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed. No new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed.