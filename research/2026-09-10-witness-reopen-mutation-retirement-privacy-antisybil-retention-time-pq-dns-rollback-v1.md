# Witness reopen, mutation-retirement, anti-sybil privacy ledger, retention-time, and PQ/DNS rollback — v1

Status: `WITNESS_REOPEN_MUTATION_RETIREMENT_PRIVACY_ANTISYBIL_RETENTION_TIME_PQ_DNS_ROLLBACK_V1_FROZEN`
Date: 2026-09-10
Parent: LAB-093 / #178
Execution priority remains LAB-086 / #163. This document is a distinct fallback evidence slice; it does not substitute for executable RED/GREEN proof.

## Per-run execution observation

LAB-086 was resumed first. GitHub connector reads are available and PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. A direct local clone probe failed before repository execution because the executor could not resolve `github.com`. No supported non-model connector-to-filesystem materializer is exposed in this run. Therefore no new LAB-086 behavioral, unsafe-seed, compileall, reconciliation, or conflict PASS is claimed.

## Objective

Freeze the next security boundary for five coupled lifecycle failures that become dangerous when an implementation treats an authenticated historical fact as permanent current authority:

1. witness finalization rollback/reopen and cross-generation acknowledgement equivocation;
2. mutation-operator provenance and retirement of verifier coverage floors;
3. privacy-budget anti-sybil verifier identity and budget-ledger recovery;
4. retention clock-source compromise/time rollback and cross-policy precedence;
5. PQ/ECH authenticated DNS transition rollback, stale negative caching, and capability-stripping intermediaries.

The common rule is:

> **Authenticated predecessor evidence remains evidence. It does not, by itself, authorize a successor to reinterpret time, identity, coverage, privacy spend, or transport capability.**

## Primary donors and limits

### RFC 9162 — Certificate Transparency v2

Useful donor mechanism: signed tree heads, consistency auditing, and preservation/detection of conflicting log views. RFC 9162 explicitly treats conflicting views as log misbehavior and notes gossip/comparison of signed heads as the mechanism for exposing it.

Limit: CT does not define this runtime's witness recovery or reopening policy. We borrow append-only lineage and split-view evidence semantics, not CT deployment assumptions.

### SLSA provenance and reproducibility guidance

Useful donor mechanism: provenance identifies the transitive trusted build platform through `builder.id`; verified reproducibility only raises assurance when rebuilders are truly independent. Reproducers sharing the same vulnerable pipeline are correlated, not independent.

Limit: SLSA does not define semantic mutation-corpus retirement. We borrow provenance and independence boundaries.

### NIST SP 800-226 — Differential Privacy

Useful donor mechanism: privacy loss composes across repeated releases; NIST explicitly describes aggregate/global privacy-budget thinking across multiple releases.

Limit: this runtime's selective-disclosure budget need not literally implement differential privacy. The reusable security principle is compositional accounting: independently valid releases can jointly exceed a global disclosure limit.

### NIST verified timestamping work

Useful donor mechanism: timestamp integrity can require aggregation across multiple high-integrity clocks; timestamp/order claims are security-relevant and vulnerable to malicious delay or compromised time sources.

Limit: this does not decide legal retention duration or precedence. Runtime policy must consume authenticated policy inputs rather than infer legal conclusions.

### RFC 9460 — SVCB/HTTPS DNS records

Useful donor mechanisms: alternative endpoints may have different capabilities and operators; denial/selective suppression of SVCB can remove security benefits; DNSSEC policy should be consistent between A/AAAA and SVCB; optimistic connection must not send information whose handling could be changed by a pending SVCB answer.

Limit: SVCB does not define a PQ requirement. We use it to model endpoint-capability continuity and downgrade/suppression paths.

### RFC 9849 — TLS Encrypted Client Hello

Useful donor mechanisms: ECH rejection is retry machinery, not normal origin-authenticated application success; public-name authentication does not authenticate the origin and session tickets from that rejection connection must be ignored; retry configuration and multi-server inconsistency require careful handling.

Limit: ECH does not define post-quantum policy. We bind its retry/config lineage semantics to an independently defined current crypto floor.

## Frozen contract

### A. Witness finalization rollback/reopen

#### A1. Finalization is versioned, not irreversible truth rewriting

`FINALIZED_GENERATION != HISTORY_CAN_NEVER_BE_REOPENED`

A finalized witness generation may later be reopened only through an authenticated successor event containing at minimum:

- predecessor generation and finalization digest;
- explicit reopen reason code;
- successor generation;
- required recovery/root quorum identities;
- timestamp/freshness evidence under current policy;
- exact set/range of historical statements whose assurance state changes;
- retained link to all predecessor and competing successor evidence.

Reopen changes the assurance state; it never deletes the old signed fact that finalization occurred.

#### A2. Reopen does not retroactively erase predecessor finalization

`REOPEN_AUTHORIZED != PREDECESSOR_FINALIZATION_NEVER_HAPPENED`

Consumers must be able to answer both:

- what was believed/finalized at time T under generation G;
- what later recovery/reopen event changed current assurance.

This is required for incident reconstruction and anti-equivocation.

#### A3. Cross-generation acknowledgement equivocation is split-view

If successor witness generation G2 acknowledges predecessor head H1 while another valid successor G2' acknowledges incompatible predecessor head H1', both descendants are preserved as conflicting lineage evidence.

`TWO_VALID_SUCCESSOR_SIGNATURES != ONE_CANONICAL_HISTORY`

No last-writer-wins rule is allowed for security lineage.

#### A4. Recovery quorum membership is precommitted

A recovery quorum cannot be selected after observing which witnesses are available or favorable. Membership/selection rule must be committed before the failure/reopen event or derived deterministically from authenticated predecessor state.

`AVAILABLE_AFTER_INCIDENT != ELIGIBLE_FOR_RECOVERY_QUORUM`

### B. Mutation-operator provenance and coverage-floor retirement

#### B1. Corpus digest without operator provenance is insufficient

`CORPUS_HASH_VALID != TEST_GENERATION_TRUSTWORTHY`

Every security corpus generation binds:

- source/generator version;
- oracle version and trust root;
- mutation-operator set and parameters;
- deterministic/random seed policy where relevant;
- semantic coverage taxonomy;
- exclusions and unsupported surfaces;
- builder/reproducer provenance.

#### B2. Coverage floor is a policy object

A verifier generation has an authenticated minimum coverage floor, e.g. mandatory semantic classes and adversarial mutation families. Passing a corpus below the current floor is not a current-security PASS.

`OLD_CORPUS_PASS != CURRENT_COVERAGE_PASS`

#### B3. Mutation-operator retirement is explicit

An operator can be retired only with a versioned disposition:

- superseded-by operator(s), with evidence of equal-or-greater semantic coverage; or
- no-longer-applicable because the guarded feature was removed; or
- accepted residual gap explicitly tracked as degraded assurance.

Silent removal is prohibited.

#### B4. Correlated reproducibility is not independent assurance

Two corpus/verifier builds produced by the same transitive control plane, dependency source, oracle, or mutation generator do not count as two independent votes merely because artifact hashes differ.

`TWO_REPRODUCERS != TWO_FAILURE_DOMAINS`

### C. Privacy-budget anti-sybil identity and ledger recovery

#### C1. Budget is keyed to protected subject/purpose/window, not verifier account alone

`NEW_VERIFIER_ID != NEW_PRIVACY_BUDGET`

A requester cannot reset disclosure allowance by rotating verifier identity, API account, region, process, or presentation key.

The accounting key must bind an authenticated logical disclosure domain such as:

`(protected_subject_or_cohort, purpose_class, policy_epoch, time_window)`

Verifier identity remains an audit dimension, not the sole budget key.

#### C2. Anti-sybil admission is separate from privacy authorization

Proof that a verifier is a unique/admitted principal does not grant disclosure. Conversely, privacy authorization does not prove verifier uniqueness.

`IDENTITY_ADMITTED != DISCLOSURE_AUTHORIZED`

#### C3. Global privacy spend is append-only and conserved

Each disclosure creates authenticated spend evidence containing request digest, disclosed predicate/field class, budget delta, logical accounting key, predecessor ledger head, and resulting head.

Concurrent/distributed spending must conserve the global cap. Partition ambiguity fails closed or uses preallocated authenticated shards whose total does not exceed the cap.

#### C4. Ledger restore cannot restore spent privacy budget

`BACKUP_RESTORE != PRIVACY_SPEND_ROLLBACK`

After restore, current spend floor is reconstructed from external witness/anchor evidence or the system enters `PRIVACY_BUDGET_STATE_UNKNOWN` and withholds disclosures that might exceed the cap.

#### C5. Compromise/recovery does not reset historical spend

A compromised verifier credential can be revoked and replaced, but already issued disclosures remain part of subject-level composition unless policy explicitly defines an expiration window that has elapsed under trustworthy time.

### D. Retention clock compromise, rollback, and policy precedence

#### D1. Wall-clock observation is not destruction authority

`LOCAL_TIME_AFTER_EXPIRY != DELETE_AUTHORIZED`

Destructive retention actions require an authenticated time/freshness source acceptable under current policy. If the clock source is compromised, stale, rollbacked, or outside tolerance, destructive deletion fails closed.

#### D2. Monotonic elapsed-time and civil-time obligations are distinct

Policies that say "retain for N days" and policies that say "retain until date D" must not be conflated. The canonical policy representation declares its time semantics and accepted clock authority.

#### D3. Clock rollback cannot resurrect an expired authorization

Once a policy transition was durably accepted under trustworthy time, restoring a machine or receiving an earlier wall clock does not automatically return predecessor authority.

`TIME_ROLLBACK != POLICY_ROLLBACK`

#### D4. Cross-policy precedence is authenticated and deterministic

When deletion, legal/retention hold, security evidence retention, and privacy minimization policies conflict, the runtime applies a predeclared precedence rule versioned by policy epoch. It must emit an explicit disposition such as:

- `DELETION_DEFERRED_BY_HOLD`;
- `DELETION_DEFERRED_TIME_UNTRUSTED`;
- `PAYLOAD_DELETED_AUDIT_EVIDENCE_RETAINED`;
- `POLICY_CONFLICT_REQUIRES_EXTERNAL_AUTHORITY`.

The runtime does not invent legal precedence.

#### D5. Policy changes do not backdate certainty

A successor retention policy can govern future actions but cannot rewrite whether a past deletion/hold was valid under the then-current policy and evidence.

### E. PQ/ECH authenticated DNS rollback and capability stripping

#### E1. DNS route success does not prove security-capability continuity

`ENDPOINT_REACHABLE != CURRENT_CRYPTO_FLOOR_SATISFIED`

Each selected endpoint is re-evaluated against current requirements including PQ/hybrid capability, ECH policy, ALPN/service identity, and resumption authority.

RFC 9460 explicitly allows alternatives with different capabilities/operators; therefore fallback endpoint choice cannot inherit stronger capability claims from a previous endpoint.

#### E2. Selective SVCB/HTTPS suppression is a downgrade signal

If policy requires a security property advertised through authenticated SVCB/HTTPS data, disappearance/failure that could result from selective suppression cannot silently fall back to an insecure authority endpoint.

State becomes `ROUTING_SECURITY_SIGNAL_UNAVAILABLE` or equivalent until the current policy can be satisfied.

#### E3. Stale positive and negative DNS cache entries are policy-versioned

A cached NODATA/SERVFAIL/negative result from an older policy/configuration epoch must not suppress newly required ECH/PQ capability indefinitely. Cache decisions bind:

- DNS name/type;
- validation status;
- TTL/expiry;
- resolver/network partition identity where relevant;
- policy epoch;
- ECH/SVCB configuration generation if known.

Network change or authenticated policy/config generation change invalidates incompatible cached routing conclusions.

#### E4. ECH rejection/retry cannot authorize origin application data

RFC 9849's public-name rejection connection is retry machinery: public-name authentication is not origin authentication and tickets/session IDs from that connection are ignored.

The runtime therefore forbids treating ECH retry success as permission to reuse predecessor origin/PQ resumption authority.

#### E5. Capability-stripping intermediaries are not transparent success

An intermediary that removes unknown/unsupported SvcParams, strips ECH-related capability, terminates TLS at a lower crypto floor, or maps to a backend without the current required capability causes explicit policy failure unless an authenticated adapter contract proves equivalent-or-stronger semantics.

`INTERMEDIARY_ACCEPTED_TRAFFIC != END_TO_END_POLICY_SATISFIED`

#### E6. Rollback requires authenticated lineage, not merely old-valid config

Old DNSSEC-valid SVCB/ECH data can remain cryptographically authentic while being operationally stale. Current authorization therefore binds freshness/config generation and current policy, not signature validity alone.

`OLD_CONFIG_SIGNATURE_VALID != CURRENT_CONFIG_AUTHORIZED`

## Required state model

The implementation should expose explicit states rather than coalescing them into generic failure:

- `WITNESS_FINALIZED`
- `WITNESS_REOPEN_PENDING`
- `WITNESS_REOPENED`
- `WITNESS_LINEAGE_SPLIT_VIEW`
- `CORPUS_COVERAGE_CURRENT`
- `CORPUS_COVERAGE_DEGRADED`
- `MUTATION_OPERATOR_RETIREMENT_UNPROVEN`
- `PRIVACY_BUDGET_AVAILABLE`
- `PRIVACY_BUDGET_EXHAUSTED`
- `PRIVACY_BUDGET_STATE_UNKNOWN`
- `RETENTION_TIME_TRUSTED`
- `RETENTION_TIME_UNTRUSTED`
- `RETENTION_POLICY_CONFLICT`
- `ROUTING_SECURITY_SIGNAL_AVAILABLE`
- `ROUTING_SECURITY_SIGNAL_UNAVAILABLE`
- `CURRENT_CRYPTO_FLOOR_SATISFIED`
- `CURRENT_CRYPTO_FLOOR_UNSATISFIED`

## RED-first regression matrix (40 cases)

### Witness finalization / reopen

1. Reopen finalized G1 with valid current recovery/root quorum -> successor event appended; G1 finalization retained.
2. Attempt reopen by editing G1 finalization row in place -> reject before mutation.
3. Two successors acknowledge incompatible G1 heads -> split-view, preserve both.
4. One successor arrives later with higher local timestamp -> must not last-writer-win over conflicting successor.
5. Recovery quorum chosen from responders only after incident -> reject eligibility.
6. Precommitted deterministic recovery membership with sufficient quorum -> accept.
7. Reopen event omits exact affected history range -> reject.
8. Reopen after restore where current lineage anchor cannot be reconstructed -> fail closed / lineage unknown.

### Mutation-operator provenance / retirement

9. Corpus hash matches but generator provenance missing -> no current-security PASS.
10. Oracle digest changes without policy transition -> reject comparison as equivalent corpus generation.
11. Mandatory mutation family silently removed -> coverage-floor failure.
12. Operator retired with proven superseding operator covering same semantic class -> accept transition.
13. Operator retired because feature removed, but feature still reachable -> reject.
14. Two rebuilders share same compromised mutation generator -> count as correlated, not independent.
15. Corpus passes old coverage floor but misses newly mandatory parser differential family -> degraded/current FAIL.
16. Historical verdict produced by later-compromised oracle -> retain verdict as historical but mark assurance degraded.

### Privacy anti-sybil / budget recovery

17. Same logical subject requested through new verifier account after spend -> budget does not reset.
18. Verifier rotates presentation key -> historical spend remains composed.
19. Two regions concurrently spend final budget unit without global authority -> at most one succeeds.
20. Partitioned preallocated shards whose sum <= cap -> bounded local spend permitted.
21. Restore database from before disclosure -> external spend floor prevents budget resurrection.
22. Spend floor unavailable after restore -> state unknown; consequential disclosure blocked.
23. Recovered verifier credential requests same disclosure -> historical subject-level spend still counts.
24. Per-verifier budgets individually pass but global subject/window cap exceeds -> reject final disclosure.

### Retention time / precedence

25. Local clock jumps forward past delete date while trusted source disagrees -> no deletion.
26. Local clock rolls backward after a valid expiry transition -> predecessor authority not resurrected.
27. Trusted time freshness exceeds tolerance -> destructive deletion blocked.
28. Relative-duration policy interpreted as civil-date deadline without declared semantics -> reject policy compilation.
29. Active authenticated hold conflicts with deletion deadline -> emit deferred-by-hold disposition.
30. Hold freshness unknown -> no destructive deletion.
31. Privacy minimization says delete payload while audit policy retains authenticated disposition -> delete payload, retain permitted audit evidence.
32. Two policy authorities conflict and precedence rule has no applicable branch -> explicit external-authority-required state; no fabricated resolution.

### PQ/ECH/DNS rollback / capability stripping

33. Authenticated SVCB endpoint with required PQ/ECH capability -> connection may proceed after current TLS/service checks.
34. SVCB lookup selectively times out while current policy requires advertised security property -> do not silently downgrade to bare A/AAAA endpoint.
35. Cached negative SVCB result survives into new policy epoch requiring ECH/PQ -> invalidate/re-resolve rather than inherit negative conclusion.
36. Network changes while DNS cache contains unvalidated endpoint data -> partition/flush cache per policy before use.
37. ECH rejection authenticates only public_name -> no application data; ignore tickets/session IDs from rejection connection as RFC 9849 requires.
38. ECH retry config from a valid rejection points to server context not satisfying current PQ floor -> reject current application session.
39. Intermediary strips mandatory SvcParam/capability and fallback endpoint is reachable -> reachability does not satisfy policy; fail closed.
40. Old DNSSEC-valid/ECH config is replayed after authenticated newer generation -> signature validity alone cannot authorize rollback.

## Implementation guidance

1. Keep each lifecycle as an append-only generation transition with explicit predecessor digest.
2. Store assurance/degradation separately from raw historical evidence.
3. Use one canonical policy evaluator for current authorization; never infer authority from the mere presence of signed old evidence.
4. Bind privacy spend and retention decisions to external monotonic/freshness anchors where rollback matters.
5. Bind routing/TLS authorization to current endpoint + service identity + current crypto policy, not origin name alone.
6. Test state restoration, partitions, duplicate/reordered events, and mixed-version readers before production refactors.

## Security audit notes

- No design here authorizes low-level ref/tree GitHub manipulation, force updates, or bypass of safety gates.
- No donor is treated as proving this runtime's implementation correct.
- Historical evidence is preserved even when current assurance degrades.
- Privacy and retention semantics intentionally fail closed when global accounting or trustworthy time is unknown.
- PQ/ECH rules reject capability stripping and stale authenticated configuration as authorization shortcuts.

## Next executable priority

LAB-086 remains first. On the next run, probe once for a supported non-model way to materialize the pinned executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` into the local executor. If available, verify every reconstructed file by Git blob identity and execute the retained full LAB-086 gate before any merge-state change.

If still unavailable, the next distinct evidence slice is: **witness reopen quorum key compromise and acknowledgement replay windows + semantic coverage claims under generated/adaptive mutation search + privacy-budget delegation/transfer and subject-merging/splitting attacks + retention time-source quorum/common-mode failure and leap/epoch handling + PQ/ECH/SVCB multi-resolver disagreement, DNSSEC key rollover and resumption after route-policy convergence**.
