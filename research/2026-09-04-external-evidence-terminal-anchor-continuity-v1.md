# External Evidence Collector + Terminal Anchor Continuity V1

Date: 2026-09-04

Verdict: `EXTERNAL_EVIDENCE_TERMINAL_ANCHOR_CONTINUITY_V1_FROZEN`

## Scope

This note freezes the side-effect and freshness contract for the external evidence consumed by the previously frozen startup verifier/recovery planner. It is a design/evidence artifact only; no production code or behavioral GREEN is claimed in this run.

The contract composes with LAB-080 shared-anchor intents, LAB-090 activation fencing, LAB-091 writer authorization, LAB-092 migration provenance, LAB-093 broker confinement, LAB-094..096 retained authority, LAB-097..099 authenticated provenance, LAB-100 activation authority, canonical byte encoding V1, parent-linked provenance chain V1, atomic append/recovery V1, durable SQL storage V1, and the startup verifier/recovery planner V1.

## Source facts observed

1. LAB-036 `SignedAnchorProvider.read()` is observational: it returns a signed `READ` observation and does not change provider position or request-result state. `reconcile_increment()` is also observational with respect to provider position: it only looks up a previously recorded `request_id` and returns a fresh signed `RECONCILE` observation for that result. `increment()` is mutating and can return `UnknownOutcome` after the provider has already advanced.

2. LAB-036 `AttestedCatchup.authenticated_read()` performs provider `read` plus verification. `catch_up_one()` is not observational: when the provider is exactly one position behind, it calls `increment()`, and on `UnknownOutcome` it calls `reconcile_increment()` for the same request id.

3. LAB-080 shared-anchor `_reauthenticate(entry)` uses a fresh challenge plus `provider.reconcile_increment(request_id=entry.request_id)`, verifies kind `RECONCILE`, and requires exact `(position, request_id)` equality before deriving a stable receipt binding. `execute()` may call `catch_up_one()` and therefore is mutating. `verify_component()` begins with authenticated read, but later may write a component watermark after validating the exact confirmed ledger slice; it is therefore not a side-effect-free evidence collector as a whole.

4. LAB-090 `FencedActivationProvider.increment()` rejects external increments while an activation reservation remains pending. Activation `release_activation()` and `abort_activation()` explicitly remove `activation_state.pending`; those calls are mutating authority operations and must never be reachable from startup evidence collection.

## Trust boundary

The startup verifier must not directly own a general-purpose provider capability. It consumes a narrow internal `ExternalEvidenceCollector` owned by the LAB-087/LAB-093 broker boundary and bound at construction to the LAB-094..096 retained-authority graph and LAB-100 activation-authority descriptor.

The collector exposes only observational operations. It cannot expose or internally call:

- provider `increment`;
- `AttestedCatchup.catch_up_one`;
- activation `prepare_activation`, `commit_activation`, `release_activation`, or `abort_activation`;
- SQLite mutation methods;
- LAB-080 `execute`, reserve/confirm/watermark mutation paths;
- any provider-generation rotation or authority-upgrade operation.

If a provider implementation cannot offer an independently audited observational read/reconcile path, it is unsupported for startup verification and recovery planning.

## Exact collector operations

### `authenticated_terminal_read(snapshot_id, request_id)`

Inputs:
- canonical retained provider identity `(provider_id, generation)`;
- one fresh unpredictable challenge generated inside the broker;
- caller-supplied deterministic `request_id` bound to the verifier run and expected chain head;
- `snapshot_id`, a local verifier-run nonce/digest that is not sent as mutable authority but is included in the returned evidence envelope.

Provider action:
- exactly one observational `read(challenge, request_id)`.

Verification:
- verify signature/MAC with the retained verification authority;
- require exact provider id and generation;
- require exact challenge and `READ` kind;
- require request id equality;
- require integer position in the canonical supported range.

Output:
`TerminalReadEvidence(provider_id, generation, position, request_id, observation_digest, snapshot_id)`.

No SQLite/provider state is written.

### `reauthenticate_request(snapshot_id, request_id, expected_position)`

Inputs:
- exact retained provider identity;
- exact historical LAB-080 request id already committed to authenticated local provenance;
- exact expected position already committed to local provenance;
- fresh challenge;
- verifier-run `snapshot_id`.

Provider action:
- exactly one observational `reconcile_increment(challenge, request_id)`.

Classification:
- `None` => `NO_PROVIDER_RESULT`;
- authenticated result with exact `(provider_id, generation, request_id, expected_position)` => `EXACT_RESULT`;
- authenticated result with a different position/request/provider/generation => `CONFLICTING_RESULT`;
- unavailable transport => `EVIDENCE_UNAVAILABLE`;
- malformed/forged/stale/replayed observation => `EVIDENCE_INVALID`.

Output includes the canonical digest of the fresh verified observation and the stable receipt binding, but does not persist either value.

No increment retry is allowed inside this operation.

### `activation_status_read(snapshot_id, exact_ticket)`

This operation is permitted only for the exact LAB-100 registered activation authority. It may query an independently verifiable observational status surface for the exact authenticated activation ticket.

It must not call release/abort/commit. If the supported activation implementation cannot prove that status inspection is observational, startup returns `EVIDENCE_UNAVAILABLE` and recovery execution remains blocked.

## Snapshot freshness and TOCTOU rule

External evidence is not timeless. Every collection run has one `snapshot_id = H(domain, db_identity, authenticated_chain_head_digest, provider_descriptor_digest, activation_authority_digest, verifier_nonce)`.

Every evidence item carries this `snapshot_id`. The verifier/planner may combine only evidence from the same snapshot.

Before any later write-capable recovery executor acts, it must re-read/recompute all local preconditions and require the planner's existing `preconditions_digest` to match. The executor must then obtain fresh external evidence for the exact action where the provider contract requires it. Evidence from the verification phase is never treated as a lock or reservation.

A provider observation carries no authority to mutate SQLite and no authority to release a fence.

## Terminal anchor continuity classification

Let `H` be the authenticated local terminal position derived by full canonical chain traversal, not cached head/MAX(rowid/epoch). Let `E` be the fresh authenticated external terminal position.

- `E == H`: `ALIGNED`.
- `E == H - 1`: `ONE_BEHIND`. This is not corruption by itself. It is actionable only if the authenticated local state contains exactly one immediate PREPARED transition whose LAB-080 request id/position/event/link bytes match the frozen recovery contract. The planner may produce an exact retry/reconcile plan; the collector itself does nothing.
- `E < H - 1`: `PROVIDER_BEHIND_UNSAFE_GAP`; fail closed. Do not synthesize or batch missing increments.
- `E > H`: `PROVIDER_AHEAD`; fail closed unless every position in `(H, E]` can be explained by already authenticated local provenance and exact provider receipts under a separately defined recovery path. In V1 startup verification, unexplained provider-ahead is corruption/rollback evidence, not a repair invitation.
- transport/status uncertainty: `UNKNOWN_OR_UNAVAILABLE`; no write-capable action unless a specific frozen PREPARED request can be reconciled by exact request id.

The collector never converts `ONE_BEHIND` into `ALIGNED`; only the write-capable recovery executor may do that through LAB-080/LAB-091 after exact-plan revalidation.

## UNKNOWN-after-commit semantics

For an authenticated local PREPARED LAB-080 request `R` at expected position `P`:

1. Startup may call only `reconcile_increment(R)`.
2. If an exact authenticated result for `R,P` exists, classify `REQUEST_COMMITTED_EXTERNALLY`.
3. If no result exists, classify `REQUEST_NOT_PROVEN_COMMITTED`; a planner may authorize exact retry of the same request id only if all local PREPARED/event/link bytes remain unchanged and provider terminal position is exactly the expected predecessor.
4. A different result, a provider position beyond `P`, or changed provider generation is fail-closed.
5. Never issue a new request id to "probe" whether the old mutation committed.

This preserves idempotency and prevents evidence collection from becoming an accidental second writer.

## Activation-fence continuity

Startup evidence collection must preserve activation fences byte-for-byte/state-for-state.

Required invariant before and after each collector call:
- no call to activation prepare/commit/release/abort;
- no call to provider increment while a fence is active;
- no mutation of `ActivationState.pending`, `committed`, or `next_fence`;
- no provider-generation rotation;
- no SQLite activation-row update.

If status inspection itself can mutate these surfaces, that provider implementation is unsupported for V1 collector use.

## Fail-closed taxonomy

The collector returns typed evidence/classification only. It does not raise generic exceptions that a caller may interpret as permission to repair.

Minimum classes:
- `ALIGNED`;
- `ONE_BEHIND_EXACT_PREPARED`;
- `NO_PROVIDER_RESULT`;
- `REQUEST_COMMITTED_EXTERNALLY`;
- `PROVIDER_BEHIND_UNSAFE_GAP`;
- `PROVIDER_AHEAD`;
- `PROVIDER_IDENTITY_MISMATCH`;
- `GENERATION_MISMATCH`;
- `CONFLICTING_RESULT`;
- `EVIDENCE_INVALID`;
- `EVIDENCE_UNAVAILABLE`;
- `ACTIVATION_STATUS_UNVERIFIABLE`.

Only the planner maps a narrow subset to an actionable `RecoveryPlan`.

## RED-first matrix

Before production implementation, execute at least these cases on exact supported source:

1. authenticated read at aligned head;
2. read one behind with exact immediate PREPARED transition;
3. one behind without PREPARED transition;
4. provider two positions behind;
5. provider one position ahead;
6. provider many positions ahead;
7. wrong provider id;
8. wrong generation;
9. forged READ;
10. stale/replayed READ;
11. request-id substitution on READ;
12. exact reconcile result for PREPARED request;
13. reconcile returns None;
14. reconcile returns wrong position;
15. reconcile returns wrong request id;
16. reconcile returns wrong provider/generation;
17. forged RECONCILE;
18. unavailable reconcile path;
19. UNKNOWN-after-commit with exact result;
20. UNKNOWN with no result and provider still at predecessor;
21. UNKNOWN with no result but provider already ahead;
22. stale snapshot mixed with a newer local chain head;
23. two evidence items from different snapshot ids;
24. local preconditions change after collection and before plan execution;
25. collector call leaves SQLite byte-for-byte/row-for-row unchanged;
26. collector call leaves provider position unchanged;
27. collector call leaves provider request-result map unchanged except provider-internal non-authority telemetry, if any;
28. collector call under active LAB-090 fence leaves `pending`, `committed`, and `next_fence` unchanged;
29. collector cannot reach `release_activation`;
30. collector cannot reach `abort_activation`;
31. collector cannot reach provider `increment`;
32. restricted LAB-093 worker cannot recover the raw provider from the collector façade;
33. provider-generation rotation between local verification and evidence collection fails generation binding;
34. activation-authority upgrade between local verification and status read fails descriptor binding;
35. confirmed historical LAB-080 receipt reauthentication exact-match;
36. confirmed historical receipt binding mismatch;
37. provider result exists for a different historical request at same position;
38. duplicate historical request id in local state rejected before provider call;
39. terminal cache says aligned but full chain says different head: full chain wins;
40. terminal provider read is aligned but authenticated chain contains an unresolved illegal fork: verification fails before evidence can authorize continuation.

## Design consequences

- `verify_component()` is not the V1 startup evidence primitive because it can advance a watermark.
- `catch_up_one()` is not an evidence primitive because it may mutate the provider.
- `reconcile_increment()` is safe only as exact request-result observation; it must never be followed by an implicit retry inside the collector.
- provider-ahead/behind classification is evidence, not authority to normalize state.
- every write remains in the separately authorized recovery executor and must revalidate local preconditions plus obtain any required fresh external evidence.

## Next distinct evidence task if exact execution remains unavailable

Freeze the recovery executor command grammar and idempotency contract: exact allowed commands, required preconditions/evidence, transaction/provider-call ordering, crash windows, and which commands may advance the terminal anchor versus only finalize authenticated local provenance. Do not implement production code until executable RED/GREEN becomes available.
