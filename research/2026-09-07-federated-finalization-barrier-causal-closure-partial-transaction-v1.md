# Federated finalization barrier / causal-closure attestation / cross-domain partial-transaction detection — V1

Status: **FEDERATED_FINALIZATION_BARRIER_CAUSAL_CLOSURE_PARTIAL_TRANSACTION_V1_FROZEN**  
Date: 2026-09-07  
Scope: LAB-093 evidence/refresh/GC contract family; design/evidence only, no production integration or behavioral PASS claimed in this run.

## 1. Problem

The previous refresh-campaign contract froze a campaign universe as:

`BaselineSnapshot(F0) ⊕ CanonicalDeltas(F0,F1]`

and required authenticated `RESOLVED_THROUGH(F1)` evidence from every material source. That is sufficient only when each source is independent. It is not sufficient when evidence, revocation, dependency-repair, liveness, archive and trust/policy domains can participate in one logical transaction or causal chain.

A vector of locally valid high-water marks can still describe an impossible global state. Examples:

- domain A records a revocation request before its local F1 while domain B records the corresponding trust downgrade only after its F1;
- archive domain records `copy-created` before F1 while availability domain's retrieve/content-check consequence remains unresolved past F1;
- a dependency repair is committed in the repair domain while the newly re-rooted GC closure is not yet materialized in the GC domain;
- an appeal/adjudication cause is included while a deterministic consequential reopen event is delayed outside the cut;
- a cross-domain transaction commits one participant before F1 and another after F1;
- a domain is quiet/offline and reports no work, but an in-flight cross-domain message or transaction participant has not been accounted for.

Therefore **per-domain resolved frontiers are necessary but not sufficient**. Finalization needs a consistent authenticated cut plus explicit accounting for in-flight cross-domain obligations.

## 2. Primary-source donor mechanisms

### Chandy–Lamport distributed snapshots

Chandy and Lamport define a global state from local process states plus channel states and show how to obtain a consistent cut without stopping the computation. The key transferable invariant is causal closure: a recorded receive/effect cannot exist in the cut without its causal send/source being represented; messages crossing the cut are recorded as channel state rather than silently disappearing.

Primary paper: K. M. Chandy, L. Lamport, *Distributed Snapshots: Determining Global States of Distributed Systems*, ACM TOCS 3(1), 1985. Author-hosted copy: https://lamport.azurewebsites.net/pubs/chandy.pdf

Transferable mechanism: **consistent cut + explicit in-flight channel state**, not the paper's FIFO-network assumptions as a literal implementation requirement.

### PostgreSQL logical-replication exported snapshot

PostgreSQL logical slot creation can export a snapshot and returns a `consistent_point`, the earliest WAL position from which streaming can start. The exported snapshot shows exactly the database state after which subsequent changes are in the stream. This is a strong local-domain pattern for binding a baseline cut to a delta frontier without scan/subscribe omission.

Primary docs:
- https://www.postgresql.org/docs/17/protocol-replication.html
- https://www.postgresql.org/docs/17/logicaldecoding-explanation.html

Transferable mechanism: **baseline snapshot and delta stream share one authenticated opening cut**.

### Apache Kafka transaction protocol

Kafka's transaction protocol uses producer identity/epochs and transaction coordination to prevent stale producers and to make a transaction's records visible according to commit/abort state rather than treating independently observed partition writes as final. Kafka 4.x strengthened transaction epochs so transaction boundaries are less vulnerable to cross-transaction duplication.

Primary docs: https://kafka.apache.org/41/operations/transaction-protocol/

Transferable mechanism: **logical transaction identity, participant/boundary evidence and fencing; do not infer transaction completion from independent partition offsets**.

### CockroachDB resolved timestamps / CDC

CockroachDB changefeeds can emit resolved timestamps. A resolved timestamp is a promise that the feed will not later emit row changes at or below that point; consumers can use resolved frontiers for ordering/completeness. CockroachDB also distinguishes commit-time metadata from processing time.

Primary docs: https://www.cockroachlabs.com/docs/stable/changefeed-message-envelopes

Transferable mechanism: **resolved-through means a monotone no-more-earlier-events promise, not merely 'currently caught up'**.

## 3. Decision summary

Freeze the following principle:

> A federated refresh/retention campaign may finalize at vector frontier `F1 = {domain_i -> position_i}` only when every material domain has authenticated its local resolved-through position under one frozen membership epoch **and** the union of domain attestations proves causal/transaction closure for the cut. Any cross-domain cause/transaction that intersects the cut must either be fully represented inside the cut or appear exactly once in an authenticated in-flight obligation set. Missing, equivocal, offline or stale closure evidence yields `UNKNOWN`, never success.

A scalar wall-clock time is not authoritative. A coordinator's observation that every queue is empty is not authoritative. Independent domain high-water marks without closure evidence are not authoritative.

## 4. Frozen objects

### 4.1 `FederationMembershipEpochV1`

Canonical fields:

- `federation_id`
- `membership_epoch`
- `previous_membership_digest | GENESIS`
- ordered `material_domains[]`
- for each domain: stable `domain_id`, authority/key generation, frontier namespace, event-schema generation, closure protocol generation
- join/drain policy
- all-domain vs explicitly policy-authorized threshold rule
- `policy_digest`
- `trust_frontier_digest`
- `created_at_position` in the federation authority log
- canonical digest/signatures

The barrier freezes one membership epoch. Membership cannot be silently recomputed at finalization time.

Default consequential rule: **all material domains are required**. A threshold is permitted only if the policy explicitly defines which missing domains can be omitted and proves that omitted domains cannot carry material causal/transaction edges for this campaign class.

### 4.2 `BarrierOpenV1`

- `campaign_id`
- `barrier_epoch`
- frozen `membership_digest`
- per-domain opening frontier `F0_vector`
- campaign obligation/root digest at open
- policy/trust/schema/verifier frontiers
- delta-retention lease digests
- opening timestamp as metadata only
- canonical digest/signatures

Every domain must start delta retention no later than its authenticated F0 cut.

### 4.3 `CrossDomainTransactionManifestV1`

For every material multi-domain transaction/effect chain that needs atomic visibility:

- immutable `tx_id`
- `tx_kind`
- `origin_domain`
- complete expected `participant_domains[]`
- per-participant operation/effect digest
- predecessor/generation bindings
- prepare/commit/abort state
- per-domain source positions where state changes are recorded
- causal parents
- canonical result/effect digest when committed
- authority/schema/policy generations
- signatures or authenticated log inclusion references

The participant set cannot be inferred after the fact only from domains that happened to report a row. The transaction's authenticated manifest defines expected closure.

### 4.4 `CausalEdgeV1`

Use when the relationship is consequential but not one atomic transaction:

- `cause_id` + cause domain/position/digest
- `effect_id` + effect domain/position/digest, or `PENDING`
- semantic edge class (`REVOCATION_EFFECT`, `REPAIR_REROOT`, `APPEAL_REOPEN`, `ARCHIVE_VERIFY`, `POLICY_INVALIDATION`, `GC_REACTIVATION`, etc.)
- deterministic/optional consequence semantics
- deadline/horizon if policy-bound
- schema generation
- authenticated producer/observer evidence

A deterministic material consequence with `cause <= F1` cannot be ignored merely because the effect position is `> F1` or has not executed yet. It becomes an in-flight obligation.

### 4.5 `DomainBarrierAckV1`

Each domain signs exactly one current acknowledgement for `(campaign_id, barrier_epoch, membership_digest)` containing:

- `domain_id`
- `F0_i`
- proposed `F1_i`
- authenticated `RESOLVED_THROUGH(F1_i)` proof
- baseline/delta coverage root
- terminal-disposition root for local obligations through `F1_i`
- outbound cross-domain transaction/causal-edge root through `F1_i`
- inbound cross-domain transaction/causal-edge root observed through `F1_i`
- local unresolved/in-flight root
- local source-equivocation state
- membership/policy/trust/schema generations
- predecessor ack digest / monotone ack generation
- signer authority generation

An ack is stale if any bound frontier/generation changes before finalization.

### 4.6 `FederatedInflightSetV1`

The coordinator/verifier deterministically joins all domain manifests/edge roots and emits the canonical set of edges crossing the cut:

- cause/send/prepare represented inside cut;
- effect/receive/commit not represented inside cut;
- transaction has only a strict subset of required participants complete inside cut; or
- a material consequence remains `PENDING`.

Each item must have exactly one terminal barrier disposition:

- `INCLUDED_COMPLETE` — all required material participants/effects are inside the cut;
- `RECORDED_INFLIGHT` — intentionally crosses the cut and is rooted as a future obligation;
- `ABORTED_AUTHENTICATED` — authoritative abort means no consequence remains;
- `POLICY_NON_MATERIAL` — independently justified under bound policy/schema;
- `REJECTED_INVALID` — malformed/untrusted source, with evidence retained;
- `UNKNOWN` — missing/conflicting evidence.

`UNKNOWN` blocks consequential finalization and destructive GC.

### 4.7 `FederatedFinalizationCertificateV1`

Canonical fields:

- `campaign_id`, `barrier_epoch`
- frozen `membership_digest`
- `F0_vector`, final `F1_vector`
- ordered domain-ack digests
- resolved-through proof digests
- transaction-manifest root
- causal-edge root
- in-flight-set root
- exact-one disposition root
- unresolved root (MUST be canonical empty for destructive finalization)
- baseline+delta final obligation-set root
- refreshed-successor/evidence root
- policy/trust/schema/verifier frontiers
- GC/sunset authorization scope
- independent verifier statement digest(s)
- federation finalizer signatures

The certificate is a compact commitment to evidence, not a substitute for retained evidence required by the dependency/GC contracts.

## 5. Consistent-cut rules

### Rule C1 — receive/effect implies cause/send

If a material effect/receive is inside the global cut, its authenticated cause/send/transaction origin must be inside the cut. A certificate with an effect but no represented cause is invalid.

### Rule C2 — cause may precede effect only as explicit in-flight state

A cause/send may be inside while the effect/receive is outside. This is legal only when the edge appears exactly once in `FederatedInflightSetV1` and remains rooted until resolved.

### Rule C3 — atomic transaction cannot be partially committed and called complete

If any required transaction participant is represented as committed inside the cut, all required participants must either be committed consistently inside the cut or the transaction is `RECORDED_INFLIGHT` / `UNKNOWN`. Independent local 'committed' rows do not create global completion.

### Rule C4 — no inferred participant shrinkage

A missing participant cannot be interpreted as 'not part of the transaction' after observing only the surviving domains. Expected participants come from the authenticated transaction manifest or a policy-authorized deterministic participant derivation committed before effects.

### Rule C5 — delayed deterministic consequence is material

If a cause at/before F1 deterministically opens a new refresh/GC/revocation obligation, finalization must include the consequence if completed or carry it as an in-flight obligation. Processing delay does not move it out of the campaign universe.

### Rule C6 — resolved frontier is domain-local

`RESOLVED_THROUGH(F1_i)` proves only that domain `i` will not later emit an earlier local event. It does not prove other domains have observed/closed causal consequences. Cross-domain closure is a separate proof obligation.

## 6. Barrier protocol

### Phase A — open

1. Authenticate/freeze `FederationMembershipEpochV1`.
2. Publish `BarrierOpenV1` with F0 vector.
3. Acquire/verify retention leases for all source histories needed from F0 onward.
4. Start or confirm baseline+delta capture for every domain at the same domain-local opening cut.

### Phase B — propose F1

5. Each domain advances to a candidate resolved position and publishes `DomainBarrierAckV1`.
6. Acks are append-only/superseding; old ack generations stay auditable but cannot authorize finalization after supersession.
7. Join transaction manifests and causal edges across domain acks.

### Phase C — closure

8. For every cross-domain manifest/edge intersecting the vector cut, require exactly one disposition.
9. Detect participant disagreement, missing participants, delayed material consequences, source equivocation and membership-generation mismatch.
10. If closure adds a new obligation/effect to a domain beyond that domain's acknowledged F1, advance that domain's F1 and obtain a fresh ack. Repeat until a fixed point is reached.

This is important: **F1 is a fixed point of material causal closure**, not a single coordinator-chosen timestamp.

### Phase D — finalize

11. Require current authenticated ack from every policy-required material domain.
12. Require all required domains `RESOLVED_THROUGH` their final F1 component.
13. Require canonical unresolved root empty for consequential/destructive finalization.
14. Independently recompute closure, obligation root and exact-one disposition root.
15. Publish `FederatedFinalizationCertificateV1`.
16. Only the final certificate may release campaign GC/sunset interlocks for evidence not otherwise rooted.

## 7. Offline, slow and partitioned domains

An offline domain is not equivalent to an empty domain.

Default behavior:

- missing ack => `UNKNOWN`;
- stale ack => `UNKNOWN`;
- ack without current resolved-through proof => `UNKNOWN`;
- unresolved membership transition => `UNKNOWN`;
- destructive finalization/GC remains blocked.

A policy may allow an explicitly non-material domain to be omitted, but that property must be frozen in the membership/policy epoch and independently verify that the domain cannot carry material causal edges for this campaign class.

No timeout converts `UNKNOWN` to success. Timeout is an operational state only.

## 8. Membership changes during a barrier

### Join

A joining domain does not silently enter an already-open barrier. It belongs to the next membership epoch unless the current epoch executes an explicit authenticated barrier-reconfiguration protocol.

If the joining domain can receive effects caused by old members before current F1, those effects must be represented as external/in-flight obligations until the next epoch can close them.

### Drain/remove

A material domain cannot be removed solely because it is offline. Removal requires an authenticated drain/decommission proof containing:

- last resolved local frontier;
- complete outbound/inbound cross-domain edge closure through that frontier;
- transfer/retention location of required evidence;
- no unresolved transactions/appeals/revocations/repair/GC consequences;
- successor authority if applicable.

The removal becomes effective only in a successor membership epoch.

### Key/schema/closure-protocol rotation

A barrier ack is bound to exact generations. A rotation before finalization stales affected acks unless an explicit handoff proves statement/subsumption continuity.

## 9. Source equivocation and forks

If a domain signs conflicting events/frontiers/manifests for the same immutable identity or position:

- publish `SOURCE_EQUIVOCATION` evidence;
- quarantine the affected domain/closure;
- mark all dependent finalization candidates `UNKNOWN` / `REVALIDATION_REQUIRED`;
- retain both forks/evidence under GC roots;
- do not resolve by latest-wins.

A federation certificate cannot launder an equivocal source merely by obtaining later signatures over one fork.

## 10. Archive-relocation composition

Archive relocation often spans storage and availability domains and is therefore a canonical partial-transaction hazard.

Required sequence:

1. destination write committed;
2. destination content address/digest verified;
3. independent retrieval succeeds;
4. authenticated archive manifest committed;
5. only then may hot-retire/GC consequence become eligible.

If F1 includes step 1 but not steps 2–4, relocation is `RECORDED_INFLIGHT`; old copy remains rooted. If F1 includes retirement without prior verified destination closure, the cut is invalid.

## 11. Revocation / repair / appeal composition

These domains can reactivate old evidence.

- revocation cause before F1 + revalidation/GC-root consequence after F1 => explicit inflight closure; stale 'campaign complete' is forbidden;
- dependency repair before F1 + blast-radius/reroot not completed => inflight/UNKNOWN;
- appeal accepted before F1 + adjudication reopen after F1 => inflight;
- a late event with source position <= an already signed `RESOLVED_THROUGH(F1_i)` is proof of source/frontier violation, not a normal delta.

## 12. Crash/restart

Barrier state is durable and idempotent.

Persist:

- open epoch/membership digest;
- every ack generation;
- manifest/edge roots;
- inflight/disposition roots;
- source retained-frontier leases;
- finalization certificate or explicit non-final state.

After crash, recompute closure from authenticated evidence. Do not trust an in-memory 'all acks received' flag. If source history required to validate an ack has been lost, return `GAP_UNRECOVERABLE` and keep GC blocked.

## 13. Independent verification algorithm

A verifier receiving a final certificate MUST be able to:

1. authenticate membership epoch and policy/trust/schema frontiers;
2. authenticate all required domain acks and their monotone generations;
3. verify each local resolved-through proof for the declared F1 component;
4. reconstruct the set of material cross-domain transaction manifests/causal edges intersecting the cut;
5. verify participant sets and causal parent bindings;
6. recompute which edges are complete vs crossing the cut;
7. recompute the exact-one disposition root;
8. prove unresolved root is empty for the requested destructive authority scope;
9. recompute the final obligation-set root from baseline+delta+closure consequences;
10. verify no bound trust/schema/membership generation changed before finalization;
11. verify certificate scope authorizes the requested GC/sunset operation.

Failure to retrieve any material dependency is `UNKNOWN`, not implicit acceptance.

## 14. Security properties

### Safety S1 — no partial-transaction completion laundering

A transaction that is split across domains cannot become 'complete' merely because every domain separately reports a locally valid state.

### Safety S2 — no delayed-consequence omission

A material consequence caused inside the cut remains in the campaign universe even if its worker executes after the candidate F1.

### Safety S3 — no offline-domain success inference

Silence, timeout, empty queue or unavailable domain never establishes closure.

### Safety S4 — no stale-ack finalization

Ack generations and all bound frontiers are immutable inputs. A newer local mutation/ack, membership change, revocation or schema/trust handoff invalidates stale finalization candidates.

### Safety S5 — no GC before global closure

Campaign roots/leases/inflight obligations remain GC roots until a current valid finalization certificate exists and all other dependency-class roots permit deletion.

### Safety S6 — source equivocation remains visible

Conflicting signed source histories poison dependent finalization; later federation aggregation cannot erase the conflict.

## 15. Liveness boundary

This contract intentionally prefers safety over forced finalization.

A permanently offline **material** domain may prevent finalization indefinitely. That is not solved by weakening the barrier. Operational recovery requires one of:

- restore the domain and produce the missing proof;
- authenticated source-history failover with continuity proof;
- policy-authorized membership drain/decommission with evidence closure;
- owner/security decision to change the assurance contract.

The protocol must surface the exact blocker (`DOMAIN_OFFLINE`, `MISSING_RESOLVED_PROOF`, `PARTIAL_TX`, `CAUSAL_GAP`, `SOURCE_EQUIVOCATION`, `GAP_UNRECOVERABLE`) rather than returning generic timeout.

## 16. RED-first executable matrix — 80 cases

The following are design-frozen regressions for later exact implementation. Each pre-fix acceptance case should RED where the current implementation incorrectly finalizes; GREEN requires deterministic fail-closed or explicit in-flight handling.

### A. Local frontier semantics (1–10)
1. all domains resolve exactly F1 -> finalizable if closure empty;
2. one domain resolved only F1-1 -> blocked;
3. current queue empty but no resolved proof -> blocked;
4. signed ack with wrong campaign id -> reject;
5. signed ack with wrong barrier epoch -> reject;
6. signed ack with wrong membership digest -> reject;
7. stale ack generation after superseding ack -> reject;
8. local event <= F1 appears after resolved proof -> equivocation/frontier violation;
9. duplicate identical ack -> idempotent;
10. conflicting same-generation ack -> equivocation.

### B. Causal cut (11–20)
11. receive/effect inside F1, cause outside/missing -> reject;
12. cause inside, effect outside and rooted inflight -> valid non-destructive barrier state;
13. cause inside, effect outside but omitted from inflight -> blocked;
14. optional non-material edge under bound policy -> may dispose NON_MATERIAL;
15. deterministic material delayed effect -> inflight required;
16. chain A->B->C with C inside but B missing -> reject;
17. two independent concurrent edges -> both classified independently;
18. causal edge bound to wrong schema generation -> reject;
19. edge producer revoked before finalization -> revalidation required;
20. effect digest does not match cause-declared expected effect -> reject.

### C. Cross-domain transactions (21–30)
21. two-participant commit both inside -> complete;
22. A committed, B prepared outside -> partial/inflight;
23. A committed, B missing -> UNKNOWN, not one-participant success;
24. participant list rewritten after commit -> reject;
25. extra unauthorized participant effect -> reject/quarantine;
26. authenticated abort before any material effect -> aborted disposition;
27. abort in one domain vs commit in another -> disagreement/UNKNOWN;
28. retry same tx id same payload -> idempotent;
29. same tx id different payload -> equivocation;
30. transaction coordinator epoch stale -> reject.

### D. Revocation/repair/appeal (31–40)
31. revocation request and all revalidation consequences inside -> complete;
32. revocation inside, GC reroot delayed -> inflight;
33. dependency repair inside, blast-radius scan incomplete -> blocked;
34. repair edge added after candidate ack but before finalization -> stale ack/fixed-point repeat;
35. appeal accepted, adjudication reopen delayed -> inflight;
36. appeal rejected authentically -> no reopen obligation;
37. verifier authority revoked during barrier -> affected ack revalidation;
38. materiality adjudicator revoked -> affected dispositions revalidation;
39. old evidence reactivated before F1 -> included/rooted;
40. old evidence reactivated after local ack but causally caused before F1 -> fixed-point advance required.

### E. Archive / availability (41–50)
41. write+verify+retrieve+manifest before F1 -> relocation complete;
42. destination write only -> inflight, old copy rooted;
43. write+digest but retrieval fails -> blocked;
44. manifest references wrong content digest -> reject;
45. hot copy retired before verified destination -> invalid cut;
46. destination disappears after ack before finalization -> stale/revalidation;
47. archive domain offline -> UNKNOWN;
48. relocation retried same identity -> idempotent;
49. two archive locations one valid one invalid -> policy-defined sufficient replicas only;
50. availability proof signed by revoked authority -> reject/revalidate.

### F. Membership / offline domains (51–60)
51. all frozen members ack -> proceed;
52. material member offline -> UNKNOWN;
53. coordinator times out missing member -> still UNKNOWN;
54. new domain joins after open -> excluded until next epoch, causal effects inflight;
55. material domain removed without drain proof -> reject membership successor;
56. drain proof with unresolved outbound tx -> reject;
57. drain proof complete -> successor epoch may omit domain;
58. stale old-membership ack mixed with new epoch -> reject;
59. explicitly non-material domain omitted per frozen policy -> allowed only if no material edge;
60. allegedly non-material domain carries material edge -> policy/closure violation.

### G. Equivocation / trust / schema (61–70)
61. source signs two payloads same position -> quarantine;
62. finalizer chooses one fork latest-wins -> reject;
63. key rotation with authenticated handoff before ack -> new generation accepted;
64. key rotation after ack before finalize -> stale ack;
65. schema changes edge materiality mid-barrier -> stale classification/ack;
66. policy changes participant derivation mid-barrier -> stale barrier or explicit handoff;
67. trust root rollback -> reject;
68. closure-protocol generation downgrade -> reject unless authorized compatibility proof;
69. recursive summary proof omits source fork identity -> reject;
70. independent verifier cannot retrieve one material manifest -> UNKNOWN.

### H. Crash / GC / fixed-point closure (71–80)
71. crash after barrier open before acks -> resume same epoch;
72. crash after some acks -> resume, no duplicate terminal dispositions;
73. crash after candidate fixed point before certificate -> recompute/reverify;
74. source retention gap after crash -> GAP_UNRECOVERABLE;
75. GC attempts delete while barrier open -> blocked by campaign roots;
76. GC attempts delete recorded inflight evidence -> blocked;
77. closure discovery advances one domain F1 -> fresh ack required;
78. repeated closure advancement converges -> final certificate only at fixed point;
79. closure keeps generating material consequences without convergence -> no finalization;
80. independent replay reproduces F1 vector, inflight root, exact-one disposition root and final obligation-set root.

## 17. Audit of the frozen design

### What this contract intentionally does not claim

- It does not provide global serializability across independent databases/services.
- It does not make arbitrary side effects rollbackable.
- It does not solve Byzantine consensus among mutually distrustful federation authorities.
- It does not permit destructive finalization while a material domain is unavailable.
- It does not infer full transaction participant sets from observed rows.

### Why the protocol is sufficient for the LAB-093 campaign use case

The campaign needs a verifiable **cut of evidence obligations**, not a globally serializable application database. A vector frontier plus explicit causal/transaction manifests can establish that every material pre-F1 cause is either fully reflected in the cut or preserved as an in-flight rooted obligation. That is the minimum property needed to prevent refresh completeness and GC authority from laundering split transactions or delayed consequences.

### Main implementation risk

The hardest part is not signing a barrier ack; it is **complete emission of causal/transaction manifests**. If producers can create consequential cross-domain effects without declaring their participant/causal edges, the barrier sees an incomplete graph. Production implementation must therefore bind edge emission to the same authenticated operation/authority paths that create revocations, repairs, appeals, archive transitions and GC reactivation—not bolt on an optional observer afterwards.

## 18. Frozen implementation direction

When exact executable source becomes available, implement RED tests before production refactors:

1. canonical dataclasses/encoders for membership, barrier, ack, transaction manifest, causal edge and final certificate;
2. deterministic vector-frontier comparison and monotone ack generations;
3. manifest joiner + exact-one disposition engine;
4. fixed-point causal-closure loop;
5. explicit UNKNOWN/error taxonomy;
6. GC campaign-root interlock;
7. independent verifier/replay path that does not call the producer's finalization helper;
8. only after RED evidence, integrate producer-side manifest emission into consequential LAB-093 authority paths.

Do not create a second locally valid authority island. These objects must compose with the previously frozen evidence dependency graph, materiality adjudication, mapper completeness, snapshot provenance, substitution, verifier-agility and cryptographic-refresh contracts.

## 19. Result

**Frozen:** `FEDERATED_FINALIZATION_BARRIER_CAUSAL_CLOSURE_PARTIAL_TRANSACTION_V1_FROZEN`.

The decisive invariant is:

`FINALIZABLE(F1_vector) := ALL_REQUIRED_DOMAINS_RESOLVED(F1) ∧ CONSISTENT_CAUSAL_CUT(F1) ∧ EXACT_ONE_DISPOSITION(all_intersecting_edges) ∧ UNRESOLVED_ROOT == EMPTY ∧ FRONTIERS_CURRENT`

for destructive completion. Causes legitimately crossing the cut remain explicit authenticated in-flight roots; they are never omitted as 'future work'.
