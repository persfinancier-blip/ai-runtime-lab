# Observer recovery, reusable holdout, privacy dual-control, retention revocation, and PQ/cross-SNI resumption v1

Date: 2026-09-10
Status: DESIGN FROZEN / RED-FIRST; executable proof pending
Primary issue: LAB-093 / #178 (architecture follow-up; LAB-086 remains priority #1)

## Why this slice exists

The prior frozen slice established authenticated observer-set epochs, holdout exposure accounting, compromise-safe privacy reconciliation-root succession, transitive retention writer-capability closure, and ticket ancestry across certificate/DC/PQ/ECH/backend/revocation/replay dimensions. This slice closes the next failure modes recorded in `state/CURRENT.md`:

1. observer-set compromise and recovery, including changes to the minimum independent-domain threshold;
2. choosing/accounting a reusable-holdout mechanism across repeated candidate families;
3. recovery after compromise of the privacy successor-root quorum itself;
4. revocation propagation and fencing for delegated/offline retention writers;
5. cross-SNI resumption after delegated-credential compromise, parent-certificate reissue, and service-equivalence-policy rollover.

No executable PASS is claimed here. These are design contracts and RED-first cases to implement only when exact-source execution is available.

## Source facts

### Transparency / observer evidence

RFC 9162 treats conflicting Merkle-tree views as log misbehavior and notes that multiple clients comparing authenticated tree heads (gossip) can detect violations of append-only behavior, while deliberately leaving the gossip mechanism itself unspecified. Therefore authenticated heads alone do not define observer admission, failure-domain diversity, or recovery after observer compromise.

Primary: https://www.rfc-editor.org/rfc/rfc9162

### Adaptive holdout reuse

The Generic Holdout separates unrestricted exploration from a holdout with deliberately limited exposure. Its core security value is not merely a fixed number of calls; it is controlling how much information from the holdout is revealed to the adaptive analyst. Therefore repeated candidate families require explicit accounting of disclosures and a mechanism-specific guarantee; repeatedly exposing scores/rankings from one holdout cannot be treated as fresh independent confirmation.

Primary paper: https://arxiv.org/abs/1809.05596

### Privacy budget continuity

NIST SP 800-226 frames interactive differential-privacy accounting as cumulative privacy loss against a total privacy budget; new interactive answers consume additional loss and the system must refuse further answers once budget is exhausted. Recovery/root rotation therefore cannot safely decrease already charged or uncertain spend merely because control-plane credentials changed.

Primary: https://www.nist.gov/publications/guidelines-evaluating-differential-privacy-guarantees

### Delegated credentials and resumption

RFC 9345 says a stolen delegated credential has no independent early-revocation mechanism; expiry revokes it, and revoking the long-term certificate key also implicitly revokes delegated credentials. It further says that if a peer caches and re-validates the certificate chain on resumption it should also cache/re-validate the delegated credential, otherwise a connection can resume after the DC expired.

Primary: https://www.rfc-editor.org/rfc/rfc9345

### TLS cross-SNI resumption and ticket ancestry

TLS 1.3 requires the new SNI to be valid for the certificate from the original session and recommends that it match the original SNI; different-SNI resumption is only reasonable when there is an external indication that the servers can accept each other's tickets. TLS also warns that serial ticket issuance can extend original keying material indefinitely and recommends an upper bound that considers certificate lifetime, revocation likelihood, and time since the original online signature.

Primary: https://www.rfc-editor.org/rfc/rfc9846

RFC 9846 also retains the conservative 0-RTT replay model: distributed acceptance needs authoritative replay/ticket coordination, and freshly restarted state must not infer replay safety from local emptiness.

## Frozen contract

Name:

`OBSERVER_RECOVERY_REUSABLE_HOLDOUT_PRIVACY_DUAL_CONTROL_RETENTION_REVOCATION_PQ_CROSS_SNI_V1_FROZEN`

### A. Observer compromise, recovery, and threshold evolution

Core distinction:

`CURRENT_OBSERVER_QUORUM_VALID != OBSERVER_HISTORY_UNCOMPROMISED`

An observer-set epoch MUST bind:

- epoch id and predecessor epoch digest;
- observer identities and keys;
- independent failure-domain labels;
- minimum number of agreeing observers;
- minimum number of independent domains;
- admission/removal/revocation reasons;
- cutoff/freshness rule;
- recovery generation and compromised interval, if any.

If enough observer keys for an epoch are compromised to satisfy its signature threshold, that epoch is permanently `COMPROMISED` for current authority. A later valid quorum from the same epoch cannot restore trust merely because the signatures verify.

Recovery MUST create a successor observer-set epoch signed under a separate recovery authority. The successor event binds:

- the last uncontested authenticated checkpoint;
- all known conflicting heads/evidence;
- the compromised epoch id;
- a new observer membership/failure-domain set;
- the new ordinary threshold and independent-domain floor;
- an explicit degraded interval.

Threshold changes are authority changes. Lowering either the signer threshold or independent-domain minimum requires the same recovery authorization as observer-set recovery; it cannot be done by the ordinary observer quorum that benefits from the reduction.

Increasing thresholds may be authorized by current policy authority but becomes effective only in a successor epoch; old signatures do not retroactively satisfy the stronger floor.

Frozen invariants:

- `SIGNATURE_THRESHOLD_MET != INDEPENDENT_DOMAIN_THRESHOLD_MET`.
- `OBSERVER_EPOCH_RECOVERED != COMPROMISED_INTERVAL_ERASED`.
- `REMOVED_OBSERVER != REMOVED_EVIDENCE`.
- `LARGER_LATE_QUORUM != PRIOR_EQUIVOCATION_REPAIRED`.
- `THRESHOLD_REDUCED != RECOVERY_AUTHORIZED`.

### B. Reusable holdout mechanism selection/accounting

Core distinction:

`MECHANISM_SUPPORTS_REUSE != THIS_ANALYSIS_USED_IT_WITHIN_ITS_GUARANTEE`

For each validation generation persist a `holdout_contract` binding:

- mechanism id/version;
- candidate-family id;
- holdout dataset/version digest;
- analyst/adaptive-controller identity;
- permitted disclosure type (bit, thresholded decision, noisy statistic, etc.);
- exposure/query budget;
- family-wise stopping rule;
- false-positive/confidence target;
- whether candidate generation may adapt to holdout responses;
- exhaustion action.

Default safe mode remains fresh post-selection confirmation. A reusable-holdout mechanism may replace that default only when its actual disclosure pattern and candidate-family adaptivity match the chosen mechanism's guarantee.

A score, ranking, loss curve, per-example error, confidence interval, or exact failure count is strictly more disclosure than a one-bit pass/fail decision and MUST NOT be silently accounted as the latter.

Reusing the same holdout for a new candidate family does not reset exposure merely because the family name changes if the analyst/controller can transfer information between families.

Frozen invariants:

- `QUERY_COUNT_WITHIN_LIMIT != DISCLOSURE_WITHIN_MECHANISM`.
- `NEW_CANDIDATE_FAMILY_LABEL != FRESH_HOLDOUT`.
- `HOLDOUT_RESULT_USED_FOR_SEARCH != INDEPENDENT_CONFIRMATION`.
- `ONE_BIT_CONTRACT != SCORE_DISCLOSURE_CONTRACT`.
- `MECHANISM_EXHAUSTED -> FRESH_CONFIRMATION_REQUIRED`.

### C. Privacy successor-root quorum compromise and dual-control recovery

Core distinction:

`NEW_ROOT_SIGNATURE_VALID != SPEND_FLOOR_RECOVERED`

A privacy accounting root is authority over cumulative loss, unresolved reservations, transfers, and fenced spenders. If the root quorum itself is compromised, ordinary root rotation is no longer sufficient because the attacker may produce syntactically valid rollback roots.

Recovery MUST require two distinct authority classes:

1. recovery/root-control quorum; and
2. independent spend-continuity witness quorum.

The recovery event binds:

- compromised root generation;
- last uncontested cumulative spend floor;
- all unresolved reservations/transfers known at cutoff;
- all spend-authority identities and fencing state;
- evidence sources used to reconstruct the floor;
- successor root keys/quorum;
- freshness/cutoff;
- degraded interval and uncertainty reserve.

Where the exact spend floor cannot be proved, recovery uses a conservative upper bound. Unknown possible disclosure is charged/fenced; it is never treated as free capacity.

The spend-continuity witness role MUST be administratively and cryptographically separated from the root-control quorum; counting two keys from one control plane as dual control is forbidden.

Frozen invariants:

- `TWO_SIGNATURE_SETS != TWO_INDEPENDENT_CONTROL_DOMAINS`.
- `RECOVERY_ROOT_VALID != UNCERTAIN_SPEND_FREE`.
- `OLD_ROOT_REPLAY_VALID_CRYPTOGRAPHICALLY != OLD_ROOT_CURRENT`.
- `CREDENTIAL_ROTATION != PRIVACY_BUDGET_RESET`.
- `RECOVERY_UNKNOWN -> CONSERVATIVE_SPEND_FLOOR`.

### D. Retention capability revocation propagation and offline-job fencing

Core distinction:

`CAPABILITY_REVOKED_AT_CONTROL_PLANE != CAPABILITY_UNSPENDABLE_EVERYWHERE`

Writer inventory MUST include direct principals plus delegated/subdelegated capabilities, queues, signed jobs, scheduler tokens, break-glass identities, replicas, batch workers, and DR/offline execution environments.

Every destructive capability carries:

- capability id;
- parent delegation lineage;
- policy generation;
- writer-membership epoch;
- revocation generation/floor;
- not-before/not-after bounds;
- allowed operation/resource scope;
- one-shot/idempotency identity where applicable.

Revocation becomes globally effective only after each destructive-capable execution domain either acknowledges the revocation floor or is fenced from the protected store/resource.

Offline jobs created before revocation MUST be re-authorized at execution against the current revocation/policy generation. A valid historical job signature is evidence of past authorization, not current deletion authority.

A worker rejoining after partition/recovery enters `DESTRUCTIVE_QUARANTINE` until it proves current membership, policy, revocation, time/freshness, and hold state.

Frozen invariants:

- `JOB_SIGNED_WHEN_QUEUED != JOB_AUTHORIZED_WHEN_EXECUTED`.
- `REVOCATION_PUBLISHED != REVOCATION_PROPAGATED`.
- `OFFLINE_WORKER_REJOINED != DESTRUCTIVE_AUTHORITY_RESTORED`.
- `PARENT_CAPABILITY_REVOKED -> DESCENDANT_CAPABILITIES_FENCED`.
- `UNKNOWN_REVOCATION_FLOOR -> NO_DESTRUCTIVE_ACTION`.

### E. PQ/ECH cross-SNI resumption after DC compromise / certificate reissue / equivalence rollover

Core distinction:

`CERTIFICATE_VALID_FOR_BOTH_SNIS != CURRENT_SERVICE_EQUIVALENCE_FOR_RESUMPTION`

Ticket ancestry MUST retain at least:

- origin SNI and service-equivalence-policy generation;
- certificate chain identity/generation;
- delegated-credential identity/generation and expiry, when used;
- PQ/hybrid algorithm-policy generation;
- ECH configuration/source generation;
- backend/route generation;
- ticket-key generation;
- revocation floor;
- replay/0-RTT generation;
- absolute ancestry creation time.

Cross-SNI resumption is permitted only when the CURRENT policy explicitly declares the origin and destination services equivalent for resumption and both are authorized under the ticket's current ancestry floors.

Delegated-credential compromise immediately fences resumption descendants whose ancestry includes that DC generation, even if the parent certificate remains otherwise valid. Parent-certificate reissue creates a new certificate generation and does not automatically re-authorize descendants of the old/DC-compromised generation.

If the parent certificate/key is revoked/reissued because the DC cannot be safely tolerated, every region must reach the corresponding revocation floor before accepting affected tickets. Late regions remain resumption-quarantined.

Service-equivalence-policy rollover is monotonic authority: a policy that removes A<->B equivalence invalidates cross-SNI use of tickets minted under the older policy even when certificate SAN coverage still overlaps.

1-RTT full handshakes may recover before resumption/0-RTT. Re-enabling 0-RTT additionally requires current replay-state authority and explicit re-enable generation.

Frozen invariants:

- `PARENT_CERT_REISSUED != OLD_DC_DESCENDANT_TICKETS_SAFE`.
- `SAN_OVERLAP != CROSS_SNI_RESUMPTION_EQUIVALENCE`.
- `NEW_SERVICE_EQUIVALENCE_POLICY != OLD_TICKET_REAUTHORIZED`.
- `REGION_HAS_NEW_CERT != REGION_HAS_CURRENT_REVOCATION_FLOOR`.
- `1RTT_FULL_HANDSHAKE_SAFE != 0RTT_SAFE`.

## RED-first matrix (40 cases)

### Observer recovery (O1-O8)

1. O1: threshold signatures all from one compromised failure domain -> reject despite signer threshold.
2. O2: compromised epoch signs apparently newer clean head -> remains COMPROMISED.
3. O3: recovery event omits known conflicting head -> reject incomplete recovery evidence.
4. O4: ordinary observer quorum lowers independent-domain floor -> reject unauthorized threshold evolution.
5. O5: valid recovery raises thresholds -> successor epoch accepts only new floor.
6. O6: removed observer later produces authenticated conflicting historical head -> append evidence/reopen, do not discard because membership changed.
7. O7: successor epoch tries to declare degraded interval clean without independent evidence -> reject.
8. O8: eclipse leaves signer threshold but misses required network/admin domains -> `OBSERVER_COVERAGE_INCOMPLETE`.

### Reusable holdout (H1-H8)

9. H1: one-bit mechanism accidentally returns exact score -> exposure contract violated.
10. H2: candidate family renamed but same adaptive controller carries prior holdout information -> exposure continues, no reset.
11. H3: within query count but disclosure statistic not supported by mechanism -> reject confirmation claim.
12. H4: holdout result used to mutate next candidate then same result called independent confirmation -> reject.
13. H5: mechanism exposure exhausted -> require fresh confirmation generation.
14. H6: genuinely fresh holdout after post-selection -> independent confirmation succeeds.
15. H7: controller receives only allowed threshold bits within predeclared budget -> mechanism may remain valid.
16. H8: hidden per-example diagnostics leak through logs/telemetry -> count as disclosure and invalidate narrower contract.

### Privacy root compromise (P1-P8)

17. P1: compromised old root signs lower spend floor -> reject as non-current.
18. P2: successor root signed by root quorum only, no independent spend witness -> reject recovery.
19. P3: two quorums share same underlying HSM/admin failure domain -> reject claimed dual control.
20. P4: recovery reconstructs exact spend and unresolved reservations -> accept monotonic successor.
21. P5: one region's disclosure outcome unknown -> conservatively charge/fence uncertainty, do not refund.
22. P6: credential rotation relabels spend authority -> budget unchanged.
23. P7: replay of historically valid recovery root after newer generation -> rollback rejected.
24. P8: recovery has partial evidence only -> choose conservative upper-bound floor or fail closed.

### Retention revocation (R1-R8)

25. R1: queued delete job signed before capability revocation executes afterward -> must re-authorize and reject.
26. R2: parent capability revoked but descendant token still cryptographically valid -> descendant fenced.
27. R3: revocation acknowledged by primary workers but DR worker unknown -> global destructive completion not declared.
28. R4: offline worker rejoins with stale policy/revocation generation -> destructive quarantine.
29. R5: worker cannot prove current trusted time/hold state -> no destructive action.
30. R6: scheduler retries one-shot destructive job after uncertain commit -> idempotency/reconciliation required, not fresh authorization.
31. R7: all writers acknowledge current floor and job obtains fresh execution authorization -> permitted.
32. R8: inventory omits a delegated queue executor -> completeness audit fails.

### PQ/ECH/cross-SNI (T1-T8)

33. T1: A/B share SAN certificate but no current equivalence policy -> reject cross-SNI resumption.
34. T2: old policy allowed A<->B, new policy removes it -> old ticket cannot cross SNI.
35. T3: DC compromised; parent cert still valid -> descendants carrying compromised DC ancestry fenced.
36. T4: parent certificate reissued after compromise -> old ticket ancestry not automatically upgraded.
37. T5: one region has new certificate but stale ticket revocation floor -> resumption quarantined there.
38. T6: safe new full 1-RTT handshake succeeds while affected resumption remains disabled -> expected staged recovery.
39. T7: 0-RTT attempted before replay authority/re-enable generation current -> reject early data.
40. T8: new ticket issued after full handshake under current cert/DC/PQ/ECH/backend/equivalence/revocation floors -> independent fresh ancestry accepted subject to ordinary ticket lifetime/replay policy.

## Implementation guidance when executable source returns

1. Tests first. Implement O/H/P/R/T matrices at the same abstraction level as the existing LAB-090..100 gates.
2. Treat generation ids and digests as authenticated data, not mutable labels.
3. Prefer monotonically increasing/fenced generations to repair-by-overwrite.
4. Do not encode “independence” as simple signer count; persist failure-domain identities and audit transitive common-control dependencies.
5. Do not claim privacy dual control when both quorums share root administration/storage/HSM authority.
6. Do not make retention revocation dependent on worker goodwill; fence stale workers at the protected resource/broker layer where possible.
7. For TLS, prefer issuing fresh post-recovery tickets after full handshakes rather than trying to transmute old ticket ancestry.
8. Re-enable 0-RTT as a separate explicit step after replay-state and regional revocation convergence.

## Audit conclusion

The important common pattern is monotonic authority continuity under compromise and recovery:

- a new observer set cannot erase a compromised interval;
- a reusable holdout cannot erase prior information exposure;
- a privacy root cannot erase prior or uncertain privacy loss;
- a revocation cannot be considered complete while stale destructive authorities remain spendable;
- a fresh certificate/DC/service-equivalence policy cannot retroactively sanitize old session-ticket ancestry.

Therefore the cross-domain design rule frozen by this slice is:

`SUCCESSOR_CONTROL_AUTHORITY != RETROACTIVE_REAUTHORIZATION_OF_PREDECESSOR_EVIDENCE_OR_CAPABILITIES`.

## Execution note for this run

Direct local exact-source checkout was re-probed before this research step and failed before repository code execution with `Could not resolve host: github.com`. GitHub connector reads/writes remain available, but no supported non-model connector-to-filesystem materialization primitive is exposed. No LAB-086 test/build/security PASS is claimed and PR #165 must remain draft.