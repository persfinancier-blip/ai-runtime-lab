# LAB-090 / LAB-100 — unified provider-authority redesign contract

Date: 2026-09-03

Status: research / regression-first design contract. No production fix or behavioral PASS is claimed by this note.

## Why one redesign is now safer than isolated patches

The current LAB-090 draft splits one logical external authority across several separately reachable or reconstructable pieces:

- `SignedAnchorProvider` owns provider id, generation, signing key, anchor value and request-idempotency results;
- `FencedActivationProvider` adds a separate `ActivationState` containing `next_fence`, `pending`, `committed`, and its own lock;
- the coordinator persists a second activation state machine in SQLite (`SQL_COMMITTED | COMMITTED`);
- `AttestedCatchup` and its verifier retain another view of provider identity/key;
- caller code can reconstruct provider objects and, today, can retain/rebind mutable activation/provider state.

The retained LAB-090 and LAB-100 findings are therefore not independent accidents. They are different manifestations of split authority and split ownership:

1. post-prepare failures can strand an external reservation before durable recovery ownership exists;
2. status/abort semantics can claim provider evidence while the provider is unavailable;
3. duplicate retry after release is mishandled because terminal provider state and durable SQL state are reconciled separately;
4. activation-id collision recovery can treat a different durable row as evidence that this exact ticket committed;
5. pre-SQL external commit can leave a committed fence with no durable recovery handle;
6. inherited generic provider rotation can change identity/key/generation without activation-state coordination;
7. caller-owned `ActivationState` can directly mutate the provider fence state;
8. reconstructed providers can combine one activation state with a different anchor value/request-result authority;
9. malformed returned tickets can leave an authentic provider reservation with no trusted cancellation handle;
10. reconstructed `next_fence` can reuse old fencing tokens.

Patching these one by one would preserve the underlying split and create more inter-phase edge cases.

## Required authority unit

A supported LAB-090 activation provider should expose one construction-bound authority object whose durable/provider-equivalent state contains, as one coherent unit:

- provider identity;
- generation;
- verification/signing key identity required by the provider implementation;
- anchor position / compare-and-swap state;
- request-idempotency result map or equivalent durable result identity;
- activation reservation state;
- committed activation state;
- monotonic fencing-token allocator/epoch;
- one synchronization/serialization primitive over all of the above.

The supported coordinator must not be able to combine the activation state from authority A with the position, key, request results, or identity from authority B.

If a real remote provider is used, the same requirement applies at the protocol boundary: the remote service (or a trusted adapter whose semantics are independently verifiable) must provide one authenticated capability representing this coherent authority. Merely returning valid-looking lifecycle strings is insufficient.

## Capability boundary

Production code must choose one explicit extension model.

### Model A — exact audited in-process provider

If LAB-090 supports only the audited implementation, accept the exact provider authority implementation and expose only least-capability/read-only views outside the coordinator/provider owner.

### Model B — trusted provider adapter protocol

If custom/remote providers are required, define an explicit trusted adapter/capability contract that supplies authenticated evidence for:

- exact provider/generation identity;
- exact expected position at prepare;
- unique monotonic fence token;
- reservation ownership handle;
- terminal activation status;
- cancellation/release outcome;
- provider availability/currentness;
- idempotent recovery after timeout/restart.

Subclassing `FencedActivationProvider` and trusting overridden return values is not such a boundary.

## Lifecycle ownership rule

A successful `prepare` is the moment from which the coordinator must possess one trusted recovery handle. There must be no fallible operation between successful prepare and establishment of recovery ownership that can strand the reservation without durable/reconstructable evidence.

Therefore the implementation must not have separate unowned windows around:

- the first status probe;
- SQLite connection open;
- SQL BEGIN;
- row validation;
- provider commit;
- durable acknowledgement;
- release.

Every outcome after successful prepare must resolve to exactly one of:

- safely aborted before provider commitment;
- durably recoverable prepared activation;
- durably recoverable committed-fenced activation;
- durably acknowledged committed activation awaiting/retrying release;
- terminal released activation whose exact durable activation ticket is already COMMITTED.

No branch may discard the only trusted reservation/ticket identity.

## Availability semantics

`unavailable` is part of provider evidence semantics, not merely an increment-path convenience.

While provider availability cannot be authenticated/confirmed, coordinator code must not synthesize authoritative lifecycle evidence from a local mutable object. In particular, status, abort, commit and release recovery decisions must all obey the same outage contract.

A provider outage may leave a recoverable operation pending; it must not become evidence that the reservation was absent, aborted, committed or released.

## Exact durable-ticket binding

SQLite recovery evidence is evidence for *this* activation only when all authority-relevant fields exact-match the trusted provider ticket and target transition:

- activation id;
- new generation id;
- provider id;
- generation;
- expected position;
- fence token;
- relevant authenticated transition/descriptor identity.

A row that merely shares `activation_id` or terminal status is not proof that the coordinator's transaction committed.

Historical activation provenance must eventually bind the exact ticket (or canonical authenticated digest of it) into authenticated provider-generation transition evidence; the mutable activation table must not authenticate itself.

## Fencing-token rule

Fence tokens must be strictly monotonic across restart/reconstruction of the same logical provider authority. Reconstructing an authority with historical tickets but a reset/default allocator is invalid.

The monotonic allocator/epoch belongs to the same durable authority as position and activation state. It must not be caller-owned mutable state.

## Generic rotation rule

Generic `SignedAnchorProvider.rotate()` cannot remain an independent mutation path on a LAB-090 provider while activation is non-quiescent.

One of the following must be true:

- generic rotation is unavailable on the supported LAB-090 authority;
- it is activation-aware and serialized under the same authority lock/state machine;
- or identity/key rotation is performed only by constructing/activating a distinct coherent provider authority.

Changing provider id/generation/key while a pending activation ticket remains bound to the old identity must be impossible through the supported surface.

## Regression-first matrix

Before production changes, exact-source RED tests should cover at least:

1. successful prepare then first status-probe failure;
2. successful prepare then SQLite connection-open failure;
3. provider unavailable during status;
4. provider unavailable during abort;
5. duplicate same-ticket retry after durable COMMITTED + provider RELEASED;
6. activation-id collision with different generation/position/fence;
7. external provider commit before SQL durability followed by SQL rollback;
8. malformed ticket returned after a real reservation was installed;
9. caller attempts to mutate retained activation state;
10. reconstructed provider with shared activation state but different anchor position/request results;
11. reconstructed provider whose fence allocator would reuse an old token;
12. generic identity/key rotation while activation is PREPARED;
13. fake/subclass provider returning valid-looking lifecycle states without a real fence;
14. restart from PREPARED, COMMITTED_FENCED and COMMITTED-before-release states;
15. UNKNOWN/timeouts at provider commit and release boundaries;
16. exact SQL activation row mismatch despite same activation id/status.

Each RED must assert not only the raised error but also preservation of authority state: no unintended provider advance, no fence release, no generation-head mutation, no invented durable acknowledgement, and no loss of the trusted recovery handle.

## Acceptance gate for a replacement implementation

A replacement LAB-090 provider boundary is not ready until all of the following are true:

- the above RED matrix turns GREEN on exact published source;
- existing LAB-090 focused concurrency/restart tests remain GREEN;
- LAB-092 schema/provenance gates remain fail-closed and are evaluated at the relevant serialization boundary;
- LAB-098/LAB-099 historical activation-presence/ticket-authentication regressions compose with the new durable ticket model;
- LAB-080/LAB-081 downstream shared-anchor behavior remains GREEN;
- a separate audit finds no second mutation route to identity/key/position/request-results/activation/fence allocation outside the supported authority unit.

## Decision

Do not continue repairing PR #175 as a collection of unrelated local checks. Treat LAB-090 and LAB-100 as one provider-authority ownership problem. The next production change should be regression-first and should replace the split authority boundary coherently rather than adding another lifecycle conditional.
