# Freshness obligation authority lifecycle / atomic admission-publication / omission-proof transparency / time common-mode provenance v1

Date: 2026-09-08
Status: FROZEN DESIGN CONTRACT; executable RED/GREEN still required
Issue family: LAB-093/#178

## Why this exists

The previous contract established that silence is `UNKNOWN` unless an independently retained bounded publication obligation exists. Four unresolved authority questions remained:

1. who may issue/cancel/supersede `FreshnessPublicationPromiseV1`;
2. how an accepted event survives a crash/partition between admission and promise creation without becoming an unprovable omission;
3. how omission evidence itself avoids selective suppression;
4. how time-source quorum independence is proved when nominally distinct clocks share upstreams, signers, operators, firmware, cloud accounts, or reference clocks.

This note freezes those boundaries. It is not executable evidence.

## Primary donors

- RFC 9162 Certificate Transparency v2: accepted submissions receive an SCT; the SCT is a signed promise to append within Maximum Merge Delay; failure can leave signed proof of log misbehavior. https://www.rfc-editor.org/rfc/rfc9162.html
- SCITT architecture draft: Issuer/Signed Statement and Transparency Service/Receipt are separate roles; registration produces independently verifiable inclusion evidence. https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/
- RFC 8633 NTP BCP: systems needing accurate time should use at least four independent, diverse sources; nominal multiplicity is insufficient when sources share common elements/vendor/firmware/reference paths. https://www.rfc-editor.org/rfc/rfc8633.html
- RFC 5905 NTPv4: selection/clustering algorithms reject falsetickers and reason over concurrent sources rather than trusting one clock. https://www.rfc-editor.org/rfc/rfc5905.html
- Roughtime protocol: nonce-bound signed responses return midpoint + radius intervals; long-term identity can delegate to bounded online keys. https://roughtime.googlesource.com/roughtime/+/HEAD/PROTOCOL.md

## Frozen invariant 1 — promise authority is separate lifecycle state

`VALID_PROMISE_SIGNATURE != CURRENT_PROMISE_AUTHORITY != VALID_CANCELLATION != VALID_SUPERSESSION`.

Define `FreshnessObligationAuthorityV1` with:

- `authority_lineage_id`;
- monotonic `generation`;
- threshold policy;
- key/control-domain membership;
- validity interval / freshness bound;
- predecessor digest;
- allowed operation classes: `ISSUE`, `SUPERSEDE`, `CANCEL_FOR_CAUSE`, `ROTATE`.

A producer that is the subject of the freshness claim MUST NOT acquire unilateral power to erase an already-issued obligation.

### Cancellation rule

An accepted, externally retained promise is append-only historical evidence. It is never deleted or rewritten.

Cancellation can only create a new `FreshnessPublicationDispositionV1` that references the exact prior promise and one of a closed set of reasons:

- `SUPERSEDED_BY_NEWER_BOUND`;
- `SUBMISSION_WITHDRAWN_BEFORE_ACCEPTANCE`;
- `AUTHORITY_COMPROMISE_REAPPRAISAL`;
- `ADMINISTRATIVE_ERROR_PROVEN`.

`CANCELLED` does not mean “the old promise never existed”. It means current appraisal follows the authenticated disposition chain.

No retroactive cancellation may convert an already-missed deadline into compliant publication unless the cancellation itself was authorized and committed before the original deadline or there is independently authenticated evidence that the original obligation was invalid ab initio.

## Frozen invariant 2 — admission and obligation creation are one durable logical transition

The dangerous state is:

`EVENT_ACCEPTED && NO_INDEPENDENTLY_RETAINED_PROMISE`.

That state MUST NOT be externally acknowledged as accepted.

Define an admission protocol with an internal durable journal:

1. receive canonical event `E`;
2. allocate monotonic `admission_id`;
3. transactionally persist `AdmissionRecord(E_digest, admission_id, state=PREPARED)` plus the exact promise payload/digest;
4. obtain required promise-authority signature(s);
5. durably persist the signed promise and change admission state to `COMMITTED` in the same recoverable logical transition;
6. only then return external `ACCEPTED + promise`;
7. asynchronously publish/log the event before deadline.

If step 4/5 cannot complete, the caller receives `UNKNOWN/NOT_ACCEPTED`, never a success acknowledgment.

### Crash semantics

- crash after PREPARED, before signed promise: recovery either completes signing/commit or aborts; no external accepted claim exists;
- signed promise exists but admission COMMITTED marker lost: retained signed promise wins as a positive obligation; recovery must reconstruct/commit, never silently discard;
- COMMITTED admission exists but promise bytes are missing: `ADMISSION_PROMISE_ATOMICITY_VIOLATION_FAIL_CLOSED`;
- external ACCEPTED response without independently recoverable committed promise is forbidden.

For remote promise authorities where one ACID transaction is impossible, use a recoverable two-party protocol with idempotent `admission_id` and a signed prepare/commit receipt. Exactly-once is not assumed; duplicate delivery is reconciled by canonical identity.

## Frozen invariant 3 — promise supersession cannot launder a deadline

A newer promise MAY tighten or extend a deadline only under an authenticated policy that was already in force when the older promise was issued.

Default safe rule:

`effective_deadline = min(all still-applicable independently retained deadlines)`.

A later issuer cannot repeatedly supersede a nearly-expired promise with a later deadline unless the original promise explicitly bound that renewal mechanism and its maximum extension.

Otherwise the system admits an infinite anti-accountability loop.

## Frozen invariant 4 — omission proof has its own transparency path

A publisher that violated an obligation must not be able to hide the resulting proof merely by suppressing monitor output.

Define `FreshnessOmissionEvidenceV1` containing:

- exact promise digest;
- canonical event/admission identity;
- deadline and time-evidence set;
- post-deadline checkpoint/view digests;
- negative/inclusion-query evidence as applicable;
- monitor identity/generation;
- appraisal policy generation;
- evidence creation time interval;
- optional counter-evidence references.

High-assurance omission evidence requires registration into at least one transparency service not controlled by the accused publication domain. Critical profiles SHOULD require witness/cross-log retention before global reliance changes.

Important boundary:

`TRANSPARENT_OMISSION_EVIDENCE != TRUE_OMISSION`.

Transparency proves that a specific evidence statement was registered and preserves equivocation/suppression evidence; semantic adjudication still verifies the promise, deadline, time interval, checkpoint continuity, and absence claim.

If omission evidence was observed by one relying party but cannot be retrieved from any required independent transparency path, current global status becomes `OMISSION_EVIDENCE_PROPAGATION_UNKNOWN`, not “no breach”.

## Frozen invariant 5 — time-source independence is provenance, not endpoint count

`TIME_ENDPOINT_COUNT != INDEPENDENT_TIME_CONTROL_DOMAINS`.

Define `TimeSourceProvenanceV1` for each source with authenticated claims for:

- logical source identity;
- signing authority / key lineage;
- operator/control account domain;
- upstream/reference-clock identities;
- implementation + firmware lineage;
- hosting/network administrative domain;
- hardware reference type when applicable;
- known dependency edges to other quorum members;
- provenance generation + freshness bound.

Define a dependency graph over all active quorum members. Two nominal sources collapse into one failure domain for a threat dimension when they share a dependency capable of inducing the same error.

Examples:

- two NTS servers signed by different keys but disciplined by the same compromised upstream GNSS receiver: not independent for reference-time compromise;
- four endpoints behind one cloud account and one operator credential: not independent for administrative compromise;
- different vendors with the same vulnerable base chipset/firmware lineage: correlated for implementation failure;
- same stratum-1 source reached through different mirrors: not independent for source correctness.

RFC 8633 explicitly warns that even different vendors may share common elements and recommends diverse reference clocks/implementations.

## Frozen invariant 6 — quorum policy is threat-dimension aware

`AuthenticatedTimeQuorumPolicyV1` binds:

- minimum independent control domains;
- minimum independent reference sources;
- tolerated correlated-failure dimensions;
- interval-overlap rule;
- outlier/falseticker rule;
- maximum provenance age;
- required provenance-attestation authorities.

A source can count in one dimension but not another. Therefore quorum evaluation returns both a time interval and an assurance vector, not just `N-of-M`.

If provenance is stale/unknown such that independence cannot be established, the source MAY be used as informational input but MUST NOT be counted toward consequential freshness quorum.

## Frozen invariant 7 — time authority rotation cannot manufacture independence

`KEY_ROTATION != NEW_TIME_SOURCE`.

`ENDPOINT_ROTATION != NEW_FAILURE_DOMAIN`.

`OPERATOR_RENAME != NEW_CONTROL_DOMAIN`.

Changing keys, DNS names, processes, regions, or provider endpoints does not reset provenance. A new logical independent source requires an authenticated provenance transition demonstrating the changed dependency graph.

## Frozen invariant 8 — post-facto provenance changes reopen current reliance

If later evidence shows that two sources previously counted as independent actually shared a compromised upstream or control domain during interval `I`, historical receipts remain immutable, but all freshness verdicts depending on the inflated quorum during `I` are re-appraised.

States:

- `HISTORICAL_TIME_QUORUM_ACCEPTED` remains factual;
- `CURRENT_RELIANCE_INVALIDATED_COMMON_MODE_DISCOVERED` if quorum definitely falls below policy;
- `CURRENT_RELIANCE_UNKNOWN_COMMON_MODE_INTERVAL` if dependency timing is uncertain.

No history rewrite.

## Minimal executable objects

```text
FreshnessObligationAuthorityV1
FreshnessPublicationPromiseV1
FreshnessPublicationDispositionV1
AdmissionRecordV1
FreshnessOmissionEvidenceV1
OmissionEvidenceReceiptV1
TimeSourceProvenanceV1
AuthenticatedTimeQuorumPolicyV1
TimeQuorumAppraisalV1
```

All consequential objects use canonical encoding, explicit schema/version, monotonic lineage generation where applicable, domain-separated signatures, predecessor digests, and fail-closed unknown states.

## RED-first matrix

### Obligation authority lifecycle
1. valid current authority issues promise -> accept;
2. retired authority issues promise -> reject;
3. same generation / different authority digest -> equivocation;
4. promise subject self-cancels without cancellation authority -> reject;
5. valid pre-deadline authorized supersession -> evaluate policy;
6. post-deadline supersession attempts to erase breach -> breach remains;
7. repeated deadline extension beyond policy maximum -> reject;
8. compromise notice reopens dependent promise appraisal.

### Admission/publication atomicity
9. crash before PREPARED -> no admission;
10. crash after PREPARED before signature -> recover/abort, never accepted;
11. signed promise retained, local commit marker lost -> recover obligation;
12. COMMITTED without promise -> fail closed;
13. response `ACCEPTED` before durable promise -> regression must fail;
14. retry same admission id -> idempotent same promise/event;
15. same admission id + different event digest -> equivocation/reject;
16. partition from promise authority -> UNKNOWN/NOT_ACCEPTED, not success.

### Omission-proof transparency
17. missed deadline + valid post-deadline view + transparent evidence -> omission proven after appraisal;
18. evidence statement registered but semantic inputs invalid -> reject semantic breach;
19. accused publisher controls only evidence channel and suppresses -> global status UNKNOWN;
20. one independent transparency receipt survives publisher deletion -> evidence recoverable;
21. same evidence id / different digest -> equivocation;
22. omission proof later countered by valid inclusion within deadline -> adjudicate contradiction, do not delete either record;
23. witness split view on omission evidence -> conflict;
24. monitor key compromise post-facto -> reopen appraisal.

### Time common-mode provenance
25. four endpoints / one upstream reference -> count as one for reference-source dimension;
26. four endpoints / one cloud-admin account -> one administrative domain;
27. four diverse operators + four diverse upstreams -> eligible independent quorum;
28. provenance missing for one source -> source excluded from consequential quorum count;
29. key rotation for same source -> independence count unchanged;
30. DNS/region rotation -> independence unchanged;
31. same firmware bug family across vendors -> correlated implementation dimension;
32. provenance rollback -> reject;
33. same provenance generation / different dependency graph -> equivocation;
34. newly discovered common upstream invalidates old current reliance where threshold drops below policy;
35. unknown onset of common-mode dependency -> current reliance UNKNOWN;
36. one far-future authenticated source outside overlap -> reject as falseticker/outlier under policy;
37. one far-past authenticated source outside overlap -> reject likewise;
38. no valid interval quorum -> latestness UNKNOWN;
39. nonce-bound fresh Roughtime reply from one source -> proves response freshness/provenance, not global correct time;
40. stale provenance plus fresh signed time -> cannot count toward high-assurance independence quorum.

### Composition / recovery
41. offline verifier misses obligation-authority rotation -> cannot accept newest promise until continuity recovered;
42. offline verifier misses time-quorum membership rotation -> catch-up required;
43. discovery registry silently drops a time source -> retirement proof required;
44. obligation authority and publication producer share one destructive control domain in critical profile -> assurance downgraded;
45. omission monitor and accused publisher share one control domain -> not independent breach witness;
46. transparency log and witness share one operator credential -> one control domain for suppression/equivocation threat;
47. crash while persisting trusted time/provenance frontier -> monotonic recovery, never rollback;
48. later valid recovery generation restores quorum -> new appraisal generation, old receipts preserved.

## Acceptance boundary for implementation

This freeze is complete only as a design contract. LAB-093 remains RED/GREEN pending.

Implementation must not claim `PREFIX_COMPLETE_PROVEN`, `CURRENT_AUTHORITY_LATESTNESS_PROVEN_WITHIN_BOUND`, or an equivalent consequential freshness state solely from:

- valid signatures;
- endpoint multiplicity;
- one publisher-controlled promise channel;
- one monitor's non-transparent evidence;
- authenticated time without provenance-backed independence;
- silence without a retained bounded obligation.

## Next distinct question

After executable tests exist, the next architecture slice is `obligation/admission authority recovery after total promise-authority loss + cross-domain durable admission journal survivability + semantic negative-proof construction for logs that do not expose canonical absence proofs`.
