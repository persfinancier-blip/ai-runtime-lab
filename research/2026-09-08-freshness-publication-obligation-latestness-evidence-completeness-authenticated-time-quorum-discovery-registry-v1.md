# Freshness publication obligation, latestness-evidence completeness, authenticated-time quorum, and discovery-registry lifecycle v1

Date: 2026-09-08
Status: `FRESHNESS_PUBLICATION_OBLIGATION_LATESTNESS_EVIDENCE_COMPLETENESS_AUTHENTICATED_TIME_QUORUM_DISCOVERY_REGISTRY_V1_FROZEN`
Scope: design/evidence contract only; **not executable proof** and not a substitute for LAB-086 or LAB-093 RED/GREEN gates.

## Objective

Close the next anti-freeze gap left by the latest-generation discovery contract:

1. define when failure to issue freshness/latestness evidence is itself positively detectable rather than merely silence;
2. prevent a compromised freshness producer from escaping an anti-freeze obligation by never producing the statement that would expose a newer generation;
3. authenticate discovery-channel membership and retirement without denominator laundering;
4. appraise multiple authenticated time sources under disagreement/Byzantine outliers without allowing one bad clock to create either permanent denial of service or stale-current acceptance.

## Primary-source donors

- RFC 9162, Certificate Transparency 2.0: an accepted submission receives an SCT, which is a signed promise to include the entry within the configured Maximum Merge Delay (MMD); after the deadline, a client can test the promise against a later tree and possess signed evidence of misbehavior if inclusion fails. https://www.rfc-editor.org/rfc/rfc9162.html
- TUF specification: version/expiration/rollback/freeze protections make a cryptographically valid stale prefix distinguishable from a current view only when the client has retained trusted metadata and applicable freshness bounds. https://theupdateframework.github.io/specification/latest/
- Uptane deployment best practices: time that is too far behind enables freeze/replay, time too far ahead creates denial of service, and time-source-key compromise can cause either outcome; clients should not accept a time earlier than a previously accepted authenticated time under the same key. https://uptane.org/docs/2.1.0/deployment/best-practices
- RFC 8915, Network Time Security: authenticated NTP protects time synchronization messages and key establishment, but authentication establishes provenance/integrity, not semantic correctness of a compromised time source. https://www.rfc-editor.org/rfc/rfc8915.html
- RFC 8633, NTP Best Current Practices: operators concerned with accurate time should use at least four independent/diverse sources; NTP selection/clustering discards apparent falsetickers, while correlated/common-control sources are not truly independent. https://www.rfc-editor.org/rfc/rfc8633.html
- RFC 5905, NTPv4: selection/clustering uses Byzantine-fault-detection principles to discard presumed falsetickers before combining surviving sources. https://www.rfc-editor.org/rfc/rfc5905.html
- Roughtime protocol: signed responses bind a client nonce to an asserted time interval; chaining requests across independent servers can produce signed evidence of inconsistent time ordering. https://roughtime.googlesource.com/roughtime/+/HEAD/PROTOCOL.md and https://roughtime.googlesource.com/roughtime/

## Fundamental distinctions

Freeze these inequalities:

`VALID_FRESHNESS_STATEMENT != FRESHNESS_PUBLICATION_OBLIGATION != OBLIGATION_FULFILLED`

`NO_FRESHNESS_STATEMENT_OBSERVED != FRESHNESS_OMISSION_PROVEN`

`AUTHENTICATED_TIME != CORRECT_TIME != CONSENSUS_TIME_INTERVAL`

`DISCOVERY_ENDPOINT_COUNT != DISCOVERY_CONTROL_DOMAIN_COUNT`

`DISCOVERY_CHANNEL_SILENCE != CHANNEL_RETIREMENT`

`LATESTNESS_EVIDENCE_AVAILABLE != SEMANTIC_AUTHORITY_CURRENT`

A signed statement can be authentic but stale, malicious, or semantically false. Conversely, absence of a statement is generally not positive evidence of producer misconduct unless an independently retained obligation proves that the statement was required.

## 1. Bounded freshness-publication obligations

### 1.1 `FreshnessPublicationPromiseV1`

A producer may create a bounded, externally auditable promise:

```text
FreshnessPublicationPromiseV1 {
  lineage_id
  producer_authority_generation
  obligation_id
  trigger_class
  trigger_digest
  accepted_at_interval
  publication_deadline_interval
  required_statement_class
  minimum_generation_or_frontier
  discovery_registry_generation
  transparency_log_ids[]
  issuer_control_domain
  signature
}
```

The promise is analogous to an SCT/MMD obligation, but the trigger must be explicit. Examples:

- an authenticated authority transition was admitted;
- a compromise/revocation adjudication was accepted;
- a newer checkpoint/freshness frontier was accepted by the publication service;
- a periodic heartbeat obligation became due under a pre-existing publication schedule.

### 1.2 Positive omission proof

`FRESHNESS_PUBLICATION_OMISSION_PROVEN` requires all of:

1. a valid retained `FreshnessPublicationPromiseV1` or an equally strong independently authenticated periodic obligation;
2. proof that the relevant publication deadline has passed under an admissible time profile;
3. an authenticated checkpoint/view whose coverage extends beyond that deadline/frontier;
4. a verifiable absence of the promised statement from the required publication surface(s), or an explicit refusal/conflicting statement;
5. no authorized supersession/cancellation of the obligation.

This converts a bounded accepted obligation into a falsifiable anti-freeze promise.

### 1.3 Silence before admission remains UNKNOWN

A compromised producer may suppress an event *before* issuing any self-controlled promise. Therefore:

`NO_PROMISE + NO_STATEMENT -> LATESTNESS_EVIDENCE_ISSUANCE_UNKNOWN`

not `NO_NEWER_GENERATION` and not `OMISSION_PROVEN`.

For critical authority transitions, the admission step should be separated from the freshness producer so that the producer cannot both accept the event and erase evidence that it accepted it. Preferred profiles:

- `F0_SELF_ADMISSION_SELF_PUBLICATION` — weakest; proves violations only after a self-issued promise exists;
- `F1_SEPARATE_KEYS_SAME_CONTROL_DOMAIN`;
- `F2_INDEPENDENT_ADMISSION_AND_PUBLICATION`;
- `F3_INDEPENDENT_ADMISSION + TRANSPARENCY + WITNESS` — high assurance.

### 1.4 Periodic publication promises

Periodic statements can bound silence only when the schedule itself is authenticated and retained before the outage. Define:

```text
FreshnessScheduleV1 {
  lineage_id
  schedule_generation
  max_publication_interval
  allowed_jitter
  required_statement_class
  effective_from_frontier
  issuer_authority
  predecessor_digest
  signature
}
```

A schedule cannot be weakened retroactively. A new schedule generation applies prospectively after its authenticated activation frontier.

Missed periodic publication yields `PUBLICATION_LIVENESS_BREACH_PROVEN` if trusted time can prove the bound elapsed. It does **not** by itself prove which authority generation is current. The safe consequence is `CURRENT_AUTHORITY_LATESTNESS_UNKNOWN` or scoped quarantine, not inventing a generation.

## 2. Latestness-evidence issuance completeness

### 2.1 `FreshnessCoverageLedgerV1`

Every checkpoint should commit to:

- active freshness producer generation;
- active discovery registry generation;
- outstanding publication promises;
- fulfilled promise IDs and statement digests;
- expired/unfulfilled promise IDs;
- current schedule generation;
- unresolved issuance gaps;
- time-appraisal profile used for deadline evaluation.

A later checkpoint cannot silently drop an unresolved obligation. Obligation resolution is append-only: `FULFILLED`, `SUPERSEDED_BY_AUTHORIZED_EVENT`, or `BREACH_PROVEN`.

### 2.2 New positive and unknown states

Freeze:

- `LATESTNESS_PUBLICATION_WITHIN_BOUND_PROVEN`
- `LATESTNESS_PUBLICATION_LIVENESS_BREACH_PROVEN`
- `LATESTNESS_EVIDENCE_ISSUANCE_UNKNOWN`
- `LATESTNESS_PUBLICATION_EQUIVOCATION_CONFLICT`

A liveness breach is stronger than silence but weaker than proof of the hidden semantic state. It is evidence that the anti-freeze publication contract failed.

### 2.3 Challenge semantics

A relying party may issue `FreshnessChallengeV1` with a fresh nonce and its retained frontier. The response must bind:

- nonce;
- relying-party retained lineage/generation/checkpoint;
- producer's current observed frontier;
- discovery registry generation;
- time interval used;
- unresolved publication obligations.

A nonce proves response freshness relative to the challenge; it does not prove that the producer disclosed every hidden authority event. Challenge evidence therefore composes with, but does not replace, independent admission/transparency obligations.

## 3. Authenticated discovery registry lifecycle

### 3.1 `DiscoveryRegistryV1`

Discovery sources are a governed denominator, not a list assembled from currently reachable endpoints:

```text
DiscoveryRegistryV1 {
  lineage_id
  registry_generation
  predecessor_digest
  effective_frontier
  members[] {
    logical_channel_id
    role
    control_domain_id
    endpoint_binding
    authority_key_or_verifier_binding
    minimum_freshness_profile
    status
  }
  threshold_or_policy
  signature_set
}
```

Membership is keyed by stable logical channel/control-domain identity; URL/IP/CDN/key rotation is not automatically a new independent member.

### 3.2 Denominator-laundering rules

Freeze:

`ENDPOINT_ROTATION != NEW_INDEPENDENT_CHANNEL`

`CHANNEL_TIMEOUT != CHANNEL_RETIREMENT`

`CHANNEL_KEY_ROTATION != CHANNEL_RETIREMENT`

`MIRROR_DELETE_FROM_CONFIG != AUTHORIZED_REGISTRY_REMOVAL`

Retirement requires an authenticated successor registry generation, predecessor continuity, effective frontier, and explicit retirement reason. For a critical channel with unresolved obligations, retirement additionally requires either final reconciliation or an explicit fail-closed transfer of those obligations to the successor channel.

A registry update that reduces required independent control domains below the active policy threshold must not silently retain the previous high-assurance status; it yields a lower assurance profile or `DISCOVERY_QUORUM_INSUFFICIENT`.

### 3.3 Registry rollback/equivocation

- lower registry generation than retained -> rollback;
- same generation + different digest -> `DISCOVERY_REGISTRY_EQUIVOCATION_CONFLICT`;
- higher generation without predecessor authorization/continuity -> untrusted fork;
- a fresh endpoint presenting an older valid registry cannot override the relying party's retained higher generation.

## 4. Authenticated-time quorum

### 4.1 Time is an interval, not an oracle scalar

Each source yields an authenticated interval:

```text
AuthenticatedTimeObservationV1 {
  logical_time_source_id
  key_generation
  control_domain_id
  request_nonce
  midpoint
  radius_or_uncertainty
  observed_network_bounds
  source_generation
  signature_or_NTS_channel_binding
}
```

Roughtime's midpoint/radius model is a useful donor: reasoning should preserve uncertainty instead of collapsing every observation to an exact timestamp.

### 4.2 Independence first

Several endpoints count as one fault domain if compromise of one shared credential, operator, cloud account, signing service, upstream reference, or implementation can coherently control them.

For high assurance, use at least four independent/diverse sources where practical, following RFC 8633's operational recommendation. The policy should specify both:

- minimum independent control domains;
- maximum tolerated Byzantine/outlier domains.

### 4.3 Quorum appraisal

Define `AuthenticatedTimeQuorumPolicyV1` with versioned membership/policy. A safe appraisal:

1. verify each source identity/key generation and nonce freshness;
2. reject rollback relative to the last accepted per-source frontier where monotonic semantics apply;
3. group observations by independent control domain;
4. form source intervals including declared/protocol/network uncertainty;
5. apply an intersection/clustering rule that can discard bounded outliers;
6. require the surviving independent-domain count to meet policy threshold;
7. persist the resulting consensus interval and source set.

Output states:

- `TIME_QUORUM_INTERVAL_PROVEN`
- `TIME_QUORUM_DISAGREEMENT_UNKNOWN`
- `TIME_QUORUM_INSUFFICIENT`
- `TIME_SOURCE_ROLLBACK_PROVEN`
- `TIME_SOURCE_EQUIVOCATION_CONFLICT`

Do **not** choose the median timestamp and discard uncertainty as a general security rule. The correctness object is a bounded interval supported by enough independent domains.

### 4.4 Fail-safe behavior under disagreement

A single far-future time source must not expire all metadata globally if the quorum rejects it. A single far-past source must not make stale metadata current if the quorum rejects it.

If no valid quorum interval exists:

`TIME_QUORUM_DISAGREEMENT_UNKNOWN -> CURRENT_AUTHORITY_LATESTNESS_UNKNOWN`

for operations whose safety depends on expiration/deadline evaluation.

This can cause scoped fail-closed unavailability, but prevents one clock from choosing between stale acceptance and global expiry. Availability-sensitive read-only operations may use a separately defined degraded policy; consequential authorization/mutation must not coerce `UNKNOWN` into current.

### 4.5 Time-key lifecycle

Time-source keys and membership are versioned authority state. Key rotation must bind predecessor/successor continuity. Post-facto compromise triggers re-appraisal of deadlines/freshness decisions whose proof depended on the compromised source during the affected interval.

Historical time receipts remain history; current reliance may be invalidated without rewriting those receipts.

## 5. Composition rules

### Rule A — MMD-like obligations require independent acceptance evidence

A self-issued publication promise is valuable once retained, but cannot prove events the same compromised producer suppressed before promise issuance. Critical semantic transitions should obtain an independent admission receipt before relying on bounded publication.

### Rule B — publication breach is not semantic latestness

`PUBLICATION_LIVENESS_BREACH_PROVEN` proves that the publication contract failed. It does not reveal whether the hidden state is g+1, compromise, recovery, or no semantic transition at all.

### Rule C — registry defines the denominator

Current reachability cannot define the required discovery set. Membership and retirement are authenticated, monotonic governance events.

### Rule D — time provenance is not time correctness

NTS/signatures authenticate who said the time and protect transport/integrity. Byzantine/outlier appraisal across independent domains is still required when one source compromise would have consequential effect.

### Rule E — weak time degrades latestness, not signature validity

When deadline/expiration cannot be safely evaluated, preserve cryptographic validity as historical evidence but classify current latestness as unknown.

### Rule F — retained frontiers dominate attacker-selected fresh starts

Catch-up begins from the relying party's retained authority, registry, time-source, publication-obligation, and transparency frontiers. A server cannot erase a missed interval by presenting a new internally valid bundle.

## 6. Fraud / contradiction classes

1. `FRESHNESS_PROMISE_OMISSION_AFTER_DEADLINE`
2. `FRESHNESS_PROMISE_EQUIVOCATION`
3. `FRESHNESS_SCHEDULE_RETROACTIVE_WEAKENING`
4. `FRESHNESS_OBLIGATION_SILENT_DROP`
5. `DISCOVERY_REGISTRY_ROLLBACK`
6. `DISCOVERY_REGISTRY_EQUIVOCATION`
7. `DISCOVERY_DENOMINATOR_LAUNDERING`
8. `DISCOVERY_CONTROL_DOMAIN_SYBIL`
9. `DISCOVERY_UNAUTHORIZED_RETIREMENT`
10. `TIME_SOURCE_ROLLBACK`
11. `TIME_SOURCE_EQUIVOCATION`
12. `TIME_CONTROL_DOMAIN_SYBIL`
13. `TIME_FAR_FUTURE_DOS_ATTEMPT`
14. `TIME_FAR_PAST_FREEZE_ATTEMPT`
15. `TIME_QUORUM_SELECTIVE_SUPPRESSION`
16. `POST_FACTO_TIME_KEY_COMPROMISE_RELIANCE_INVALIDATION`

## 7. RED-first matrix (48 cases)

### Freshness publication obligations — 1..12
1. accepted promise + inclusion before deadline;
2. accepted promise + no publication after proven deadline;
3. promise exists but deadline not yet provably passed;
4. no promise, no statement;
5. self-admission suppressed before self-promise;
6. independent admission exists but producer emits no promise;
7. promise silently omitted from later coverage ledger;
8. obligation explicitly superseded by authorized successor;
9. retroactively relaxed schedule;
10. periodic heartbeat missed under trusted time;
11. heartbeat missed under unknown time;
12. same obligation ID with conflicting digests.

### Discovery registry — 13..24
13. endpoint/key rotation preserving logical channel identity;
14. endpoint timeout treated incorrectly as retirement;
15. authorized retirement after final reconciliation;
16. retirement with unresolved obligation;
17. lower registry generation replay;
18. same-generation conflicting membership;
19. three endpoints under one control domain counted as three;
20. independent mirror addition;
21. threshold silently reduced below previous assurance;
22. offline verifier presented only newest registry without chain;
23. removed channel later resurrects with old key;
24. registry update and publication promise crash between commits.

### Authenticated time — 25..40
25. four diverse agreeing authenticated sources;
26. one far-future outlier among four;
27. one far-past outlier among four;
28. two-vs-two incompatible interval split;
29. only two sources available below high-assurance threshold;
30. four endpoints sharing one signer/control domain;
31. NTS-authenticated but semantically wrong compromised source;
32. Roughtime nonce replay attempt;
33. time source returns interval not containing quorum interval;
34. per-source authenticated time rollback;
35. same source generation returns incompatible signed intervals for equivalent ordering;
36. time-key rotation with predecessor/successor continuity;
37. unchained new time key;
38. post-facto compromise covers prior deadline decision;
39. trusted local secure clock + external sources disagree;
40. unknown local time + no external quorum.

### Composition / offline catch-up — 41..48
41. hidden g11 compromise, visible g12 recovery, publication obligations preserved;
42. attacker gives fresh registry but omits missed promise breach;
43. newer witness checkpoint positively proves mirror stale;
44. all mirrors silent with no outstanding bounded obligation;
45. challenge nonce is fresh but producer suppresses pre-admission event;
46. publication breach + time quorum later repaired;
47. crash persists statement but not obligation resolution atomically;
48. recovery after time-source and freshness-producer compromise requires re-appraisal from retained frontier.

## 8. Acceptance semantics for eventual implementation

A production implementation of this contract is not GREEN until tests show:

- promise creation and admission are atomic or safely reconcilable;
- no unresolved promise can disappear from future checkpoints;
- registry generation/membership is monotonic and conflict-detecting;
- channel independence is evaluated by control domain, not endpoint count;
- time observations are nonce-bound/authenticated and represented as intervals;
- one bounded outlier cannot force stale-current acceptance or global expiry under a quorum policy that should tolerate it;
- no-quorum time yields explicit UNKNOWN for consequential latestness decisions;
- post-facto compromise reopens current reliance without rewriting historical receipts;
- offline catch-up starts from retained trusted frontiers and cannot skip hidden intermediate obligations/generations.

## 9. Decision

Freeze `FRESHNESS_PUBLICATION_OBLIGATION_LATESTNESS_EVIDENCE_COMPLETENESS_AUTHENTICATED_TIME_QUORUM_DISCOVERY_REGISTRY_V1_FROZEN`.

The key result is deliberately asymmetric:

- **after an independently provable accepted obligation**, bounded non-publication can become positive, signed/auditable misbehavior evidence in the CT/MMD style;
- **before such an obligation exists**, producer silence remains `UNKNOWN` and cannot be upgraded into proof that no newer state exists;
- **authenticated time** is necessary but not sufficient: high-impact freshness decisions require an independently governed, outlier-tolerant time quorum/interval or a secure local time basis;
- **discovery membership** is itself authority state, so endpoint disappearance cannot shrink the anti-freeze denominator without an authenticated lifecycle transition.

No executable LAB-093 or LAB-086 success is claimed by this research freeze.