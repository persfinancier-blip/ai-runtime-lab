# Transparency witness, holdout threshold, privacy dual-resolver, external effects, and ticket emergency rotation — v1

Date: 2026-09-10
Status: FROZEN DESIGN / RED-FIRST — not executable proof
Contract: `TRANSPARENCY_WITNESS_HOLDOUT_THRESHOLD_PRIVACY_DUAL_RESOLVER_EXTERNAL_EFFECT_TICKET_EMERGENCY_ROTATION_V1_FROZEN`

## Why this slice exists

LAB-086 exact local execution remains blocked by the current runtime transport/materialization boundary. This slice advances the next distinct evidence task recorded in `state/CURRENT.md` without pretending that design evidence substitutes for LAB-086 RED/GREEN execution.

## Sources / donors

Primary or near-primary donors used for mechanisms, not copied implementation:

1. RFC 9162, Certificate Transparency v2.0 — append-only Merkle logs, signed tree heads, inclusion/consistency proofs, auditing, and the explicit distinction between validating a particular authenticated view and establishing consistency of views presented to all parties. RFC 9162 notes that cross-party view consistency requires response sharing/gossip and does not itself define that mechanism.
2. Dwork et al., *Generalization in Adaptive Data Analysis and Holdout Reuse* (2015) — adaptive reuse of a holdout can overfit the holdout itself; validity depends on controlling information leaked across adaptive rounds.
3. Nakkiran & Błasiok, *The Generic Holdout* (2018) — exploration/holdout separation plus deliberately limited holdout exposure; returning richer scores than the declared mechanism changes the guarantee.
4. NIST SP 800-226 (final, 2025) — privacy budget is an upper bound on allowable cumulative privacy loss; interactive answers consume additional budget.
5. Apache Kafka design / Kafka Streams documentation — exactly-once processing is achieved when input offsets, state updates, and outputs are in the same transactional system; this guarantee does not automatically cover external side effects.
6. RFC 9345, Delegated Credentials for TLS/DTLS — a stolen delegated credential has no independent early-revocation mechanism; resumption should revalidate a cached DC so an expired DC does not silently continue to authorize resumed sessions.
7. RFC 9849, TLS Encrypted Client Hello — ECH rejection authenticated only for the public name does not authenticate the origin; clients must ignore session tickets/session IDs presented on that rejection connection.
8. TLS 1.3 / QUIC resumption model (RFC 8446 / RFC 9001) — resumption and especially 0-RTT carry retained security state; 0-RTT requires replay-aware handling and cannot be treated as ordinary fresh authentication.

## Frozen invariants

### A. Transparency witness equivocation and recovery-root inclusion

`SIGNED_RECOVERY_ROOT != RECOVERY_HISTORY_COMPLETE`

A recovery root is acceptable only when it commits to the predecessor authenticated root, the recovery epoch, the admitted witness set/threshold, and the complete set of known conflicting heads/evidence visible at the declared cutoff. A signature over the new root authenticates that root; it does not prove that predecessor evidence was not omitted.

`WITNESS_QUORUM_AT_T1 != GLOBAL_VIEW_CONSISTENCY`

A quorum proves only the statements actually observed/signed by those witnesses. It cannot prove absence of a censored split view outside their observation domains. Cross-domain gossip or an equivalent independent observation mechanism remains a separate requirement.

`WITNESS_COMPROMISED_AFTER_SIGNING != EVIDENCE_ERASED`

Previously authenticated conflicting heads remain durable evidence after witness compromise, removal, or key rotation. Successor admission may reduce future authority but cannot rewrite the historical evidence set.

`RECOVERY_ROOT_INCLUDED != RECOVERY_ROOT_CANONICAL`

Merkle inclusion proves that a particular recovery statement is in a particular authenticated log view. Canonicality additionally requires consistency from the last uncontested root and the required independent-domain witness policy for the recovery epoch.

### B. Reusable-holdout witness compromise and threshold changes

`NEW_HOLDOUT_WITNESS_THRESHOLD != FRESH_HOLDOUT`

Changing a holdout witness quorum, keys, or threshold does not reset dataset provenance, adaptive-controller lineage, disclosure history, or exposure budget.

`WITNESS_QUORUM_VALID != HOLDOUT_STATISTIC_UNLEAKED`

Witnesses authenticate that a declared holdout mechanism was followed; they do not restore independence after the mechanism has already disclosed richer statistics, rankings, gradients, per-slice scores, or other information outside the declared exposure contract.

`COMPROMISED_WITNESS_EPOCH != ZERO_PRIOR_EXPOSURE`

Recovery from a witness compromise inherits the maximum authenticated prior exposure plus an `UNKNOWN` floor for intervals where the compromise makes disclosure completeness uncertain.

`THRESHOLD_DECREASE != AUTHORITY_CONTINUITY`

Emergency threshold reduction must be a separately authenticated successor transition with explicit expiry and predecessor evidence. It cannot be a silent parameter edit that makes previously insufficient signatures retroactively sufficient.

### C. Privacy resolver poisoning detection and dual-resolver reconciliation

`ONE_RESOLVER_SAYS_DISTINCT != SUBJECTS_DISJOINT`

A single identity resolver is not sufficient authority for privacy-budget separation. Administrative identities, hashed identifiers, device IDs, and inferred person clusters can all be poisoned, split, or merged.

`TWO_RESOLVERS_AGREE != GROUND_TRUTH_PROVEN`

Dual-resolver agreement is evidence, not proof of ontological identity. Independence requires separate implementation/data-provenance/failure domains; shared upstream embeddings, shared lookup tables, or one resolver derived from the other collapse the claimed independence.

`RESOLVER_DISAGREEMENT => CONSERVATIVE_OVERLAP`

If independent resolvers disagree about whether two scopes overlap, privacy accounting carries the union of cumulative spend, reservations, transfers, and unknown-loss floors until reconciliation produces authenticated evidence strong enough to prove disjointness.

`RESOLVER_RECOVERY != BUDGET_RESET`

Replacing a poisoned resolver cannot mint fresh budget. Successor scope mappings inherit predecessor semantic-subject lineage and cumulative privacy loss.

### D. External-system receipt authenticity and exactly-once boundaries

`LOCAL_TX_COMMITTED != EXTERNAL_EFFECT_EXACTLY_ONCE`

A local ledger/Kafka/database transaction cannot by itself prove exactly-once execution of an external HTTP/API/payment/device/storage side effect outside that transaction boundary.

`IDEMPOTENCY_KEY_ACCEPTED != EFFECT_IDENTITY_AUTHENTICATED`

An idempotency key is useful only if the external system binds it durably to the full logical operation identity and rejects semantic mismatch. Key collision/reuse with different resource/action/parameters must fail closed.

`HTTP_2XX_RECEIVED != DURABLE_EXTERNAL_EFFECT_PROVEN`

A response authenticates only what the external system actually signs/attests. For destructive or irreversible effects, reconciliation should prefer an authenticated receipt containing logical operation id, resource identity, canonical parameters or digest, external effect id/version, result, authority epoch, and server-side commit/fence evidence where available.

`TIMEOUT_AFTER_SEND != SAFE_TO_RETRY`

Timeout after request transmission is `EFFECT_UNKNOWN`, not failure. Blind retry is safe only when the external system offers durable semantic idempotency/fencing covering the exact operation; otherwise reconcile first or fence predecessor execution authority.

`EXACTLY_ONCE_CLAIM != END_TO_END_EXACTLY_ONCE`

Exactly-once is always scoped. If any effect-capable hop lies outside the atomic/deduplicated boundary, the composed system must expose at-least-once/at-most-once/unknown semantics for that hop rather than laundering the internal guarantee into an end-to-end claim.

### E. Ticket ancestry cutoff after emergency root-CA/DC/PQ rotation and replay-state loss

`NEW_CERT_CHAIN_VALID != OLD_TICKETS_AUTHORIZED`

Emergency replacement of a root/intermediate/end-entity certificate, delegated credential, PQ policy/key, or ECH configuration does not automatically retire tickets minted under predecessor ancestry.

`TICKET_DECRYPTS != RESUMPTION_POLICY_CURRENT`

A ticket must carry or resolve to ancestry metadata sufficient to compare against current certificate/DC/PQ/ECH/backend/revocation policy floors. Decryptability is necessary transport evidence, not authorization.

`DC_REPLACED != DC_ANCESTRY_CLEARED`

Because delegated credentials have bounded validity and no independent early revocation, resumed sessions associated with a DC must respect its validity/revocation ancestry. Reissuing a parent certificate or DC does not make predecessor tickets fresh.

`ECH_REJECTION_TICKET != ORIGIN_RESUMPTION_AUTHORITY`

A ticket presented on an ECH rejection connection authenticated only for `public_name` must not become origin resumption authority; RFC 9849 requires ignoring those tickets/session IDs.

`REGIONAL_REPLAY_STATE_LOST != ZERO_RTT_SAFE`

After cross-region replay-state loss, 0-RTT remains quarantined until the new region proves convergence on the relevant anti-replay/admission state. Full 1-RTT may recover earlier if fresh authentication and current policy floors pass; PSK resumption requires its own convergence gate; 0-RTT adds the replay gate.

`EMERGENCY_ROTATION_COMPLETE != TICKET_ANCESTRY_CUTOFF_COMPLETE`

Emergency rotation is complete for resumption only after all eligible ticket-spend authorities either acknowledge the cutoff or are fenced; predecessor ticket decryption/recovery keys are retired across active KMS/HSM, backup/DR, and regional restore domains; and rejoining regions cannot spend old tickets without re-proving the current cutoff.

## RED-first matrix (40 cases)

### Transparency / witness (T01-T08)
1. T01 conflicting signed heads observed by two independent witnesses; recovery root omits one -> reject.
2. T02 recovery root includes both heads but lacks consistency from last uncontested root -> reject.
3. T03 inclusion proof valid for recovery statement in a censored view only -> do not call canonical.
4. T04 witness removed after signing conflict evidence -> evidence remains required.
5. T05 witness key rotated with same operator/failure domain -> no new independence credit.
6. T06 compromised witness signs successor root after compromise cutoff -> signature excluded from required independent threshold.
7. T07 emergency witness admission expires -> no future vote; historical signed evidence remains valid evidence.
8. T08 complete predecessor/conflict evidence + valid successor transition + required independent domains -> accept recovery epoch.

### Holdout / threshold (H01-H08)
9. H01 same holdout, new witness keys -> exposure budget unchanged.
10. H02 same holdout, threshold 3->2 without successor transition -> reject.
11. H03 emergency threshold decrease with authenticated expiry but no predecessor exposure floor -> reject.
12. H04 score/ranking revealed despite one-bit declared mechanism -> mark mechanism violated.
13. H05 compromised witness interval with uncertain disclosure -> inherit max known exposure + UNKNOWN.
14. H06 candidate family renamed while same adaptive controller/data lineage persists -> no fresh budget.
15. H07 new compact provenance root omits prior disclosure event -> reject completeness.
16. H08 fresh independent holdout generation with complete predecessor closure and declared mechanism -> allow new generation under its own budget.

### Privacy resolver (P01-P08)
17. P01 resolver A says subjects distinct, resolver B says same -> conservative overlap.
18. P02 two resolvers share same upstream identity graph -> do not count as independent corroboration.
19. P03 resolver compromise causes one person to split into N scopes -> cumulative budget remains shared.
20. P04 later merge of scopes -> sum/upper-bound predecessor spend and unresolved reservations; never choose minimum.
21. P05 poisoned merge joins unrelated subjects -> quarantine mapping and do not erase prior per-subject spend.
22. P06 resolver replacement with new IDs only -> inherit semantic lineage.
23. P07 disjointness proof authenticated from independent authoritative identity evidence -> permit separation prospectively, retaining predecessor history.
24. P08 unresolved identity probability/ambiguity after recovery -> carry UNKNOWN overlap floor.

### External effects / exactly-once (E01-E08)
25. E01 local tx commits, external request never sent -> local success must not imply external success.
26. E02 external effect commits, response lost, local tx aborts -> state EFFECT_UNKNOWN; no blind retry.
27. E03 retry uses same idempotency key with different canonical parameters -> external adapter must reject semantic mismatch.
28. E04 duplicate exact request, external durable idempotency record present -> return/reconcile same effect identity, no second effect.
29. E05 external receipt is unsigned/unbound to resource/operation -> insufficient for destructive reconciliation.
30. E06 authenticated receipt binds operation/resource/params/effect version -> reconcile exact effect.
31. E07 two replicas race same logical operation without shared external fence -> do not claim exactly-once even if local DB dedupes.
32. E08 all effect-capable hops share one atomic transaction or durable semantic idempotency/fencing contract -> exactly-once claim allowed only for that explicitly bounded surface.

### TLS/PQ/ECH/tickets (R01-R08)
33. R01 emergency cert/DC/PQ rotation occurs, predecessor ticket still decrypts -> resumption rejected if ancestry floor stale.
34. R02 parent certificate revoked/reissued while cached DC ancestry predates cutoff -> reject resumption.
35. R03 ECH rejection connection presents ticket for public_name -> ignore ticket for origin.
36. R04 region loses anti-replay state but retains ticket keys -> disable/quarantine 0-RTT.
37. R05 region has current cert/PQ/ECH floors but stale ticket-cutoff epoch -> full 1-RTT may pass; PSK resumption remains quarantined.
38. R06 PSK admission converged but replay state not converged -> 1-RTT PSK may pass policy; 0-RTT remains quarantined.
39. R07 removed region restores old KMS/backup ticket key after disaster recovery -> reject old-ticket spend until current cutoff/fence is re-proved.
40. R08 all current floors, predecessor keys retired/fenced across recovery domains, ticket-cutoff acknowledgements converged, replay state current -> resumption/0-RTT admitted according to separate gates.

## Engineering consequences

1. Prefer monotonic epoch/cutoff objects over mutable booleans (`is_recovered`, `is_fresh`, `is_revoked`).
2. Every recovery successor must commit predecessor evidence and uncertainty, not merely new authority.
3. Separate authenticity, completeness, freshness, independence, and authorization predicates; none implies the others.
4. Exactly-once must be named with its atomic/deduplication boundary. External effects need their own receipt/idempotency/fencing contract.
5. TLS full-auth, PSK 1-RTT, and 0-RTT are separate recovery stages; never use one `TLS_RECOVERED` flag.

## Implementation posture

This note freezes architecture and tests only. It does not supersede LAB-086, does not claim executable RED/GREEN evidence, and does not authorize merging any current draft PR. When exact source execution becomes available, implement tests first at the abstraction level of the eventual LAB-093..100 integration surface and preserve the separate gates above.
