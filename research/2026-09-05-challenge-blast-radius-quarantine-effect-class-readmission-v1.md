# Challenge blast-radius quarantine / effect-class re-admission V1

Status: `CHALLENGE_BLAST_RADIUS_QUARANTINE_EFFECT_CLASS_READMISSION_V1_FROZEN`

Date: 2026-09-05

Scope: design contract only; no production behavioral PASS is claimed.

## Objective

Define how a source-capability, evidence, verdict, credential, provider-semantics, or global-provenance challenge maps to the smallest safe quarantine set; how read-only reconciliation continues while external send/mutation authority is removed; and how an effect class can later be re-admitted without reviving old request identities, clearing consumed keys, weakening trust-epoch boundaries, or bypassing explicit product/security/business authorization.

This contract extends the frozen manual-reconciliation challenge lifecycle and the previously frozen provider-capability / UNKNOWN-oracle / post-reroot contracts.

## Core security decision

**Quarantine is authority subtraction, never historical mutation. Re-admission is a new authenticated authority generation, never rollback or un-quarantine-by-flag.**

A challenge may remove external-effect authority from only the dependency closure that actually relies on the challenged object. Unrelated effect classes may continue if and only if their complete current authority graph is independently valid.

## Non-negotiable invariants

1. **Minimal safe blast radius.** Quarantine is derived from a typed dependency graph, not from global panic and not from operator intuition.
2. **Fail closed on uncertainty.** Unknown dependency edges expand quarantine; they never shrink it.
3. **Read != send.** Read-only evidence collection, status queries, reconciliation, audit, and provenance verification may remain available while SEND/MUTATE/RESUME/TOKEN-MINT authority is removed.
4. **Historical identities stay consumed.** Quarantine/re-admission never resets an application idempotency key, provider token, request ID, operation ID, consumed-key epoch, or historical effect namespace.
5. **No stale-generation resurrection.** A quarantined capability/effect generation can never become current again by deleting a challenge row, restoring an old config, or replaying an older checkpoint.
6. **Authenticated monotonic generations.** Every quarantine and re-admission transition is parent-linked to the shared LAB-097..100 global provenance chain and guarded by expected-head CAS.
7. **Provider/effect-class granularity.** Quarantine keys include provider/service/operation/API/account/region/scope/adapter/effect-class and trust/effect-namespace generation where relevant.
8. **In-flight UNKNOWN is conservative.** Removing send authority never permits resending an UNKNOWN; read-only reconciliation may continue under a still-trusted oracle.
9. **Re-admission requires fresh proof.** Replacing or repairing a capability is not enough by itself. The new generation must satisfy evidence, quorum, compatibility, drill/canary, and startup-verifier gates before new effects are admitted.
10. **Consequential discontinuity remains owner-bound.** Where post-reroot or trust discontinuity already requires explicit product/security/business authorization, re-admission cannot bypass that requirement.

## Donor mechanisms and rationale

### NIST incident response

NIST SP 800-61 Rev. 3 treats response and recovery as integrated risk-management activities rather than a one-shot reset. The design adopts the same containment -> recovery separation: quarantine constrains authority first; restoration happens only after evidence supports a safe recovery state.

### Least privilege / assessment

NIST SP 800-53 / 800-53A provide the donor principle that privileges and controls should be limited to what is necessary and assessed before reliance. The quarantine model therefore removes only affected mutation privileges and preserves lower-capability read/reconciliation functions where their trust dependencies remain intact.

### TUF threshold/root recovery

TUF's root-role model is a donor for compromise-resilient re-authorization: compromised keys are replaced by currently trusted root authority; if the root threshold itself is compromised, recovery must occur out of band. Re-admission therefore cannot be self-authorized by the challenged generation or by a silently lowered threshold.

### Transparency witnesses

C2SP witness/checkpoint semantics provide the donor for rollback resistance: witnesses track the latest verified checkpoint and only advance when consistency is proven. Quarantine/re-admission generations therefore advance monotonically and must not accept an older locally valid state as current.

## Canonical authority objects

All objects use the shared canonical V1 encoding/digest rules frozen by the LAB-097..100 provenance line.

### `QuarantineTriggerV1`

Required fields:

- `trigger_id`
- typed challenge/revocation/provenance source object ID
- discovery/effective time
- exact challenged authority generation
- asserted affected dimensions
- evidence references
- reporter identity
- global provenance parent

A trigger has no direct send authority and does not itself choose the final blast radius.

### `AuthorityDependencyEdgeV1`

Represents a versioned edge from an authority object to a runtime capability/effect class.

Fields include:

- `from_authority_id`
- `to_authority_id_or_effect_class`
- dependency kind: `AUTHENTICATION`, `NEGATIVE_PROOF`, `POSITIVE_PROOF`, `IDEMPOTENCY`, `OUTCOME_ORACLE`, `PROVIDER_FENCE`, `ACTIVATION`, `SIGNING`, `REVIEW_QUORUM`, `GLOBAL_PROVENANCE`, `TRUST_EPOCH`, `NAMESPACE_SEPARATION`
- provider/service/operation/API/account/region/scope/adapter selectors when applicable
- generation bounds
- mandatory/optional flag
- canonical edge digest

Edges that can affect consequential authority MUST be created before use of that authority generation. A newly discovered undocumented dependency is treated as a challenge to the affected current generation until incorporated and reassessed.

### `QuarantineGenerationV1`

Required fields:

- monotonically increasing `quarantine_generation`
- parent generation digest
- trigger closure digest
- quarantined selectors/effect classes
- retained read-only capabilities
- explicitly removed capabilities (`SEND`, `MUTATE`, `RESUME`, `TOKEN_MINT`, `ACTIVATE`, `ROTATE`, etc.)
- in-flight case disposition rules
- authorizing policy/quorum
- global provenance parent

The authoritative runtime decision is derived from the latest valid generation, not from mutable per-class flags.

### `ReadOnlyReconciliationGrantV1`

Optional least-capability grant for a quarantined class.

It may permit only predeclared operations such as:

- provider status GET/describe/list with exact scope;
- read-only outcome-oracle query;
- evidence retrieval;
- transparency/witness verification;
- local verification/audit;
- append-only reconciliation evidence ingestion.

It MUST NOT permit:

- retry/resend;
- resume that may execute the original effect;
- provider mutation;
- new idempotency token construction;
- activation/release/abort actions with external side effects;
- credential/key rotation unless governed by a separate trusted recovery authority.

### `ReAdmissionCandidateV1`

Binds a proposed replacement/current-safe generation:

- exact effect-class selector
- predecessor quarantine generation
- successor capability IDs/generations
- provider semantic evidence package
- oracle/idempotency/fencing evidence as required
- trust-epoch/effect-namespace identity
- compatibility result
- conformance/drill result
- reviewer/authorizer quorum
- explicit statement that historical request identities remain consumed/retired
- required owner authorization reference when trust discontinuity rules demand it

### `ReAdmissionDecisionV1`

Allowed decisions:

- `REJECT`
- `KEEP_QUARANTINED`
- `READ_ONLY_ONLY`
- `ADMIT_NEW_EFFECTS`

There is deliberately no `RESTORE_OLD`, `RETRY_OLD`, `CLEAR_CONSUMED`, or `ROLLBACK_QUARANTINE` decision.

## Blast-radius algorithm

The verifier computes quarantine from the authoritative dependency graph.

### Step 1: resolve challenged roots

Start from exact challenged/revoked objects: source capability generation, evidence authority, reviewer/authorizer credential, provider semantic generation, reconciliation oracle, trust root, provenance checkpoint, or policy predicate.

### Step 2: compute consequential dependency closure

Traverse only authority-relevant edges to effect classes and in-flight operations.

The closure is keyed by exact dimensions, not provider name alone. Example:

`provider=P / service=S / operation=CreateX / account=A / region=R / adapter=v3 / effect_class=money_move`

may be quarantined while an independently evidenced read-only `DescribeX` class remains usable.

### Step 3: widen on unknowns

If the graph cannot prove whether a consequential class depends on the challenged authority, that class is included. Missing dependency evidence never permits exclusion.

### Step 4: subtract capabilities

For each affected class, remove the minimum unsafe capabilities. A source-idempotency challenge may remove `SEND` while preserving an independent read-only outcome oracle. A global provenance/root challenge may require full authority suspension because even local dependency facts are no longer trustworthy.

### Step 5: classify in-flight operations

For each operation:

- `CONFIRMED/COMMITTED` remains historical and consumed;
- `UNKNOWN` remains consumed and may only use still-trusted read-only reconciliation;
- `PREPARED` with no external send yet may be cancelled locally only if cancellation itself is proven side-effect-free and provenance-safe;
- provider-side pending/fenced operations remain quarantined and follow their pre-existing recovery contract; quarantine does not invent abort/release authority.

## Quarantine modes

### `SEND_BLOCKED_READ_ALLOWED`

Use when mutation authority is suspect but a separately trusted read-only oracle remains valid.

### `EFFECT_CLASS_BLOCKED`

All consequential external mutations for the exact class are disabled; local audit and unaffected classes may continue.

### `PROVIDER_SCOPE_BLOCKED`

Use when compromise/drift cannot be bounded below one provider/account/region/scope boundary.

### `RUNTIME_MUTATION_BLOCKED`

Use when a shared authority such as signing/provenance/activation is challenged across multiple classes.

### `GLOBAL_FAIL_CLOSED`

Use only when the root/global provenance/dependency graph itself is untrustworthy or the safe blast radius cannot be bounded. This is not the default for an isolated provider capability challenge.

## Startup and delegation contract

Startup computes one `EffectiveAuthoritySnapshotV1` from:

- current authenticated global provenance head;
- current challenge closure;
- latest quarantine generation;
- current provider-capability generations;
- trust epoch/effect namespace;
- unresolved manual-reconciliation cases;
- active re-admission decisions.

Delegation tokens/capabilities MUST be minted from this snapshot. A worker or agent receives no SEND/MUTATE capability for a quarantined class even if stale local configuration says otherwise.

A stale worker holding an earlier capability generation must fail at the authoritative broker/ledger boundary because the request carries an obsolete authority-generation binding.

## Read-only reconciliation during quarantine

Read-only reconciliation may continue only if:

1. the oracle/source used for reading is outside the challenged dependency closure;
2. exact account/region/scope/operation identity is preserved;
3. the query itself cannot mutate or resume the effect;
4. evidence is appended under the current quarantine generation;
5. weak negative results remain weak negatives;
6. no query mints a new provider request identity.

If the only reconciliation oracle is challenged, automation may continue local verification but must move the external UNKNOWN to manual/security reconciliation rather than resend.

## Re-admission gates

`ADMIT_NEW_EFFECTS` requires all applicable gates:

1. **Challenge disposition:** triggering challenge is resolved, superseded, or explicitly bounded away from the candidate generation.
2. **Fresh capability generation:** no reuse of the challenged capability generation.
3. **Authenticated provenance continuity:** successor is parent-linked from the current global head; no rollback/fork.
4. **Dependency graph completeness:** all consequential dependencies for the class are declared and verified.
5. **Provider semantics evidence:** idempotency, normalization, retention, scope, UNKNOWN/oracle and fencing semantics satisfy the frozen provider-capability contract.
6. **Namespace separation:** trust epoch/effect namespace/provider token construction cannot collide with historical identities when discontinuity exists.
7. **Conformance/drill:** safe sandbox/synthetic/reversible/zero-impact validation passes for the exact provider/API/adapter generation where available.
8. **Independent review/quorum:** challenged credentials/generations have zero weight in approving their own replacement.
9. **Startup/recovery verification:** restart from durable state derives the same admitted snapshot without repair-by-assumption.
10. **Owner authorization if required:** post-reroot/consequential discontinuity boundaries remain binding.

Re-admission applies only to **new effect identities** created after the decision's authority point. Historical UNKNOWN/consumed operations remain governed by their original pinned generation and reconciliation rules.

## Rollback resistance

A valid older quarantine/re-admission object is not sufficient authority if a newer generation exists.

Required checks:

- monotonic generation number;
- exact parent digest;
- global provenance head membership;
- witness/checkpoint freshness where configured;
- expected-head CAS on append;
- startup rejection of locally restored but globally stale state.

Deleting the latest quarantine row must not reveal an older admitted state as current. Recovery must use the shared global provenance/recovery contract rather than local `MAX(generation)` alone.

## Concurrency and crash ordering

### Challenge arrives while a new effect is being admitted

The authoritative send gate rechecks the latest effective authority snapshot immediately before external I/O. If the quarantine head advanced, the operation fails before send.

### Crash before quarantine append

No new quarantine authority exists; the triggering evidence remains staged and must be reprocessed idempotently.

### Crash after quarantine append but before worker revocation propagation

Broker/ledger-side generation checking remains authoritative; stale worker capabilities fail even before local revocation propagation completes.

### Crash during re-admission

Intermediate candidate/drill/review records do not grant SEND. Only the final parent-linked `ReAdmissionDecisionV1(ADMIT_NEW_EFFECTS)` changes authority.

## Authority separation

Automation MAY:

- ingest authenticated challenge evidence;
- compute dependency closure;
- append a quarantine generation that only subtracts authority;
- continue permitted read-only reconciliation;
- run safe conformance checks;
- assemble a re-admission candidate;
- reject candidates that fail deterministic gates.

Automation MUST NOT autonomously grant consequential authority when:

- required owner authorization is missing;
- root/global provenance authority is challenged;
- clearing the challenge requires threshold downgrade;
- the new effect namespace follows an acknowledged trust discontinuity requiring explicit business/security acceptance;
- provider semantics cannot be demonstrated safely;
- independent quorum is unavailable.

## RED-first matrix (64 minimum)

### Dependency closure / minimal blast radius (12)
1. exact capability challenge quarantines only dependent class;
2. unrelated provider class remains admitted with independent graph;
3. unknown dependency edge widens quarantine;
4. optional non-authority telemetry edge does not quarantine send;
5. shared signer challenge quarantines all classes depending on signer;
6. account-scoped challenge does not hit independently evidenced other account;
7. region-scoped challenge remains region-bounded when evidence proves scope;
8. provider-wide compromise expands to all dependent accounts/scopes;
9. negative-proof predicate challenge removes only classes requiring it;
10. root/global provenance challenge selects global fail-closed;
11. dependency graph rollback is detected;
12. undeclared newly discovered consequential edge challenges current generation.

### Capability subtraction / read-only mode (10)
13. SEND removed while trusted status GET remains allowed;
14. read-only oracle cannot call provider mutation endpoint;
15. reconciliation query cannot mint new token;
16. resume endpoint classified as mutating and blocked;
17. local verification remains allowed;
18. evidence ingestion remains append-only;
19. weak NOT_FOUND remains weak during quarantine;
20. only oracle challenged -> manual reconciliation, no resend;
21. stale worker SEND capability rejected at broker/ledger gate;
22. local stale config cannot override current quarantine generation.

### In-flight identity safety (10)
23. historical COMMITTED key remains consumed;
24. UNKNOWN token remains retired/consumed;
25. quarantine never creates MISS;
26. re-admission never retries old UNKNOWN;
27. old provider token cannot be reused in new generation;
28. PREPARED/no-send cancellation allowed only under side-effect-free proof;
29. provider-side pending fence does not gain synthetic abort authority;
30. stale retry after re-admission remains pinned to old generation;
31. trust-epoch change forces new namespace for new effects;
32. same application key in old namespace cannot be silently mapped to new namespace.

### Re-admission evidence / quorum (14)
33. fresh replacement capability + all gates -> new effects admitted;
34. same challenged generation -> reject;
35. missing provenance parent -> reject;
36. stale global head -> reject;
37. provider semantics drift unresolved -> keep quarantined;
38. idempotency retention not evidenced -> keep send blocked;
39. unsafe provider namespace collision -> reject;
40. safe conformance drill passes exact generation;
41. drill from different account/API/adapter cannot substitute;
42. challenged reviewer has zero quorum weight;
43. independent replacement quorum succeeds;
44. threshold downgrade attempt -> reject;
45. required owner authorization absent -> no consequential admission;
46. owner authorization bound to different payload/effect class -> reject.

### Rollback / crash / concurrency (12)
47. delete latest quarantine row -> startup does not resurrect older admit;
48. restore stale DB snapshot -> global head mismatch fail closed;
49. crash before quarantine append -> no authority change;
50. crash after append -> restart preserves quarantine;
51. challenge races send -> final authority recheck blocks send;
52. stale worker after crash cannot send;
53. concurrent independent challenges both preserved;
54. re-admission CAS on stale parent -> reject;
55. crash before final re-admission decision -> no SEND;
56. crash after final decision -> restart derives same authority snapshot;
57. replay same re-admission decision idempotent;
58. forked quarantine generations -> security-owner/global recovery path.

### Scope / audit / owner boundary (6)
59. quarantine records exact provider/account/region/effect selectors;
60. read-only grant access is audited;
61. redacted operator view cannot alter authority digest;
62. product/security/business authorization boundary survives re-admission;
63. automation may subtract authority without owner decision when authenticated policy requires containment;
64. automation cannot add consequential authority across a trust discontinuity requiring owner approval.

## Explicit non-goals

This contract does not:

- define a new provider retry mechanism;
- clear historical UNKNOWN cases;
- authorize a post-reroot business cutover;
- replace the provider-capability or outcome-oracle contracts;
- make SQLite/local state the sole source of freshness;
- define a generic incident-management UI.

## Frozen implementation direction

When exact executable source becomes available, implement RED-first in the shared authority/provenance layer rather than adding provider-specific quarantine booleans.

Minimum implementation slices:

1. canonical dependency-edge and quarantine-generation schemas;
2. deterministic closure verifier;
3. effective-authority snapshot derivation;
4. broker/ledger final send-gate generation binding;
5. least-capability read-only reconciliation grants;
6. re-admission candidate verifier and final decision state machine;
7. crash/restart/global-provenance regressions;
8. exact composition tests with LAB-093 provider capability, UNKNOWN oracle, challenge lifecycle, post-reroot trust epoch, and LAB-097..100 provenance/startup contracts.

No production implementation should claim PASS until these RED cases execute against the actual integrated runtime surface.

## Sources / primary donors

- NIST SP 800-61 Rev. 3, *Incident Response Recommendations and Considerations for Cybersecurity Risk Management*, final April 2025 — containment/recovery framing.
- NIST SP 800-53 Rev. 5 / SP 800-53A Rev. 5 — least privilege and independent assessment concepts.
- The Update Framework specification/FAQ — threshold root compromise, revocation and out-of-band root recovery model.
- C2SP Transparency Log Witness Protocol / Trust Policy — latest verified checkpoint, consistency proof and quorum witness model for rollback/split-view resistance.

## Decision

Freeze `CHALLENGE_BLAST_RADIUS_QUARANTINE_EFFECT_CLASS_READMISSION_V1_FROZEN`.

The next distinct fallback, if exact execution remains unavailable, should define an **authority dependency manifest / policy compiler + static/runtime completeness verifier contract**: how dependency edges are declared from code/config/provider adapters, how omitted consequential dependencies are detected, how the manifest is signed/versioned and bound to builds, and how runtime proves that every SEND/MUTATE surface is dominated by the effective-authority gate rather than relying on manually maintained graph declarations.