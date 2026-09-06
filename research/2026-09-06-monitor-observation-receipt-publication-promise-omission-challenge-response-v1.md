# Monitor observation receipt / publication promise / omission challenge-response — v1 frozen

Status: `MONITOR_OBSERVATION_RECEIPT_PUBLICATION_PROMISE_OMISSION_CHALLENGE_RESPONSE_V1_FROZEN`

Date: 2026-09-06

Scope: LAB-093 trust-frontier/monitoring follow-up. Design and RED contract only; no production monitor network, prover, or behavioral PASS is claimed.

## Problem

The prior monitor-completeness contract distinguishes stale, suspected omission, proven omission, and fork states, but leaves one dangerous gap: a timeout or missing response is not itself cryptographic evidence that a log or monitor violated a publication obligation. Network partition, challenger failure, clock skew, cache lag, or ordinary service loss can produce the same symptom.

Conversely, if a log has made an authenticated publication promise, or a monitor has already acknowledged a newer frontier, the system needs a replay-resistant transcript that can turn a missed deadline or selective stale response into durable evidence rather than an unauditable operational suspicion.

This contract freezes that boundary.

## Primary donor mechanisms

### RFC 9162 — Certificate Transparency v2

RFC 9162 models an SCT as a log promise to incorporate an accepted item within a configured Maximum Merge Delay (MMD). An auditor can later test that promise against a sufficiently new signed tree head and inclusion proof. It also treats failure to incorporate promised entries and inconsistent views as log misbehavior.

Donor mechanism: omission becomes externally checkable only when a prior authenticated promise and a later authenticated frontier/proof can be compared under a declared deadline.

Reference: https://www.rfc-editor.org/rfc/rfc9162.html

### C2SP transparency-log checkpoint / witness model

Checkpoint/witness mechanisms provide authenticated, persistable frontier statements suitable for independent comparison across time and channels. A witness that has persisted and cosigned a newer checkpoint has stronger evidentiary significance than a party that merely fails to answer later.

Donor mechanism: previously held authenticated state is the basis for proving stale serving or contradictory selective responses; silence alone is not.

References:
- https://c2sp.org/tlog-checkpoint
- https://c2sp.org/tlog-witness

## Frozen decisions

### 1. Publication promise is a signed capability statement

A `publication_promise` is content-addressed and signed by the authority that owns the relevant publication obligation. It binds at least:

- `promise_generation`;
- log/origin generation and public-key identity;
- subject class (`accepted_entry`, `frontier_advance`, `checkpoint_refresh`, `monitor_observation`);
- exact subject digest or event identifier;
- predecessor/frontier checkpoint digest known at promise issuance;
- not-before / deadline semantics and allowed skew;
- time-source generation;
- required publication surface/channel classes;
- policy generation;
- nonce/sequence domain;
- signature algorithm/key generation.

Unsigned configuration saying “publish every N minutes” is policy input, not proof that a particular obligation was accepted.

### 2. Promise acceptance must be externally durable

A consequential promise counts only after the requester holds the signed promise bytes or another independently retrievable immutable commitment to those exact bytes.

A server-side database row that the accused operator can later rewrite/delete is insufficient by itself.

### 3. Observation receipt proves what was served, not global truth

An `observation_receipt` binds:

- monitor generation;
- challenged log/origin generation;
- challenge id and requester generation;
- requested baseline/frontier digest;
- response checkpoint digest/size/sequence;
- consistency/inclusion proof digests when supplied;
- response classification (`CURRENT`, `OLDER`, `NO_ADVANCE`, `UNAVAILABLE`, `REJECTED`);
- observation time/time-source generation;
- channel/endpoint generation;
- policy generation;
- monitor signature.

A valid receipt proves that this monitor served/observed this state for this challenge. It does not prove that no newer state existed elsewhere.

### 4. Challenges are nonce-bound and replay-resistant

Every challenge contains a cryptographically random or deterministic-domain-separated challenge id plus requester generation, target generation, retained baseline checkpoint, requested proof class, issue time, expiry, and policy generation.

Responses must bind the entire challenge digest. A receipt from another challenge, another origin, an old policy generation, or an expired window cannot satisfy the obligation.

Challenge identifiers are single-use for verdict authority even if transport retries are idempotent.

### 5. A timeout is evidence of non-response, not omission proof

A locally observed timeout may advance `CURRENT/DELAY_PENDING -> STALE` or contribute to `OMISSION_SUSPECTED`, but it cannot alone create `OMISSION_PROVEN`.

Timeout evidence must preserve requester-side send/receive records and authenticated time-source context, but remains diagnostic unless paired with stronger signed/previously-held evidence.

### 6. `STALE -> OMISSION_SUSPECTED`

At least one of the following is required:

- an eligible independent archive/mirror/witness channel presents a newer authenticated checkpoint consistent with the retained baseline while the challenged path remains stale beyond policy;
- a previously held signed publication promise reaches its deadline and no required publication is observable on the promised independent publication surfaces;
- another challenger in an independent control/network domain receives a newer authenticated checkpoint during an overlapping challenge window while this challenger receives only the older frontier.

This state still allows benign partition as an explanation; consequential authority degrades fail-closed.

### 7. `OMISSION_SUSPECTED -> OMISSION_PROVEN`

`OMISSION_PROVEN` requires durable evidence of a violated authenticated statement, not inference from silence. Sufficient proof classes include:

1. **promise violation** — a signed promise for subject X with deadline D plus an authenticated post-D checkpoint from the same log proving X was still absent, where inclusion/completeness semantics make that absence verifiable;
2. **stale-after-knowledge** — the monitor/log previously signed or cosigned checkpoint C_new, then later signed an observation receipt serving C_old where C_old is a strict ancestor of C_new and policy forbids downgrade;
3. **selective contradictory service** — two valid challenge-bound receipts from the same authority for overlapping policy windows that cannot both satisfy its declared monotonic serving contract;
4. **acknowledged-storage omission** — a mirror/archive authority previously signed that it retained C_new/content, then signs a challenge receipt claiming only an older state without an authorized rollback/recovery event.

Simple HTTP 404/timeout, unsigned logs, dashboard screenshots, or third-party allegations are never sufficient alone.

### 8. Selective answering must produce comparable transcripts

Challenge policy defines canonical request classes and response envelopes. Authorities cannot evade comparison by returning semantically incomparable formats to different challengers.

For a given origin/policy generation and challenge class, the receipt commits to normalized response semantics and exact underlying artifact digests. Optional fields cannot hide a newer checkpoint.

### 9. Challenge requester identity is scoped, not privileged truth

Requester generations are authenticated so transcripts cannot be fabricated, but requester signatures do not make requester clocks or network claims authoritative.

Policies may require challenger diversity. Multiple requesters sharing operator, transport, DNS/CDN, clock, or collector control collapse into one failure domain for omission inference.

### 10. Clock manipulation fails closed

Deadlines use a versioned time-source policy. Evidence records both wall time and monotonic/process epoch where available.

If required skew bounds cannot be established, the verdict does not advance to `OMISSION_PROVEN` merely because a local clock says the deadline passed. Clock uncertainty can degrade freshness authority.

### 11. Previously held evidence outranks a later downgrade

If a process has already durably retained C_new or a signed receipt/promise committing to C_new, restart, cache eviction, archive restore, or endpoint migration cannot make C_old authoritative again without a verified recovery event consistent with the global frontier.

Challenge state and receipts are append-only evidence. Recovery does not delete the transcript that triggered suspicion/proof.

### 12. Challenge flooding cannot weaken authority

Rate limiting may reject challenges, but the rejection itself must be authenticated when it affects consequential monitoring coverage. Exhaustion does not auto-relax monitor thresholds or extend deadlines silently.

A challenge mechanism is not allowed to become an unauthenticated DoS oracle that forces `OMISSION_PROVEN`; repeated unavailable/rejected responses degrade coverage but remain distinct from cryptographic proof of omission.

## Canonical transcript

A proof bundle contains at least:

- exact policy and promise generations;
- retained baseline checkpoint;
- publication promise bytes/digest/signature if one exists;
- challenge bytes/digest/requester generation;
- delivery/send record and time-source generation;
- observation receipt or authenticated rejection;
- returned checkpoint/proof artifact digests;
- independent witness/mirror/archive observations;
- diversity-domain classification;
- deadline/skew calculation;
- state transition and reason code;
- all evidence needed for an independent verifier to reproduce `STALE`, `OMISSION_SUSPECTED`, or `OMISSION_PROVEN` without querying mutable current configuration.

## Fail-closed state machine

`CURRENT -> DELAY_PENDING -> STALE -> OMISSION_SUSPECTED -> OMISSION_PROVEN`

`FORK` is orthogonal and takes precedence when incompatible authenticated checkpoints are observed.

Transitions may skip forward only when stronger evidence directly satisfies the later state's proof rule. Recovery can return a monitor to current eligibility only after consistent catch-up and required re-admission; it does not erase historical omission evidence.

## 80-case RED-first matrix

### A. Publication promise identity / binding (1–10)
1. unsigned promise rejected;
2. wrong origin generation rejected;
3. wrong policy generation rejected;
4. altered deadline invalidates signature;
5. altered subject digest invalidates promise;
6. promise key rotation with stale key rejected;
7. duplicate promise id with different bytes => conflict;
8. mutable server-only promise row is insufficient;
9. promise lacking skew/time-source semantics fails consequential use;
10. promise for checkpoint refresh cannot satisfy accepted-entry obligation.

### B. Challenge replay resistance (11–20)
11. receipt for different challenge id rejected;
12. receipt for different requester rejected;
13. receipt for different origin rejected;
14. expired challenge rejected for current liveness;
15. replayed old receipt cannot satisfy new window;
16. transport retry with same challenge is idempotent but counts once;
17. response not binding baseline rejected;
18. response not binding policy generation rejected;
19. challenge nonce collision across domains rejected;
20. fabricated requester signature rejected.

### C. Observation receipt semantics (21–30)
21. unsigned receipt rejected;
22. wrong monitor generation rejected;
23. altered checkpoint digest rejected;
24. `CURRENT` receipt with older-than-baseline checkpoint rejected;
25. `NO_ADVANCE` with hidden returned newer artifact rejected;
26. malformed consistency proof fails receipt authority;
27. receipt with incomparable response schema rejected;
28. optional metadata cannot substitute checkpoint digest;
29. duplicate URL receipts from same monitor count once;
30. receipt from revoked/quarantined monitor excluded.

### D. Timeout / stale boundary (31–40)
31. one local timeout never proves omission;
32. pre-deadline timeout remains `DELAY_PENDING`;
33. post-deadline silence may become `STALE`;
34. unauthenticated dashboard heartbeat does not cure stale state;
35. local DNS failure does not prove remote omission;
36. challenger crash cannot fabricate timeout proof;
37. restarted requester preserves prior challenge transcript;
38. unknown clock skew blocks proven-deadline transition;
39. rate-limit rejection degrades coverage but is not omission proof;
40. missing optional monitor does not affect required threshold.

### E. Upgrade to `OMISSION_SUSPECTED` (41–50)
41. newer valid mirror checkpoint + stale origin => suspected;
42. newer archive checkpoint must be ancestry-valid;
43. newer checkpoint from revoked witness is insufficient;
44. same-control mirror/origin do not provide diversity alone;
45. independent challenger receives newer overlapping receipt => suspected;
46. non-overlapping stale historical receipt is insufficient;
47. signed promise passes deadline with no visible fulfillment => suspected at minimum;
48. unsigned publication schedule is insufficient promise evidence;
49. forged archive checkpoint rejected;
50. cache-stale path plus current independent path degrades only affected path.

### F. Upgrade to `OMISSION_PROVEN` (51–60)
51. timeout alone cannot prove omission;
52. signed promise + valid post-deadline absence proof can prove violation;
53. promise without verifiable absence semantics cannot prove violation;
54. prior signed C_new then later signed C_old downgrade proves stale-after-knowledge;
55. unsigned prior observation does not prove knowledge;
56. contradictory overlapping challenge receipts prove selective violation when contract is monotonic;
57. incomparable policy generations require explicit migration analysis, not automatic proof;
58. mirror retention acknowledgement + later authenticated rollback without recovery evidence proves violation;
59. authorized recovery event prevents false omission proof when policy permits rollback;
60. fork evidence routes to `FORK`, not omission classification.

### G. Clock / partition / selective service (61–70)
61. forward clock jump cannot manufacture deadline violation;
62. backward clock jump cannot restore expired authority;
63. challenger partition + healthy independent channels => stale challenger, not proven omission;
64. all challengers behind one partition collapse to one domain;
65. server selectively answers by IP with different monotonic receipts => comparable contradiction detected;
66. CDN cache returns old checkpoint after origin signed new checkpoint => affected channel flagged; origin blame requires authority binding;
67. endpoint migration cannot discard retained baseline;
68. challenge response from wrong network/channel class cannot satisfy required class;
69. forged liveness telemetry rejected;
70. telemetry collector common-mode collapse enforced.

### H. Restart / recovery / auditability (71–80)
71. restart retains unresolved suspicion;
72. archive restore cannot lower retained checkpoint;
73. resolved omission transcript remains durable;
74. catch-up requires consistency from retained/global frontier;
75. compromised monitor requires new generation/re-admission;
76. old receipt after key revocation cannot regain current eligibility;
77. proof bundle missing promise/challenge bytes fails independent adjudication;
78. independent verifier recomputes same state transition from bundle;
79. disagreement between verifiers fails closed for consequential admission;
80. thresholds never auto-relax because challenge service is unavailable.

## Integration constraints

- Compose with the frozen trust-frontier witness/split-view and monitor-completeness contracts; do not create a parallel local authority island.
- Historical proof bundles remain bound to their original policy/time-source/key generations.
- Omission evidence is not a substitute for fork evidence, and vice versa.
- No production activation until executable RED fixtures demonstrate that silence alone cannot become `OMISSION_PROVEN` and that signed stale-after-knowledge/selective-service cases do.

## Result

Frozen design contract only. The key safety boundary is explicit: **absence of a response can degrade trust, but proven omission requires a prior authenticated obligation or previously held authenticated knowledge plus contradictory post-condition evidence.**
