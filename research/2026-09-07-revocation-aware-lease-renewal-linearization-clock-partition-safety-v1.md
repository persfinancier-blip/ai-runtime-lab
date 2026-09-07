# REVOCATION_AWARE_LEASE_RENEWAL_LINEARIZATION_CLOCK_PARTITION_SAFETY_V1_FROZEN

Date: 2026-09-07
Status: FROZEN design evidence; exact RED/GREEN implementation pending
Parent: LAB-093 / #178
Priority context: LAB-086 remains priority #1 and is blocked in this runtime before repository execution by direct git DNS failure; this document is the recorded distinct fallback from `state/CURRENT.md`.

## Question

When LAB-093 classifies a delegated capability as D2 (bounded, server-enforced lease), what exact protocol makes the claimed revocation horizon trustworthy under renewal-vs-revoke races, partitions, stale issuers, crash recovery, clock skew/rollback, provider-side expiry, retries and hidden renewal paths?

## Result

A D2 lease may support `CLOSED_LOGICAL` only when **renewal authority, revocation authority and use-time enforcement are causally bound to one authenticated monotonic lease generation**. A wall-clock TTL written into a bearer token is not sufficient by itself.

The safe protocol has two supported forms:

1. **Online-mediated D2** — every consequential use reaches an authoritative enforcement point that checks the current lease generation/state. Network partition therefore fails closed. TTL bounds orphaned server-side state but does not grant offline authority.
2. **Provider-expiring D2** — a remote provider may accept an otherwise offline bearer until an expiration it enforces using its own trusted time. This is acceptable only if renewal is linearized at the same provider/authority generation, stale issuers are fenced, maximum lifetime is non-extendable by old credentials, and the provider itself rejects all uses after its authoritative expiry. The client clock is never the security boundary.

Anything else is D3/D4, not D2, for destructive-finalization purposes.

## Primary-source donors and exact mechanism

### etcd Lease API

Current etcd v3.7 documentation defines leases as cluster-granted TTL state: the cluster expires a lease if it does not receive keepalive within the TTL; `LeaseRevoke` revokes it; keys attached to an expired/revoked lease are deleted; keepalive returns the server's remaining TTL. Mechanism reused here: lease grant/renew/revoke are authority-side state transitions, not client-local timeout guesses.

Source: https://etcd.io/docs/v3.7/learning/api/

### Kubernetes Lease API

Kubernetes represents lease ownership through server-stored Lease objects with `renewTime` and `leaseDurationSeconds`; leader-election candidates update shared server state and lose leadership when they fail to renew within the selected timeout. Mechanism reused here: renewal is a shared coordination-state update, not an unauthenticated local timer.

Source: https://kubernetes.io/docs/concepts/architecture/leases/

### Spanner / TrueTime

Google's current Spanner Omni TrueTime documentation represents time as an uncertainty interval and requires bounded clock-rate error; strict ordering is achieved by reasoning over authoritative interval bounds rather than trusting an arbitrary machine wall clock. Mechanism reused here: if physical time participates in a safety proof, uncertainty is explicit and bounded; otherwise use logical epochs and server-side enforcement.

Source: https://docs.cloud.google.com/spanner-omni/true-time-external-consistency

## Threat model

The protocol must remain safe when any of the following occurs without assuming Byzantine consensus among the LAB processes themselves:

- a renewal request races a revoke request;
- a renewal response is delayed until after revocation;
- an issuer crashes after accepting renewal but before replying;
- an old issuer restarts from stale state;
- client wall time jumps backward or forward;
- VM suspend/resume or migration invalidates local monotonic-time assumptions;
- a network partition isolates holder from authority while holder still has cached credentials;
- duplicate retry requests reach multiple authority replicas;
- a provider session has its own renewal/refresh mechanism outside the nominal broker;
- a queued task wakes after the parent lease was revoked;
- a credential is copied to another process/device before revoke;
- audit/registry state lags real provider state.

## Lease authority state

Freeze the following conceptual state as `RevocableLeaseV1`:

```text
lease_id                 stable random identity
capability_root_digest   delegated capability root
holder_identity          authenticated holder
issuer_epoch              monotonically fenced authority generation
lease_generation          monotonically increasing renewal generation
state                     ACTIVE | REVOKED | EXPIRED | CLOSED
issued_at_authority       authority time/sequence
not_after_authority       authority-enforced upper bound
max_not_after_authority   immutable lifetime ceiling for this delegation root
rights_digest             attenuated rights/resource scope
parent_envelope_digest    CapabilityEnvelopeV1 parent
revocation_generation     root revocation generation observed at issue/renew
last_transition_seq       consensus/serialized authority sequence
```

No field supplied only by the holder may extend authority.

## Linearization rules

### Grant

`GRANT` linearizes at the authority after it verifies:

- parent envelope is current and allows delegation;
- requested rights are an attenuation;
- issuer epoch is current;
- root is not revoked;
- requested expiry is `<= max_not_after_authority`;
- no conflicting lease identity exists.

The returned receipt commits to the resulting authority sequence and generation.

### Renew

`RENEW(lease_id, expected_generation, requested_not_after, request_id)` is a compare-and-swap transition.

It succeeds exactly once only if all are true at its linearization point:

- state is ACTIVE;
- issuer epoch is current;
- `expected_generation == lease_generation`;
- root revocation generation still matches;
- requested bound does not exceed immutable `max_not_after_authority`;
- authority has not already crossed the current expiry according to its own admissible clock/sequence rule;
- `request_id` is either unseen or an exact idempotent replay of the same transition.

Success increments `lease_generation` and returns the committed result. A stale or differently parameterized replay fails closed.

### Revoke

`REVOKE(root_or_lease, expected_revocation_generation, request_id)` linearizes in the same serialization domain as renewals. Once the revoke transition is committed:

- no later renewal under the revoked generation may commit;
- any renewal that linearized before revoke is bounded by `max_not_after_authority` and the revoke campaign's chosen closure rule;
- online-mediated use fails immediately on observing REVOKED/current root generation;
- provider-expiring use may remain possible only until the already-authorized provider-enforced expiry; therefore the revocation closure proof must wait through that maximum provider horizon unless the provider supports immediate invalidation.

A revoke must never rely on the holder seeing a cancellation message.

## Renewal-vs-revoke race truth table

The authority serialization order is the only truth:

- `RENEW < REVOKE`: renewal may be valid, but revoke prevents all subsequent renewal. Closure waits only through the renewed bound if immediate use-time revocation is unavailable.
- `REVOKE < RENEW`: renewal must fail; a success response is evidence of stale issuer/equivocation.
- concurrent requests observed at clients: no special state; authority order decides.
- lost renewal response: holder must treat authority as unknown/expired unless an idempotent query proves the exact committed generation.
- timeout after revoke request: revocation state is `UNKNOWN` until authority read/receipt proves the commit; timeout is never success.

## Clock safety

### Forbidden security assumptions

Do not base D2 closure on:

- `datetime.now()` / local wall clock on holder;
- NTP synchronization without a proven uncertainty bound and failure handling;
- token `exp` checked only by the holder;
- process uptime after suspend/restore if monotonic-clock semantics are not guaranteed for that environment;
- comparing timestamps originating in different unsynchronized authority domains.

### Preferred rule

Use **monotonic logical generations for ordering** and authority/provider time only to establish a finite upper lifetime bound.

For online-mediated D2, the holder never decides whether authority is still usable: the enforcement point reads/validates current lease/root generation on every consequential operation.

For provider-expiring D2, the provider's enforcement clock is authoritative. The proof must record the provider's documented maximum skew/expiry semantics or conservatively add an uncertainty margin `epsilon_provider`. Closure horizon is:

```text
H_close >= last_possible_authorized_not_after + epsilon_provider + delivery/commit uncertainty
```

If the provider offers no enforceable maximum expiry or can refresh through an uncontrolled path, classify the capability D3/D4 instead.

## Partition semantics

### Online-mediated mode

Partition between holder and enforcement authority => consequential use unavailable. This is intentional fail-closed behavior and preserves immediate revocation.

Partition among authority replicas => only a replica that can participate in the serialization/quorum may grant/renew/revoke. Minority/stale replicas cannot extend authority.

### Provider-expiring mode

Partition may preserve already-issued authority until provider-enforced expiry, but **cannot extend it**. Renewal requires reaching a current fenced issuer/provider. Therefore availability during partition is bounded and known before the partition begins.

A design that permits locally minted extension during a partition is not D2.

## Stale issuer fencing

Every issuer instance carries an `issuer_epoch` obtained from the serialized authority domain. All lease receipts and provider credentials commit to it.

After reconfiguration/recovery:

- old epochs cannot grant or renew;
- provider/enforcement requests derived from old epochs are rejected where the external system supports epoch/fence validation;
- if an external provider cannot fence old issuers or bound their credential lifetime, physical closure is not provable and the capability is D3/D4.

Issuer identity alone is insufficient; a restarted process with the same identity but stale epoch remains fenced.

## Crash recovery

Authority restart reconstructs lease state only from durable serialized transitions/checkpoints. It must never infer ACTIVE authority solely from holder-provided receipts.

Required recovery invariants:

- committed REVOKED never becomes ACTIVE after restart;
- generation/epoch never decreases;
- duplicate `request_id` is idempotent across crash;
- an in-doubt renewal with no committed transition is not reconstructed as successful;
- an acknowledged renewal must survive restart with the same generation and bound;
- expiry processing may be delayed by crash, but consequential use-time enforcement must still reject authority past the authoritative bound before declaring closure.

## Hidden-renewal-path completeness

A bounded horizon is meaningful only if **all mechanisms capable of extending useful authority are enumerated and fenced**. `RenewalPathInventoryV1` must include, as applicable:

- broker keepalive/renew RPC;
- OAuth/session refresh token;
- cloud/provider credential refresh;
- connection/session heartbeat that silently extends server state;
- queue visibility/ack extension;
- SDK automatic retry/refresh worker;
- child process or plugin holding refresh authority;
- delegated credential minting key;
- administrative/manual renewal endpoint;
- recovery path that recreates sessions after restart.

Each path receives one disposition: `MEDIATED_BY_CURRENT_EPOCH`, `DISABLED`, `BOUNDED_PROVIDER_EXPIRY`, or `UNKNOWN`.

Any `UNKNOWN` material renewal path prevents D2 closure.

## Proof objects

### `LeaseIssuanceProofV1`

Commits to lease/root identity, holder, rights, issuer epoch, generation, authority sequence, `not_after`, immutable max horizon, provider binding and parent capability envelope.

### `LeaseRevocationBarrierV1`

Commits to revoke serialization point, new revocation generation, issuer epoch, set/root of known active leases, no-new-renewal policy and maximum remaining provider horizon.

### `LeaseClosureProofV1`

May assert `CLOSED_LOGICAL` only when:

1. revoke barrier is authenticated and current;
2. every renewal path has a terminal known disposition;
3. no current issuer epoch can extend the revoked root;
4. online enforcement rejects the revoked generation, or the maximum provider-enforced expiry horizon has definitely passed including uncertainty margin;
5. all discovered late renewals/descendants are reconciled;
6. no fraud proof or source equivocation remains unresolved.

### Fraud proofs

Freeze compact evidence shapes for:

- `POST_REVOKE_RENEWAL_COMMITTED`;
- `STALE_ISSUER_RENEWAL_ACCEPTED`;
- `MAX_HORIZON_EXTENSION_PROVEN`;
- `POST_EXPIRY_USE_ACCEPTED`;
- `HIDDEN_RENEWAL_PATH_PROVEN`;
- `CLOCK_BOUND_VIOLATION_PROVEN`;
- `REVOCATION_GENERATION_ROLLBACK_PROVEN`.

Any proven case invalidates dependent closure/finalization/GC certificates and re-roots the affected evidence closure.

## Composition with prior frozen LAB-093 contracts

- `CapabilityEnvelopeV1` defines what authority may be delegated and requires monotonic attenuation.
- `EffectCapabilityInventoryV1` requires the lease/refresh capability itself to be registered.
- `RevocationCampaignV1` supplies the descendant/root revocation generation.
- D1 descendants can close via complete enumeration + mediated rejection.
- D2 descendants can close via this protocol.
- D3/D4 remain UNKNOWN unless an external stronger containment proof exists.
- `CLOSED_LOGICAL` remains distinct from `CLOSED_PHYSICAL`.

## RED-first matrix — 80 cases

### Grant / identity / bounds (1-10)
1. exact valid grant succeeds;
2. grant from revoked parent rejects;
3. grant from stale issuer epoch rejects;
4. rights widening rejects;
5. resource-scope widening rejects;
6. requested expiry beyond immutable max rejects;
7. duplicate exact request id is idempotent;
8. duplicate request id with changed fields rejects;
9. lease-id collision rejects;
10. missing parent-envelope binding rejects.

### Renewal linearization (11-20)
11. current-generation renewal succeeds;
12. stale-generation renewal rejects;
13. future/fabricated generation rejects;
14. exact retry returns same committed renewal;
15. conflicting retry rejects;
16. renewal after expiry rejects;
17. renewal cannot extend max horizon;
18. renewal cannot widen rights;
19. renewal cannot change holder silently;
20. renewal receipt binds authority sequence.

### Revoke races (21-30)
21. renew-before-revoke has bounded final validity;
22. revoke-before-renew rejects renewal;
23. delayed pre-revoke response does not authorize extra generation;
24. revoke timeout remains UNKNOWN;
25. lost renewal reply recovered only by exact idempotent query;
26. duplicate revoke idempotent;
27. conflicting revoke request id rejects;
28. root revoke covers child leases;
29. lease-specific revoke cannot revoke unrelated root;
30. post-revoke grant under old root generation rejects.

### Partitions / replicas (31-40)
31. holder partition blocks online-mediated use;
32. holder partition cannot locally renew;
33. minority authority replica cannot renew;
34. stale leader epoch cannot renew after failover;
35. majority/current issuer may renew normally;
36. provider-expiring credential works only until pre-issued bound;
37. partition cannot extend provider expiry;
38. healed partition rejects stale renewal replay;
39. split-brain two-success renewals produce equivocation/fail closed;
40. quorum loss produces UNKNOWN, not success.

### Clock / expiry (41-50)
41. holder wall-clock rollback does not extend authority;
42. holder wall-clock jump does not prematurely prove closure;
43. provider expiry is checked provider-side;
44. documented provider uncertainty is included in horizon;
45. unknown provider skew prevents closure;
46. VM suspend cannot turn expired lease valid;
47. authority clock-bound violation blocks time-based proof;
48. logical epoch order survives wall-clock discontinuity;
49. cross-domain timestamp comparison without bound rejects;
50. post-expiry provider acceptance yields fraud proof.

### Crash / recovery (51-60)
51. committed renewal survives authority restart;
52. uncommitted renewal not resurrected;
53. committed revoke survives restart;
54. issuer epoch never rolls back after restore;
55. request-id idempotency survives restart;
56. checkpoint + log replay reconstruct exact generation;
57. stale backup restore is fenced;
58. expired-but-not-cleaned row cannot authorize use;
59. recovery path cannot recreate revoked provider session;
60. in-doubt transition stays UNKNOWN until reconciled.

### Hidden renewal paths (61-70)
61. SDK auto-refresh path is inventoried;
62. refresh token is disabled/revoked with lease;
63. child plugin cannot hold unregistered renew capability;
64. queue visibility extension is treated as renewal path;
65. provider session heartbeat is treated as renewal path;
66. admin/manual refresh endpoint is dispositioned;
67. unknown refresh path blocks closure;
68. late-discovered refresh path invalidates closure;
69. delegated minting key is a renewal-equivalent capability;
70. restart automation cannot silently refresh revoked authority.

### Closure / fraud / GC (71-80)
71. online-mediated revoked generation closes immediately after enforcement ack;
72. provider-expiring mode waits through maximum horizon;
73. unresolved late descendant blocks closure;
74. stale issuer acceptance invalidates prior closure;
75. max-horizon extension invalidates prior closure;
76. hidden-path fraud invalidates prior closure;
77. GC cannot remove renewal evidence before closure finality;
78. closure proof binds exact root/revocation/issuer generations;
79. logical closure does not claim physical clawback;
80. all races converge to one of ACTIVE, REVOKED/EXPIRED, CLOSED_LOGICAL or UNKNOWN without unsafe success.

## Production decision

For LAB-093, prefer **online-mediated D2** for consequential authority whenever possible. It is simpler to prove: no client clock is trusted, partitions fail closed, and revocation takes effect at the authoritative enforcement point.

Use provider-expiring D2 only when the provider itself enforces a finite maximum lifetime and stale issuers cannot extend it. A bearer credential whose lifetime/refresh cannot be bounded by the external enforcement domain must not be called D2.

## Audit

Security audit of this design found three tempting but invalid shortcuts and rejects all three:

1. client-side TTL expiry as revocation proof;
2. successful revoke RPC without ordering it against renewals;
3. enumerating nominal lease APIs while ignoring SDK/provider/session refresh paths.

No production behavioral PASS is claimed. This is a frozen design/test contract to be implemented only when exact source execution becomes available.

## Next distinct question

**Lease/enforcement quorum handoff / issuer-epoch transition / provider-fence continuity semantics**: define how a D2 authority changes replica membership, consensus generation, broker/provider implementation or signing root without a gap where old and new issuers can both renew, and how an offline verifier proves the handoff chain after historical issuers are retired.
