# Convergence evidence revocation propagation, post-completion invalidation, continuous assurance and re-open semantics — v1

Date: 2026-09-08
Status: `CONVERGENCE_EVIDENCE_REVOCATION_PROPAGATION_POST_COMPLETION_INVALIDATION_CONTINUOUS_ASSURANCE_V1_FROZEN`
Parent: LAB-093 / #178

## Question

A prior migration may have reached `CONVERGENCE_PROVEN_*` using authenticated verifier evidence, an enumerated authority topology and negative old-lineage probes. What happens if later evidence proves that one of those premises was false or ceased to be true — for example a verifier key compromise, a resurrected old endpoint, stale DR activation, a topology omission, selective probe steering, or a contradictory attestation?

A one-time convergence certificate is unsafe because evidence authority and effective topology are not immutable.

## Primary-source donors

1. **RFC 9334 — RATS Architecture**
   - Evidence is appraised by a Verifier; Attestation Results are then appraised by a Relying Party.
   - Freshness is an explicit policy decision. An Attestation Result must not be used beyond the period for which the relying party considers it fresh.
   - The architecture explicitly warns that appraisal policy, endorsements and reference values can change; freshness is needed so stale results do not silently survive those changes.
   - https://www.rfc-editor.org/rfc/rfc9334.html

2. **RFC 9943 — SCITT Architecture**
   - A transparency receipt proves registration/inclusion of a signed statement in a transparency service; it does not make the statement semantically true.
   - This supplies the historical-preservation rule: an invalidated convergence statement remains part of the append-only history even after it loses current authority.
   - https://www.rfc-editor.org/rfc/rfc9943.html

3. **The Update Framework specification**
   - Trusted metadata has monotonic versions and expiration; clients must not accept rollback or expired metadata.
   - Key rotation can invalidate previously cached timestamp/snapshot authority and requires recovery behavior rather than silently continuing to use stale trusted state.
   - This supplies the model for monotonic invalidation generations and fail-closed stale cached verdicts.
   - https://theupdateframework.github.io/specification/v1.0.26/

4. **Kubernetes API list/watch and EndpointSlice semantics**
   - `resourceVersion` connects a consistent snapshot to subsequent changes; lost watch continuity requires re-list/reconciliation rather than assuming nothing changed.
   - EndpointSlice clients must aggregate the complete set of slices and tolerate duplication/change propagation.
   - This supplies the topology-continuity model for convergence assurance after completion.
   - https://kubernetes.io/docs/reference/using-api/api-concepts/
   - https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/

## Frozen boundary

`HISTORICALLY_PROVEN_CONVERGENCE != CURRENTLY_VALID_CONVERGENCE`

`TRANSPARENCY_RECEIPT != CURRENT_AUTHORITY`

`COMPLETION_EVENT != PERMANENT_COMPLETION`

`NEW_CONTRADICTORY_EVIDENCE != HISTORY_REWRITE`

A previously valid convergence decision is an historical fact about an evidence set at a particular frontier. It is not an irrevocable grant of current authority.

## 1. Convergence verdicts are versioned authority objects

Define:

```text
ConvergenceVerdictV1 {
  migration_id
  lineage_from
  lineage_to
  verdict_generation
  topology_frontier
  evidence_frontier
  verifier_policy_generation
  evidence_authority_generation
  freshness_not_after
  verdict
  evidence_set_digest
  transparency_receipts[]
}
```

Allowed current verdicts:

- `CONVERGENCE_PROVEN_CURRENT`
- `CONVERGENCE_PROVEN_BOUNDED_RESIDUAL_LEGACY`
- `CONVERGENCE_REOPENED_PENDING_REAPPRAISAL`
- `CONVERGENCE_INVALIDATED_EVIDENCE_AUTHORITY`
- `CONVERGENCE_INVALIDATED_TOPOLOGY`
- `CONVERGENCE_INVALIDATED_EFFECTIVE_CUTOVER`
- `CONVERGENCE_EVIDENCE_CONFLICT_NO_COMPLETION`
- `CONVERGENCE_CURRENT_STATUS_UNKNOWN_STALE`

Historical records are never mutated from PROVEN to INVALID. Instead, a later authenticated generation supersedes the earlier current verdict.

## 2. Invalidation is a first-class authenticated statement

Define:

```text
ConvergenceInvalidationV1 {
  migration_id
  invalidation_generation
  invalidates_verdict_generation
  discovered_at_frontier
  reason_class
  affected_evidence_ids[]
  affected_topology_ids[]
  affected_verifier_or_issuer_keys[]
  contradiction_digest
  authority_policy_generation
  signatures[]
  receipts[]
}
```

The invalidation must itself be authenticated under the current invalidation/appraisal authority. A random telemetry event cannot revoke convergence, but neither can an old convergence receipt override a later authenticated invalidation.

Monotonic rule:

```text
if trusted_invalidation_generation > verdict_generation.current_invalidation_generation:
    old verdict MUST NOT regain current-validity from cache/replay
```

## 3. Mandatory reopen triggers

A current `CONVERGENCE_PROVEN_*` MUST reopen when any authority-relevant premise becomes disproven or cannot remain fresh enough for the operation class.

Mandatory trigger classes:

1. **Evidence/verifier key compromise** whose affected issuance interval intersects evidence used by the verdict.
2. **Verifier-policy compromise or supersession** that makes the old appraisal result no longer acceptable.
3. **Topology omission proof** showing a consequential endpoint/replica existed at the claimed frontier but was absent from the committed coverage ledger.
4. **Endpoint resurrection** where a decommissioned old-lineage-capable endpoint becomes routable/reachable again.
5. **DR/failover activation** of a replica whose lineage/cutover state was not covered by the closed verdict.
6. **Probe-steering proof** showing negative probes were selectively routed away from stale backends.
7. **Contradictory effective-path evidence** showing any consequential request is still accepted under the old lineage after the claimed cutover.
8. **Lost topology-watch continuity** or equivalent unbounded discovery gap for a topology whose membership can change.
9. **Freshness expiry** of evidence required for current consequential authority when no valid refresh exists.
10. **Verifier-independence collapse** discovered after closure, where the counted quorum was actually one correlated failure/control domain and threshold safety depended on that false independence.

## 4. Scope of invalidation

Do not over-revoke automatically.

Each invalidation is classified by the smallest proven affected scope:

- `EVIDENCE_ITEM_ONLY`
- `VERIFIER_ISSUANCE_INTERVAL`
- `TOPOLOGY_SUBSET`
- `OPERATION_CLASS`
- `REGION_OR_FAILURE_DOMAIN`
- `ENTIRE_MIGRATION_CURRENT_AUTHORITY`

If the convergence proof still satisfies its threshold and coverage contract after excluding the tainted scope, it may be re-appraised without pretending the contradiction never happened. If safety depends on the tainted evidence, current convergence reopens.

Unknown compromise onset is handled conservatively: if the affected interval cannot be bounded and the old verdict depends materially on that authority, current status becomes `CONVERGENCE_REOPENED_PENDING_REAPPRAISAL`.

## 5. Propagation contract

Relying parties need an authenticated monotonic invalidation frontier, not best-effort telemetry.

Define:

```text
TrustedConvergenceFrontierV1 {
  migration_id
  highest_verdict_generation
  highest_invalidation_generation
  topology_frontier
  evidence_authority_generation
  freshness_not_after
}
```

Rules:

- a relying party MUST persist the highest authenticated invalidation generation it has accepted;
- lower generations are rollback attempts;
- equal generation with different content is equivocation;
- caches/CDNs may transport artifacts but cannot decide revocation authority;
- a transparency receipt can prove that both the original verdict and its later invalidation were registered; it cannot choose which is current;
- current consequential operations require a frontier fresh enough for their operation class.

## 6. Historical receipts remain valid historical evidence

After invalidation:

- the original `ConvergenceVerdictV1` remains byte-verifiable;
- its SCITT/transparency receipt remains verifiable;
- statements such as “this verdict was issued and registered at frontier F” remain true;
- the separate claim “this verdict is currently authoritative” becomes false or unknown according to the newest authenticated invalidation frontier.

Therefore:

`INVALIDATED_CURRENT_AUTHORITY != ERASED_HISTORY`

Deleting or rewriting the original verdict is prohibited.

## 7. Continuous assurance

A migration is not continuously re-proven from scratch on every request. Instead, current assurance is a composition of monotonic change streams and bounded freshness:

1. topology membership/version continuity;
2. evidence/verifier authority lifecycle continuity;
3. effective-path cutover checks for newly admitted or resurrected backends;
4. contradiction/invalidation stream continuity;
5. freshness renewal before consequential use.

A topology that can change requires either uninterrupted authenticated watch continuity from the closed frontier or a new consistent snapshot plus reconciliation. If continuity is lost, current convergence degrades to `CONVERGENCE_CURRENT_STATUS_UNKNOWN_STALE` until reconciled.

## 8. Endpoint admission after closure

No new or resurrected endpoint inherits convergence by association with a Service, cluster, hostname, autoscaling group or deployment.

Before it may serve consequential traffic it must enter a post-close admission path:

```text
new endpoint discovered
 -> bind endpoint identity to current topology generation
 -> attest current L1-only enforcement state
 -> negative old-lineage challenge on effective path or equivalent stronger proof
 -> record coverage result
 -> only then mark consequentially routable
```

If routing can occur before this admission completes, the migration verdict reopens for that operation class/failure domain.

## 9. Re-close semantics

A reopened migration may be closed again only by a **new verdict generation**.

Required `ConvergenceReclosureV1` inputs:

- reference to every invalidation/contradiction since the previous close;
- proof that each affected evidence item was removed, replaced or independently revalidated;
- current authenticated verifier/evidence authority generations;
- fresh reconciled topology snapshot plus continuity from that snapshot through the re-close frontier;
- exhaustive or statistically bounded negative old-lineage coverage according to the frozen topology/probe contract;
- explicit treatment of resurrected/DR endpoints;
- current enforcement-cutover attestations;
- independent appraisal quorum satisfying the current independence policy;
- new transparency receipt(s).

A re-close cannot delete the old failure interval. The lineage is:

```text
PROVEN(g7)
 -> INVALIDATED(g8, reason=X)
 -> REOPENED(g9)
 -> PROVEN(g10, supersedes g7 only for current authority)
```

Historical queries must be able to reconstruct the entire sequence.

## 10. Conflict semantics

If two authenticated authorities publish incompatible invalidations or incompatible reclosure verdicts for the same generation/frontier:

`CONVERGENCE_EVIDENCE_CONFLICT_NO_COMPLETION`

Do not choose:

- newest wall-clock timestamp;
- first-seen;
- last-write-wins;
- majority of telemetry events;
- the verdict with the larger topology count;
- the verdict that preserves availability.

Resolution requires the higher-order authority/governance mechanism defined for the relevant authority lineage.

## 11. Safety invariant at enforcement points

Client-side knowledge is not sufficient. Once a current authenticated invalidation says old-lineage consequential authority may still exist, enforcement points must fail closed for the affected scope unless an explicitly defined bounded-degradation policy permits otherwise.

A stale client replaying the old `CONVERGENCE_PROVEN_*` artifact cannot override a newer gateway/server-side invalidation frontier.

This is the same asymmetry used in prior activation-epoch work: knowledge of a newer authority state is monotonic and cannot be forgotten merely because an old signed object remains cryptographically valid.

## 12. Fraud / contradiction proof classes

Freeze the following proof classes:

1. `EVIDENCE_KEY_COMPROMISE_INTERSECTS_VERDICT`
2. `VERIFIER_POLICY_SUPERSEDED_UNAPPRAISED`
3. `TOPOLOGY_OMISSION_AFTER_CLOSE`
4. `DECOMMISSIONED_ENDPOINT_RESURRECTED`
5. `UNCOVERED_DR_FAILOVER_ACTIVE`
6. `NEGATIVE_PROBE_STEERING_PROVEN`
7. `OLD_LINEAGE_EFFECTIVE_ACCEPTANCE_OBSERVED`
8. `TOPOLOGY_WATCH_CONTINUITY_LOST`
9. `CONVERGENCE_EVIDENCE_FRESHNESS_EXPIRED`
10. `VERIFIER_INDEPENDENCE_COLLAPSE`
11. `INVALIDATION_ROLLBACK_REPLAY`
12. `CONFLICTING_INVALIDATION_OR_RECLOSURE`

## 13. RED-first matrix

Freeze at least these 48 cases before implementation.

### A. Key / verifier authority (8)
1. compromise after close, outside issuance interval -> historical verdict remains appraisable;
2. compromise intersects one nonessential evidence item -> re-appraise without global reopen if quorum remains safe;
3. compromise intersects threshold-critical evidence -> reopen;
4. unknown compromise onset -> reopen when verdict depends on key;
5. retired-but-not-compromised key -> historical result remains valid for issuance interval;
6. stale cached issuer policy after rotation -> reject current use;
7. lower invalidation generation replay -> reject;
8. same generation/different content -> equivocation conflict.

### B. Topology change / resurrection (10)
9. new backend appears after closure and is not routable -> pending admission, no global break;
10. new backend becomes consequentially routable before admission -> reopen affected scope;
11. old decommissioned endpoint resurrects -> reopen;
12. stale DR replica activates -> reopen;
13. autoscaler creates L1-compliant endpoint, full admission passes -> preserve/reclose current status;
14. endpoint disappears normally with authenticated topology continuity -> no false reopen;
15. discovery snapshot omits backend later proven active at close frontier -> invalidate old proof;
16. topology watch gap with no replacement snapshot -> current status unknown stale;
17. consistent relist proves no consequential change across gap -> re-appraise/reclose;
18. duplicate EndpointSlice observations do not inflate coverage denominator.

### C. Effective cutover / probe evidence (8)
19. production request succeeds under L0 after close -> reopen;
20. negative probe failure to one pinned backend -> reopen affected scope;
21. probe steering discovered after prior all-pass result -> invalidate dependent verdict;
22. synthetic-only health endpoint passes but real path is untested -> cannot reclose;
23. probabilistic sample remains within declared bound -> only bounded claim;
24. sample denominator changes after challenge seed -> invalid proof;
25. backend identity missing from probe result -> insufficient evidence;
26. current positive L1 probe + negative L0 probe on all bounded critical replicas -> eligible for reclose.

### D. Freshness / propagation (8)
27. old verdict receipt replayed after authenticated invalidation -> historical only;
28. CDN cache TTL outlives invalidation -> current use rejected;
29. relying party offline beyond freshness -> status unknown, no consequential mutation;
30. relying party learns invalidation then rolls local cache back -> invalidation remains monotonic;
31. invalidation receipt present but issuer unauthorized -> no revocation authority;
32. valid invalidation not yet seen by partitioned RP but server enforcement has it -> server blocks old authority;
33. partitioned RP with explicit bounded low-risk allowance -> only scoped allowance;
34. partition expires beyond allowance -> fail closed.

### E. Reclosure / history (8)
35. reclose attempts to delete old invalidation -> reject;
36. reclose omits one contradiction from evidence lineage -> reject;
37. reclose uses same tainted verifier quorum without new authority evidence -> reject;
38. reclose with fresh independent quorum/topology/cutover evidence -> accept new generation;
39. old verdict remains historically verifiable after reclose -> pass;
40. old verdict is mistakenly treated as current after newer generation -> reject;
41. two different reclosures for same generation -> conflict/no completion;
42. newer reclosure generation with valid supersession chain -> current authority updates.

### F. Crash / atomicity / governance (6)
43. invalidation registered but local frontier persistence crashes -> recovery must not silently accept old verdict if durable transparency/frontier evidence shows newer invalidation;
44. local frontier advanced but artifact body missing -> fail closed/re-fetch, never synthesize body;
45. reclosure partially published -> no current completion until complete authenticated artifact set exists;
46. invalidation signer self-authorizes a new policy generation -> reject;
47. governance resolves conflict but historical branches remain archived -> pass;
48. governance resolution rewrites/removes losing branch -> reject.

## 14. Implementation order

When exact executable source becomes available:

1. tests first for monotonic verdict/invalidation generations and cache rollback;
2. tests for key-compromise interval re-appraisal;
3. topology post-close admission + resurrection/DR cases;
4. watch-gap -> UNKNOWN semantics;
5. effective-path contradiction and probe-steering invalidation;
6. reclosure lineage tests;
7. crash/atomicity tests;
8. only then production integration.

Do not implement this design before the earlier LAB-086 exact executable gate if LAB-086 source execution is available; LAB-086 remains priority #1.

## Decision

Freeze the contract:

**`CONVERGENCE_EVIDENCE_REVOCATION_PROPAGATION_POST_COMPLETION_INVALIDATION_CONTINUOUS_ASSURANCE_V1_FROZEN`**.

A convergence close is a current, freshness-bounded authority verdict over a specific evidence/topology frontier — not a permanent certificate. Later authenticated contradictions supersede its current authority without erasing its historical receipt. Reclosure requires a new generation that explicitly consumes and resolves the contradiction history.