# Promise-authority loss, admission-journal survivability, and semantic absence — v1

Status: `PROMISE_AUTHORITY_LOSS_ADMISSION_JOURNAL_SURVIVABILITY_SEMANTIC_ABSENCE_V1_FROZEN`

Date: 2026-09-08

Scope: non-executable design fallback while LAB-086 exact branch execution remains unavailable. This note does not substitute for LAB-086 RED/GREEN or compile evidence.

## Problem

The prior freshness-obligation work established that `EVENT_ACCEPTED && NO_INDEPENDENTLY_RETAINED_PROMISE` is forbidden, and that admission + signed promise creation is one recoverable logical transition. Three unresolved failure modes remain:

1. the promise-authority threshold becomes unavailable or compromised after an admission has reached PREPARED but before a valid promise is durably retained;
2. the local admission journal is lost with one administrative/destructive domain, allowing the system to forget that an obligation ever entered PREPARED;
3. the downstream log/query API exposes no canonical non-inclusion proof, so an empty query / 404 / timeout can be confused with proof that publication did not occur.

The objective is to preserve fail-closed semantics without inventing evidence and without making one lost signing service permanently destroy recoverability.

## Primary-source donors

### RFC 9162 — Certificate Transparency v2

https://www.rfc-editor.org/rfc/rfc9162.html

Useful mechanism:

- when a log accepts a valid submission it returns an SCT;
- the SCT is a signed promise to include that submission within the log's Maximum Merge Delay (MMD);
- a client that retained an SCT can later demand inclusion against an STH after the deadline;
- monitors can fetch all entries for a tree, verify the tree root, and audit consistency/append-only behavior;
- signed evidence of an unfulfilled SCT is evidence of log misbehavior.

Important boundary: CT's dense append-only log provides inclusion and consistency proofs. It does not turn a bare application-level `404` into a cryptographic proof that an arbitrary semantic event never existed.

### RFC 9943 — SCITT architecture

https://www.rfc-editor.org/rfc/rfc9943.html

Useful mechanism:

- issuer statement and transparency-service receipt are separate evidence;
- a statement can be registered independently with multiple Transparency Services and carry multiple receipts;
- receipts prove registration in a VDS, not semantic truth of the statement;
- registration may be performed by a client other than the issuer.

This is a strong donor for cross-domain survivability: independently retained admission/promise evidence should be registrable in more than one destructive/control domain.

### TUF specification

https://theupdateframework.github.io/specification/

Useful mechanism:

- top-level trust changes preserve a predecessor/successor chain;
- replacing root keys requires signatures satisfying both the previous and new root thresholds;
- an outdated verifier advances through intermediate root generations rather than jumping directly to an untrusted latest root;
- if a threshold of root keys is compromised, the specification calls for out-of-band root recovery; safe in-line recovery is not assumed.

This is the donor for total promise-authority loss: when ordinary predecessor authorization is no longer available, recovery must use a separately provisioned recovery anchor/new lineage rather than self-authorized key replacement.

### SQLite atomic commit / WAL documentation

https://www.sqlite.org/atomiccommit.html
https://www.sqlite.org/wal.html

Useful mechanism and boundary:

- SQLite provides atomic commit for changes inside one database;
- durability depends on journal/WAL and synchronous/storage behavior;
- WAL does not provide cross-host atomicity and attached databases are not one atomic distributed transaction.

Therefore a local SQLite admission transaction can make local PREPARED/promise state atomic, but it cannot by itself prove cross-domain survivability. Remote independent retention must be modeled as a protocol with receipts/acks, not as one distributed SQLite transaction.

### Trillian verifiable log/map documentation

https://transparency.dev/verifiable-data-structures/

Useful mechanism:

- a verifiable log commits an append-only sequence and supports inclusion/consistency verification;
- a sparse verifiable map deterministically assigns keys to leaves, so an authenticated empty leaf/path can support compact non-inclusion semantics.

This motivates a future compact negative-proof surface keyed by obligation id. It is not a claim that an existing dense log already has that property.

## Frozen distinctions

```
PRIVATE_PROMISE_AUTHORITY_AVAILABLE
    != HISTORICAL_PROMISES_VERIFIABLE
    != ADMISSION_OBLIGATION_RECOVERABLE

LOCAL_JOURNAL_DURABLE
    != CROSS_DOMAIN_JOURNAL_SURVIVABLE

EMPTY_QUERY
    != CANONICAL_NON_INCLUSION_PROOF
    != EXHAUSTIVE_AUTHENTICATED_PREFIX_ABSENCE

PROMISE_AUTHORITY_LOSS
    != PROMISE_AUTHORITY_COMPROMISE
    != ADMISSION_CANCELLATION
```

A lost private signing threshold does not invalidate already issued promises whose public verification lineage remains trustworthy. Conversely, possession of historical public keys does not create authority to issue new promises.

## 1. Admission state machine under authority loss

Define one canonical `AdmissionObligationIdV1` before any external ACCEPTED response. It binds at minimum:

- logical subject/source identity;
- canonical event digest;
- admission generation;
- intended publication class/log lineage;
- original publication deadline/bound;
- policy generation;
- predecessor obligation id when applicable.

State machine:

```
NEW
  -> PREPARED_LOCAL
  -> PREPARED_SURVIVABLE
  -> PROMISE_ISSUED
  -> ACCEPTED
  -> PUBLISHED | OMISSION_PROVEN | CANCELLED_BY_AUTHORITY
```

Exceptional states:

```
PREPARED_AUTHORITY_UNAVAILABLE
PREPARED_AUTHORITY_COMPROMISED
RECOVERY_REISSUE_PENDING
RECOVERY_LINEAGE_REQUIRED
```

### Rule A1 — no external ACCEPTED before durable promise

`ACCEPTED` is externally visible only after a valid promise is durably recoverable under the retention policy. A PREPARED journal row alone is not equivalent to ACCEPTED.

### Rule A2 — total signer unavailability after PREPARED is fail-closed, not forgetful

If the promise-authority threshold becomes unavailable after PREPARED:

- retain the obligation as unresolved;
- do not return ACCEPTED;
- do not delete or silently cancel it;
- do not extend its original deadline merely because signing infrastructure is unavailable;
- expose `PREPARED_AUTHORITY_UNAVAILABLE` for recovery/operations.

If the authority later recovers without a trust-lineage break, it may issue the original bounded promise for the existing obligation id. The promise must bind the original admission time/deadline semantics, not pretend the event was newly admitted.

### Rule A3 — compromise requires recovery authority, not the compromised authority itself

If the promise-authority threshold is compromised, the compromised authority cannot authorize its own trustworthy successor.

Recovery requires one of:

1. predecessor/successor continuity under a still-trusted higher/offline recovery root; or
2. an explicitly provisioned out-of-band recovery/new-lineage ceremony.

If neither exists, status is `RECOVERY_LINEAGE_REQUIRED`; current positive issuance stops. Historical evidence remains available for appraisal but no new same-lineage authority is fabricated.

### Rule A4 — recovery reissue never launders a missed bound

A recovery authority may create `RecoveredPublicationPromiseV1` only when it references the original obligation id and authenticated admission evidence. Unless a prior policy explicitly authorized bounded renewal, effective deadline is no later than the original still-applicable deadline.

A recovery promise issued after that deadline can document/repair authority continuity, but it cannot erase an already provable omission interval.

## 2. Cross-domain durable admission journal

### Threat model

One administrative/destructive domain may lose or intentionally delete:

- the local SQLite DB and its WAL/journal;
- backups reachable by the same account;
- one object-store bucket and replicas controlled by the same credentials;
- one transparency/admission service.

Counting replicas without control-domain independence is insufficient.

### `AdmissionJournalEnvelopeV1`

Each PREPARED admission produces a canonical signed/authenticated envelope containing:

- `obligation_id`;
- event digest and source identity;
- original deadline/policy generation;
- local journal sequence/predecessor digest;
- authority lineage/generation used for admission;
- creation monotonic token / authenticated time evidence when available;
- payload schema version.

The envelope itself must not grant publication authority. It is evidence that an admission obligation existed.

### `AdmissionRetentionReceiptV1`

A retention domain returns a receipt binding:

- exact envelope digest;
- retention domain identity;
- destructive/control-domain identity declaration;
- receipt generation/sequence;
- durable registration checkpoint/receipt where supported.

External state becomes `PREPARED_SURVIVABLE` only after policy-required receipt quorum is met across independent destructive/control domains.

Recommended critical profile:

```
J0_LOCAL_ONLY
J1_LOCAL_PLUS_SAME_CONTROL_BACKUP
J2_TWO_INDEPENDENT_DESTRUCTIVE_DOMAINS
J3_MULTI_DOMAIN_PLUS_TRANSPARENCY_RECEIPT
```

Only J2/J3 should support a claim that one administrative/destructive domain can disappear without erasing admission existence.

### No fake distributed transaction

Do not claim local DB + remote retention are one atomic transaction unless an actual distributed atomic protocol is implemented and executed.

Instead use a recoverable protocol:

1. durable local `PREPARED_LOCAL`;
2. transmit canonical envelope to independent retention domains;
3. durably record returned receipts locally;
4. once quorum is met, transition to `PREPARED_SURVIVABLE`;
5. obtain/retain signed publication promise;
6. only then expose ACCEPTED.

Crash recovery resumes from the highest locally/externally provable state. Duplicate envelope registration is idempotent by `obligation_id + envelope_digest`.

### Split-view / conflicting journal evidence

Same `obligation_id` with different authenticated event/deadline/policy digests is `ADMISSION_EQUIVOCATION_CONFLICT`, not last-write-wins.

A later generation may supersede an obligation only through an explicit authenticated transition that references the predecessor and obeys the deadline-laundering rule.

## 3. Semantic negative proof when the log has no canonical absence proof

### Rule N1 — 404/empty/timeout are observations, not proofs

The following are never sufficient for `NON_PUBLICATION_PROVEN`:

- HTTP 404;
- empty search result;
- timeout;
- one mirror returning no row;
- one monitor's incomplete local cache;
- a query endpoint saying `not found` without an authenticated completeness commitment.

They produce `NON_PUBLICATION_UNKNOWN` unless composed with stronger evidence.

### Rule N2 — dense-log exhaustive-prefix absence is possible, but expensive

For an RFC-9162-like append-only log that supports complete leaf retrieval and authenticated tree heads, a monitor can create `ExhaustivePrefixAbsenceEvidenceV1` for bounded semantic absence through checkpoint C:

1. retain a valid signed checkpoint/STH C with tree size N/root R;
2. fetch every leaf `0..N-1` required by the log protocol;
3. verify each leaf encoding and reconstruct the exact Merkle root R;
4. evaluate a frozen canonical matching predicate `P_v` over every authenticated leaf;
5. demonstrate zero matching leaves for the obligation/event digest;
6. bind C, N, R, predicate version, obligation id, enumeration digest, and monitor identity into the absence evidence;
7. optionally register that evidence with independent transparency/witness services.

This is positive evidence of absence **relative to that authenticated complete prefix and predicate**. It is not proof that no event exists outside the prefix, that the source never generated it, or that the producer did not suppress it before log admission.

If the log API cannot retrieve/verify the complete prefix, this construction is unavailable.

### Rule N3 — compact future negative proof requires an authenticated indexed structure

For future protocol versions, maintain a log-backed verifiable map keyed by `AdmissionObligationIdV1` (or a collision-resistant canonical derivative). Map value records publication state/digest.

A signed map root plus a valid sparse-Merkle empty-leaf/non-inclusion proof can establish compact `NO_PUBLICATION_FOR_OBLIGATION_AT_MAP_ROOT`.

The map root must itself be bound into the append-only log/checkpoint lineage so the map cannot silently rewrite history. Thus:

```
APPEND_ONLY_LOG = chronology / history
VERIFIABLE_MAP = keyed present-or-absent state
LOG_BACKED_MAP = compact negative proof + auditable history
```

Do not bolt a self-hash onto a mutable row and call it a non-inclusion proof.

### Rule N4 — omission proof still needs a retained obligation

Even perfect non-inclusion at deadline does not prove a broken promise unless there was a valid, independently retained obligation requiring publication by that deadline.

Therefore:

```
PROVABLE_OMISSION =
    VALID_RETAINED_OBLIGATION
    + DEADLINE_PROVEN_ELAPSED
    + AUTHENTICATED_PREFIX/MAP_STATE_AFTER_DEADLINE
    + POSITIVE_NON_PUBLICATION_EVIDENCE
```

Without the first term, the result is at most `EVENT_NOT_OBSERVED_IN_BOUND`, not promise violation.

## 4. Recovery after complete local journal loss

A recovering node must not initialize a fresh empty admission journal merely because local rows disappeared.

Recovery sequence:

1. identify trusted admission-journal lineage/generation from retained root/recovery state;
2. query all required independent retention domains;
3. verify receipts/envelopes and predecessor continuity;
4. detect same-obligation conflicting digests;
5. reconstruct unresolved PREPARED/PROMISE_ISSUED obligations;
6. reconcile against publication log/map/checkpoints;
7. only after reconciliation allow new admissions.

If policy says J2/J3 but fewer than required independent domains are reachable, state is `ADMISSION_JOURNAL_RECOVERY_INCOMPLETE_UNKNOWN`; do not treat missing evidence as an empty fresh journal.

## 5. Authority-loss liveness without fail-open

Availability mechanism is separated from trust continuity:

- ordinary promise-authority outage: queue/retain PREPARED obligations, stop ACCEPTED;
- bounded degraded mode may reject or shed new admissions before PREPARED, but may not delete existing obligations;
- recovery authority can restore issuance only according to already-authenticated recovery policy;
- if recovery root itself is lost/compromised beyond threshold, same-lineage recovery is unproven and an external rebootstrap/new lineage is required.

This mirrors the TUF boundary that compromise of a root threshold requires out-of-band recovery rather than pretending ordinary online metadata can repair the trust root.

## 6. Fraud / contradiction classes

1. `ADMISSION_ACCEPTED_WITHOUT_DURABLE_PROMISE`
2. `PREPARED_OBLIGATION_SILENTLY_DROPPED`
3. `PROMISE_AUTHORITY_SELF_RECOVERY_AFTER_THRESHOLD_COMPROMISE`
4. `RECOVERY_PROMISE_DEADLINE_LAUNDERING`
5. `SAME_OBLIGATION_DIFFERENT_EVENT_DIGEST`
6. `SAME_OBLIGATION_DIFFERENT_DEADLINE`
7. `SAME_OBLIGATION_DIFFERENT_POLICY_GENERATION`
8. `RETENTION_DOMAIN_COUNT_SYBIL_SAME_CONTROL`
9. `LOCAL_JOURNAL_LOSS_TREATED_AS_FRESH_BOOTSTRAP`
10. `REMOTE_RETENTION_RECEIPT_REPLAY_WRONG_ENVELOPE`
11. `EMPTY_QUERY_MISREPRESENTED_AS_NON_INCLUSION_PROOF`
12. `INCOMPLETE_PREFIX_MISREPRESENTED_AS_EXHAUSTIVE_ABSENCE`
13. `PREDICATE_VERSION_REWRITE_AFTER_CHECKPOINT`
14. `MAP_ROOT_NOT_BOUND_TO_APPEND_ONLY_HISTORY`
15. `NON_INCLUSION_WITHOUT_VALID_OBLIGATION`
16. `POST_DEADLINE_RECOVERY_SUPERSESSION_ERASES_OMISSION`

## 7. RED-first executable matrix

Freeze these regressions before production refactor. They are design requirements, not current PASS claims.

### Authority loss / recovery (12)

1. PREPARED then all ordinary promise signers unavailable -> no ACCEPTED, obligation retained.
2. signer availability restored -> original obligation can issue without new admission identity.
3. outage recovery cannot extend original deadline.
4. threshold compromise -> ordinary successor signed only by compromised threshold rejected.
5. valid higher/offline recovery authorization -> successor accepted.
6. no recovery anchor -> `RECOVERY_LINEAGE_REQUIRED`.
7. already issued historical promise remains signature-verifiable after private-key loss.
8. public-key compromise interval invalidates current reliance only in affected scope.
9. recovered promise references exact predecessor obligation.
10. recovered promise with changed event digest rejected.
11. recovered promise after missed deadline does not erase omission status.
12. crash during recovery-authority rotation resumes without dual-current authorities.

### Admission journal survivability (12)

13. local PREPARED commit survives process crash.
14. local-only PREPARED never claims cross-domain survivability.
15. two endpoints under one destructive credential count as one domain.
16. independent-domain receipt quorum -> `PREPARED_SURVIVABLE`.
17. crash after first receipt -> recovery resumes collection idempotently.
18. crash after quorum before local state update -> external receipts reconstruct quorum.
19. one domain destroyed -> J2/J3 reconstruct obligation.
20. same obligation/different envelope across domains -> equivocation conflict.
21. receipt for wrong envelope digest rejected.
22. complete local journal deletion cannot silently fresh-bootstrap when remote lineage exists.
23. unreachable required retention domain -> recovery incomplete UNKNOWN.
24. remote duplicate registration returns idempotent equivalent receipt/no duplicate obligation.

### Semantic absence / omission (14)

25. HTTP 404 alone -> UNKNOWN.
26. empty search result alone -> UNKNOWN.
27. timeout alone -> UNKNOWN.
28. complete N-leaf prefix + verified root + no canonical match -> bounded absence proven.
29. one missing leaf in purported exhaustive prefix -> UNKNOWN.
30. wrong reconstructed root -> evidence rejected.
31. predicate version changed after checkpoint -> evidence rejected.
32. same leaf bytes under alternate parser cannot change frozen predicate semantics.
33. valid sparse-map non-inclusion under signed root -> keyed absence proven.
34. unsigned/stale map root -> negative proof rejected.
35. map root not anchored to log history -> no historical absence claim.
36. non-inclusion before deadline -> not omission proof.
37. non-inclusion after deadline but no retained obligation -> not promise violation.
38. retained obligation + elapsed deadline + verified absence -> omission proven.

### Composition / crash / catch-up (10)

39. offline monitor reconstructs obligation before evaluating latest log state.
40. selectively omitted historical retention receipt is detected by retained predecessor frontier.
41. stale checkpoint cannot prove post-deadline absence.
42. newer checkpoint with incomplete leaf retrieval remains UNKNOWN.
43. post-facto discovered retention-domain common control reopens current survivability appraisal.
44. post-facto log split view reopens absence appraisal.
45. obligation cancellation issued after deadline cannot erase prior omission.
46. cancellation before deadline must be separately authorized and independently retained.
47. total recovery-root threshold loss -> same-lineage issuance stops.
48. external rebootstrap creates explicit new lineage and preserves old unresolved evidence as historical input, not rewritten history.

## 8. Implementation direction when exact execution returns

Do not implement this fallback ahead of LAB-086.

When LAB-093/LAB-094+ execution reaches this layer, smallest coherent prototype should be:

1. value-only canonical `AdmissionJournalEnvelopeV1` + deterministic digest;
2. local SQLite state machine with explicit PREPARED/PROMISE_ISSUED/ACCEPTED states and crash tests;
3. abstract retention-receipt interface with test doubles representing independent destructive domains;
4. recovery reconstruction from retained receipts;
5. `ExhaustivePrefixAbsenceEvidenceV1` prototype against a small verifiable append-only test log;
6. only after that, evaluate whether a log-backed sparse map is justified for compact non-inclusion.

Do not claim a cryptographic non-inclusion property from an API that does not actually expose an authenticated complete prefix or authenticated indexed map.

## Decision

Freeze:

`PROMISE_AUTHORITY_LOSS_ADMISSION_JOURNAL_SURVIVABILITY_SEMANTIC_ABSENCE_V1_FROZEN`.

Core invariant:

```
A publication omission may be declared PROVEN only when the system can prove
both sides of the contradiction:

(1) an independently retained valid obligation required publication by bound B; and
(2) authenticated complete state after B positively proves the obligated publication is absent.

Loss of the ordinary promise-authority or one storage/control domain may block
new acceptance, but must not erase an already existing admission obligation.
```
