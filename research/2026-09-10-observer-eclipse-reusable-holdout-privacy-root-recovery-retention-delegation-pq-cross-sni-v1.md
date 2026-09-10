# Observer eclipse, reusable holdout, privacy-root recovery, retention delegation, and PQ/cross-SNI ticket ancestry — v1

Date: 2026-09-10
Status: FROZEN DESIGN / RED-FIRST; executable proof pending
Contract: `OBSERVER_ECLIPSE_REUSABLE_HOLDOUT_PRIVACY_ROOT_RECOVERY_RETENTION_DELEGATION_PQ_CROSS_SNI_V1_FROZEN`

## Scope

Distinct fallback while LAB-086 exact executable materialization remains unavailable. This design does **not** substitute for LAB-086 RED/GREEN execution.

## Primary donors

- RFC 9162, Certificate Transparency Version 2 — authenticated tree heads, inclusion/consistency proofs, split-view detection assumptions; gossip itself is outside the protocol.
- Nakkiran & Blasiok, *The Generic Holdout: Preventing False-Discoveries in Adaptive Data Science* (arXiv:1809.05596) — exploration/holdout separation and limited exposure under adaptive search.
- The Update Framework (TUF) specification — versioned trusted metadata, rollback/freeze resistance, threshold root rotation/recovery semantics.
- RFC 9345, Delegated Credentials for TLS and DTLS — delegated credential cryptographic binding and bounded validity; compromise cannot be revoked independently of the parent certificate.
- RFC 9846 / RFC 8446, TLS 1.3 — resumption PSK/SNI rules and ticket ancestry/lifetime considerations.

## Frozen boundaries

### 1. Conflict observer admission/removal and eclipse resistance

`ENOUGH_SIGNATURES_ON_ONE_VIEW != SUFFICIENT_OBSERVER_COVERAGE`

A checkpoint/adjudication package MUST bind an observer-set epoch containing at least: observer identity, independent failure-domain identity, admission/removal transition, expected coverage class, and observation cutoff. Admission/removal is itself authenticated successor state; an operator cannot silently delete an observer after it reports a conflicting head.

A quorum over observers sharing one network/control-plane failure domain does not establish eclipse resistance. Coverage thresholds count qualified independent failure domains, not raw signatures. Missing required domains produce `OBSERVER_COVERAGE_INCOMPLETE`; they do not prove absence of a hidden conflicting view.

Late authenticated conflicts append evidence and may reopen finality. Earlier cutoff evidence is retained rather than rewritten.

### 2. Reusable holdout accounting for repeated flaky-candidate confirmation

`HOLDOUT_QUERY_LIMIT_NOT_EXCEEDED != HOLDOUT_REMAINS_INDEPENDENT`

Every confirmation exposure consumes an accounting unit tied to holdout generation, candidate family, released statistic, and analyst/search state. A binary pass/fail bit leaks less than a full score but is still adaptive information.

Default safe mode is one fresh confirmation generation per selected candidate family. Reuse requires an explicit reusable-validation mechanism with a predeclared exposure budget and proof assumptions; otherwise any outcome used to rank, mutate, prune, stop, or choose the next candidate burns independence for ordinary inference.

Post-selection confirmation must use data not used by adaptive search or previous candidate selection.

### 3. Privacy reconciliation-root compromise recovery

`NEW_RECONCILIATION_ROOT_VALID != OLD_SPEND_HISTORY_REAUTHORIZED`

Recovery creates a successor root generation that commits to: compromised predecessor generation, last accepted monotonic spend/checkpoint floor, unresolved reservations/transfers, fenced authorities, recovery quorum, and transition nonce.

Old valid reconciliation roots remain historical evidence but lose authority after compromise cutoff. Replaying an older signed root or restoring an old database cannot decrease charged/unknown cumulative privacy spend.

If the recovery process cannot prove whether a reservation/disclosure crossed the boundary, the amount remains charged-or-unknown until independent evidence resolves it; compromise recovery never mints budget.

### 4. Retention writer-capability delegation/subdelegation inventory closure

`PRINCIPAL_NOT_LISTED_AS_WRITER != PRINCIPAL_LACKS_DESTRUCTIVE_AUTHORITY`

Writer inventory is capability-closure, not an ACL snapshot. For every membership epoch it MUST include direct writers plus delegated/subdelegated destructive capabilities, service-account impersonation paths, break-glass paths, queued/offline jobs, and recovery/DR authorities.

Delegation records bind delegator, delegatee, capability scope, validity interval, epoch, revocation generation, and whether subdelegation is allowed. Inventory completeness requires traversing this authenticated delegation graph to a fixed point.

A writer removed from the top-level membership list but still reachable through an unrevoked delegation keeps the interval `INVENTORY_INCOMPLETE`. Reconciliation requires gap-free receipts or authenticated fencing for every reachable destructive-capable authority.

### 5. PQ/ECH ticket ancestry across delegated credentials, certificate revocation, cross-SNI resumption, and stale issuers

`CROSS_SNI_CERT_COVERAGE != CROSS_SNI_RESUMPTION_AUTHORITY`

TLS permits cross-SNI resumption only under specific conditions; certificate name coverage alone is insufficient runtime authority. A resumption ticket/descendant MUST carry ancestry floors for original SNI, current requested SNI, certificate identity/generation, delegated-credential generation/expiry, PQ/hybrid policy generation, ECH source/config generation, backend/route authority, ticket-key generation, revocation floor, and replay floor.

RFC 9345 delegated credentials are bounded and cannot be independently revoked without revoking the parent certificate. Therefore a ticket issued under a delegated credential MUST NOT outlive the effective authenticated identity floor chosen by policy; a descendant ticket does not erase DC/certificate ancestry.

After parent-certificate revocation, DC compromise, PQ-policy increase, or regional issuer compromise, stale issuers are fenced from issuing descendants. A late region must prove current revocation/PQ/ECH/ticket-key/replay floors before accepting resumption; otherwise use full 1-RTT authentication. Cross-SNI resumption is additionally denied unless an explicit current policy authorizes that SNI pair/service-equivalence class.

## RED-first matrix (40 cases)

### Observer/eclipsing (8)
1. Remove observer after conflicting-head report; removal cannot erase evidence.
2. Five observers in one failure domain fail a three-domain coverage threshold.
3. Required observer partitioned at cutoff -> `OBSERVER_COVERAGE_INCOMPLETE`.
4. Late conflicting head reopens finality without rewriting old cutoff package.
5. Unauthenticated observer admission is ignored.
6. Replayed old observer-set epoch cannot satisfy current adjudication.
7. Two admitted identities mapping to same failure domain count once.
8. Observer rejoin requires current epoch/floor before contributing quorum.

### Reusable holdout (8)
9. Candidate chosen after viewing confirmation bit cannot reuse same bitset as independent proof.
10. Full score exposure burns more explicit budget than binary threshold exposure.
11. Fresh holdout confirms candidate selected only on exploration data.
12. Holdout outcome used to mutate candidate burns generation.
13. Sequential stop after first pass is represented in accounting.
14. Candidate-family alias cannot bypass exposure budget.
15. Restored snapshot cannot reset holdout query ledger.
16. Reusable mechanism without declared assumptions fails closed to fresh holdout.

### Privacy-root recovery (8)
17. Replay old signed reconciliation root after successor recovery rejected.
18. DB rollback below monotonic spend floor rejected.
19. Unknown in-flight disclosure remains charged/unknown through recovery.
20. Compromised root cannot self-authorize its successor alone.
21. Successor root binds explicit predecessor compromise cutoff.
22. Fenced old regional authority cannot commit new reservations.
23. Old transfer acknowledgement cannot mint capacity in new generation.
24. Recovery with missing unresolved-reservation inventory fails closed.

### Retention delegation closure (8)
25. Direct writer removed but subdelegation remains -> still writer-capable.
26. Delegation with expired validity excluded after trusted-time proof.
27. Revoked delegation replay rejected by revocation generation.
28. Break-glass capability appears in canonical inventory.
29. DR restore authority appears even when region inactive.
30. Queue worker with destructive token appears until token/fence revoked.
31. Delegation cycle terminates deterministically and does not hide members.
32. Omitted reachable writer downgrades reconciliation to `INVENTORY_INCOMPLETE`.

### PQ/ECH/cross-SNI ancestry (8)
33. Certificate covers A+B but ticket from A cannot resume B without explicit service-equivalence policy.
34. Authorized A->B cross-SNI resumption still fails when PQ floor increased.
35. Descendant ticket issued after DC expiry cannot erase expired identity ancestry.
36. Parent certificate revoked -> affected ticket ancestry rejected.
37. Compromised stale region cannot issue valid descendant after fencing generation advances.
38. Late region lacking current ECH source/revocation floor uses full handshake only.
39. Ticket issued under pre-incident key remains tainted after descendant issuance.
40. Full 1-RTT recovery may pass while 0-RTT remains disabled until replay/revocation floors converge.

## Implementation consequences

- Add authenticated observer-set epochs and independent failure-domain coverage accounting to LAB-093+ witness/checkpoint contracts.
- Separate adaptive search data from fresh confirmation generations; persist holdout exposure ledger monotonically.
- Treat privacy reconciliation roots like versioned authority state with successor anti-rollback and unresolved-spend carry-forward.
- Compute retention writer inventory from authenticated capability/delegation graph closure, not only membership rows.
- Carry explicit identity/PQ/ECH/route/revocation ancestry in ticket policy metadata and fence stale regional issuers.

## Validation status

Research/design only. Direct Git transport was probed in this run and failed before repository code execution with `Could not resolve host: github.com`. Connector reads/writes work, but no supported non-model connector-to-filesystem materializer is exposed. No LAB-086 executable PASS is claimed.
