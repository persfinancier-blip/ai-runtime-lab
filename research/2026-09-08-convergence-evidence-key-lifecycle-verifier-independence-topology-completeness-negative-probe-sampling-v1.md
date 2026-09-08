# Convergence-evidence key lifecycle, verifier independence, topology completeness and negative-probe sampling — v1

Status: `CONVERGENCE_EVIDENCE_KEY_LIFECYCLE_VERIFIER_INDEPENDENCE_TOPOLOGY_COMPLETENESS_NEGATIVE_PROBE_SAMPLING_V1_FROZEN`

Date: 2026-09-08

## Context

The preceding convergence-evidence contract established that raw telemetry is not authority, the governed cohort inventory defines the denominator, effective cutover must be proven at the data plane, and silence is not decommission evidence.

That leaves four second-order roots of trust that must not remain implicit:

1. the signing/verifying keys used by evidence issuers and attestation verifiers;
2. the claimed independence of multiple verifiers;
3. the discovery mechanism that claims to enumerate every authority-bearing path;
4. the negative-probe mechanism that claims an old lineage can no longer perform consequential operations.

If these are not frozen explicitly, an attacker can produce perfectly signed but stale evidence after key compromise, count several aliases of one control domain as an independent quorum, hide a stale replica from the topology feed, or steer synthetic `L0` probes only toward migrated replicas while real traffic can still reach an accepting replica.

This contract freezes those boundaries.

## Primary-source findings

### RATS: a Verifier is itself part of the trust model

RFC 9334 separates Evidence, Verifier appraisal and Attestation Results. The Relying Party must trust the Verifier, its appraisal result, and the relevant appraisal policy. The architecture explicitly notes that a Relying Party can require the Verifier itself to act as an Attester before trusting it. This supports treating verifier identity/implementation/policy as an authority subject, not as an unquestioned oracle.

Source: RFC 9334, Remote ATtestation procedureS (RATS) Architecture, January 2023: https://www.rfc-editor.org/rfc/rfc9334.html

### NIST key lifecycle: compromise changes future authority but historical metadata remains necessary

NIST SP 800-57 Part 1 Rev. 5 defines key lifecycle states, requires compromise/revocation transitions to be recorded, and recommends retaining metadata for audit even when public keys are no longer used operationally. It also distinguishes processing historical protected information from using a compromised private key to create new protection.

Source: NIST SP 800-57 Part 1 Rev. 5, Recommendation for Key Management: https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final

### SCITT: receipt transparency proves registration, not truth of the signed claim

RFC 9943 makes Signed Statements and their transparency receipts independently verifiable. The Relying Party still applies signature, key/identity and local validation policy. A receipt proves that a particular statement was registered in the transparency system; it does not prove that the issuer's claim was semantically true.

Source: RFC 9943, An Architecture for Trustworthy and Transparent Digital Supply Chains, August 2025: https://www.rfc-editor.org/rfc/rfc9943.html

### Kubernetes: topology is versioned state, not a one-time endpoint list

Kubernetes EndpointSlices enumerate service backends and include serving/ready/terminating state plus node/zone information. Multiple EndpointSlices may represent one Service, and different controllers may manage slices. The API list/watch model binds a collection snapshot to `resourceVersion` and then tracks later mutations; if watch history is lost, the client must perform a fresh list rather than assume continuity.

Sources:
- EndpointSlices: https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/
- Kubernetes API concepts / list-watch and `resourceVersion`: https://kubernetes.io/docs/reference/using-api/api-concepts/

### SPIRE: attestation identity depends on independently validated node/workload attributes

SPIRE node attestation verifies node identity using platform-specific attestors and associates selectors with the resulting identity. Workload registration then maps identities to selectors and parent identity. This is a useful donor for binding evidence producers/verifiers to independently checked execution identity instead of accepting a self-declared logical name.

Source: SPIRE concepts: https://spiffe.io/docs/latest/spire-about/spire-concepts/

## Frozen boundaries

`VALID_EVIDENCE_SIGNATURE != CURRENT_EVIDENCE_ISSUER_AUTHORITY`

`DISTINCT_VERIFIER_IDENTITIES != INDEPENDENT_VERIFIERS`

`SERVICE_DISCOVERY_SNAPSHOT != COMPLETE_AUTHORITY_TOPOLOGY`

`NEGATIVE_PROBE_PASS != UNIVERSAL_L0_REJECTION`

`TRANSPARENCY_RECEIPT != CLAIM_TRUTH`

A convergence completion claim must satisfy every relevant boundary separately.

## Threat model

Assume migration from lineage `L0` to `L1` and an attacker/failure model including:

- an old evidence-issuer private key is compromised after legitimate historical statements were emitted;
- a verifier key is rotated but stale verifiers still accept the old key for new Attestation Results;
- several verifier IDs are aliases behind one operator, one signing key, one build pipeline or one appraisal-policy administrator;
- a verifier implementation is compromised while continuing to emit cryptographically valid results;
- the service-discovery feed omits shadow listeners, canary pools, manually configured endpoints, DR replicas, direct IP paths, terminating-but-serving endpoints or stale load-balancer members;
- autoscaled instances are created after a topology snapshot and before the probe round completes;
- the load balancer recognizes synthetic probe metadata/source IP/user-agent and routes probes only to migrated replicas;
- probabilistic probes repeatedly miss a small stale pool;
- a topology controller and data-plane router disagree about effective membership;
- a transparency log records a false all-green statement exactly as signed.

## Frozen data model

### `ConvergenceEvidenceAuthorityV1`

Every issuer/verifier authority generation binds:

- `authority_domain_id`;
- `authority_generation`;
- role: `EVIDENCE_ISSUER`, `ATTESTATION_VERIFIER`, `TOPOLOGY_ATTESTER`, `PROBE_COORDINATOR`, `CUTOVER_APPRAISER`;
- public verification key/certificate identity and algorithm;
- activation boundary;
- optional deactivation/retirement boundary;
- compromise status and, when known, effective compromise boundary;
- permitted evidence/attestation classes;
- appraisal-policy digest or allowed policy set;
- implementation/build measurement requirements where applicable;
- operator/control-domain identity;
- predecessor/successor authority relation;
- canonical digest and authorizing signatures/quorum;
- transparency registration receipt/checkpoint when policy requires it.

Planned retirement does not invalidate historical statements issued while the key was authorized. A known compromise boundary invalidates authority for statements after that boundary. If compromise onset is unknown and a completion claim depends on the affected authority, the historical result is `UNKNOWN_EVIDENCE_AUTHORITY_DUE_TO_COMPROMISE_WINDOW` rather than silently accepted.

### `AttestationVerifierIndependenceProfileV1`

Independence is appraised across explicit failure/control domains, not inferred from the number of signatures. Bind at minimum:

- operator/administrative owner;
- signing-key custody/HSM domain;
- verifier implementation/build lineage;
- deployment/runtime cluster or host domain;
- cloud/hosting provider and region/failure zone where material;
- network ingress/egress/control plane;
- appraisal-policy author/approval domain;
- reference-value/endorsement source dependencies;
- software supply-chain/release authority;
- telemetry/evidence source dependencies.

Two verifiers that share a policy administrator, signing key, runtime cluster and evidence collector are not independent merely because they have different service names.

A quorum policy must specify acceptable intersection/correlation limits. Numeric `m-of-n` without independence appraisal is insufficient for a high-assurance convergence claim.

### `AuthorityTopologySnapshotV1`

A topology snapshot used for cutover proof binds:

- `topology_generation`;
- migration/rebootstrap generation;
- exact operation classes being retired from `L0`;
- every known authority-bearing logical service;
- every effective gateway/listener/region/zone;
- load-balancer/backend-pool membership;
- service-discovery endpoints;
- caches/edge workers that can make or preserve authority decisions;
- async workers/queues that can execute consequential requests;
- DR/failover/shadow/canary/manual endpoints;
- autoscaling groups/templates and rules able to instantiate new authority-bearing replicas;
- direct-address/private-network bypass paths where supported;
- lifecycle state (`SERVING`, `DRAINING`, `TERMINATING_SERVING`, `FENCED`, `DECOMMISSIONED`);
- source-specific version/freshness marker, such as Kubernetes `resourceVersion`;
- canonical digest and authenticated source statement.

One discovery feed cannot prove its own completeness. A high-assurance snapshot must reconcile at least two differently controlled evidence planes when available, for example:

1. desired/control-plane membership (service discovery / orchestrator / LB config), and
2. observed/effective data-plane membership (router/LB/backend connection telemetry, direct reachability, or independently enumerated infrastructure inventory).

Material disagreement yields `TOPOLOGY_CONFLICT_NO_COMPLETION`.

### `TopologyCoverageLedgerV1`

For each topology generation, maintain append-only coverage state:

- discovered subject identity;
- discovery source(s);
- first/last observed generation;
- whether authority-bearing;
- required probe class;
- probe attempts/results;
- decommission/fence evidence;
- replacement/supersession identity;
- unresolved discrepancies;
- final coverage classification.

An endpoint does not disappear from coverage because a later feed omitted it. Explicit lifecycle/decommission evidence is required to retire it.

### `NegativeCutoverChallengeV1`

A probe challenge binds:

- migration generation and `L0` lineage digest;
- operation class;
- committed `AuthorityTopologySnapshotV1` digest;
- target selection method;
- unpredictable challenge nonce/seed committed after the topology snapshot;
- direct target identity or routing-path class;
- indistinguishability requirements if using production routing;
- request/effect identity;
- expected rejection class;
- expiry/freshness boundary;
- probe coordinator identity;
- canonical digest/signature.

The target set must be committed **before** random sampling/challenge generation so a controller cannot remove an inconvenient replica after seeing which endpoints will be tested.

### `NegativeCutoverProbeResultV1`

Each result binds:

- exact challenge digest;
- resolved network/service target identity;
- actual responder/backend identity when observable;
- route/LB metadata needed to prove which backend handled the request;
- observed response/rejection;
- proof that no consequential effect occurred where the operation is effectful;
- trusted freshness data;
- issuer and verifier identities;
- appraisal-policy digest;
- signature and optional transparency receipt.

A `403`/rejection response without backend identity does not prove all replicas reject `L0`.

## Negative-proof strategy

### Tier 1 — direct exhaustive endpoint proof

For bounded critical topology, prefer exhaustive endpoint-addressed or backend-pinned probes that bypass load-balancer steering and prove every authority-bearing replica rejects `L0` consequential authority.

Required when:

- the fleet is small enough;
- a stale replica would create high-impact authority bypass;
- backend identity can be reached safely and independently.

### Tier 2 — production-path randomized challenge

When direct probing is impossible, use post-commit unpredictable challenges over the real routing path.

Safety conditions:

- probes must be indistinguishable from ordinary requests to routing logic to the extent practical;
- route/backend identity must be attested or independently observed;
- challenge seed is generated after topology snapshot commitment;
- the sampling plan predeclares confidence parameters and maximum tolerated unobserved stale fraction;
- results are grouped by region/zone/pool/path so heavy traffic to one pool cannot hide another;
- a routing layer that can intentionally distinguish probes is treated as part of the trusted computing base and must itself be attested/audited.

A probabilistic result is never labeled universal proof. It yields a claim such as `NO_L0_ACCEPTANCE_OBSERVED_AT_DECLARED_SAMPLING_BOUND`.

### Tier 3 — synthetic-only health probes

Synthetic health-check endpoints or headers that the load balancer can special-case are diagnostic only. They cannot independently satisfy cutover authority proof.

## Autoscaling and topology race contract

Topology is not static during a cutover. Therefore:

1. acquire/authenticate topology snapshot generation `T`;
2. commit `digest(T)`;
3. generate challenge seed after that commitment;
4. probe all required subjects/classes for `T`;
5. concurrently watch topology mutations from `T` forward;
6. any newly created/reintroduced authority-bearing endpoint enters the required coverage set before completion;
7. if watch continuity is lost, perform a fresh consistent list/snapshot and reconcile rather than assuming no changes;
8. freeze completion only at a frontier where every subject introduced up to that frontier is either successfully cut over/fenced or explicitly decommissioned.

This borrows the Kubernetes list-then-watch property: a snapshot plus a versioned continuation is stronger than a one-time list.

## Evidence/verifier key rotation

For evidence and Attestation Result keys:

- new keys require explicit predecessor-authorized rotation or an already frozen external rebootstrap path;
- old and new key generations have non-overlapping or explicitly bounded issuance authority intervals;
- verifiers/relying parties preserve old public material needed for historical verification;
- new consequential statements after activation must not be accepted from a retired key merely because the signature verifies;
- compromise notices are append-only and propagated independently of cache TTL;
- ambiguity about whether a statement falls inside an unknown compromise window blocks use toward a convergence-complete claim;
- rotation policy and appraisal-policy generation are both bound into the signed result.

## Verifier-quorum independence contract

A convergence policy may require multiple Attestation Results, but quorum acceptance is allowed only after `AttestationVerifierIndependenceProfileV1` appraisal.

At minimum, the selected quorum must not be entirely capturable by one of the policy-declared fault domains. Examples:

- three logical verifiers all using one signing key count as one key-custody domain;
- three services deployed on the same cluster/build/policy controller do not provide three implementation/control-plane failure domains;
- two verifiers that consume one unauthenticated topology feed do not independently prove topology completeness;
- two verifiers independently appraising the same authenticated evidence can provide appraisal diversity, but not evidence-source diversity.

If the system cannot establish required independence, verdict is `VERIFIER_INDEPENDENCE_UNPROVEN`, not an inflated numeric quorum.

## Fail-closed verdicts

- `UNKNOWN_EVIDENCE_AUTHORITY_DUE_TO_COMPROMISE_WINDOW`
- `STALE_EVIDENCE_AUTHORITY_GENERATION`
- `ATTESTATION_POLICY_GENERATION_UNKNOWN`
- `VERIFIER_INDEPENDENCE_UNPROVEN`
- `VERIFIER_QUORUM_CORRELATED`
- `TOPOLOGY_SNAPSHOT_STALE`
- `TOPOLOGY_WATCH_CONTINUITY_LOST`
- `TOPOLOGY_CONFLICT_NO_COMPLETION`
- `UNRESOLVED_AUTHORITY_ENDPOINT`
- `PROBE_TARGET_IDENTITY_UNPROVEN`
- `PROBE_STEERING_SUSPECTED`
- `NEGATIVE_PROBE_COVERAGE_INSUFFICIENT`
- `CONVERGENCE_EVIDENCE_CONFLICT_NO_COMPLETION`

None of these may be converted to success via latest timestamp, majority telemetry, dashboard percentage, LWW or silence.

## Fraud / contradiction proofs

Freeze the following proof classes for executable implementation:

1. `STALE_EVIDENCE_KEY_USE_PROOF` — statement issued under a retired generation after its allowed boundary.
2. `EVIDENCE_KEY_COMPROMISE_WINDOW_PROOF` — relied-upon statement lies in an unknown/known-compromised interval.
3. `VERIFIER_ALIAS_CORRELATION_PROOF` — nominally distinct verifiers share a prohibited fault domain.
4. `VERIFIER_POLICY_REBIND_PROOF` — attestation result uses an appraisal-policy generation different from the authorized one.
5. `TOPOLOGY_OMISSION_PROOF` — effective routing/infra evidence names an authority-bearing endpoint absent from governed topology.
6. `TOPOLOGY_RESURRECTION_PROOF` — decommissioned/fenced endpoint later reappears as serving.
7. `TOPOLOGY_WATCH_GAP_PROOF` — completion used a snapshot whose mutation stream lost continuity without resnapshot/reconciliation.
8. `PROBE_STEERING_PROOF` — synthetic probes are routed under a materially different rule/path from production traffic.
9. `PROBE_BACKEND_IDENTITY_MISMATCH_PROOF` — claimed target differs from attested/observed responder.
10. `NEGATIVE_EFFECT_CONTRADICTION_PROOF` — response claims rejection while durable downstream effect evidence shows the consequential action occurred.
11. `SAMPLING_DENOMINATOR_LAUNDERING_PROOF` — target pool changed after challenge selection without carrying new members into coverage.
12. `TRANSPARENCY_TRUTH_CONFUSION_PROOF` — a receipt is presented as semantic proof without valid issuer/verifier appraisal.

## RED-first executable matrix

### Key lifecycle — 10 cases

1. active issuer key/current policy accepted;
2. retired issuer key verifies cryptographically but cannot issue a new convergence statement;
3. pre-retirement historical statement remains verifiable;
4. known post-compromise statement rejected;
5. unknown compromise onset yields unknown historical authority;
6. new verifier key without predecessor/rebootstrap authorization rejected;
7. stale cache still trusting old verifier generation rejected after observed successor;
8. appraisal-policy digest mismatch rejected;
9. transparency receipt for unauthorized key does not rescue statement;
10. crash during key-generation activation cannot create two current issuance generations.

### Verifier independence — 10 cases

11. two genuinely independent verifier domains satisfy 2-of-2 policy;
12. two logical IDs sharing one signing key count as correlated;
13. separate keys but same verifier process/build/policy owner fail a policy requiring implementation diversity;
14. separate processes but one evidence collector fail evidence-source-diversity requirement;
15. one verifier compromised, independent peer contradiction blocks completion;
16. majority of correlated aliases cannot outvote one independent contradiction;
17. verifier self-declared independence without authenticated profile rejected;
18. independence profile stale after deployment/control-domain move rejected;
19. policy explicitly requiring only appraisal diversity can accept shared evidence source when declared;
20. policy requiring evidence-source diversity cannot.

### Topology completeness — 14 cases

21. bounded topology reconciles orchestrator/LB/data-plane inventory successfully;
22. stale LB member absent from service discovery yields topology conflict;
23. terminating-but-serving endpoint remains in coverage;
24. shadow/canary endpoint remains in coverage;
25. DR replica not receiving current traffic remains required if it can become authoritative;
26. manual/direct-IP bypass endpoint remains required;
27. autoscaled endpoint created after snapshot enters coverage via watch;
28. endpoint deleted then recreated with new identity cannot inherit old proof silently;
29. lost watch continuity forces resnapshot;
30. omitted EndpointSlice/page cannot be treated as full set;
31. duplicate discovery records map to one stable endpoint identity without inflating coverage;
32. topology controller says removed but router still serves -> conflict;
33. router quiet but control plane still permits failover activation -> not decommissioned;
34. explicit decommission plus routing/failover fence removes endpoint from active coverage while retaining history.

### Negative probes — 16 cases

35. exhaustive direct per-backend L0 consequential probes all reject and show no effect;
36. one stale backend accepts -> cutover incomplete;
37. load balancer sends all probe-tagged requests only to migrated pool -> steering detected/insufficient;
38. backend identity unavailable behind LB -> cannot claim universal replica proof;
39. challenge target set committed before seed -> accepted sampling setup;
40. target pool changed after seed -> new members added to coverage;
41. small stale pool missed probabilistically -> result remains sampling-bounded, not universal;
42. region-weighted sampling prevents one high-traffic region hiding another;
43. rejection response but downstream effect recorded -> contradiction;
44. timeout/UNKNOWN cannot be counted as rejection;
45. stale cached rejection response rejected by nonce/freshness binding;
46. synthetic health endpoint pass is diagnostic only;
47. direct backend probe proves backend cutover but not public LB routing membership by itself;
48. production-path randomized probe plus authenticated responder identity supports declared confidence bound;
49. probe coordinator key stale -> probe evidence cannot satisfy completion;
50. transparency receipt proves probe statement registration but not successful cutover semantics by itself.

### Composition / crash / dispute — 10 cases

51. topology generation changes during probe round and new endpoint is included before completion;
52. topology evidence and verifier result disagree -> fail closed;
53. verifier key rotates mid-round and every accepted result is classified against correct authority interval;
54. crash after topology commit/before challenge resumes without reseeding away inconvenient targets;
55. crash after partial probes preserves unresolved target set;
56. two verifier quorums produce conflicting threshold-valid results -> dispute/no completion;
57. issuer key compromise notice arrives after prior completion -> affected completion is reclassified if its authority interval is implicated;
58. decommissioned endpoint resurrection invalidates current convergence frontier;
59. old lineage cannot regain consequential authority through DR/failover activation after cutover;
60. complete bounded inventory + independent verifier quorum + effective negative proof reaches `CONVERGENCE_PROVEN_FOR_BOUNDED_INVENTORY`.

## Implementation direction

When executable source becomes available, do not build a second standalone security subsystem. Compose this contract with LAB-093's already frozen migration/convergence model:

- evidence authority/key generations become authenticated inputs to `MigrationEvidenceEnvelopeV1`;
- verifier independence is an appraisal layer before quorum counting;
- `AuthorityTopologySnapshotV1` and its version frontier feed `EnforcementCutoverAttestationV1`;
- negative challenge/result records become evidence items tied to the exact topology generation;
- contradiction proofs feed the existing fail-closed convergence dispute state;
- transparency receipts remain audit/publication evidence, not semantic truth.

Write RED tests at the contract boundary before production refactors.

## Decision

Freeze `CONVERGENCE_EVIDENCE_KEY_LIFECYCLE_VERIFIER_INDEPENDENCE_TOPOLOGY_COMPLETENESS_NEGATIVE_PROBE_SAMPLING_V1_FROZEN`.

The strongest new invariant is:

**A migration cutover is not proven merely because signed verifiers report success. The system must prove that the signing/verifying authorities were current, that any required verifier quorum satisfies declared independence constraints, that the topology denominator includes every authority-bearing path through a versioned contradiction-aware discovery frontier, and that negative old-lineage probes cannot be selectively steered away from stale authority surfaces.**

## Exact next research boundary if execution remains unavailable

Freeze **convergence evidence revocation propagation / post-completion invalidation / continuous assurance and re-open semantics**: define how a previously `CONVERGENCE_PROVEN_*` frontier is invalidated when a verifier key compromise, resurrected endpoint, stale DR activation, topology omission or contradictory evidence is discovered later; how relying parties learn that invalidation; whether old cutover receipts remain historical-only; and what evidence is required to re-close convergence after reopening without erasing the original failure history.
