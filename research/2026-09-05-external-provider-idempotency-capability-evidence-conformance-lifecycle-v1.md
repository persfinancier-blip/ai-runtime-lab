# External provider idempotency capability evidence + conformance lifecycle V1

Status: `EXTERNAL_PROVIDER_IDEMPOTENCY_CAPABILITY_EVIDENCE_CONFORMANCE_LIFECYCLE_V1_FROZEN`

Date: 2026-09-05

Composes with: LAB-093 application-idempotency/effect registry, LAB-100 trusted activation/provider capability authority, post-re-root trust/effect epoch migration, epoch-aware client/API negotiation and external cutover adapter.

## Problem

A local runtime can construct a stable idempotency key and still be unsafe if the external provider interprets, scopes, retains or compares that token differently from what the runtime assumes. Provider behavior may also drift independently of local code: documentation can change; an account/region/API version can expose different semantics; an adapter can truncate or normalize a token; a provider can expire deduplication state; UNKNOWN outcomes can become unqueryable.

Therefore `supports idempotency` is not a boolean feature flag. It is a versioned, evidence-backed capability contract whose exact semantics must be known before a new external effect is admitted.

This contract does **not** authorize a production post-re-root cutover. It only determines whether a provider/adapter/effect-class combination has sufficient evidence to be eligible for an already-authorized effect namespace.

## Primary-source observations

### IETF Idempotency-Key draft

The current HTTPAPI draft remains an Internet-Draft rather than a final RFC. It states that a resource may expire idempotency keys, should publish its expiration policy, and is responsible for the key lifecycle. It also makes the uniqueness contract a resource-owner/client concern. This is useful design evidence, but provider-specific semantics must still be measured or documented for the concrete service.

Source: https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header-07

### AWS EC2 / EBS / ECS

AWS documents concrete client-token semantics rather than a universal AWS-wide rule. EC2 specifies case-sensitive client tokens and same-token/same-parameters retry behavior, while changed parameters produce an idempotency mismatch. EBS StartSnapshot similarly documents same-token/same-parameters replay and conflict on changed parameters. ECS RunTask explicitly scopes idempotency to a cluster and documents a 24-hour client-token TTL. These are materially different capability properties even within one provider.

Sources:
- https://docs.aws.amazon.com/ec2/latest/devguide/ec2-api-idempotency.html
- https://docs.aws.amazon.com/ebs/latest/userguide/ebs-direct-api-idempotency.html
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_Idempotency.html

### Google Cloud Storage

Google Cloud Storage distinguishes always-idempotent, conditionally-idempotent and non-idempotent operations, with conditional safety depending on preconditions such as generation/metageneration matches or ETags. This reinforces that capability evidence belongs to an exact operation/effect class, not merely to a provider account.

Source: https://docs.cloud.google.com/storage/docs/retry-strategy

## Frozen V1 decision

Provider idempotency is represented by an immutable **Provider Idempotency Capability Evidence Record** (`PICER`) plus an independently retained activation state. New effects are admitted only when the exact effect class resolves to one `ACTIVE`, non-expired, non-invalidated record whose required properties have sufficient evidence.

Previously bound retries never silently migrate to a newer capability record. They remain pinned to the provider/adapter/account/API/effect identity and evidence generation under which their provider request identity was created. If that historical capability becomes unsafe for resend, the operation transitions to fail-closed/manual reconciliation rather than being rebound to a fresh token or policy.

## Canonical capability identity

A capability record is bound to at least:

- `capability_evidence_id` — digest over canonical record;
- `provider_family` and exact service/API operation;
- provider API version/protocol revision when exposed;
- account/project/tenant identity class;
- region/zone/cluster/resource scope when semantics depend on it;
- adapter implementation identity/version and configuration digest;
- credential/endpoint class where routing can alter scope;
- local `effect_class` and canonical payload/fingerprint version;
- `trust_epoch_id` + `effect_namespace_id` compatibility set;
- provider-token construction version;
- evidence generation and parent generation;
- observed/documented timestamp bounds;
- activation status.

A change to any authority-relevant field produces a new record; it never mutates the meaning of an already-active record in place.

## Required semantic properties

For each effect class, the record must explicitly classify every property below as `PROVED`, `DOCUMENTED`, `OBSERVED`, `UNKNOWN`, or `NOT_SUPPORTED` with evidence references.

1. **Token syntax** — maximum bytes/chars, allowed alphabet, case sensitivity.
2. **Provider normalization** — Unicode/ASCII normalization, case folding, whitespace treatment, URL/header decoding, SDK transformations.
3. **Truncation** — whether the provider or adapter truncates, hashes or rewrites the token.
4. **Scope** — account/project/tenant, service, region, zone, cluster, resource or global scope.
5. **Payload binding** — behavior for same token + same payload versus same token + changed payload; exact mismatch error if defined.
6. **Retention/expiry** — lower bound, upper bound or unknown token-deduplication lifetime.
7. **Retry-after-success** — whether the original result/resource is returned or only duplicate suppression is promised.
8. **Concurrent duplicates** — behavior for simultaneous requests with the same token.
9. **UNKNOWN/timeout semantics** — whether a request outcome can be authoritatively queried independently of retry.
10. **Deletion/recreation semantics** — whether deleting a created resource can make a token reusable or alter duplicate behavior.
11. **API-version drift** — whether an API/version/SDK change can change token semantics.
12. **Cross-region/account collision behavior** — whether identical tokens in distinct scopes collide or are independent.
13. **Provider error taxonomy** — mismatch, duplicate-in-progress, expired/not-found and retryable transport errors.
14. **Outcome identity** — provider operation/resource/request identifier that can be durably bound to local evidence.

An `UNKNOWN` property is acceptable only if it is irrelevant to the safety claim for that effect class. Any safety-relevant `UNKNOWN` blocks new effect admission.

## Evidence hierarchy

Evidence is ranked by what it can establish; lower-ranked evidence cannot silently override contradictory higher-confidence evidence.

### E0 — local assumption

Code comments, remembered behavior, SDK defaults or operator belief. Never sufficient for production admission.

### E1 — provider documentation

Current official provider documentation for the exact service/operation/version. Establishes declared semantics only. Must retain retrieval timestamp, source locator and a content digest/snapshot reference where legally/operationally practical.

### E2 — safe observed probe

A controlled provider/account/region/API probe that exercises semantics without creating an externally consequential business effect. Establishes observed behavior for the tested environment and time. It does not prove an undocumented universal guarantee.

### E3 — documented + observed conformance

Provider documentation and independent safe probes agree on the authority-relevant property. Preferred activation evidence.

### E4 — authoritative outcome-query proof

For UNKNOWN/retry safety, a provider-supported independent status/read surface demonstrates the outcome associated with the bound provider identity. This can permit reconciliation when duplicate-token retention alone is insufficient.

Conflicts are fail-closed: if E2/E3 behavior contradicts E1 documentation, the capability enters `DRIFT_SUSPECTED` and new effects stop until the discrepancy is resolved. The runtime never chooses the more permissive interpretation automatically.

## Authenticated evidence envelope

Every record is stored through the existing authenticated global provenance chain; it must not form a parallel locally-valid trust island. The canonical record commits to:

- all canonical identity fields;
- property classifications and exact evidence digests;
- probe harness/version/configuration;
- provider-returned non-secret metadata needed to interpret results;
- timestamps and expiry/recheck deadlines;
- parent evidence generation;
- actor/authority that performed activation;
- reason for invalidation/supersession when applicable.

Secrets, bearer tokens and provider credentials are never embedded in the evidence record. Account identity uses a non-secret stable identifier/digest sufficient to prevent cross-account evidence reuse.

## Capability state machine

`DRAFT -> EVIDENCE_COMPLETE -> CONFORMANCE_VERIFIED -> ACTIVE`

Exceptional states:

- `DRIFT_SUSPECTED` — contradiction or unexpected probe result;
- `EXPIRED` — revalidation deadline passed;
- `INVALIDATED` — authority-relevant provider/adapter/account/config change;
- `UNSUPPORTED` — known inability to meet the effect-class contract;
- `SUPERSEDED` — replaced by a newer generation, while historical retry bindings remain valid under the older record's own rules.

Only `ACTIVE` admits **new** effects. No state transition can alter provider request identities already bound to existing operations.

## Activation gate

Before a new effect can reserve/bind a provider request identity, require:

1. exact effect class -> exact capability record resolution;
2. record state is `ACTIVE`;
3. authenticated provenance verification succeeds;
4. current provider/account/endpoint/adapter/API identity matches the record;
5. current time is within evidence validity/recheck bounds;
6. all safety-relevant properties are sufficiently evidenced;
7. token construction is injective after all known adapter/provider transforms for the active namespace;
8. dedupe retention/outcome-query semantics safely cover the runtime retry policy;
9. no newer invalidation/drift record exists;
10. post-re-root effects additionally satisfy the separately authorized trust/effect epoch cutover contract.

This gate happens before provider I/O and before an operation can become eligible for an external side effect.

## Already-bound retry rule

A durable operation stores at least:

- exact `capability_evidence_id`;
- exact provider request/token identity;
- effect payload/fingerprint identity;
- provider account/scope identity;
- first-send time and last safe resend deadline if retention is time-bounded;
- independently queryable outcome identity when available.

Later evidence drift does **not** rewrite these fields.

After capability invalidation:

- new effects are blocked immediately;
- an existing operation may retry only if the historical record still proves that this particular retry remains safe;
- if the safe resend horizon has expired, retry is forbidden;
- if an authoritative outcome query exists, reconciliation may continue without generating a new effect identity;
- otherwise state becomes fail-closed/manual reconciliation.

No retry is cloned into a new capability generation, new provider token or new trust epoch merely to regain availability.

## Evidence expiry and invalidation triggers

A capability must be re-evaluated on at least:

- explicit provider documentation change affecting idempotency/retry semantics;
- provider API version change;
- adapter release or token-construction change;
- account/project/tenant migration;
- endpoint/region/cluster scope change when scope is authority-relevant;
- credential-routing or proxy/gateway change capable of rewriting headers/parameters;
- observed behavior conflicting with the active record;
- expiry of the configured conformance interval;
- provider incident/advisory that may affect duplicate suppression or outcome queries;
- post-re-root namespace activation where domain separation must be re-proved.

Inability to fetch fresh documentation alone need not invalidate a still-within-policy record, but expiry of the evidence interval does. A record cannot renew itself based solely on its prior contents.

## Safe canary / drill contract

A conformance drill must not create an unbounded or user-visible business side effect. Preferred mechanisms, in order:

1. provider sandbox/test-mode endpoint whose semantics are documented to match production for the property under test;
2. provider operation with a naturally reversible/zero-impact resource dedicated to conformance;
3. read/conditional-write operation where preconditions make duplicate execution harmless;
4. explicitly provisioned synthetic test tenant/resource with bounded cost and automatic cleanup.

A drill must bind one unique probe run and record exact observed requests/responses stripped of secrets.

Minimum probe families where safely supported:

- same token + same payload repeated serially;
- same token + changed payload;
- concurrent same-token duplicates;
- same token across relevant scopes (region/cluster/resource/account test boundaries);
- adapter round-trip of maximum-length and case-distinct tokens;
- authoritative outcome query after induced client-side timeout when a non-consequential endpoint can safely simulate it;
- retention-boundary probe only when provider test facilities make it safe and economically bounded.

Never run a destructive/financial/user-visible canary merely to prove idempotency. If a required safety property cannot be tested safely and lacks sufficient authoritative documentation, mark it `UNKNOWN` and block that effect class rather than probing production destructively.

## Documentation-versus-probe reconciliation

- Documentation says safe, probe says safe: keep/activate if all other gates pass.
- Documentation says safe, probe contradicts: `DRIFT_SUSPECTED`, block new effects.
- Documentation is silent, probe says safe: observed evidence may support a narrow environment/time-bounded claim only if product policy explicitly allows E2 for that property; never generalize it to other scopes.
- Documentation says unsupported/unsafe, probe appears safe: treat as unsupported; do not override a restrictive provider contract with a fortunate observation.
- Documentation changes to be more restrictive: invalidate affected active records immediately once authenticated/verified.

## Drift response

When drift is detected:

1. atomically append authenticated `CAPABILITY_DRIFT_DETECTED` evidence;
2. block reservation/admission of new effects using the affected record;
3. leave existing provider-token bindings untouched;
4. classify already-bound operations by `safe_retry`, `query_only`, or `manual_reconciliation` using their historical record and timing;
5. create a candidate successor evidence generation only after research/probes;
6. require normal provenance activation before successor becomes `ACTIVE`;
7. never auto-replay operations from the invalidated generation through the successor.

## Relationship to LAB-100 provider capability authority

LAB-100 decides **which provider/adapter implementation is trusted to implement the external fencing/effect primitive**. This contract decides **what concrete idempotency semantics that implementation/provider combination is evidenced to have right now**. Both gates are required; passing one never substitutes for the other.

An exact trusted adapter with stale/unknown provider semantics blocks new effects. Conversely, strong provider documentation does not make an arbitrary caller-overridable adapter trustworthy.

## Relationship to LAB-093 application idempotency

Local permanent non-reuse prevents the runtime from knowingly issuing two application effects for one key. External capability evidence prevents a transport/provider retry from accidentally producing a second external effect because the remote dedupe domain was misunderstood or expired.

Neither layer replaces the other.

## Relationship to post-re-root cutover

After a historical discontinuity, a new trust/effect epoch may be technically eligible only if this evidence proves provider-side namespace separation after all real transformations. This contract cannot approve the security/product decision to perform the cutover; it only produces a fail-closed capability verdict for the exact provider/effect class.

## RED-first conformance matrix

The production implementation must start with executable regressions. Minimum V1 matrix:

### Evidence identity / provenance
1. active record matches exact provider/service/operation/account/adapter -> admits new effect.
2. same record reused for another account -> reject.
3. same record reused for another region when scope is regional -> reject.
4. adapter version changes without successor record -> reject.
5. token construction version changes -> reject.
6. evidence record tampered -> reject.
7. parent generation missing -> reject.
8. rollback to older active record after newer invalidation -> reject.

### Evidence completeness
9. token max length unknown but construction can exceed it -> reject.
10. normalization unknown and token alphabet can collide -> reject.
11. retention unknown while runtime permits delayed resend -> reject.
12. UNKNOWN outcome unqueryable and resend safety not proven -> reject.
13. changed-payload behavior unknown when local reuse bug could occur -> reject.
14. irrelevant unknown property does not block when formally excluded from effect claim.

### Documentation/probe hierarchy
15. documented + matching probe -> activate.
16. documented safe + contradictory probe -> drift/block.
17. documented unsafe + observed lucky success -> remain unsupported.
18. probe-only evidence cannot silently claim another account/region/API version.
19. stale documentation snapshot beyond recheck policy -> no new admission.
20. documentation retrieval failure before expiry does not rewrite active semantics.

### Provider transformation
21. adapter truncation creates two-token collision -> reject before provider I/O.
22. provider case folding collapses epoch-separated tokens -> reject.
23. account-scoped tokens proven independent across accounts -> keep scope explicit.
24. cluster-scoped token evidence cannot be promoted to global scope.
25. SDK silently replaces caller token -> reject.
26. gateway strips idempotency header/parameter -> reject.

### Retention / UNKNOWN
27. retry within proven retention horizon -> allowed under pinned record.
28. retry after retention horizon with no outcome query -> fail closed.
29. retry after retention horizon with authoritative completed outcome -> return/reconcile, no resend.
30. timeout with queryable pending outcome -> query/reconcile, no new token.
31. timeout with unqueryable UNKNOWN and unsafe resend -> manual reconciliation.
32. newer record with longer TTL cannot extend old operation's historical safe resend deadline.

### Drift / lifecycle
33. provider docs change restrictively -> invalidate new admission.
34. probe drift -> append drift evidence and stop new admission.
35. successor record activation does not mutate old retry bindings.
36. expired record cannot self-renew.
37. account migration invalidates account-bound evidence.
38. API-version upgrade invalidates version-bound evidence.
39. rollback to superseded generation is detected.
40. restart reconstructs same active/invalidation state from authenticated provenance.

### Canary safety
41. sandbox probe result is labelled sandbox-scoped unless production equivalence is authoritative.
42. destructive production probe request is refused by harness policy.
43. synthetic resource cleanup failure does not falsify semantic result but raises operational follow-up.
44. changed-payload probe never uses a real customer effect.
45. concurrent duplicate probe uses bounded synthetic effect only.
46. secrets are redacted from retained evidence.

### Cross-epoch / cutover
47. provider domain separation proven for E0/E1 tokens after all transforms -> eligible only after separate cutover authorization.
48. provider truncation erases epoch prefix -> block effect class.
49. legacy client cannot select successor capability without epoch acknowledgement.
50. old UNKNOWN cannot be cloned to successor epoch/capability.
51. old consumed key cannot become MISS because successor capability exists.
52. cutover authorization cannot activate a capability record with missing evidence.

### LAB-100 composition
53. trusted exact adapter + active evidence -> can proceed to other gates.
54. untrusted adapter + perfect provider evidence -> reject.
55. trusted adapter + expired evidence -> reject new effect.
56. runtime adapter identity mismatch after restart -> reject.

### Crash / atomicity
57. crash after drift append before in-memory block -> restart blocks from durable evidence.
58. crash after successor evidence creation before activation -> successor remains non-active.
59. crash after provider-token bind before first send -> retry uses exact same pinned identity.
60. crash after first send/UNKNOWN -> never generate successor token automatically.
61. concurrent admission racing with invalidation linearizes before or after authenticated invalidation; no admission observes an unauthenticated hybrid.
62. concurrent successor activations use parent-generation CAS; at most one becomes current.

### Negative guarantees
63. evidence never stores provider credentials/secrets.
64. provider docs alone never authorize post-re-root product/security cutover.

## Implementation boundary

V1 freezes semantics only. Production implementation waits for the repository's exact executable RED/GREEN capability to return. Do not implement this by a mutable JSON feature flag, environment variable, SDK-version heuristic or unauthenticated cache.

## Decision

`EXTERNAL_PROVIDER_IDEMPOTENCY_CAPABILITY_EVIDENCE_CONFORMANCE_LIFECYCLE_V1_FROZEN`.

The runtime may trust external idempotency only as an exact, versioned, authenticated, scope-bound and time-bounded capability claim. Documentation and safe probes are evidence inputs, not permanent truth. Drift blocks **new** effects immediately while already-bound operations retain their original provider request identity and can only retry within the safety proven by their historical evidence. Unknown or expired remote semantics reduce availability; they never authorize a fresh side effect.