# Manual reconciliation canonical case/evidence schema + verifier/state-machine V1

Status: `MANUAL_RECONCILIATION_CANONICAL_CASE_EVIDENCE_VERIFIER_STATE_MACHINE_V1_FROZEN`

Date: 2026-09-05

Scope: design contract only; no production behavioral PASS is claimed.

## Objective

Make manual resolution of an external-provider `UNKNOWN` outcome deterministic, append-only, auditable, least-capability, and composable with LAB-097..100 global provenance. A terminal human verdict or later supersession must never mutate the historical effect, reuse the original application key/provider token, or turn missing evidence into proof of absence.

This contract refines the previously frozen manual-resolution authority contract. It specifies the immutable wire objects, source-capability declarations, verifier rules, append-only state machine, redaction boundary, and crash-recovery behavior required before implementation.

## Non-negotiable invariants

1. Historical effect identity is immutable. `request_id`, `application_key_digest`, `provider_token_digest`, `trust_epoch_id`, `effect_namespace_id`, payload digest, provider/account/region/scope, and original first-I/O provenance are never rewritten by reconciliation.
2. `UNKNOWN` is historical fact. A later verdict appends interpretation/evidence; it does not erase the original uncertainty.
3. Missing evidence is `NO_EVIDENCE`, never `NOT_COMMITTED`.
4. Evidence strength is bounded by a versioned source-capability declaration. An observation cannot prove more than its source is declared and verified to cover.
5. Terminal verdicts are only `COMMITTED`, `NOT_COMMITTED`, or `UNRESOLVED`; no `RETRY`, `RESET`, `MISS`, `SAFE_TO_RETRY`, or equivalent state exists.
6. Original provider token/application key remain consumed/retired under every verdict.
7. Corrections and reviewer/authorizer changes are append-only supersessions. Prior objects remain addressable and verifiable.
8. Redaction may hide presentation fields but must not change the digest/authenticated identity of the underlying evidence object.
9. No manual-case interface exposes provider send/resume, token minting, SQL mutation, root/recovery, or effect-admission capabilities.
10. Every authoritative transition is parent-linked into the existing global provenance chain; no locally-valid reconciliation island is authoritative.

## Canonical encoding

Use the repository's shared canonical V1 envelope pattern. For this contract, canonical payloads are JSON objects encoded with RFC 8785 JSON Canonicalization Scheme semantics before hashing/signing:

- UTF-8 / I-JSON-compatible data;
- duplicate object keys forbidden;
- deterministic property ordering;
- no insignificant whitespace;
- no NaN/Infinity;
- integers that may exceed interoperable IEEE-754 precision are represented as decimal strings;
- timestamps are UTC RFC3339 strings with explicit `Z` and canonical fixed precision selected by the schema;
- opaque bytes are lowercase hex strings unless the shared V1 envelope already mandates another representation.

The digest domain is explicit and versioned:

`SHA256("ai-runtime-lab/manual-reconciliation/v1/" || object_type || 0x00 || canonical_json_bytes)`

No object may be accepted merely because re-serializing a permissively parsed representation yields the same semantic values. Decoder rejects duplicate keys, unknown critical fields, invalid Unicode, schema-version mismatch, noncanonical timestamp/integer forms, and illegal enum values before identity computation.

RFC 8785 is selected because cryptographic hashing/signing needs invariant serialization; its I-JSON restrictions and deterministic property sorting directly serve immutable evidence identity. RFC 8949 deterministic CBOR remains a valid future alternative, but V1 MUST NOT mix multiple canonical encodings for the same object type.

## Immutable object types

### 1. `ReconciliationCaseV1`

Required authority-relevant fields:

- `schema_version = "manual-reconciliation-case/v1"`
- `case_id` = digest-derived immutable ID
- `historical_effect_id`
- `request_id`
- `application_key_digest`
- `provider_token_digest`
- `payload_digest`
- `provider_id`, `service_id`, `operation_id`
- `account_id_digest`, `region`, `scope_digest`
- `trust_epoch_id`, `effect_namespace_id`
- `capability_generation_id`
- `oracle_generation_id`
- `first_io_provenance_ref`
- `unknown_transition_ref`
- `opened_at`
- `opened_by_principal_id`
- `global_parent_provenance_id`

Creating a case does not create or re-open effect authority.

### 2. `EvidenceSourceCapabilityV1`

Versioned declaration of what a source can prove:

- source identity and implementation/version;
- provider/account/region/scope bindings;
- query/record class;
- positive coverage semantics;
- negative coverage semantics;
- consistency model;
- maximum propagation/visibility bound if documented/proved;
- asynchronous acceptance horizon;
- retention/tombstone horizon;
- clock/time-source assumptions;
- authentication/integrity mechanism;
- fields that are authoritative versus advisory;
- known blind spots/exclusions;
- evidence provenance (`OFFICIAL_DOCUMENTATION`, `MEASURED_CONFORMANCE`, `LOCAL_POLICY`);
- activation and expiry times;
- superseded-by reference.

Verifier MUST cap observation strength to this declaration. For example, a generic audit log with incomplete event coverage can corroborate a positive event but cannot become authoritative negative proof just because no event is present.

### 3. `ImportedEvidenceV1`

Immutable raw-or-normalized evidence envelope:

- `evidence_id` digest;
- `case_id`;
- `source_capability_id`;
- capture/query timestamp and observation window;
- exact query selectors/scope;
- raw artifact digest;
- normalized claims;
- source authentication verification result;
- importer principal/tool identity;
- import provenance parent;
- privacy classification;
- optional sealed blob locator + digest;
- explicit `observation_kind` such as `POSITIVE_MATCH`, `NEGATIVE_OBSERVATION`, `PENDING`, `FINAL_FAILURE`, `ERROR`, `UNAVAILABLE`.

An imported evidence object never directly changes the case verdict.

### 4. `EvidenceAssessmentV1`

Deterministic verifier output over a fixed set of evidence IDs and source-capability IDs:

- `assessment_id` digest;
- case ID;
- ordered evidence set digest;
- ordered capability set digest;
- verifier implementation/version digest;
- verifier policy generation;
- resulting lattice value;
- satisfied predicates;
- failed predicates;
- conflicts;
- stale/expired evidence list;
- earliest time at which a currently weak negative could become eligible for strong-negative evaluation;
- global provenance parent.

Allowed lattice:

`COMMITTED_MATCH`, `FINAL_FAILURE_MATCH`, `PENDING_MATCH`, `STRONG_NEGATIVE`, `WEAK_NEGATIVE`, `AMBIGUOUS`, `SOURCE_UNAVAILABLE`, `EVIDENCE_CONFLICT`.

### 5. `ReviewDecisionV1`

Reviewer adjudication over one immutable assessment:

- reviewer identity/role;
- assessment ID;
- decision: `ENDORSE`, `REJECT`, `REQUEST_MORE_EVIDENCE`;
- bounded rationale digest/text;
- conflict-of-interest/separation-of-duties assertions;
- timestamp;
- previous-review supersession reference if correcting a review.

### 6. `ResolutionDecisionV1`

Authorizer decision:

- exact case ID;
- exact assessment ID;
- exact accepted reviewer-decision IDs;
- exact policy generation;
- verdict only `COMMITTED`, `NOT_COMMITTED`, `UNRESOLVED`;
- authorization quorum/role evidence;
- timestamp;
- predecessor resolution ID if superseding a prior interpretation;
- global provenance parent.

`NOT_COMMITTED` is syntactically invalid unless the referenced assessment is `STRONG_NEGATIVE` and all policy-required corroboration/separation predicates are satisfied. `COMMITTED` requires matching authoritative positive evidence. Conflicting authoritative positives/negatives force `UNRESOLVED`/`EVIDENCE_CONFLICT`; policy cannot select the convenient side silently.

### 7. `PresentationRedactionV1`

Presentation-only overlay:

- target object ID;
- fields hidden or transformed for the viewer;
- reason/policy;
- viewer/audience class;
- redactor identity;
- timestamp.

The overlay MUST reference the original immutable object ID. It cannot be hashed as though it were the original evidence and cannot alter verifier inputs.

## State machine

Case state is derived from append-only events; it is not an independently mutable authority column.

`OPEN -> EVIDENCE_COLLECTING -> ASSESSED -> REVIEWED -> RESOLVED`

Additional derived states:

- `WAITING_FOR_VISIBILITY_BOUND`
- `EVIDENCE_CONFLICT`
- `SOURCE_UNAVAILABLE`
- `UNRESOLVED_TERMINAL`
- `SUPERSEDED_INTERPRETATION`

Rules:

- imported evidence may append in any non-corrupt case state;
- any newly accepted evidence after assessment invalidates only that assessment as current; it does not delete it;
- reviewer correction appends a superseding review;
- resolution correction appends a new `ResolutionDecisionV1` referencing the prior decision and a new/current assessment; old decision remains historical;
- no transition leads back to effect admission, provider resend, or application-key availability;
- case closure is an operational UI state only, never a mutation of historical evidence authority.

## Deterministic verifier rules

### Positive proof

A `COMMITTED_MATCH` requires an authoritative source-capability declaration whose positive semantics cover the exact original provider/account/region/scope and bind the observed resource/operation to the pre-I/O request/token/payload identity strongly enough to exclude a different operation.

### Strong negative proof

`STRONG_NEGATIVE` requires all of:

1. exact original identity/scope selectors are covered;
2. source is authoritative for absence, not merely advisory;
3. documented/proved visibility/propagation bound elapsed;
4. asynchronous acceptance horizon elapsed;
5. retention/tombstone/status window still includes the original operation time;
6. source capability was valid for the relevant provider/API/account generation;
7. no contradictory positive/pending/final-failure evidence exists;
8. policy-required corroboration is present;
9. query authentication/authorization succeeded and wrong-scope denial cannot masquerade as absence.

Repeated `WEAK_NEGATIVE` observations do not promote by count.

### Conflict handling

- authoritative `COMMITTED_MATCH` plus authoritative contradictory negative -> `EVIDENCE_CONFLICT`;
- two positive records bound to incompatible provider resource identities for the same original request -> `EVIDENCE_CONFLICT`;
- stale evidence remains visible but cannot satisfy current predicates beyond its valid retention/capability window;
- source-capability drift invalidates new automatic assessments using the stale declaration but does not rewrite historical assessments.

### No-proof conditions

The following are never sufficient by themselves for `NOT_COMMITTED`:

- generic `404` / `NOT_FOUND` from an eventually consistent API;
- absent generic audit-log event;
- expired idempotency record;
- missing operation ID after an initial timeout;
- operator recollection;
- screenshot without authenticated source linkage;
- provider documentation describing behavior not bound to the actual account/API generation;
- repeated weak negatives.

## Crash and concurrency semantics

Every append uses one transaction/CAS boundary over `expected_case_head` plus global provenance parent:

1. verify current case head and global parent;
2. verify object canonical bytes/digest/schema;
3. append immutable object;
4. append case-head transition referencing the object;
5. append/link global provenance transition;
6. commit atomically where one durable store is used; otherwise use the already-frozen prepare/commit/recovery protocol of LAB-097..100.

Crash before authoritative head/provenance commit leaves an orphan/staged object with no authority. Crash after commit leaves an authoritative append that recovery must rediscover idempotently. Two concurrent reviewers may both append reviews, but a resolution transaction must bind the exact accepted review set and current assessment; stale-head CAS fails closed and requires re-read/reassessment.

No recovery path performs delete-and-rewrite, provider resend, or implicit terminal verdict.

## Privacy and access boundary

Manual reconciliation evidence can contain customer/provider identifiers and sensitive operational metadata. V1 therefore separates:

- immutable authority fields/digests used by verifier;
- sealed raw artifacts accessible only to evidence roles;
- normalized minimum claims for review;
- presentation redactions for lower-privilege viewers;
- append-only access audit for raw/sealed evidence reads and exports.

Redaction is not evidence destruction. Retention/disposition of sealed raw artifacts must preserve whatever minimum authenticated digest/provenance is required to keep historical assessments verifiable. If underlying evidence is legally/operationally deleted, the deletion/disposition event is appended; verifier must not continue claiming raw evidence availability.

## Global provenance composition

Authoritative case open, evidence import acceptance, capability activation/supersession, assessment, review, resolution, supersession, redaction-policy change, and evidence disposition events are parent-linked to the shared LAB-097..100 global provenance chain.

A locally self-consistent case database whose global parent linkage is missing, forked, stale, or unauthenticated fails closed for terminal resolution. Startup/recovery verifies both local append-only continuity and the global chain before exposing a case as authoritative.

## RED-first matrix (72 minimum)

### Canonical/schema identity (12)
1. same semantic object/different key order -> same canonical digest;
2. duplicate JSON key -> reject;
3. unknown critical field -> reject;
4. noncanonical integer -> reject;
5. invalid timestamp precision/offset -> reject;
6. NaN/Infinity -> reject;
7. invalid Unicode/lone surrogate -> reject;
8. schema-version mismatch -> reject;
9. digest-domain/object-type substitution -> reject;
10. case ID not matching canonical body -> reject;
11. historical-effect identity mutation -> reject;
12. provider token/application key replacement -> reject.

### Source capability / evidence import (12)
13. valid authoritative positive import;
14. wrong account scope -> cannot prove;
15. wrong region -> cannot prove;
16. expired capability -> stale;
17. incomplete audit source absent event -> weak only;
18. eventually consistent NOT_FOUND before bound -> weak;
19. authenticated sealed artifact digest mismatch -> reject;
20. importer metadata change cannot alter raw evidence identity;
21. provider/API generation mismatch -> reject/cap strength zero;
22. source unavailable -> no absence proof;
23. measured behavior contradicts documentation -> conflict/drift;
24. retention window expired -> no strong negative.

### Verifier lattice / conflicts (16)
25. exact authoritative committed match;
26. exact authoritative final failure;
27. pending match;
28. strong negative only after all horizons;
29. repeated weak negatives stay weak;
30. missing evidence stays no-evidence;
31. positive + contradictory authoritative negative -> conflict;
32. two incompatible positive resources -> conflict;
33. wrong-scope auth failure cannot become negative;
34. stale evidence visible but predicate-ineligible;
35. generic 404 alone insufficient;
36. missing audit event alone insufficient;
37. expired idempotency record alone insufficient;
38. lost operation ID alone insufficient;
39. screenshot/operator recollection insufficient;
40. current stronger capability cannot retroactively strengthen old observation without new evidence.

### Review / resolution authority (12)
41. COMMITTED from valid committed assessment + quorum;
42. NOT_COMMITTED from strong negative + quorum;
43. NOT_COMMITTED from weak negative -> reject;
44. UNRESOLVED from conflict;
45. reviewer cannot self-authorize where policy separates roles;
46. stale assessment resolution -> CAS/reject;
47. omitted required reviewer -> reject;
48. altered rationale cannot alter referenced assessment;
49. supersession keeps old decision addressable;
50. no RETRY/RESET/MISS enum accepted;
51. resolution never frees original application key/provider token;
52. resolution cannot invoke provider adapter mutation.

### Crash / concurrency / provenance (12)
53. crash before object append;
54. crash after staged object before head commit;
55. crash after head before external/global commit -> recovered by shared protocol;
56. replay same append idempotent;
57. concurrent evidence imports preserve both;
58. concurrent assessments: stale one cannot silently win;
59. concurrent reviewer decisions bind exact IDs;
60. resolution stale-head CAS fails;
61. missing global parent -> fail closed;
62. forked global parent -> fail closed;
63. local case rollback -> detected;
64. supersession rollback -> detected.

### Privacy / redaction / disposition (8)
65. redaction leaves original digest/verifier input unchanged;
66. low-privilege viewer cannot fetch sealed raw artifact;
67. raw-evidence read creates access audit append;
68. export creates access audit append;
69. redaction overlay cannot hide verifier conflict from authority engine;
70. evidence disposition appends tombstone/provenance, not silent delete;
71. disposed raw artifact cannot be represented as currently available;
72. redacted presentation cannot be re-imported as stronger original evidence.

## Donors / primary references

- RFC 8785, JSON Canonicalization Scheme: canonical, hashable JSON representation for cryptographic operations; I-JSON restrictions and deterministic property sorting.
- RFC 8949, CBOR section 4.2: deterministic encoding requirements; retained as a future-format donor, not mixed into V1 object identity.
- NIST SP 800-53 Rev. 5/5.1, AU family: audit record protection, non-repudiation/identity binding, retention, and audit generation provide the control rationale for immutable reviewer/producer bindings, protected evidence history, and retention-aware verification.
- NIST SP 800-92: log-management lifecycle and retention/preservation concepts; supports treating logs as bounded evidence sources rather than magical complete history.

## Decision

Freeze `MANUAL_RECONCILIATION_CANONICAL_CASE_EVIDENCE_VERIFIER_STATE_MACHINE_V1_FROZEN` as the implementation contract for LAB-093 manual UNKNOWN reconciliation. Production implementation remains blocked on executable RED/GREEN and the retained LAB-086/088/090/091/092 dependency gates.

## Exact implementation order when executable source becomes available

1. Add pure canonical-schema encoder/decoder + digest tests for the 12 identity cases.
2. Add source-capability and imported-evidence immutable SQL tables plus append-only triggers/fences.
3. Add deterministic pure verifier and cases 13-40 before any operator UI.
4. Add reviewer/resolution state machine and separation-of-duties checks; cases 41-52.
5. Bind every authoritative append into the shared LAB-097..100 provenance/recovery protocol; cases 53-64.
6. Add sealed-artifact access/redaction/disposition layer; cases 65-72.
7. Run restart/crash/concurrency and full retained-stack regression suite; audit that no path can resend the historical provider request or release its application key/provider token.
