# Authoritative latest-generation discovery / anti-freeze dissemination / mirror+witness availability v1

Date: 2026-09-08
Status: `AUTHORITATIVE_LATEST_GENERATION_DISCOVERY_ANTI_FREEZE_MIRROR_WITNESS_AVAILABILITY_V1_FROZEN`
Parent: LAB-093 / #178

## Scope

This note extends the frozen offline catch-up, witness-rotation, compromise/recovery, source-transparency, checkpoint, convergence-evidence, and rebootstrap contracts. It answers a narrower question: after an offline interval, how does a relying party decide whether the authority/witness/quorum state it can validate is also plausibly the latest state, when one mirror may selectively withhold newer generations and trusted time may be weak or unavailable?

This is a design contract only. It is not executable proof and does not supersede LAB-086 priority or any exact RED/GREEN gate.

## Core distinction

The system MUST preserve all of these distinctions:

`VALID_CHAIN != CURRENT_CHAIN != LATEST_CHAIN_KNOWN`

`MIRROR_AVAILABILITY != AUTHORITY_TRUTH`

`WITNESS_CHECKPOINT_FRESHNESS != SEMANTIC_AUTHORITY_TRUTH`

`NO_NEWER_GENERATION_OBSERVED != NO_NEWER_GENERATION_EXISTS`

A valid retained chain proves authorization continuity only up to its terminal generation. It does not prove that the terminal generation is current. A mirror can serve a perfectly valid stale prefix without forging any signature.

Therefore a relying party MUST NOT represent a stale-but-valid chain as current merely because all signatures verify.

## Donor mechanisms and limits

### TUF

TUF explicitly treats withholding as a freeze attack. Clients persist versioned metadata, reject rollback, and reject expired metadata. Root updates are sequential; an outdated client walks N+1 generations rather than jumping to an arbitrary latest root. TUF also acknowledges that a repository-controlling attacker can withhold newer root metadata without compromising root keys; the damage is bounded by expiration of the last metadata known to the client.

Reusable mechanism:
- monotonic retained versions;
- sequential authority update;
- a short-lived freshness role analogous to timestamp metadata;
- expiration as a bound on stale validity;
- multiple mirrors as availability paths, not separate semantic trust roots.

Limit: expiration only gives anti-freeze value if the client has a trustworthy enough notion of time. A single mirror can still withhold until the freshness bound is crossed.

### Uptane

Uptane documents the exact weak-clock failure mode: if time is too far behind, an attacker can freeze/replay old metadata; if no secure clock exists, a signed Time Server can provide time attestations, while clients retain a monotonic previously observed time floor.

Reusable mechanism:
- never accept signed time older than the retained trusted-time frontier for the same authority;
- use independently authenticated time attestations when local secure time is absent;
- treat inability to establish sufficient time freshness as an unknown-currentness state, not as evidence that stale metadata is current.

### RFC 9162 / transparency witnesses

Append-only consistency can prove that checkpoint B extends retained checkpoint A. Independent monitors/witnesses can expose split views or inconsistent histories.

Reusable mechanism:
- relying party retains its own checkpoint frontier;
- independent witnesses advertise/cosign checkpoints;
- same lineage/size (or same logical generation) with different authenticated roots is equivocation;
- a newer independently observed checkpoint proves that an older mirror view is stale.

Limit: append-only consistency does not prove semantic truth, and lack of a newer checkpoint does not prove no newer state exists.

### SCITT

A statement may be registered with multiple independent Transparency Services, producing multiple receipts. This is useful for dissemination/survivability and makes selective suppression harder across independent services.

Limit: receipts prove registration, not semantic authority truth or global latestness.

### NTS / authenticated time

NTS authenticates NTP synchronization using TLS/AEAD. It is useful when the client can validate its authenticated time path. It is not by itself a universal proof that an authority generation is latest, and time-source trust remains separate from authority semantics.

## New objects

### `AuthorityFreshnessStatementV1`

A short-lived, signed statement issued by the currently authorized freshness role:

- `authority_lineage_id`
- `authority_generation`
- `authority_digest`
- `witness_set_generation`
- `quorum_policy_generation`
- `transparency_checkpoint_refs[]`
- `issued_at`
- `not_after`
- `freshness_sequence`
- `predecessor_freshness_digest`
- `issuer_generation`
- `signature`

The freshness role MUST NOT gain authority to alter semantic authority contents. It only attests which already-authenticated generation it considers current at issuance time.

### `DiscoveryObservationV1`

Local, append-only relying-party observation:

- discovery channel identity/control domain;
- observed authority generation/digest;
- observed checkpoint/witness frontier;
- observed authenticated time interval, if any;
- response binding/challenge nonce;
- observation time source class;
- transport/result status.

Observations are evidence for latestness appraisal, not authority statements.

### `TrustedLatestnessFrontierV1`

Persisted crash-safely by the relying party:

- highest authenticated authority generation seen;
- terminal authority digest;
- highest freshness sequence;
- highest witness/checkpoint generations seen;
- highest authenticated time lower bound;
- unresolved higher-generation observations;
- unresolved split-view/conflict evidence;
- discovery policy generation.

Rollback below this frontier MUST fail closed.

### `DiscoveryPolicyV1`

Versioned policy defining:

- minimum independent discovery control domains;
- allowed channels (authority origin, mirrors, transparency logs, witness feeds, out-of-band directory, peer/gossip where applicable);
- secure-time requirements;
- maximum permitted stale interval;
- challenge-response requirements;
- what constitutes a higher-generation hint versus authoritative proof;
- quorum for declaring `LATESTNESS_SUFFICIENT`;
- bounded degraded/offline behavior.

Policy rotation follows the already-frozen predecessor+successor and rollback/equivocation rules.

## Latestness state machine

The relying party MUST expose an explicit state, not a boolean hidden behind signature validation.

### `CURRENT_AUTHORITY_LATESTNESS_PROVEN_WITHIN_BOUND`

Allowed only when:
1. authority chain is valid from retained trust frontier through the candidate terminal generation;
2. all required intermediate generations are reconstructed or covered by an authenticated prefix proof under the frozen catch-up contract;
3. freshness evidence is within policy bound using an acceptable trusted-time mechanism; and
4. required independent discovery channels agree that no higher authenticated generation/checkpoint has been observed, while any higher-generation hints are resolved; and
5. no split-view/equivocation evidence is unresolved.

This is deliberately bounded, not metaphysical proof that no future/new hidden generation exists anywhere.

### `CURRENT_AUTHORITY_LATESTNESS_UNKNOWN`

Required when the chain is valid but currentness cannot be established, including:
- all reachable mirrors return the same valid generation but secure time is unavailable beyond the policy grace bound;
- discovery channels are below independence quorum;
- a mirror/witness channel is unavailable and the policy requires it;
- a higher-generation hint is seen but its authenticated chain cannot be fetched;
- retained freshness statement has expired;
- an offline interval exceeds the maximum no-contact bound;
- current checkpoint can be validated but its recency relative to policy cannot be established.

A stale-but-valid chain may remain useful for forensic/historical verification, but MUST NOT authorize consequential current operations under a policy requiring currentness.

### `CURRENT_AUTHORITY_STALE_PROVEN`

A higher authenticated generation/checkpoint/freshness sequence has been independently observed, but the local candidate is older.

### `CURRENT_AUTHORITY_EQUIVOCATION_CONFLICT`

Same generation/logical frontier with different authenticated digests/roots/policies. Never resolve by newest wall-clock timestamp, first response, last-write-wins, fastest mirror, or majority of replicas under one control domain.

## Discovery independence

Counting endpoints is insufficient. Independent discovery evidence MUST be appraised by control domain.

At minimum, profile fields SHOULD cover:
- operator/administrative domain;
- credential/key custody;
- deployment/cloud/account domain;
- software/build lineage;
- network/egress dependency;
- upstream metadata source;
- transparency/witness governance domain.

Three mirrors behind one CDN account and one origin credential count as one availability/control domain for anti-withholding purposes.

## Anti-freeze dissemination profile

For high-assurance currentness, use heterogeneous dissemination:

1. authority origin/freshness role;
2. at least one independently controlled mirror;
3. transparency checkpoint feed;
4. witness/cosigner feed independent of the transparency operator;
5. optional second transparency service / cross-log registration;
6. authenticated time source or bounded monotonic-time substitute.

No single channel is semantic truth. The goal is to make selective withholding require simultaneous control/isolation across independent paths.

## Challenge-before-response rule

Discovery SHOULD be challenge-bound when practical. The relying party commits or generates an unpredictable nonce before querying channels, and responses bind the nonce, candidate lineage/generation, and checkpoint frontier.

This does not prevent a fully malicious channel from withholding data, but it prevents reuse of a cached response as if it were a fresh interactive observation and makes selective replay evidence explicit.

## Weak or unavailable trusted time

Wall-clock freshness is not silently replaced by signature validity.

### Time classes

`T0_SECURE_LOCAL_CLOCK`
- hardware/OS protected clock with defined rollback resistance.

`T1_AUTHENTICATED_NETWORK_TIME`
- e.g. NTS or equivalent authenticated time, with independently appraised server/control domains.

`T2_SIGNED_TIME_ATTESTATION`
- authority-independent signed rough/time-server attestations with retained monotonic lower bound.

`T3_MONOTONIC_ELAPSED_ONLY`
- reliable elapsed-time counter since a previously trusted instant, but no absolute current wall clock.

`T4_UNTRUSTED_OR_UNKNOWN_TIME`
- no freshness-capable time evidence.

Policy decides which classes are sufficient. `T4` cannot support expiration-based `LATESTNESS_PROVEN_WITHIN_BOUND`.

With T3, the system may maintain a conservative bound only while continuity of the monotonic counter is proven; reboot/reset without protected persistence loses that assurance.

## Mirror rules

- Mirrors cache and distribute authenticated artifacts; they are not authority roles merely because they serve bytes.
- A mirror returning generation g cannot prove that g is latest.
- Failure/404 from one mirror does not prove removal or nonexistence.
- A higher generation advertised by any authenticated independent channel creates an unresolved higher-generation obligation until fetched/validated or cryptographically disproven.
- Mirror-list metadata itself is versioned authority and subject to rollback/freshness checks; an attacker cannot shrink the required discovery denominator by serving an old mirror list.
- Partial mirrors MUST declare scope; absence outside declared scope is not evidence.

## Witness/checkpoint rules

- A newer valid witness checkpoint is sufficient to prove an older checkpoint is stale, subject to membership/key-policy appraisal.
- Lack of a newer witness checkpoint is not sufficient to prove latestness.
- Witness freshness has a policy bound; indefinitely old but valid cosignatures become historical evidence only.
- Same checkpoint generation/size with different root remains equivocation.
- Witness set/key rotation must be reconstructed before counting fresh cosignatures.
- Cross-log anchoring improves survivability and selective-withholding resistance but does not create semantic truth.

## Freshness authority compromise

The freshness role is intentionally less powerful than semantic authority, but compromise can still cause freeze/fast-forward DoS.

Rules:
- freshness generation/key lifecycle is separately versioned;
- freshness role cannot create/authorize semantic authority generations;
- a freshness statement naming a generation whose semantic chain is invalid is rejected;
- a freshness sequence lower than retained is rollback;
- same sequence with different digest is equivocation;
- post-facto freshness-key compromise can invalidate current reliance on freshness observations for the affected interval without deleting historical receipts;
- recovery follows the already-frozen compromise/recovery-root/adjudication contracts.

## Offline catch-up algorithm

Given retained `TrustedLatestnessFrontierV1` F:

1. Load F before network observations.
2. Establish acceptable time class or mark time freshness unavailable.
3. Query required discovery channels with a fresh challenge.
4. Collect higher-generation/checkpoint/freshness hints; do not yet replace F.
5. Reconstruct semantic authority generations sequentially from F.
6. Reconstruct witness-set, quorum-policy, witness-key, compromise/recovery and transparency checkpoint continuity as already frozen.
7. Reject rollback and same-generation conflicts.
8. Verify current freshness statement only after semantic authority and freshness-role authority are current through the candidate generation.
9. Reconcile independent discovery observations and unresolved higher-generation hints.
10. Atomically persist the advanced semantic + latestness frontier before authorizing consequential operations.
11. If any required step is unavailable, return `CURRENT_AUTHORITY_LATESTNESS_UNKNOWN`; retain the old frontier for historical verification but do not silently treat it as current.

## Outage vs selective withholding

Absence cannot generally distinguish benign outage from malicious withholding. The contract therefore avoids pretending it can.

Evidence may upgrade the result:
- independent channel has newer authenticated generation -> stale proven;
- same-generation conflicting digest -> equivocation proven;
- retained freshness deadline exceeded with sufficient trusted time -> freeze/staleness bound violated;
- all channels unavailable -> availability failure, currentness unknown;
- one channel unavailable while independent required channels provide a fresh consistent extension -> ordinary outage may be tolerated if policy quorum remains satisfied.

The safe default is `UNKNOWN`, not an invented adversarial verdict and not current trust.

## Consequential-operation policy

Operations are partitioned by currentness requirement.

`HISTORICAL_VERIFY`
- may operate on valid historical chain even when latestness is unknown, clearly labeled historical.

`READ_NONCONSEQUENTIAL`
- policy may permit bounded stale reads with explicit age/latestness metadata.

`MUTATE_OR_AUTHORIZE`
- requires `CURRENT_AUTHORITY_LATESTNESS_PROVEN_WITHIN_BOUND` under high-assurance profile.

`EMERGENCY_FAIL_CLOSED`
- may be triggered by credible stale/conflict evidence without waiting for global semantic adjudication.

No mutation/authorization path may internally coerce `UNKNOWN` to current.

## Required RED-first matrix

### A. Valid-but-stale / mirror withholding
1. Single mirror serves retained g10 while g11 exists -> must not call g10 latest.
2. Two endpoints same CDN/control domain serve g10 -> still one discovery domain.
3. Independent mirror serves g11 -> g10 becomes `STALE_PROVEN`.
4. Origin g10, witness checkpoint proves g11-related append -> unresolved higher-generation obligation.
5. All mirrors g10, freshness statement expired with secure time -> no current trust.
6. All mirrors g10, no secure time -> `LATESTNESS_UNKNOWN`, not current.
7. Partial mirror omits g11 outside declared scope -> omission not proof.
8. Old signed mirror list hides new independent mirror -> mirror-list rollback rejected.

### B. Time weakness
9. Local clock rolled backward -> expiration cannot be relied upon.
10. NTS/authenticated time advances beyond freshness expiry -> stale bound enforced.
11. One signed time source lies far ahead -> independence/policy prevents unilateral permanent DoS.
12. Signed time lower than retained trusted-time frontier -> rollback rejected.
13. Monotonic counter survives process restart -> bounded elapsed freshness can continue if policy allows.
14. Monotonic counter resets after reboot without protected persistence -> downgrade to unknown.
15. Fresh semantic generation but expired freshness statement -> latestness not proven.
16. Freshness statement valid under untrusted wall clock only -> latestness not proven.

### C. Freshness-role attacks
17. Compromised freshness key points to nonexistent g99 -> semantic-chain validation rejects.
18. Freshness role points to old valid g10 while g11 exists -> independent higher hint prevents current trust.
19. freshness sequence rollback -> reject.
20. same sequence/different digest -> equivocation.
21. freshness key rotated but missing intermediate authority generation -> catch-up incomplete.
22. post-facto freshness-key compromise overlaps prior latestness decision -> current reliance reappraised/invalidation generated.

### D. Witness/checkpoint dissemination
23. retained checkpoint c20, mirror serves c20 forever, independent witness has c21 -> stale proven.
24. c20 and c20' same logical frontier/different roots -> conflict.
25. stale cosignature from retired witness -> historical only.
26. new witness key without reconstructed membership/key rotation -> not counted.
27. three witnesses under one operator -> one control domain for independence.
28. cross-log receipt for old generation only -> survivability evidence, not latestness proof.
29. one transparency service unavailable, second fresh service extends retained statement -> tolerate only if discovery policy quorum remains satisfied.
30. all transparency services unavailable -> currentness unknown after bound.

### E. Offline selective truncation
31. retained g10; attacker serves g13 while omitting g11 compromise/g12 recovery -> sequential catch-up rejects.
32. attacker serves syntactically valid g11 that does not extend retained digest -> reject.
33. higher-generation hint exists but artifact unavailable -> unknown, not fall back to current g10.
34. retained checkpoint chain cannot be connected to downloaded checkpoint -> unknown/conflict as applicable.
35. mirror serves fresh timestamp/freshness metadata but old semantic snapshot -> digest/version binding rejects mix-and-match.
36. stale mirror plus fresh witness quorum naming higher checkpoint -> stale proven.

### F. Availability and denominator manipulation
37. required discovery channel removed by stale policy -> policy rollback rejected.
38. channel timeout -> not proof of malicious withholding.
39. one channel 404, other independent channels fresh -> may proceed only if policy quorum permits.
40. attacker creates many fake mirrors -> no independence inflation.
41. DNS poisoning isolates one mirror set -> heterogeneous discovery prevents counting it as global absence.
42. network partition leaves only one control domain -> latestness unknown after bounded grace.

### G. Crash/atomicity
43. crash after observing g11 but before persisting frontier -> retry may re-fetch, never regress below persisted F.
44. crash after semantic frontier persisted but before latestness frontier -> recovery must conservatively mark latestness unknown until reconciled.
45. crash after higher-generation obligation persisted -> obligation survives restart.
46. torn persistence produces mismatched semantic/latestness frontier -> fail closed and reconcile.
47. old local backup restores lower freshness sequence -> rollback detected from protected frontier/external anchor where available.
48. no protected persistence survives full-device rollback -> lineage freshness falls back to previously frozen external-anchor/rebootstrap semantics; do not claim local anti-rollback.

## Security conclusions

1. Cryptographic validity proves authenticity/authorization of an observed prefix; it does not prove currentness.
2. Anti-freeze requires both a freshness bound and a way to evaluate that bound. Weak time therefore degrades currentness to `UNKNOWN` rather than weakening expiration semantics.
3. Independent dissemination paths and witnesses can positively prove staleness/conflict when they expose a newer or conflicting authenticated view, but silence cannot prove global latestness.
4. The relying party's retained frontier is part of the trust state. Catch-up must chain from it, not from a fresh attacker-selected starting checkpoint.
5. Discovery/mirror/witness evidence must remain separate from semantic authority truth.
6. Consequential mutation/authorization should require bounded latestness assurance; historical verification may continue under explicitly historical semantics.

## Exact implementation follow-up

When exact source execution is available, LAB-093 implementation should begin RED-first with the matrix above, then compose the resulting latestness state into the already-frozen authority/recovery/witness catch-up state machine. Avoid a single `is_current` boolean; preserve provenance and reason-coded `UNKNOWN/STALE/CONFLICT/PROVEN_WITHIN_BOUND` outcomes.

Potential concrete implementation slice:
- immutable `TrustedLatestnessFrontierV1` serialization with crash-safe monotonic update;
- `AuthorityFreshnessStatementV1` verification independent from semantic-authority verification;
- discovery-channel independence appraisal;
- explicit time-class provider interface;
- sequential offline catch-up with unresolved higher-generation obligations;
- regression harness capable of selectively withholding generations per mirror/witness channel.

## Sources

Primary donors consulted in this run:
- The Update Framework Specification, v1.0.26: version rollback rules, expiration/freeze checks, sequential root updates, mirror semantics, and explicit note that repository control can freeze clients by withholding newer root metadata until expiry.
- Uptane Deployment Best Practices 1.2.0: secure-time requirement and replay/freeze behavior when client time is too far behind; signed Time Server recommendation for ECUs without secure clocks.
- RFC 9162, Certificate Transparency Version 2.0: append-only checkpoint/consistency and monitor semantics.
- RFC 9943, SCITT Architecture: signed statements may be registered in multiple Transparency Services with independent receipts; transparency/registration remains distinct from issuer semantic truth.
- RFC 8915, Network Time Security: authenticated NTP synchronization via TLS/AEAD.
