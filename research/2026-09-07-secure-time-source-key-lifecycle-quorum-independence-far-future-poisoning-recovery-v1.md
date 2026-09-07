# Secure-time source key lifecycle, quorum independence, and far-future poisoning recovery v1

Date: 2026-09-07
Status: `SECURE_TIME_SOURCE_KEY_LIFECYCLE_QUORUM_INDEPENDENCE_FAR_FUTURE_POISON_RECOVERY_V1_FROZEN`
Scope: LAB-093 design follow-up. This is a design/evidence freeze, not executable LAB-086 proof.

## Question

The previous freshness contract introduced a nondecreasing `TrustedTimeFloorV1`. That creates a new irreversible-looking authority surface: an authenticated but malicious, compromised, miscalibrated, or operationally erroneous time source can push the floor far into the future and make every legitimate current credential/epoch appear expired.

This note defines:

1. authenticated time-source identity and signing/key lifecycle;
2. independence and correlation requirements for multi-source time decisions;
3. recovery from a poisoned far-future time floor without turning recovery into an ordinary rollback primitive.

## Primary-source facts

### Authentication does not prove correctness of time

RFC 5905 explicitly separates authentication from correctness: an authenticated NTP source can still be a falseticker, and NTP uses multiple associations plus selection/agreement logic to choose acceptable sources.

RFC 8915 adds cryptographic identity, packet authentication, replay protection and request/response consistency to NTP. Its security section also states that compromise of the NTS cookie-encryption key permits server impersonation and recommends removing compromised keys and forcing renegotiation.

Therefore `AUTHENTICATED_SOURCE_RESPONSE != CORRECT_TIME`.

### Multiple endpoints are not automatically independent

RFC 8633 recommends multiple time sources and warns that a single anycast address can collapse apparent multiplicity to one effective source. It recommends separate anycast pools where multiple sources are required.

RFC 9523 Khronos models attackers controlling or influencing a fraction of time servers and network paths, including server compromise, ISP/AS-level influence, nation-state jurisdiction, DNS poisoning and BGP hijacking. It deliberately samples across a large pool and trims extremes.

Therefore independence must account for at least operator/control authority, PKI/key custody, network path/AS, DNS/discovery, hosting/provider, jurisdiction, and implementation lineage. Counting hostnames or IPs is insufficient.

### Time-signing compromise needs explicit historical treatment

RFC 3628 requires a TSA to publish compromise/loss-of-calibration information, stop issuing timestamps until recovery, and where possible identify affected tokens. It notes that an audit trail, or timestamps from two different TSAs, may help discriminate genuine from false backdated tokens.

Therefore time-source key status is historical and interval-scoped; `revoked now` does not automatically mean `all historical samples invalid`, while unknown compromise onset cannot be treated as known-safe history.

### Fast-forward poisoning needs an exceptional recovery path

TUF explicitly defines a fast-forward attack in which an attacker arbitrarily increases trusted metadata versions. Its recovery procedure requires trusted key rotation and then discards previously trusted timestamp/snapshot metadata so clients can recover from attacker-inflated version numbers.

This is a useful donor for time-floor poisoning: a monotonic anti-rollback variable can itself be poisoned upward, and recovery requires a higher-order trust transition rather than simply accepting a lower ordinary value.

## Frozen distinctions

```text
AUTHENTICATED_TIME_SAMPLE
!= CORRECT_TIME_SAMPLE
!= INDEPENDENT_TIME_SAMPLE
!= QUORUM_TIME_DECISION
!= TRUSTED_TIME_FLOOR
!= CURRENT_AUTHORITY
```

And:

```text
ROUTINE_TIME_SAMPLE
!= TIME_FLOOR_RECOVERY_AUTHORITY
```

A routine source that was allowed to advance `TrustedTimeFloorV1` must not by itself be allowed to lower or reset that floor.

## Data contracts

### `TimeSourceIdentityV1`

Immutable identity for one authority lineage:

- `source_lineage_id`
- `operator_identity_digest`
- `service_identity`
- `protocol_profile` (e.g. NTS profile / authenticated timestamp profile)
- `key_generation`
- `public_key_or_pkix_anchor_digest`
- `valid_from`
- `valid_until`
- `status_statement_log_lineage`
- declared correlation domains:
  - operator/control domain
  - key-custody domain
  - hosting/provider domain
  - network/AS/path domain
  - DNS/discovery domain
  - jurisdiction domain
  - implementation/build lineage
  - upstream reference-clock lineage where known.

Changing a hostname or certificate under the same effective control domain does not create a new independent source.

### `TimeSourceKeyStatusV1`

Append-only statement:

- source lineage + key generation
- status: `ACTIVE | RETIRED | COMPROMISED | CALIBRATION_LOSS | UNKNOWN_HISTORICAL_TRUST`
- `effective_not_before` when known
- `detected_at`
- evidence/provenance digest
- predecessor statement digest
- governance authorization digest.

Semantics:

- planned retirement after a sample does not retroactively invalidate it;
- known compromise/calibration-loss onset invalidates authority from the effective boundary;
- if only detection time is known and onset is unknown, samples whose safety depends on that key become `UNKNOWN_HISTORICAL_TIME_TRUST`, not silently valid.

### `TimeSourceIndependenceMatrixV1`

For every pair/group of sources record whether they share each correlation domain. A quorum policy is evaluated over independent authority groups, not raw source count.

A policy may state for example:

- at least 3 accepted samples;
- from at least 2 operator/control domains;
- at least 2 key-custody domains;
- at least 2 network/AS path domains where observable;
- no single DNS/discovery or hosting authority may satisfy the whole quorum;
- bounded implementation-lineage concentration.

The exact production thresholds remain policy parameters; the frozen property is that numeric `q-of-n` over correlated endpoints is insufficient.

### `QuorumTimeDecisionV1`

Contains:

- canonical set of accepted `AuthenticatedTimeSampleV1` digests;
- rejected/falseticker samples + reasons;
- independence-matrix digest;
- interval intersection / robust-selection result;
- lower/upper UTC bound, not only a point estimate;
- uncertainty bound;
- policy generation;
- resulting candidate floor;
- complete source-key status frontier used for the decision.

The decision may advance `TrustedTimeFloorV1` only to a conservative bound justified by the quorum, never to an unconstrained single sample timestamp.

## Key rotation contract

Normal source key rotation is continuity-preserving:

1. old trusted source lineage/key authorizes or is linked through the already trusted PKI/governance root to the new generation;
2. the new generation has an explicit activation boundary;
3. source-key status history is append-only;
4. verifiers preserve old public keys/status statements for historical verification;
5. removing old operational private keys does not erase historical verification evidence;
6. compromise rotation publishes both the replacement key and the historical compromise statement.

A new key learned only from the same already-suspect time response cannot self-authorize its own recovery role.

## Far-future poisoning model

Attack/example:

1. trusted floor is 2026-09-07;
2. an otherwise authenticated source/key (or correlated quorum) returns year 2099;
3. implementation accepts it and persists `TrustedTimeFloorV1=2099`;
4. all normal certificates, metadata and activation freshness windows now appear expired;
5. ordinary legitimate 2026 sources cannot lower the floor because anti-rollback semantics correctly reject them.

Blindly allowing a majority of ordinary time samples to lower the floor creates the opposite vulnerability: an attacker can deliberately replay old time and invoke the same mechanism as a rollback primitive.

## `TimeFloorPoisonRecoveryV1`

Recovery is a separate governance/security action, not ordinary synchronization.

Required inputs:

1. the poisoned floor and exact `QuorumTimeDecisionV1` that advanced it;
2. historical source/key status and independence evidence;
3. contradiction evidence showing the accepted floor is outside a policy-bounded plausible interval;
4. a `TimeFloorRecoveryAuthorityV1` signed under a higher-order recovery policy independent of the routine time-source quorum;
5. a conservative replacement lower-bound interval supported by a fresh independent time quorum and/or independently witnessed publication/activation frontiers;
6. an explicit `poisoned_floor_generation -> recovered_floor_generation` transition preserved forever.

The recovery artifact must name:

- affected verifier/time lineage;
- poisoned floor digest/value/generation;
- cause classification (`KEY_COMPROMISE`, `CALIBRATION_LOSS`, `CORRELATED_QUORUM_FAILURE`, `IMPLEMENTATION_BUG`, `OPERATOR_ERROR`, `UNKNOWN`);
- evidence digest;
- replacement trusted-time interval/floor;
- recovery-policy generation;
- approver/quorum identities;
- activation frontier;
- audit/fraud-proof references.

Routine time sources cannot sign this artifact merely by virtue of being routine time sources.

## Recovery safety rules

### 1. No silent lowering

A lower `TrustedTimeFloorV1` is invalid unless accompanied by a valid `TimeFloorPoisonRecoveryV1`. Clock set, VM restore, cache deletion, config edit, database restore, or receipt from ordinary NTS/NTP sources is insufficient.

### 2. Recovery is generation-changing, not history-rewriting

Never rewrite the poisoned record. Persist both the bad accepted decision and the recovery decision. Historical evaluations can then answer what the verifier believed at each generation.

### 3. Recovery authority must be structurally independent

The higher-order recovery quorum must not be fully controlled by the same operator/key/network/discovery domains that satisfied the poisoned routine quorum. Otherwise the attacker that poisoned time can authorize its own rollback/recovery.

### 4. Conservative reset

Recovery sets a new bounded floor from independently corroborated evidence. It does not grant arbitrary wall-clock write authority.

### 5. Revalidation after recovery

All authority decisions made only because of the poisoned future floor are re-evaluated. Recovery does not automatically resurrect credentials/events that were independently revoked, superseded or invalid for non-time reasons.

### 6. Known versus unknown compromise onset

If the time-source key compromise start is known, only samples from/after that boundary are distrusted. If onset is unknown and the poisoned decision depended on that source, mark the historical decision unknown/affected rather than pretending a precise boundary.

## Source quorum independence decision

The high-assurance baseline is not `3 servers`. It is a policy over failure domains.

Minimum recommended architecture for consequential authority freshness:

- multiple authenticated time sources;
- at least two independent operator/control and key-custody domains;
- network-path diversity where practical;
- no one discovery plane or anycast pool counted as independent multiplicity;
- robust interval/trim/selection rejecting outliers rather than averaging all authenticated samples;
- conservative uncertainty propagation;
- source/status transparency and historical key status;
- higher-order poison-recovery authority separate from routine synchronization.

This is a design baseline, not a claim that a particular number of sources mathematically solves Byzantine time.

## Fraud / contradiction proofs

Freeze the following proof classes:

1. `TIME_SOURCE_KEY_EQUIVOCATION_PROVEN`
2. `TIME_SOURCE_STATUS_ROLLBACK_PROVEN`
3. `TIME_SOURCE_CORRELATION_OMISSION_PROVEN`
4. `FALSE_INDEPENDENT_QUORUM_PROVEN`
5. `TIME_SAMPLE_OUTSIDE_DECLARED_UNCERTAINTY_PROVEN`
6. `TIME_FLOOR_FAST_FORWARD_POISON_PROVEN`
7. `UNAUTHORIZED_TIME_FLOOR_LOWERING_PROVEN`
8. `POISON_RECOVERY_SELF_AUTHORIZATION_PROVEN`
9. `RECOVERY_HISTORY_REWRITE_PROVEN`
10. `STALE_TIME_SOURCE_KEY_REACTIVATION_PROVEN`

## RED-first matrix (64 cases)

### Source/key lifecycle
1. valid active key accepted.
2. planned new key before activation rejected.
3. planned old key after retirement rejected for new samples.
4. old key remains historically verifiable before retirement.
5. compromised key after known effective boundary rejected.
6. pre-boundary sample remains valid when compromise onset is proven later.
7. unknown compromise onset yields unknown historical trust.
8. status statement rollback rejected.
9. same-generation conflicting key status => equivocation.
10. new key cannot self-authorize from untrusted time response.
11. expired PKI service cert cannot create new authority sample.
12. cached old key status cannot override newer compromise statement.

### Independence/correlation
13. three hostnames, one operator => not three independent authorities.
14. three anycast addresses terminating same control plane => correlated.
15. separate IPs but one DNS/discovery authority cannot satisfy discovery diversity.
16. separate operators behind same constrained network path record correlation.
17. separate operators + keys + paths satisfy configured independence policy.
18. duplicate source lineage counts once.
19. source alias/certificate rotation does not manufacture new independence.
20. same implementation/build lineage concentration reported.
21. same upstream reference clock concentration reported.
22. independence metadata omission fails closed for high-assurance class.
23. claimed independent sources with proven shared key custody invalidate quorum.
24. quorum remains valid when one nonessential correlated source is removed.

### Robust time decision
25. one far-future authenticated outlier trimmed/rejected.
26. one far-past authenticated outlier trimmed/rejected.
27. accepted intervals have safe intersection.
28. no safe intersection => `TIME_QUORUM_DISAGREEMENT`.
29. uncertainty too large => no consequential freshness decision.
30. simple arithmetic average of poisoned endpoints is forbidden baseline.
31. source replay caught despite valid historical signature.
32. delay-inflated sample widens uncertainty and cannot advance floor past safe bound.
33. candidate floor cannot exceed conservative quorum lower/upper policy bound.
34. wall clock cannot overwrite quorum decision.
35. single authenticated source cannot advance high-assurance floor if policy requires diversity.
36. numeric q-of-n passes but domain policy fails => reject.

### Far-future poison
37. legitimate 2026 -> malicious 2099 single source cannot poison diversified quorum.
38. correlated malicious quorum falsely counted as independent is detected by matrix.
39. accepted 2099 decision persists as evidence after recovery.
40. normal 2026 sample cannot lower 2099 floor.
41. deleting local floor then resyncing is not recovery.
42. VM snapshot rollback is not recovery.
43. local administrator wall-clock reset is not recovery.
44. recovery artifact naming wrong poisoned generation rejected.
45. recovery artifact signed only by poisoned routine source rejected.
46. recovery policy threshold insufficient => no lowering.
47. valid independent recovery artifact permits bounded generation transition.
48. recovered floor cannot be lower than independently supported recovery interval.
49. recovery cannot alter activation/publication monotonic frontiers.
50. credentials independently revoked remain revoked after time recovery.
51. decisions expired only because of poison are re-evaluated, not blindly restored.
52. repeated recovery attempt for already superseded poison generation rejected.

### Crash/replay/governance
53. crash before recovery persistence leaves old floor authoritative.
54. crash after atomic transition replays recovered generation exactly.
55. partial floor/history write fails closed.
56. recovery artifact replay against another verifier lineage rejected.
57. recovery artifact replay against another policy generation rejected.
58. conflicting valid recovery artifacts => governance equivocation/fail closed.
59. recovery-key compromise handled with historical status boundary.
60. stale recovery policy cannot authorize a new lowering.
61. archive retains retired source keys/status for historical proof.
62. source termination preserves public verification/status evidence.
63. source replacement does not reset trusted-time history.
64. audit can reproduce exactly which samples/domains advanced or recovered each floor generation.

## Implementation implication for LAB-093

`TrustedTimeFloorV1` must not be a bare timestamp field. The executable design should persist a generation-linked graph:

`source identity/key status -> authenticated samples -> independence matrix -> quorum decision -> trusted floor generation -> optional poison recovery transition`.

Any destructive or authority-bearing action that depends on freshness must verify the current graph, not merely compare `now >= floor`.

## Donors / provenance

Primary donors researched in this run:

- RFC 8915 — authenticated NTP/NTS identity, replay/request binding, compromised cookie-key handling.
- RFC 5905 — authentication is not equivalent to correct time; multi-source selection/falseticker model.
- RFC 8633 — robust deployments require multiple time sources; single anycast source can defeat apparent diversity.
- RFC 9523 Khronos — adversarial fraction of servers/paths, random multi-source sampling, trimming, panic model.
- RFC 3628 — TSA compromise/calibration-loss publication, suspension, affected-token identification, independent TSA evidence.
- TUF specification — fast-forward poisoning and recovery after trusted version counters have been maliciously advanced.

## Frozen verdict

`SECURE_TIME_SOURCE_KEY_LIFECYCLE_QUORUM_INDEPENDENCE_FAR_FUTURE_POISON_RECOVERY_V1_FROZEN`.

The core safety rule is:

> Routine authenticated time may monotonically advance authority only through an independence-aware bounded quorum decision. Once that monotonic state is poisoned upward, it may be lowered only by an explicit higher-order, independently authorized, append-only recovery generation; ordinary time samples can never serve as their own rollback authority.
