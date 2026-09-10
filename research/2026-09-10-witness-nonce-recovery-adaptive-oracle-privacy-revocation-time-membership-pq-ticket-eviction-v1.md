# Witness nonce recovery, adaptive-oracle independence, privacy revocation, time-membership, and PQ ticket eviction v1

Status: `WITNESS_NONCE_RECOVERY_ADAPTIVE_ORACLE_PRIVACY_REVOCATION_TIME_MEMBERSHIP_PQ_TICKET_EVICTION_V1_FROZEN`

Date: 2026-09-10

## Scope

Distinct follow-up to the LAB-093 design line while LAB-086 exact executable closure remains blocked by the current run's lack of a supported byte-exact connector-to-filesystem materializer and direct Git DNS failure.

This note freezes five additional authority boundaries and a 40-case RED-first test matrix. It is architecture evidence only; it does **not** substitute for executable RED/GREEN proof on LAB-086 or LAB-093..100.

## Primary donors

- RFC 9162 — append-only/log consistency and split-view evidence semantics.
- RFC 5011 — authenticated trust-anchor addition/revocation, compromise recovery, hold-down state.
- RFC 6781 — DNSSEC operational rollover, emergency rollover, propagation/cache overlap.
- RFC 9846 (TLS 1.3) — 0-RTT anti-replay, single authoritative storage zone per ticket, startup replay window.
- SLSA FAQ — reproducible verification requires truly independent rebuilders; common pipeline/control-plane defects remain correlated.
- NIST SP 800-226 — privacy-loss composition and global privacy-budget reasoning.

---

## 1. Witness acknowledgement nonce store: rollback/GC is authority state, not cache state

### Frozen boundary

`NONCE_ABSENT_LOCALLY != ACKNOWLEDGEMENT_FRESH`

A witness acknowledgement nonce/transition-id store is security state. Absence after snapshot rollback, replica restore, compaction, GC, failover, or region rebuild is not proof that the acknowledgement has never been consumed.

### Required authority model

Each consequential acknowledgement binds at minimum:

- predecessor digest;
- successor digest;
- witness-set / quorum generation;
- signing-key generation;
- role (`REOPEN`, `FINALIZE`, `RECOVERY_BRIDGE`, etc.);
- transition id;
- nonce or unique spend id;
- policy generation;
- freshness window or monotonic sequence.

The consumed-acknowledgement floor must be monotonic across restore-capable domains. GC is permitted only when replay remains impossible from all retained artifacts or when a successor authenticated checkpoint makes all lower spends permanently invalid.

### Recovery after compromised acknowledgement key

`NEW_KEY_VALID != OLD_ACKNOWLEDGEMENT_HISTORY_REPAIRED`

Compromise creates an assurance boundary. Recovery requires an authenticated bridge from the last non-degraded checkpoint to a successor key/quorum generation. The bridge must name the compromised generation and the exact admissible history interval. A successor key cannot retroactively convert unverifiable predecessor acknowledgements into trusted ones.

RFC 5011 is a useful donor: explicit revocation is a first-class state, and a newly accepted trust anchor appears only after authenticated continuity and hold-down semantics; compromise recovery is not modeled as silently forgetting the old key.

### Consequence

A recovered node whose nonce database is older than the durable witness-history checkpoint must enter `ACK_SPEND_STATE_UNKNOWN` and refuse consequential reopen/finalize acknowledgements until it reconstructs or proves a monotonic spend floor.

---

## 2. Adaptive mutation: reward/oracle collusion and metamorphic independence

### Frozen boundaries

`ADAPTIVE_SEARCH_SCORE_HIGH != SECURITY_COVERAGE_HIGH`

`ORACLE_AGREES_WITH_GENERATOR != ORACLE_INDEPENDENT`

An adaptive mutation system can learn the blind spots of its own reward/oracle. A clean run is especially weak if generator, oracle, coverage metric, parser, canonicalizer, and build pipeline share implementation or provenance.

### Required evidence object

Authenticated test evidence separates:

- immutable base corpus root;
- mutation-operator set and versions;
- adaptive search algorithm and version;
- seeds / RNG commitment where deterministic replay is expected;
- search budget and stopping rule;
- reward features;
- oracle implementations and provenance;
- semantic invariants / metamorphic relations;
- differential peers;
- coverage-floor version;
- excluded mutation families and reasons.

### Metamorphic/differential rule

At least one security-relevant oracle path must not merely call the same normalization/parser/decision function under test. Where exact expected outputs are unavailable, use authenticated metamorphic relations (for example canonicalization idempotence, equivalent-representation agreement, forbidden-field preservation, monotonic-policy relations) and independently implemented differential checks.

SLSA's independent-rebuilder warning is the donor principle: two outputs from one vulnerable shared pipeline are not two independent authorities.

### Failure state

If generator/reward/oracle provenance collapses into a common failure domain, record `ORACLE_INDEPENDENCE_DEGRADED`; do not silently count the run as multi-oracle evidence.

---

## 3. Privacy-budget delegation revocation and race safety

### Frozen boundaries

`DELEGATION_REVOKED != IN_FLIGHT_SPEND_ERASED`

`CHILD_CREDENTIAL_ROTATED != CHILD_BUDGET_RESET`

`PURPOSE_RELABELED != NEW_GLOBAL_PRIVACY_BUDGET`

Delegated disclosure authority is a conserved spend capability. Revocation stops future authorization but does not erase already committed or concurrently reserved spend.

### Two-phase spend model

Consequential disclosure uses a durable reservation protocol:

1. resolve canonical subject lineage and purpose-policy generation;
2. reserve budget under parent/global accounting authority;
3. obtain disclosure proof/result;
4. commit exact spend against reservation;
5. release reservation only when the operation is proven not to have disclosed.

Timeout/UNKNOWN after disclosure generation must conservatively retain or reconcile the reservation; it cannot be treated as free budget.

### Revocation race

Revocation is ordered against reservations by authenticated monotonic generation/sequence. A child cannot create a fresh credential, split a subject, merge identities, change verifier id, or relabel purpose to outrun a revocation already ordered before its reservation.

### Composition

NIST SP 800-226 is the donor for the underlying privacy-loss composition principle: repeated releases compose. The runtime extension is that delegation topology and credential lifecycle must not manufacture additional global budget.

### Failure state

Unknown parent lineage, unknown global spend, or uncertain revocation ordering yields `PRIVACY_BUDGET_STATE_UNKNOWN` and blocks consequential disclosure.

---

## 4. Retention time quorum membership rotation and holdover

### Frozen boundaries

`CLOCK_STILL_TICKS != TIME_AUTHORITY_STILL_CURRENT`

`QUORUM_MEMBERSHIP_CHANGED != OLD_TIME_VOTES_REUSABLE`

`HOLDOVER_WITHIN_DEVICE_SPEC != RETENTION_DEADLINE_AUTHORIZED`

A time quorum is a versioned authority set, not a bag of timestamps. Membership rotation, source loss, holdover, leap handling, restore, and recovery must preserve a monotonic destructive-action floor.

### Required time attestation

Each accepted time statement binds:

- time-authority membership epoch;
- source identity and key generation;
- observed time / uncertainty;
- monotonic local sequence where available;
- upstream source/failure-domain identity commitment;
- holdover state and maximum uncertainty;
- leap-state handling;
- policy generation.

A quorum result binds the exact member epoch and the contributing statements. Votes from retired membership epochs cannot be mixed with new membership to fabricate quorum unless an authenticated transition contract explicitly permits overlap.

### Holdover

When external sources disappear, local oscillator holdover is evidence with increasing uncertainty, not equivalent authority to a fresh quorum. Destructive retention actions require a policy-defined maximum uncertainty; beyond it the system enters `RETENTION_TIME_UNCERTAIN` and defers deletion rather than guessing.

### Common-mode failure

Counting sources requires transitive independence over network path, operator, upstream clock, KMS/signing authority, recovery mechanism, and software/control-plane dependencies. Three APIs backed by one upstream clock are one correlated failure domain for quorum reasoning.

---

## 5. PQ/ECH/SVCB route convergence and session-ticket eviction

### Frozen boundaries

`ROUTE_CONVERGED != OLD_TICKET_REAUTHORIZED`

`DNSSEC_CHAIN_RECOVERED != STALE_TICKET_POLICY_CURRENT`

`TICKET_KEY_STILL_DECRYPTS != TICKET_STILL_SPENDABLE`

DNSSEC/SVCB/ECH recovery determines authenticated route/config state; it does not automatically revive resumption authority minted under a prior route, backend, ALPN, ECH config, certificate generation, or PQ/hybrid policy epoch.

### Ticket authority record

A resumable ticket/PSK is bound to at least:

- origin / inner service identity;
- SNI/ECH inner-name context where applicable;
- ALPN;
- issuing backend/service generation;
- certificate/authentication generation as required by policy;
- current PQ/hybrid minimum-policy epoch;
- route/SVCB/ECH configuration generation where routing affects authorization;
- replay/spend-authority generation;
- issue time / expiry;
- ticket-key generation.

### Emergency DNSSEC rollover

RFC 6781 explicitly requires operators to account for old signed data remaining in caches during rollover; RFC 5011 similarly models trust-anchor transition/revocation as stateful over time. Therefore post-incident route convergence requires a cache-overlap-aware resumption policy.

The safe default after a security-significant DNSSEC/SVCB/ECH rollback or emergency rollover is:

- evict or generation-invalidate tickets minted under incompatible route/security policy;
- reject 0-RTT where replay ownership or route authority is ambiguous;
- permit 1-RTT resumption only if every current authorization input is revalidated and policy allows it;
- otherwise require a full handshake and mint a successor ticket under the new policy generation.

RFC 9846 strengthens the anti-replay side: a single authoritative storage zone per ticket gives stronger 0-RTT replay protection, and freshly started implementations should reject 0-RTT while replay-recording windows overlap startup.

### Session-ticket cache eviction is authority revocation

Eviction/generation invalidation must reach edge caches, service-mesh sidecars, regional ticket decryptors, warm standbys, DR snapshots, and any delegated resumption authority. Deleting the origin's ticket key record while replicas can still decrypt/use the key is not complete revocation.

---

# RED-first matrix (40 cases)

## A. Witness nonce rollback/GC and compromised-key bridges

1. Consume acknowledgement nonce N; restore nonce DB to pre-N snapshot; replay N -> must fail closed.
2. GC N while an old backup containing pre-consumption state remains restorable -> GC must be refused or replay must remain impossible via successor checkpoint.
3. Region A consumes N; region B is promoted from stale replica -> B must not accept N.
4. Nonce absent after fresh-node bootstrap but witness history shows higher spend floor -> `ACK_SPEND_STATE_UNKNOWN`.
5. Same nonce reused with different successor digest -> reject.
6. Same transition id replayed under rotated witness membership -> reject unless explicitly bridged.
7. Old acknowledgement key compromised; successor key signs a statement claiming predecessor history is clean -> predecessor assurance must remain degraded.
8. Recovery bridge signed by authorized survivor quorum names exact predecessor/successor checkpoint and compromise interval -> successor generation may activate without rewriting predecessor assurance.

## B. Adaptive mutation and oracle collusion

9. Generator and oracle share parser bug and agree on malformed duplicate-field input -> independent metamorphic/differential oracle must catch or mark independence degraded.
10. Adaptive reward learns to maximize branch coverage while avoiding security-critical semantic family -> coverage floor remains unmet.
11. Mutation operator family silently removed between corpus versions -> verification rejects evidence unless retirement is authenticated and coverage replacement proved.
12. Search budget reduced after failures disappear -> evidence records budget change; cannot compare as equivalent pass.
13. Two oracle binaries reproduced from same compromised build pipeline -> count as one failure domain.
14. Canonicalization metamorphic relation `canon(canon(x)) == canon(x)` violated -> fail even if expected-output oracle says pass.
15. Equivalent semantic encodings produce different authority decisions -> differential failure.
16. Oracle timeout categorized as pass by adaptive scorer -> test framework must record unknown/failure, never success.

## C. Privacy delegation revocation/races

17. Parent revokes child after child reservation but before disclosure commit -> reconcile reservation; no budget refund merely due to revocation.
18. Parent revokes child before reservation; child uses stale credential -> reject.
19. Child rotates credential after revocation -> budget/authority remains revoked.
20. Subject split into aliases after near-exhausted budget -> aliases inherit conserved global spend.
21. Aliases merge after separate spends -> composed spend reconciles; merge cannot discard one branch.
22. Timeout after disclosure bytes may have left process -> reservation remains spent/unknown until proven otherwise.
23. Same logical disclosure requested under relabeled purpose to evade budget -> policy lineage prevents reset unless genuinely separate budget is explicitly authorized.
24. Restore accounting DB to lower spend while external disclosure evidence shows higher checkpoint -> block as `PRIVACY_BUDGET_STATE_UNKNOWN`.

## D. Retention time-quorum membership/holdover

25. Old-epoch two votes + new-epoch one vote appear to satisfy 3-of-5 -> reject cross-epoch quorum unless transition contract permits overlap.
26. Membership rotates while one old source is compromised -> new quorum cannot reuse its old vote.
27. All sources disappear; local clock enters holdover within uncertainty bound -> non-destructive operations may continue; deletion only if policy explicitly permits current uncertainty.
28. Holdover exceeds uncertainty bound before retention deadline -> defer deletion.
29. VM snapshot rollback moves wall clock backward -> monotonic destructive-action floor remains unchanged.
30. Three named time APIs share one upstream source -> independence calculation collapses common domain.
31. Leap-state disagreement among otherwise signed sources -> explicit ambiguity state; do not choose weakest/earliest destructive deadline.
32. Recovery from time-service outage introduces new member keys without authenticated epoch transition -> quorum rejected.

## E. PQ/ECH/SVCB route convergence and ticket eviction

33. DNSSEC emergency rollover converges, but cached ticket was minted under old PQ policy epoch -> old ticket cannot downgrade current minimum.
34. SVCB route moves origin to new backend generation; old ticket key remains decryptable at edge -> decryption alone does not authorize resumption.
35. ECH config rotates while client presents old ticket bound to old inner-route generation -> require current-context validation; reject incompatible 0-RTT.
36. One region evicts compromised ticket generation; stale DR region is promoted -> stale region must reject 0-RTT until replay/ticket authority is reconciled.
37. Freshly restarted anti-replay service overlaps recording window -> reject 0-RTT per TLS guidance.
38. DNSSEC-valid stale cache and newer DNSSEC-valid answer disagree during rollover -> explicit route-generation ambiguity; no weakest-capability fallback.
39. Ticket remains valid for ALPN A but route convergence selects service/ALPN B -> reject early data / incompatible resumption authority.
40. Full handshake under recovered route succeeds and current PQ/hybrid policy is satisfied -> mint successor ticket under new route/security/replay generations; old incompatible generation remains revoked.

---

## Implementation implications for LAB-093..100

1. Treat nonce/spend/freshness stores as durable authority state with authenticated monotonic checkpoints, not disposable caches.
2. Make key-compromise recovery bridges explicit typed records; preserve degraded-history labels forever unless separately adjudicated with stronger evidence.
3. Test infrastructure must authenticate oracle/generator/build provenance and count failure-domain independence, not process count.
4. Privacy budget uses reserve/commit/reconcile semantics and canonical subject/purpose lineage across delegation and credential lifecycle.
5. Time quorum has authenticated membership epochs and uncertainty-aware holdover; destructive actions fail closed on ambiguous time authority.
6. TLS/PQ ticket caches use generation invalidation tied to current route/service/security/replay authority; route convergence alone is not reauthorization.

## Non-claims

- No LAB-086 source was executed in this run.
- No exact branch-local behavioral PASS is added by this research note.
- No PR readiness/merge state should change because of this note.
- These are frozen design/test obligations to be converted to executable RED tests once byte-exact source execution is available.
