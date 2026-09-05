# Manual reconciliation source-capability revocation / evidence-compromise / verdict-challenge lifecycle V1

Status: `MANUAL_RECONCILIATION_SOURCE_CAPABILITY_REVOCATION_EVIDENCE_COMPROMISE_VERDICT_CHALLENGE_V1_FROZEN`

Date: 2026-09-05

Scope: design contract only; no production behavioral PASS is claimed.

## Objective

Define fail-closed behavior when evidence that previously supported a manual `UNKNOWN` reconciliation verdict later becomes untrustworthy: a source is compromised, its retention/consistency declaration was overstated, provider behavior drifts, a reviewer/authorizer credential is revoked, a sealed artifact is corrupted, or append-only/global provenance continuity is challenged.

This contract extends the frozen canonical case/evidence verifier state machine. It does not authorize a new provider attempt, mutate the historical effect, or erase prior decisions. A challenge changes the current trust interpretation of historical evidence through new append-only objects.

## Non-negotiable invariants

1. **Challenge is append-only.** Historical evidence, assessments, reviews, and verdicts remain addressable and cryptographically verifiable as historical claims.
2. **No resend authority exists.** Challenge, revocation, supersession, re-evaluation, or a new verdict never frees the original application key/provider token and never creates `RETRY`, `MISS`, `RESET`, or `SAFE_TO_RETRY`.
3. **Compromise time matters.** If a source/key compromise time can be independently bounded, evidence before that bound may remain eligible under policy; evidence at/after the bound is ineligible until revalidated. Unknown compromise time is treated conservatively.
4. **Source capability limits evidence.** Revoking or narrowing a source declaration propagates to every current assessment whose predicates depended on the removed capability.
5. **Historical verdict != current trust.** A prior verdict can remain as an immutable historical decision while its current authority status becomes `CHALLENGED`, `SUSPENDED`, or `SUPERSEDED`.
6. **Fail-closed asymmetry.** A challenged `NOT_COMMITTED` can never become implicit permission to resend. A challenged `COMMITTED` preserves the consumed identity and treats the effect as potentially committed until strong contradictory evidence is adjudicated.
7. **Absence never upgrades.** Loss/corruption/revocation of supporting evidence cannot be interpreted as evidence that the external effect did not happen.
8. **Global propagation is mandatory.** Authority-affecting challenge state is parent-linked into LAB-097..100 global provenance and participates in startup/delegation/admission verification.
9. **Ordinary operators cannot erase compromise.** Affected source/reviewer/authorizer credentials cannot self-clear their own challenge.
10. **Security-owner boundary is explicit.** When trust roots, compromise timing, or conflicting authoritative evidence cannot be resolved deterministically, automation stops at a challenge state requiring security-owner adjudication.

## Threat / trigger classes

A challenge MAY be opened only from a typed trigger:

- `SOURCE_CREDENTIAL_COMPROMISE`
- `SOURCE_IMPLEMENTATION_COMPROMISE`
- `SOURCE_CAPABILITY_OVERSTATEMENT`
- `PROVIDER_SEMANTICS_DRIFT`
- `RETENTION_BOUND_INVALIDATED`
- `CONSISTENCY_BOUND_INVALIDATED`
- `SCOPE_COVERAGE_INVALIDATED`
- `SEALED_ARTIFACT_CORRUPTION`
- `EVIDENCE_AUTHENTICATION_FAILURE`
- `REVIEWER_CREDENTIAL_REVOKED`
- `AUTHORIZER_CREDENTIAL_REVOKED`
- `REVIEWER_CONFLICT_OF_INTEREST_DISCOVERED`
- `GLOBAL_PROVENANCE_FORK_OR_ROLLBACK`
- `EXTERNAL_TRANSPARENCY_OR_WITNESS_ALERT`
- `POLICY_BUG_INVALIDATED_PREDICATE`

A generic operator concern is recorded as `UNVERIFIED_ALERT` until it is bound to evidence. `UNVERIFIED_ALERT` may suspend automation under policy but cannot by itself rewrite a verdict.

## Canonical lifecycle objects

All objects use the repository shared canonical V1 encoding/digest rules frozen by the previous reconciliation schema contract.

### `ChallengeNoticeV1`

Required fields:

- `challenge_id`
- `case_id`
- typed trigger
- exact target IDs (`source_capability_id`, `evidence_id`, `assessment_id`, `review_id`, `resolution_id`, credential/key ID, or provenance transition ID)
- discovery timestamp
- alleged/known compromise interval (`not_before`, `not_after`, either may be unknown)
- trigger evidence IDs
- reporter principal/tool identity
- severity
- global provenance parent

Opening a challenge never deletes or mutates a target.

### `CapabilityRevocationV1`

Defines future/current trust change for a source capability:

- exact capability generation
- revocation kind: `FULL`, `PREDICATE_NARROWING`, `TIME_BOUNDED`, `SCOPE_BOUNDED`
- predicates removed or narrowed
- effective compromise interval
- authorizing authority/quorum
- successor capability if any
- reason/evidence references
- global provenance parent

A successor declaration does not retroactively strengthen old observations. Old evidence is re-evaluated only against capability semantics that were valid and independently justified for its observation time.

### `EvidenceIntegrityChallengeV1`

Used when the artifact itself is suspect:

- exact evidence/raw artifact digest
- failure type (`DIGEST_MISMATCH`, `SIGNATURE_INVALID`, `SEAL_UNREADABLE`, `SOURCE_RECORD_RETRACTED`, `CHAIN_BROKEN`, `UNKNOWN`)
- independent verification observations
- disposition (`SUSPEND`, `INVALIDATE_CURRENT_USE`, `RESTORED_FROM_AUTHENTIC_COPY`)
- restoration evidence, if any

A byte-for-byte authentic restored copy may restore availability, but cannot silently clear a source-compromise challenge.

### `CredentialTrustChallengeV1`

For reviewer/authorizer/source credentials:

- credential/key identity
- credential role
- compromise/revocation interval
- independent revocation evidence
- affected signed object IDs
- policy result for pre-compromise objects

Revocation policy MUST distinguish cryptographic validity from authorization validity. A signature may remain cryptographically valid while its authorization weight is withdrawn for a bounded interval.

### `VerdictChallengeAssessmentV1`

Deterministic recomputation over the challenged graph:

- affected object closure digest
- current valid capability/credential generations
- retained-valid evidence IDs
- suspended/invalid evidence IDs
- resulting reconciliation lattice
- prior verdict
- resulting verdict-authority state
- required human/security actions

Allowed verdict-authority state:

`UNCHALLENGED`, `CHALLENGED_PENDING`, `SUSPENDED`, `RECONFIRMED`, `SUPERSEDED`, `SECURITY_OWNER_REQUIRED`.

### `ChallengeResolutionV1`

Closes only the challenge interpretation, not history:

- exact challenge IDs
- exact challenge assessment
- resolution: `RECONFIRM_PRIOR_VERDICT`, `SUPERSEDE_WITH_COMMITTED`, `SUPERSEDE_WITH_NOT_COMMITTED`, `SUPERSEDE_WITH_UNRESOLVED`, `LEAVE_SUSPENDED`
- required review/authorization quorum
- explicit statement that original application key/provider token remain consumed
- global provenance parent

`SUPERSEDE_WITH_NOT_COMMITTED` still cannot create resend authority.

## Dependency / blast-radius graph

The verifier MUST compute challenge propagation as an explicit graph, not by ad-hoc UI flags.

Edges include:

`source capability -> imported evidence -> assessment -> review -> resolution -> case current interpretation`

and

`credential/key -> signed capability/evidence/review/resolution`

and

`global provenance transition -> every authority object anchored beneath it`.

Rules:

- revoking one predicate invalidates only dependent predicates but forces reassessment of every assessment that used it;
- evidence may remain usable for positive claims while losing negative-proof authority, or vice versa, depending on the narrowed capability;
- a revoked reviewer does not automatically invalidate raw evidence, but does invalidate review/quorum predicates that depended on that reviewer;
- a compromised source credential may invalidate evidence authentication even if normalized claims are otherwise plausible;
- global provenance fork/rollback suspends terminal authority for all dependent current interpretations until continuity is re-established under the existing DR/re-root contracts.

## Time-bounded compromise semantics

Time-bounded revocation is permitted only when the bound itself is supported by evidence independent of the compromised authority.

Example rule:

- trusted evidence establishes key compromise occurred no earlier than `T1` and no later than `T2`;
- objects signed before `T1` may remain eligible subject to policy and freshness;
- objects signed in `[T1,T2]` are challenged;
- objects after `T2` are invalid for authorization;
- if no defensible lower bound exists, all objects under that authority generation are challenged.

Sigstore/TUF is a useful donor here: compromise-aware root metadata can revoke key material with compromise timing while preserving verifiability of legitimate earlier signatures. This pattern is adopted conceptually; the repository does not inherit Sigstore trust automatically.

## Asymmetric fail-closed treatment of prior verdicts

### Prior `NOT_COMMITTED`

If any predicate required for the prior `STRONG_NEGATIVE` becomes invalid, the current interpretation immediately loses `NOT_COMMITTED` authority and becomes `CHALLENGED_PENDING` or `SUSPENDED`.

It MUST NOT:

- become a retryable operation;
- free the historical application key/provider token;
- be converted to a fresh attempt under the same effect namespace;
- infer absence from missing/corrupted evidence.

Reconfirmation requires a new assessment with currently trusted strong-negative evidence and the normal resolution quorum.

### Prior `COMMITTED`

If positive evidence is challenged, runtime treats the historical effect conservatively as **potentially committed**. The consumed identity remains locked. Automatic external resend is forbidden.

A new `NOT_COMMITTED` interpretation requires independently authoritative contradictory evidence satisfying the strong-negative contract plus challenge-resolution quorum. If positive and negative authoritative evidence conflict, result is `UNRESOLVED` / security escalation, not convenient selection.

### Prior `UNRESOLVED`

Challenge does not improve authority. It may remove evidence and keep/strengthen `UNRESOLVED`; it cannot become `COMMITTED` or `NOT_COMMITTED` without new currently trusted evidence and normal resolution authority.

## Provider drift semantics

Provider drift is versioned against exact provider/service/operation/API/account/scope/adapter generations.

Detection inputs may include:

- official documentation change;
- safe conformance probe mismatch;
- changed response shape/status semantics;
- observed retention shorter than declared;
- changed normalization/truncation/idempotency scope;
- changed consistency/visibility behavior.

On credible drift:

1. mark affected source capability `DRIFT_SUSPECTED`;
2. block new effects that depend on the affected capability where the provider-capability contract requires it;
3. recompute current manual-case assessments whose evidence strength depended on the drifted property;
4. do not mutate already pinned provider request identities;
5. do not retroactively import improved later semantics into historical evidence.

## Corrupted / missing sealed evidence

A stored digest/provenance record can prove what bytes were previously accepted, but not make unavailable bytes reviewable again.

- authentic backup with exact digest + authenticated storage/provenance continuity may restore availability;
- mismatched bytes are rejected;
- permanent loss appends a disposition/challenge event;
- if a terminal verdict required predicates that can no longer be independently re-verified, current authority may become `SUSPENDED` even though the historical verdict remains immutable;
- loss never becomes negative provider evidence.

## Credential revocation and separation of duties

For reviewer/authorizer compromise:

- affected historical signatures remain in the log;
- policy determines whether pre-compromise approvals remain eligible based on independently bounded compromise time;
- current/new approvals from revoked credentials have zero weight;
- a challenged reviewer/authorizer cannot participate in clearing its own challenge;
- replacement reviewers/authorizers must satisfy the same separation-of-duties/failure-domain requirements as normal resolution;
- if enough independent authority does not remain, state becomes `SECURITY_OWNER_REQUIRED` rather than threshold downgrade.

## Startup, delegation, and effect-admission propagation

Startup/recovery MUST verify the current challenge head in the same global provenance chain as other LAB-097..100 authority transitions.

Fail closed before consequential delegation/admission when any of the following holds:

- a currently relied-upon source capability is challenged and the effect class requires it for safe UNKNOWN recovery;
- a manual `NOT_COMMITTED` verdict used by policy is suspended;
- global provenance challenge state is forked/rolled back/stale;
- challenge assessment requires security-owner adjudication;
- source compromise invalidates the only authoritative reconciliation oracle for in-flight `UNKNOWN` operations.

Unaffected effect classes may continue only if policy dependency closure proves they do not rely on challenged authority.

## Automation boundary

Automation MAY:

- ingest authenticated revocation/drift/monitor alerts;
- construct challenge notices;
- compute dependency closures;
- suspend affected capabilities/verdict authority;
- run deterministic reassessment;
- request new read-only evidence;
- restore exact authenticated evidence bytes from an already trusted backup path.

Automation MUST stop and require security-owner adjudication when:

- compromise time cannot be bounded and the blast radius includes terminal consequential verdicts;
- two authoritative sources conflict irreconcilably;
- the root/provenance authority itself is compromised;
- clearing the challenge would require threshold downgrade or trusting the challenged authority to validate itself;
- re-enabling external effects would constitute a new product/security/business decision.

## Append-only state machine

Derived challenge lifecycle:

`OPEN -> IMPACT_COMPUTED -> SUSPENDED_IF_REQUIRED -> REASSESSED -> REVIEWED -> RESOLVED`

Additional terminal/current states:

- `RECONFIRMED`
- `SUPERSEDED`
- `UNRESOLVED`
- `SECURITY_OWNER_REQUIRED`

Every transition uses expected-head CAS plus the shared global provenance append/recovery protocol. Crash before authoritative append leaves no challenge authority; crash after append is recovered idempotently. A crash may not clear suspension.

## RED-first matrix (64 minimum)

### Challenge identity / triggers (8)
1. valid source-compromise challenge;
2. invalid target object -> reject;
3. unsupported free-form trigger cannot become authority;
4. duplicate challenge idempotent;
5. same evidence challenged for two independent reasons preserves both;
6. challenge object mutation changes digest/rejects;
7. wrong case target -> reject;
8. missing global parent -> fail closed.

### Capability revocation / narrowing (12)
9. full source revocation invalidates dependent current assessments;
10. negative-proof predicate narrowing removes strong-negative eligibility only;
11. positive-only evidence remains usable after negative predicate narrowing;
12. time-bounded revocation before safe cutoff preserves eligible earlier object;
13. unknown compromise start challenges whole generation;
14. successor capability cannot retroactively strengthen old observation;
15. wrong account/region scope revocation does not hit unrelated scope;
16. overstated retention invalidates affected strong negative;
17. overstated consistency invalidates affected strong negative;
18. provider drift marks capability suspect and blocks configured new effects;
19. challenged source cannot self-authorize its revocation clearance;
20. threshold downgrade to clear challenge -> reject.

### Evidence integrity / sealed artifacts (8)
21. raw digest mismatch -> suspend evidence;
22. exact authenticated backup restores availability;
23. backup with same claims/different bytes -> reject;
24. missing raw bytes never becomes absence proof;
25. corrupted artifact used by old verdict triggers reassessment;
26. unavailable advisory evidence does not over-propagate;
27. evidence restoration does not clear independent source compromise;
28. silent deletion detected by provenance/disposition verification.

### Credential / reviewer / authorizer challenge (8)
29. revoked reviewer loses current quorum weight;
30. independently proven pre-compromise review remains eligible under policy;
31. unknown compromise time challenges all approvals from generation;
32. revoked authorizer cannot clear own challenge;
33. replacement quorum with separation of duties reconfirms;
34. insufficient surviving quorum -> security-owner required;
35. cryptographically valid but authorization-revoked signature has zero current weight;
36. conflict-of-interest discovery triggers superseding review path.

### Verdict asymmetry (12)
37. challenged NOT_COMMITTED -> suspended, never retryable;
38. challenged NOT_COMMITTED application key remains consumed;
39. challenged NOT_COMMITTED provider token remains retired;
40. challenged COMMITTED remains potentially committed/fail closed;
41. challenged COMMITTED never auto-resends;
42. new strong negative + proper quorum may supersede COMMITTED only as interpretation;
43. conflicting authoritative positive/negative -> UNRESOLVED;
44. challenged UNRESOLVED cannot improve without new evidence;
45. loss of negative evidence cannot produce NOT_COMMITTED;
46. reconfirmation appends new decision, old verdict remains addressable;
47. supersession cannot mutate original effect identity;
48. no challenge resolution enum grants SEND/RETRY/MISS.

### Startup / crash / provenance / blast radius (12)
49. crash before challenge append -> no authority change;
50. crash after suspension append -> restart preserves suspension;
51. stale challenge-head CAS -> reject;
52. concurrent independent challenges both preserved;
53. global provenance rollback -> startup fail closed;
54. split/forked challenge history -> security-owner required;
55. affected effect class blocked while unrelated dependency-free class can continue;
56. challenged only oracle for in-flight UNKNOWN blocks automatic resend/reconciliation escalation path;
57. replay same reassessment idempotent;
58. challenge-resolution rollback detected;
59. clearing local DB flag without global provenance rejected;
60. startup uses current challenge closure, not only historical resolution row.

### Automation / owner boundary (4)
61. automation may suspend from authenticated compromise alert;
62. automation may not clear root-compromise challenge;
63. irreconcilable authoritative conflict requires security owner;
64. re-enabling consequential external effects after trust discontinuity requires explicit product/security/business authorization where already required by frozen contracts.

## Donors / primary references

- RFC 6962, Certificate Transparency: append-only Merkle history and consistency proofs provide the model for preserving prior evidence while detecting contradictory/forked views; detection does not erase historical entries.
- Sigstore threat model / TUF-root usage: compromise recovery includes key rotation/revocation, threshold/offline root authority, and compromise-time-aware treatment that can preserve legitimate pre-compromise verification while rejecting compromised intervals.
- Sigstore Rekor/transparency model: immutable signed metadata remains auditable; monitor-detected misbehavior is appended/acted on rather than rewritten out of history.
- NIST SP 800-53 / 800-53A AU-family concepts: protect audit information, retain sufficient evidence, assess controls, and separate evidence integrity/availability from authority decisions.

## Audit pass

- No operation in this contract releases the original application key/provider token.
- No challenge or supersession deletes historical evidence or verdicts.
- `NOT_COMMITTED` loses authority immediately when any required strong-negative predicate is revoked; this is intentionally stricter than positive-history handling because the dangerous failure mode is using a weak absence claim to justify replay.
- A challenged `COMMITTED` is conservatively treated as potentially committed, preventing duplicate side effects.
- Time-bounded compromise is accepted only with independent evidence; otherwise blast radius expands conservatively.
- Source capability, evidence integrity, credential authority, and global-provenance compromise remain separate dimensions so one healthy dimension cannot silently compensate for another compromised one.
- Exact RED/GREEN implementation remains blocked on executable source access and is not claimed here.
