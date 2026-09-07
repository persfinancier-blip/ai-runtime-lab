# Descendant discovery completeness / revocation-set closure / offline-delegate resurrection semantics — V1 FROZEN

Date: 2026-09-07
Issue context: LAB-093 / #178
Status: design-frozen; executable RED/GREEN pending exact-source execution

## Question

After a consequential capability has been delegated through processes, plugins, queues, duplicated/transferred OS handles, broker credentials, provider sessions, or delayed tasks, what evidence is sufficient to claim that revocation has reached **every still-live descendant**?

The previous capability-envelope contract established authenticated per-instance lineage and monotonic attenuation. That is not enough for revocation completion: a revoker can invalidate every descendant it currently knows about while an offline worker, partitioned queue, duplicated raw handle, or stale provider session remains usable and later reappears.

The safety property therefore cannot be “all registry rows are revoked.” It must be a closure property over the set of descendants that could still exercise authority.

## Primary-source / donor findings

### 1. Raw delegated handles are not automatically enumerable or clawed back

FreeBSD Capsicum capability descriptors may be inherited across `fork`/`exec` and passed over UNIX-domain sockets; rights can be reduced but not expanded. This is a useful attenuation primitive, but it also means descendant copies can exist outside the issuer's current descriptor table.

Linux `SCM_RIGHTS` similarly transfers file descriptors between processes. The receiver obtains a usable descriptor referring to the underlying open-file description; revocation cannot be inferred merely from closing the sender's local descriptor.

Fuchsia exposes per-process handle tables and stable kernel object identifiers, but its own documentation notes that not all live objects are necessarily visible from one process's handle listing. A local enumeration is therefore not a universal proof that no external descendant exists.

Decision: **local handle enumeration is evidence, never global descendant-completeness authority unless the deployment proves a closed mediation domain that prevents unregistered transfer/duplication.**

### 2. Leases give a safe completion horizon only when use is synchronously enforced

Distributed lease systems use expiration so a server can reclaim authority after a disconnected client can no longer renew. USENIX lease literature describes the mutually agreed expiration time as the point after which a disconnected client's right ends; reconfiguration protocols commonly wait for old leases to expire before granting conflicting authority.

Decision: a finite lease may turn unbounded descendant discovery into a bounded waiting problem **only if every authority use is checked against the authoritative lease epoch/expiry by an enforcement point that the delegate cannot bypass**. A timestamp embedded in an unmediated OS handle is not a lease.

### 3. Attenuated bearer credentials still require a verification point

Macaroons demonstrate chained attenuation through caveats, but they remain bearer credentials whose restrictions are enforced by the target verifier. This is an important boundary: attenuation and expiry are effective when every consequential use must pass through a verifier that knows the current policy/revocation state.

Decision: broker/service-mediated capability descendants can reach mechanically provable revocation closure; raw capabilities that remain independently exercisable may not.

## Threat model

A revoked ancestor A may have descendants produced by:

- fork/exec inheritance;
- explicit duplicate/transfer/re-delegation;
- UNIX `SCM_RIGHTS` or equivalent handle transfer;
- plugin/FFI/native code retaining a handle or session;
- queued/delayed work serialized before revocation and executed after it;
- broker retry/redelivery;
- provider/API sessions or bearer credentials cached on offline workers;
- crash recovery restoring an old checkpoint;
- network partitions or split-brain brokers;
- replicas that observed delegation but not revocation;
- unregistered descendants caused by a producer/manifest/schema/inventory omission already covered by prior fraud-proof contracts.

The revocation protocol must fail closed under omission and resurrection, not merely converge when all actors are online and cooperative.

## Core model

### `RevocationCampaignV1`

A campaign is immutable and content-addressed over:

- `campaign_id`;
- `root_capability_id` and root envelope digest;
- `root_delegation_epoch`;
- `revocation_generation`;
- `opened_frontier` for every material registry/broker/provider/runtime domain;
- `delegation_schema_generation`;
- `effect_inventory_generation`;
- `policy/trust frontier`;
- `closure_mode`;
- `lease_horizon`, when applicable;
- `required_observation_domains`;
- `opened_at` and authenticated issuer identity.

A campaign never mutates its meaning after opening. New evidence extends the campaign through append-only observations and dispositions.

### Descendant classes

Every capability type is classified into one of four revocation-discovery classes before consequential use:

1. **D1 — mechanically enumerable and mediated**
   - every delegation is recorded by the sole enforcement broker;
   - duplicate/transfer cannot bypass that broker;
   - every use rechecks current revocation generation.
   - Example shape: server-side opaque session ID checked on every request.

2. **D2 — logically discoverable with bounded lease**
   - descendant creation may be partitioned/offline temporarily;
   - every consequential use still requires a non-renewable/renewable lease checked by an authoritative service;
   - after an authenticated no-renew frontier plus maximum lease duration and clock/uncertainty bound, old descendants are unusable.

3. **D3 — independently observable but not mechanically complete**
   - some uses can be detected/reconciled after the fact, but descendant creation or use may bypass the central registry;
   - observations can prove a violation but absence of observations cannot prove closure.

4. **D4 — unmediated / physically non-clawback capability**
   - raw OS handle, local secret, bearer credential, provider session, or native capability remains usable without consulting a revocation-aware enforcement point;
   - copies may be impossible to enumerate completely.

Only D1, and D2 after its safe horizon, can normally reach destructive `CLOSED` revocation-set authority. D3/D4 remain `UNKNOWN` unless separately upgraded by a stronger physical containment mechanism.

## Closure states

`RevocationClosureV1.state` is one of:

- `OPEN` — campaign in progress;
- `UNKNOWN` — completeness cannot currently be proven;
- `QUIESCING` — no new delegations/renewals allowed; waiting for bounded outstanding authority to expire;
- `CLOSED_LOGICAL` — every future mediated use is guaranteed to reject the revoked generation, but raw physical descendants may still exist;
- `CLOSED_PHYSICAL` — deployment-specific proof establishes that no usable physical descendant remains;
- `VIOLATED_AFTER_CLOSE` — authenticated evidence proves a supposedly closed descendant later exercised authority;
- `GAP_UNRECOVERABLE` — required registry/log/epoch history needed to establish closure has been lost.

`CLOSED_LOGICAL` must never be silently promoted to `CLOSED_PHYSICAL`.

## Revocation-set closure invariant

For root `R` and revocation generation `g`, let `Reachable(R,g)` be every descendant that could have been created under authority derived from R before the revocation cut, including descendants not currently online.

A campaign may emit `CLOSED_LOGICAL` only if one of these proof strategies succeeds:

### Strategy A — complete mediated enumeration

- the delegation graph is append-only/authenticated;
- every transfer/duplicate/redelegation is enforced through a registrar;
- registrar frontiers prove all delegation events through cut `F` are resolved;
- new delegation under generation `< g` is rejected after the cut;
- every enumerated live descendant has terminal disposition `REVOKED`, `EXPIRED`, `DESTROYED`, or `SUPERSEDED_BY_STRONGER_REVOCATION`;
- every use path rechecks generation `>= g`.

### Strategy B — lease closure

- new renewals for generation `< g` are rejected at authenticated frontier `Fdeny`;
- maximum authority lease duration is finite and policy-bound;
- all enforcement clocks satisfy the specified uncertainty bound or use server-side expiry;
- the campaign waits through `Fdeny + max_lease + uncertainty`;
- no mechanism permits offline renewal, cached extension, or authority use without expiry validation;
- durable recovery cannot restore a pre-revocation lease as current.

Then descendants need not all be individually contacted; their authority becomes unusable by construction after the horizon.

### Strategy C — physical containment

A deployment-specific mechanism may establish stronger physical closure, for example terminating the sole isolated worker/process tree and proving no capability could leave that containment boundary. Such a proof must compose with LAB-087-style process/filesystem/network isolation and the delegation-envelope rules. A simple `kill(pid)` is not sufficient if handles/credentials could already have escaped.

## No-central-registry rule

A central registry is not assumed complete merely because all supported code writes to it.

For the registry to carry completeness authority, the system must prove:

1. every capability-creating primitive is either denied or intercepted;
2. every transfer/duplicate primitive is either denied or intercepted;
3. inherited/pre-opened capabilities are inventoried before workload start;
4. plugin/FFI/native paths cannot bypass registration;
5. recovery/restart cannot restore an unregistered descendant;
6. provider-side session creation is independently reconciled where the provider is outside the local TCB.

Otherwise the registry is D3 evidence only.

## `RevocationClosureProofV1`

A closure proof binds:

- campaign digest;
- exact root and revocation generation;
- descendant-discovery class;
- delegation-graph root / registry frontier vector;
- no-new-delegation barrier evidence;
- per-descendant terminal dispositions or lease-horizon proof;
- queue/broker drain frontiers;
- provider-session revoke/expiry frontiers;
- process/runtime epoch frontiers;
- recovery checkpoint minimum generation;
- independent reconciliation observations;
- unresolved-gap set, which must be empty for `CLOSED_LOGICAL`;
- physical-containment witness if claiming `CLOSED_PHYSICAL`;
- verifier version and trust/policy/schema/inventory frontiers.

The proof is invalid if any required frontier regresses, any source equivocates, or a later authenticated descendant-use event is causally attributable to the revoked generation.

## Offline workers

An offline worker never counts as revoked merely because it missed the campaign.

Safe outcomes:

- **mediated use:** worker may reconnect, but its first consequential use is rejected because the broker/service checks current generation;
- **lease:** worker's last valid lease expires before closure horizon, and offline renewal is impossible;
- **unmediated raw authority:** closure remains `UNKNOWN` until physical containment or another stronger proof exists.

Reconnection after campaign closure must present worker/runtime epoch. A worker restoring an epoch older than the campaign cut is quarantined before receiving new authority.

## Partitioned queues and delayed tasks

Queued work is a descendant authority object, not mere data.

Required rules:

- enqueue freezes root capability/delegation generation and task authority envelope;
- execution revalidates revocation generation, expiry, recipient epoch, policy and trust frontiers;
- queue partitions expose authenticated high-water/resolved frontiers;
- campaign closure requires either terminal disposition for all pre-cut authority-bearing tasks or a proof that execution-time validation makes every stale task harmless;
- dead-letter/retry queues are included in the same authority universe;
- replay after crash cannot mint a fresh delegation epoch.

A queue without execution-time authority validation is D3/D4, even if its primary topic is perfectly enumerable.

## Duplicated/transferred OS handles

For raw descriptors/handles:

- sender close does not prove receiver close;
- local process-table enumeration does not prove absence elsewhere;
- `fork`, inherited descriptors and `SCM_RIGHTS` create additional lineage obligations;
- if duplicate/transfer can occur outside a trusted broker and use does not re-enter a revocation-aware enforcement point, claim `REVOCATION_UNENFORCEABLE` and keep closure `UNKNOWN` for physical-authority purposes.

To obtain bounded closure, production architecture should replace raw long-lived write authority with brokered opaque capabilities, revocable indirection, or short server-validated leases wherever the operation is consequential.

## Provider sessions / cloud credentials

Provider sessions are treated as external descendants.

A provider integration can support closure only if one of the following is independently verifiable:

- provider exposes session/token IDs plus revocation and introspection with a trustworthy effective time;
- credentials are short-lived and provider validates expiry server-side;
- all provider operations are forced through a local broker holding the only underlying credential;
- provider account/role versioning invalidates pre-cut credentials and old credentials cannot act after the version change.

“Called revoke API successfully” is not enough if revocation is eventually consistent and its effective frontier is unknown. Campaign remains `QUIESCING`/`UNKNOWN` until the documented or observed effective horizon is crossed and reconciliation succeeds.

## Crash recovery and resurrection

Durable recovery state must carry a minimum accepted revocation generation.

On restore:

- any capability/task/session envelope below the minimum generation is stale and cannot be used or renewed;
- a checkpoint cannot reset descendant state to `ACTIVE` merely because the checkpoint predates the campaign;
- campaign and descendant terminal dispositions are monotonic across restart;
- loss of required campaign/log history yields `GAP_UNRECOVERABLE`, not fresh bootstrap.

## Split-brain brokers

Broker leadership/authority has an epoch. A broker serving delegation or use decisions under an old epoch cannot create valid descendants after a newer revocation barrier.

Closure requires:

- authenticated broker epoch transition;
- no-old-epoch issuance barrier;
- stale broker requests rejected by downstream enforcement using broker epoch/fence;
- reconciliation of any effects accepted during ambiguous leadership.

If downstream accepts both epochs without fencing, registry completeness is invalid and closure cannot reach `CLOSED_LOGICAL`.

## Fraud / contradiction proofs

### `OmittedDescendantProofV1`

Proves a material descendant existed but was absent from the claimed discovery set. Inputs include root lineage, descendant envelope/effect evidence, campaign discovery-root commitment and non-membership proof. Verdict: `REVOCATION_SET_OMISSION_PROVEN`.

### `PostClosureUseProofV1`

Proves an effect accepted after the closure frontier under a capability generation that the closure proof claimed unusable. Verdict: `REVOCATION_CLOSURE_FALSE_PROVEN`.

### `StaleQueueResurrectionProofV1`

Binds enqueue authority, campaign cut and post-cut execution to prove delayed work resurrected revoked authority.

### `OldEpochBrokerIssuanceProofV1`

Proves a fenced broker epoch issued or authorized a descendant after its authority ended.

Any such proof:

- invalidates dependent finalization/GC/destructive-retention certificates;
- re-roots affected E2/E3/E4 evidence;
- opens an additive repair campaign;
- never rewrites historical evidence to make the old closure appear correct.

## GC / destructive-retention interlock

No object that is the only evidence needed to discover, invalidate, or prosecute a descendant may be garbage-collected while revocation closure is `OPEN`, `QUIESCING`, `UNKNOWN`, or under appeal/repair.

For D1/D2 closure, GC requires:

- closure proof finalized;
- fraud-proof challenge window/policy satisfied;
- all registry/log/queue/provider frontiers retained or safely substituted under the previously frozen semantic-equivalence contracts;
- recovery checkpoints at or above the revocation generation;
- no unresolved observation gaps.

For D3/D4, inability to prove closure keeps relevant evidence rooted indefinitely or until a separately authorized risk/retention policy explicitly changes the claim. Time passing alone is not evidence of revocation.

## Completion semantics

### May claim `CLOSED_LOGICAL`

Only when all future consequential uses are guaranteed to encounter a revocation-aware enforcement point, or every old authority instance has passed a proven bounded expiry horizon.

### May claim `CLOSED_PHYSICAL`

Only with a stronger containment-specific proof showing no usable physical descendant can remain. This is intentionally rare.

### Must remain `UNKNOWN`

When any material descendant can continue acting through an unmediated raw capability and the system cannot completely enumerate/claw back those copies.

This permanent `UNKNOWN` is a correct security result, not a protocol failure to be papered over.

## RED-first matrix — 80 cases

### A. Discovery / enumeration (1–10)
1. all registered descendants discovered;
2. one omitted registered descendant;
3. descendant appears exactly at opening cut;
4. duplicate registration IDs for same physical handle;
5. one physical descendant mapped to two envelopes;
6. inherited pre-opened handle absent from registry;
7. plugin-created descendant after inventory scan;
8. FFI-created descendant bypasses registrar;
9. local handle enumeration misses remote process;
10. independent reconciliation finds an unregistered session.

### B. Offline / reconnect (11–20)
11. offline worker with mediated capability reconnects after close;
12. offline worker with expired lease reconnects;
13. offline worker with raw bearer secret reconnects;
14. reconnect presents pre-campaign runtime epoch;
15. reconnect presents forged newer epoch;
16. worker receives revocation but crashes before ack;
17. ack recorded but worker checkpoint predates revocation;
18. worker remains offline beyond lease horizon;
19. worker clock skew exceeds declared uncertainty;
20. offline renewal path incorrectly remains available.

### C. Queue / delayed work (21–30)
21. pre-cut queued task executes and revalidation rejects;
22. pre-cut queued task executes without revalidation;
23. retry queue omitted from drain set;
24. dead-letter queue later replays stale task;
25. task duplicated across partitions;
26. enqueue and revocation race at same frontier;
27. task envelope loses ancestor generation on serialization;
28. consumer restart treats task as fresh delegation;
29. queue reports resolved frontier before delayed replica catches up;
30. cancelled task resurrects from recovery snapshot.

### D. OS handles / transfer (31–40)
31. sender closes after `SCM_RIGHTS` transfer;
32. receiver closes while third process retains duplicate;
33. fork inheritance before revocation;
34. fork after no-new-delegation barrier must fail/attenuate;
35. exec inherits descriptor unexpectedly;
36. descriptor number reused for different object;
37. stable object identity distinguishes reused FD;
38. raw capability cannot be clawed back -> UNKNOWN;
39. brokered indirection rejects after revocation;
40. process-tree kill with prior escaped descriptor cannot claim physical closure.

### E. Provider sessions / credentials (41–50)
41. provider revokes session synchronously;
42. provider revocation has documented propagation lag;
43. lag unknown -> UNKNOWN;
44. short-lived token expires server-side;
45. cached token accepted after local expiry due provider clock policy;
46. old role/session version rejected after version bump;
47. offline provider region accepts stale session;
48. revoke API success but introspection still ACTIVE;
49. credential copied to unmanaged plugin;
50. sole local broker owns underlying provider credential.

### F. Broker epochs / split brain (51–60)
51. clean broker epoch rollover;
52. stale broker issues after fence;
53. downstream rejects old broker epoch;
54. downstream accepts both epochs -> closure blocked;
55. partitioned broker rejoins with queued delegations;
56. leader change loses revocation-generation state;
57. duplicated campaign ID under two broker epochs;
58. equivocation in no-new-delegation frontier;
59. independent log detects old-epoch effect;
60. recovery starts broker from pre-revocation snapshot.

### G. Leases / horizon (61–70)
61. finite lease, no renewal after cut, horizon passes;
62. one lease has longer duration than declared maximum;
63. renewal committed exactly before deny frontier;
64. renewal attempted exactly after deny frontier;
65. server-side expiry vs client-side expiry divergence;
66. uncertainty bound violated;
67. infinite/untimed capability mislabeled lease;
68. lease can be extended offline;
69. policy changes max lease during open campaign;
70. clock rollback after restart.

### H. Closure / fraud / GC (71–80)
71. closure proof with empty unresolved-gap set;
72. omission fraud proof after CLOSED_LOGICAL;
73. post-closure use proof reopens dependency closure;
74. GC tries to delete delegation log during QUIESCING;
75. GC after valid D1 closure and challenge policy;
76. D4 raw capability incorrectly promoted to CLOSED_PHYSICAL;
77. recovery checkpoint below revocation generation;
78. lost registry segment -> GAP_UNRECOVERABLE;
79. additive repair campaign after contradiction;
80. historical false closure remains immutable and linked to superseding repair.

## Architecture consequence for LAB-093

The production capability boundary should prefer **revocable indirection** over handing consequential raw authority to arbitrary descendants:

- trusted broker/process owns the raw mutable provider/OS capability;
- delegated components receive opaque operation-scoped envelopes;
- every consequential use returns through the broker and rechecks revocation generation;
- queue tasks carry frozen authority lineage and revalidate at execution;
- external provider credentials are broker-held or short-lived/server-validated;
- raw non-clawback delegation is an explicitly weaker mode that cannot support claims requiring complete descendant revocation.

This composes the prior LAB-093 capability-envelope design with LAB-087 isolation instead of pretending Python object encapsulation can revoke authority already copied outside the trusted process.

## Frozen decision

`DESCENDANT_DISCOVERY_REVOCATION_SET_CLOSURE_OFFLINE_RESURRECTION_V1_FROZEN`

1. Revocation completion is closure over **all potentially usable descendants**, not all rows currently known to a registry.
2. Descendant types are classified D1–D4 by enforceability/discoverability before consequential use.
3. D1 can close by authenticated complete enumeration + mediated-use rejection.
4. D2 can close after a proven no-renew frontier plus a finite, server-enforced lease horizon.
5. D3/D4 cannot use absence-of-observation as completeness evidence; unmediated non-clawback authority remains `UNKNOWN` unless stronger containment proves otherwise.
6. Offline workers, queues, provider sessions, broker epochs and recovery checkpoints are first-class descendants/frontiers in the campaign.
7. `CLOSED_LOGICAL` and `CLOSED_PHYSICAL` are distinct guarantees.
8. Omitted-descendant or post-closure-use evidence invalidates dependent finalization/GC proofs and triggers additive repair; history is not rewritten.
9. GC is interlocked with revocation closure and must retain discovery/prosecution evidence until the relevant guarantee is safely closed.
10. Production LAB-093 should route consequential delegation through revocable brokered indirection or short server-validated leases whenever complete revocation is a required property.

## Next distinct question

**Revocation-aware lease issuance / renewal linearization / clock-and-partition safety semantics.** Define the exact protocol that makes D2's bounded horizon trustworthy: authoritative server time vs monotonic epochs, renewal-vs-revoke races, maximum lease enforcement, partition behavior, crash recovery, provider-side expiry, clock rollback/skew, and proof that no hidden renewal path can extend old authority beyond the declared horizon.