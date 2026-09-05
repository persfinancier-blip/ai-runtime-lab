# Manual UNKNOWN reconciliation evidence + operator-resolution authority V1

Status: `MANUAL_UNKNOWN_RECONCILIATION_OPERATOR_RESOLUTION_AUTHORITY_V1_FROZEN`

Date: 2026-09-05

Scope: LAB-093 follow-up. This document defines the manual-resolution boundary entered only after an external effect has durably reached `MANUAL_RECONCILIATION_REQUIRED` under the frozen provider UNKNOWN-outcome oracle contract. It does **not** implement production code and does not claim behavioral PASS.

## 1. Safety objective

Manual reconciliation must let an authorized human record what can be justified from independent evidence without turning judgment into hidden resend authority, rewriting the historical UNKNOWN, or reusing the old provider request identity.

The historical effect record remains immutable in identity and history:

- original application key remains permanently consumed;
- original provider request/idempotency token is never minted again, rebound, or reused for a new business attempt;
- original `UNKNOWN` remains part of provenance even after a manual verdict;
- a manual verdict is a **governance/evidence conclusion**, not cryptographic proof of provider history;
- conflicting, incomplete, stale, scope-ambiguous, or unauthenticated evidence resolves to `UNRESOLVED` rather than the most convenient terminal state.

## 2. Why this boundary is separate from the automated oracle

The automated oracle contract already permits only read-only, identity-bound reconciliation. Manual resolution begins only when the proven automatic query/resend bounds are exhausted or the provider does not expose an adequate authoritative oracle.

Human operators may have access to additional evidence surfaces unavailable to the runtime, such as provider consoles, audit logs, bank/acquirer settlement records, business ledgers, customer acknowledgements, or support-case evidence. Those surfaces vary in authority, consistency, retention, and scope. They therefore require an explicit evidence and authorization model rather than an ad-hoc operator checkbox.

## 3. Evidence package: least-capability diagnostic view

A manual case exposes a sealed diagnostic package, not a mutable runtime/provider capability.

Required package identity:

- `manual_case_id`;
- immutable historical `effect_id`;
- `application_key_digest` (not a reusable secret/key value if unnecessary for diagnosis);
- `trust_epoch_id` and `effect_namespace_id`;
- provider/service/operation/account/region/scope identity;
- original provider request/idempotency token digest and, where operationally necessary, the exact token under access control;
- canonical request payload fingerprint;
- first-send timestamp and all observed attempt timestamps;
- capability-generation and oracle-generation identities pinned at first send;
- all observed provider-assigned operation/resource IDs;
- full automated reconciliation result history including `PENDING`, weak negatives, unavailable reads, and expiry boundaries;
- the reason automatic handling entered `MANUAL_RECONCILIATION_REQUIRED`;
- provenance-chain parent and digest covering the package.

The diagnostic interface MUST NOT expose send/resume/retry provider methods, token generators, adapter mutation methods, raw signing authority, DR root authority, or a general SQL/filesystem mutation handle.

## 4. Evidence classes

Evidence is stored as immutable evidence objects with source identity, retrieval time, relevant time window, selectors used, scope/account, retention/consistency caveats, content digest, collector identity, and provenance parent.

### E1 — provider authoritative operation/resource evidence

Examples: an exact provider operation/resource read keyed by a provider-assigned immutable ID, or a provider control-plane record whose documented semantics uniquely identify the original request/effect.

Strongest when it binds exact account/scope, original request token or operation ID, canonical payload/business identity, terminal status, and provider timestamp.

### E2 — provider audit/event evidence

Examples: immutable/searchable provider audit history or exported audit trail showing the exact mutation. Audit evidence is useful only when the relevant event class is actually logged and retention covers the incident window.

Donor: AWS CloudTrail Event history is searchable and described as immutable for the past 90 days of management events, but it excludes data events and has a finite retention window unless a trail/event data store is configured. Therefore absence from generic audit history cannot automatically prove non-execution.

### E3 — independent transactional/settlement evidence

Examples: acquirer/bank settlement record, payment-network reference, shipment carrier acceptance, signed external transaction ledger, or another system of record independent of the calling runtime.

This may strongly support `COMMITTED` when it uniquely maps to the original business effect. It must not be treated as `NOT_COMMITTED` evidence merely because no record is visible if the external system has eventual consistency, batching, delayed settlement, incomplete search selectors, or finite retention.

### E4 — application/business-system evidence

Examples: ERP/order ledger, customer-visible resource, fulfillment record, downstream webhook retained independently of the caller.

Useful as corroboration, but authority depends on whether the system can independently distinguish the original effect from a later/manual/duplicate action.

### E5 — human/support attestation

Examples: provider support statement, customer acknowledgement, operator note.

This can add context but is never sufficient by itself for `NOT_COMMITTED`; for `COMMITTED`, it requires exact identity binding and policy-defined authority. Unstructured verbal assertions remain supporting evidence only.

## 5. Normalized manual verdicts

Only three business-history verdicts exist:

### `COMMITTED`

Meaning: sufficient independent evidence supports that the original historical effect occurred.

Consequences:

- historical operation remains consumed/closed;
- no resend is permitted;
- result delivery may use the manually established business outcome if policy permits and the outcome payload is separately authenticated/bound;
- historical `UNKNOWN` remains recorded as an earlier state/evidence fact.

### `NOT_COMMITTED`

Meaning: policy-defined strong independent evidence supports that the original historical effect did not occur and cannot still occur from the old request.

This is deliberately harder than `COMMITTED`. A missing resource, absent audit event, support statement, expired idempotency cache, or repeated weak negative does not qualify alone.

Consequences:

- the **old effect remains permanently closed and non-reusable**;
- the old provider request token remains retired;
- the old application key remains consumed;
- any desired business retry is a separate explicit new business attempt with a new `effect_id` and, when required by discontinuity rules, a new authorized effect namespace/request identity.

### `UNRESOLVED`

Meaning: evidence does not meet terminal policy, conflicts materially, cannot be authenticated, is outside retention/visibility bounds, or cannot uniquely bind to the historical effect.

Consequences:

- no resend permission;
- no automatic conversion to another state over time;
- case may remain open, gather new evidence, or be explicitly closed administratively as unresolved, but the underlying effect stays non-reusable.

There is no operator verdict named `RETRY`, `SAFE_TO_RETRY`, `RESET`, `MISS`, or equivalent.

## 6. Terminal-evidence requirements

### `COMMITTED` minimum

At least one policy-approved evidence path must uniquely bind the original effect to a terminal external outcome. For high-consequence effect classes, require two independent evidence domains unless the provider offers a documented authoritative immutable operation record.

Evidence must cover:

1. exact provider/account/scope;
2. original operation/request/business identity;
3. terminal successful/committed semantics;
4. no material identity ambiguity;
5. authenticated provenance and collector identity.

### `NOT_COMMITTED` minimum

All of the following are required:

1. a provider/system-of-record evidence surface whose documented semantics can prove non-occurrence for the exact original identity;
2. proven visibility/settlement/async-acceptance horizon elapsed;
3. retention window still covers the incident;
4. exact account/region/scope/selectors verified;
5. no contradictory positive or pending evidence;
6. no still-live asynchronous provider workflow capable of later committing;
7. policy-defined independent corroboration for consequential effects.

If any requirement is unknown, verdict is `UNRESOLVED`.

## 7. Separation of duties

Manual terminal resolution is security-sensitive because it changes how the organization interprets an externally consequential historical operation.

Adopt least privilege and separation of duties consistent with NIST SP 800-53 Rev. 5 AC-5:

- **Evidence Collector**: may obtain/import diagnostic evidence, but cannot approve the terminal verdict alone.
- **Independent Reviewer**: validates identity binding, source authority, scope, retention, contradictions, and policy fit.
- **Resolution Authorizer**: records terminal verdict only after required review/quorum. For high-consequence classes, collector and authorizer must be different principals/failure domains.
- **Runtime/Provider Executor**: not part of manual verdict authority and receives no implicit send permission from the verdict.

Policy defines quorum per effect class. Ordinary provider credentials, worker credentials, runtime admin, or database admin access do not substitute for resolution authorization.

## 8. Resolution record

A terminal/manual record is append-only and parent-linked into the global provenance chain. It includes:

- case/effect identities;
- verdict (`COMMITTED`, `NOT_COMMITTED`, `UNRESOLVED`);
- exact evidence object digests and source classes;
- policy version and required quorum;
- collector/reviewer/authorizer identities and signatures/attestations as supported;
- reasoning code(s), not merely free text;
- timestamp;
- explicit statement that the old application key and provider request identity remain non-reusable;
- optional outcome payload digest for `COMMITTED`;
- conflict flags and any accepted limitations.

A later correction creates a new superseding resolution record; it never edits/deletes the old one. The system must retain both and make the contradiction visible.

## 9. New business attempt after `NOT_COMMITTED` or unresolved closure

A business owner may separately decide that the desired real-world action should be attempted again. That decision is not part of reconciliation.

Required representation:

- new `effect_id`;
- new provider request/idempotency identity;
- explicit `supersedes_business_intent_of=<old effect_id>` or equivalent link;
- new authorization/admission check under the current trust epoch/effect namespace;
- old application key remains consumed and cannot be used as the new attempt's idempotency identity;
- current provider capability/conformance evidence must permit the new attempt;
- if the historical loss/re-root discontinuity rules require domain separation, the new attempt must use the new epoch-aware namespace.

This prevents a human verdict from silently becoming a resend of the ambiguous request.

## 10. Evidence conflict rules

- Positive provider terminal evidence vs generic `NOT_FOUND` => conflict; generic negative is discarded as terminal authority.
- Two independently authenticated terminal records referring to the same exact provider operation but disagreeing => `UNRESOLVED` + provider evidence-integrity incident.
- Business evidence says delivered but provider says terminal failure => `UNRESOLVED` until identity mapping explains the discrepancy; do not choose by convenience.
- Evidence from wrong account/region/tenant/sandbox => inadmissible.
- Evidence outside proven retention window => cannot support absence.
- Screenshot/manual transcription without source authentication => supporting context only.
- Newly discovered evidence after a terminal verdict => append a review/supersession record; never erase prior governance history.

## 11. Privacy and least-data rules

The case package contains only data necessary to distinguish the effect. Sensitive payload fields should be represented by canonical digest or selectively revealed fields where possible. Evidence export must preserve source/provenance metadata while avoiding unrelated customer/provider data. Human access is auditable and scoped to the case.

## 12. Provider/audit donor findings

### AWS CloudTrail

AWS documents Event history as a searchable/downloadable immutable record of the past 90 days of **management events** in the current Region. Data events are not included, and longer-term records require a trail or event data store. This supports the rule that audit-event presence can be strong evidence when exact identity semantics are known, while generic absence is not sufficient unless event coverage and retention are proven.

Source: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html

### Google Cloud Audit Logs

Google documents Admin Activity audit logs as always enabled, while Data Access logs are generally disabled by default unless explicitly enabled. This supports per-operation evidence capability declarations: an operator cannot infer non-occurrence from an audit class that may not have been collected.

Source: https://docs.cloud.google.com/logging/docs/audit/configure-data-access

### Stripe idempotency

Stripe documents finite idempotency replay windows (API-version dependent; e.g. API v1 24 hours and API v2 30 days under documented scope). This supports the rule that expiry of provider idempotency state does not itself prove the original request was never committed and cannot authorize reuse of the historical identity.

Sources:
- https://docs.stripe.com/api-v2-overview
- https://docs.stripe.com/error-low-level

### NIST separation of duties

NIST SP 800-53 Rev. 5 AC-5 requires identifying duties that require separation and defining access authorizations that support that separation. This is used as the donor for collector/reviewer/authorizer separation, not as proof of provider history.

Source: https://csrc.nist.gov/CSRC/media/Projects/risk-management/800-53%20Downloads/800-53r5/SP_800-53_v5_1-derived-OSCAL.pdf

## 13. RED-first regression matrix (64 cases)

The implementation phase must create executable RED tests before production changes.

### A. Entry and package identity (1-8)
1. manual case only after durable `MANUAL_RECONCILIATION_REQUIRED`;
2. wrong effect id rejected;
3. wrong trust epoch rejected;
4. wrong effect namespace rejected;
5. payload fingerprint mismatch rejected;
6. provider/account/scope mismatch rejected;
7. capability/oracle generation mismatch is visible, never silently rebound;
8. case package provenance digest mismatch fails closed.

### B. Least-capability surface (9-16)
9. diagnostic view cannot send;
10. cannot mint provider token;
11. cannot resume old operation;
12. cannot mutate provider adapter;
13. cannot mutate SQL effect history directly;
14. cannot obtain DR/root signing material;
15. redacted application-key representation cannot be reused as request identity;
16. evidence import cannot alter original request fields.

### C. `COMMITTED` evidence (17-24)
17. exact authoritative operation record accepted;
18. exact settlement record accepted under configured policy;
19. unrelated resource with similar business fields rejected;
20. wrong-account positive rejected;
21. stale screenshot alone insufficient;
22. positive + weak negative resolves according to stronger exact positive evidence;
23. positive evidence with payload mismatch rejected;
24. committed verdict never enables resend.

### D. `NOT_COMMITTED` evidence (25-32)
25. generic provider `NOT_FOUND` insufficient;
26. repeated weak negatives insufficient;
27. missing CloudTrail event insufficient when event class coverage is unproven;
28. absent Data Access log insufficient when logging was disabled/not proven enabled;
29. expired audit retention insufficient;
30. strong exact negative before async horizon insufficient;
31. proven exact negative after all horizons and with corroboration may satisfy policy;
32. `NOT_COMMITTED` still keeps application key/provider token permanently retired.

### E. Conflict and unresolved behavior (33-40)
33. contradictory terminal provider records => unresolved/incidence;
34. provider success vs business missing => unresolved unless policy explains lag/identity;
35. provider failure vs independent settlement success => unresolved;
36. ambiguous selector collision => unresolved;
37. unauthenticated evidence => unresolved;
38. wrong-region evidence => inadmissible/unresolved;
39. evidence arriving after administrative unresolved closure can reopen evidence review but not old resend;
40. time passage alone never converts unresolved to not-committed.

### F. Authorization and separation of duties (41-48)
41. collector alone cannot terminally approve high-consequence case;
42. reviewer cannot impersonate authorizer;
43. same principal in prohibited roles rejected;
44. insufficient quorum rejected;
45. wrong policy version rejected;
46. ordinary runtime admin cannot approve;
47. provider credential holder alone cannot approve;
48. authorized quorum can append verdict but receives no provider mutation capability.

### G. Provenance and correction (49-56)
49. verdict append is parent-linked to global provenance;
50. evidence digest mutation detected;
51. deletion of prior resolution detected/fails verification;
52. correction appends superseding record rather than overwrite;
53. contradictory supersession remains visible;
54. crash before resolution append leaves case unresolved;
55. crash after durable append is idempotently recoverable without duplicate authority;
56. provenance replay from another DB/history rejected.

### H. New business attempt boundary (57-64)
57. old application key cannot become new attempt identity;
58. old provider token cannot be reused;
59. new attempt requires new effect id;
60. new attempt explicitly links old business intent/effect;
61. new attempt runs current admission/capability checks;
62. post-re-root discontinuity requires current epoch/namespace separation;
63. unresolved old effect does not silently block an explicitly authorized distinct business action, but cannot be substituted for it;
64. new attempt outcome never rewrites the historical UNKNOWN/manual verdict chain.

## 14. Composition constraints

This contract composes with, and may not weaken:

- LAB-093 permanent application-key non-reuse and durable request/effect registry;
- provider idempotency capability evidence/conformance lifecycle;
- automated UNKNOWN reconciliation oracle;
- authenticated archive/retention contracts;
- LAB-097..100 global canonical provenance/recovery chain;
- post-re-root trust epoch/effect namespace migration;
- human security ceremony authority.

A manual resolution must be represented as a new provenance event over immutable historical evidence, never as mutation of the old effect into a state that makes it appear the runtime had stronger provider knowledge than it actually had.

## 15. Frozen decision

`MANUAL_UNKNOWN_RECONCILIATION_OPERATOR_RESOLUTION_AUTHORITY_V1_FROZEN`:

1. manual reconciliation is evidence adjudication, not resend authority;
2. verdicts are only `COMMITTED`, `NOT_COMMITTED`, `UNRESOLVED`;
3. `NOT_COMMITTED` requires strong exact absence proof and all visibility/retention/async bounds, not repeated weak negatives;
4. historical `UNKNOWN`, application-key consumption, provider-token retirement, and provenance remain permanent;
5. terminal decisions require policy-bound separation of duties/quorum for consequential effects;
6. corrections append/supersede; they do not rewrite history;
7. any later business retry is a distinct effect with fresh identity under current admission/capability/epoch rules.

No production code or behavioral PASS is claimed by this artifact.