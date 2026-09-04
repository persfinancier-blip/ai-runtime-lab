# Provenance startup verifier + recovery planner V1

Date: 2026-09-04
Status: design contract frozen; exact RED/GREEN pending
Related: LAB-080/081, LAB-086/#163, LAB-090/#169, LAB-092/#176, LAB-093/#178, LAB-097..100/#182..185

## Objective

Freeze a side-effect-free startup verifier and a pure recovery-planner API over the already-frozen canonical provenance encoding, parent-linked chain, atomic append protocol and durable SQL schema. Verification must never mutate SQLite or provider state. Recovery eligibility must be represented as data and executed later through the already-defined LAB-080/LAB-091/LAB-087 write boundaries.

A fresh direct `git clone --no-checkout` again failed before repository access with `Could not resolve host: github.com`; no production verifier code and no exact repository behavioral PASS are claimed in this run.

## Core boundary

V1 separates three phases:

1. `verify_startup(snapshot_inputs) -> VerifyResult`
2. `plan_recovery(VerifyResult, external_evidence) -> RecoveryPlan`
3. `execute_recovery(RecoveryPlan)` — outside the verifier, through the exact LAB-080/LAB-091 transaction/provider protocol.

The verifier and planner are pure with respect to durable/runtime mutation. They may read SQLite and call authenticated read/reconcile endpoints only through an explicit evidence collector, but they do not write, release a fence, re-bootstrap history, create schema, update a head, confirm an intent, or delegate a worker.

## Frozen API shape

Conceptual typed surface:

```python
@dataclass(frozen=True)
class VerifyInputs:
    logical_database_identity_digest: bytes
    retained_authority_graph_digest: bytes
    initialization_certificate_digest: bytes
    expected_schema_digest: bytes
    expected_protocol_version: int

@dataclass(frozen=True)
class ExternalEvidenceRequest:
    kind: Literal[
        "AUTHENTICATED_READ",
        "REAUTHENTICATE_CONFIRMED_RECEIPT",
        "RECONCILE_PREPARED_REQUEST",
    ]
    anchor_intent_id: str
    request_id: str
    expected_position: int
    receipt_binding: bytes | None

@dataclass(frozen=True)
class VerifiedHead:
    epoch: int
    link_digest: bytes
    provider_head_digest: bytes
    authority_digest: bytes
    schema_state_digest: bytes

@dataclass(frozen=True)
class PreparedTransition:
    transition_id: bytes
    parent_epoch: int
    parent_link_digest: bytes
    successor_link_digest: bytes
    event_digest: bytes
    anchor_intent_id: str
    request_id: str
    expected_position: int
    local_anchor_state: Literal["PREPARED", "CONFIRMED"]
    receipt_binding: bytes | None

@dataclass(frozen=True)
class VerifyResult:
    verified_head: VerifiedHead
    prepared: PreparedTransition | None
    evidence_requests: tuple[ExternalEvidenceRequest, ...]
    warnings: tuple[str, ...] = ()

@dataclass(frozen=True)
class RecoveryPlan:
    kind: Literal[
        "NONE",
        "RETRY_EXACT_PREPARED_REQUEST",
        "CONFIRM_EXACT_RECONCILED_REQUEST_THEN_COMMIT",
        "COMMIT_CONFIRMED_PREPARED_TRANSITION",
    ]
    transition_id: bytes | None
    anchor_intent_id: str | None
    exact_request_id: str | None
    exact_position: int | None
    successor_link_digest: bytes | None
    preconditions_digest: bytes | None
```

Any corruption is returned as a typed failure, not encoded as an actionable plan.

## Ordered startup reads

Startup performs reads in this exact logical order before any repair/release/delegation:

1. **SQLite object inventory** — exact four provenance tables plus required LAB-080 tables/triggers; no `CREATE IF NOT EXISTS` on ordinary restart.
2. **Initialization identity** — load authenticated logical DB identity / initialization certificate and require it matches retained construction inputs.
3. **Head cache** — read the singleton cached head, but treat it only as a candidate terminal index.
4. **Genesis row** — require exactly one epoch-0, NULL-parent link for this DB identity; decode canonical bytes and verify digest.
5. **All chain links for this DB** ordered by epoch with SQLite `typeof()` checks before Python conversion.
6. **All provenance transitions for this DB** ordered by `parent_epoch`.
7. **Referenced immutable events** for every reachable link/transition.
8. **Referenced LAB-080 intents** by exact `anchor_intent_id`; do not scan by “latest”, rowid, timestamp or MAX(position) as authority.
9. **Event-specific durable state** needed to validate legal state deltas: provider-generation head/history, activation ticket commitments, authority descriptor, migration/schema state.
10. Only after all local structural/authenticated checks succeed may the result request narrow external evidence for the one eligible current PREPARED transition.

## Canonical verification

For every event/link/transition:

- storage class must match the V1 SQL contract;
- every BLOB digest is exactly 32 bytes;
- canonical bytes are decoded with the shared domain-separated V1 decoder;
- duplicate, unknown, reordered, malformed, non-UTF-8 or trailing canonical fields fail closed;
- recomputed SHA-256 must equal stored digest;
- decoded fields must exactly reproduce indexed SQL columns;
- INTEGER means strict Python integer semantics, never bool/REAL/numeric TEXT coercion;
- protocol/domain/version must be exactly supported.

No local self-hash, status flag or matching SQL columns substitute for canonical-byte verification.

## Full-chain traversal

The verifier reconstructs authority from genesis forward, never backward from the cached head alone.

For epoch `e > 0`:

- exactly one link exists at epoch `e`;
- its `parent_link_digest` equals the authenticated link at `e-1`;
- exactly one transition names the previous link/epoch and this successor;
- transition event digest equals the link event digest;
- transition post-state digests equal the successor link’s canonical post-state commitment;
- the transition’s referenced LAB-080 intent is exact and belongs to `component_id='provenance-chain'` under the executable integration;
- event-specific state delta is legal: provider event changes only provider head, migration only schema state, authority transition only authority state.

The COMMITTED prefix must be contiguous from genesis to the cached head. The verifier rejects:

- gaps;
- siblings/forks;
- two transitions for one parent;
- orphan reachable links;
- COMMITTED transition beyond cached head;
- cached head through PREPARED evidence;
- cached head rollback to an earlier otherwise-valid prefix;
- attacker-chosen MAX(epoch), rowid or timestamp terminal selection.

## PREPARED classification

At most one PREPARED transition may exist, and it must be the exact immediate child of the authenticated current head.

It is locally eligible only when:

- parent epoch/digest equal current head;
- successor epoch is exactly parent+1 and within V1 range;
- exact event/link/transition bytes and digests verify;
- no sibling child or sibling transition exists;
- event-specific preconditions are still true;
- exact referenced LAB-080 intent exists;
- LAB-080 request id/position/content match the frozen transition commitment;
- local LAB-080 state is PREPARED or CONFIRMED only.

Any historical PREPARED row, multiple PREPARED rows, wrong-parent PREPARED row, missing event/link or changed LAB-080 identity is corruption and yields no recovery action.

## External evidence boundary

The verifier does not silently contact a provider during arbitrary chain traversal. It emits the minimum external evidence request only for the one locally eligible PREPARED child.

### Local LAB-080 PREPARED

Request exact reconciliation for that row’s `(request_id, expected_position)`.

Allowed evidence classes:

- exact request absent and authenticated provider position still equals predecessor -> planner may emit `RETRY_EXACT_PREPARED_REQUEST`;
- exact request proved committed at expected position with valid receipt -> planner may emit `CONFIRM_EXACT_RECONCILED_REQUEST_THEN_COMMIT`;
- provider ahead but exact request cannot explain the advance -> corruption / unexplained advance;
- request id exists with different position/content -> corruption.

### Local LAB-080 CONFIRMED

Require re-authentication of the exact persisted receipt binding for the exact request/position. Only successful re-authentication permits `COMMIT_CONFIRMED_PREPARED_TRANSITION`.

A local CONFIRMED flag without external receipt re-authentication is never enough.

## Recovery planner purity

`plan_recovery()` consumes an already-successful `VerifyResult` plus exact external evidence. It must not re-read mutable state behind the verifier’s back and must not perform mutations.

Every non-NONE plan contains a `preconditions_digest` over the exact verified head, transition id, anchor intent id, request id, position, successor link and relevant event-specific preconditions. `execute_recovery()` must re-read and compare these values inside the final LAB-091-authorized `BEGIN IMMEDIATE` transaction before any local mutation. A stale plan fails closed rather than being refreshed implicitly.

## Corruption / error taxonomy

V1 freezes explicit classes so callers cannot collapse corruption into “migration needed” or “retry”:

- `SchemaMissingAfterInitialization`
- `SchemaDefinitionMismatch`
- `InitializationProvenanceMismatch`
- `DatabaseIdentityMismatch`
- `CanonicalEncodingError`
- `DigestMismatch`
- `StorageTypeMismatch`
- `UnsupportedProtocolVersion`
- `GenesisCardinalityError`
- `ChainGap`
- `ChainFork`
- `ParentMismatch`
- `TransitionCardinalityError`
- `IllegalStateDelta`
- `HeadCacheMismatch`
- `HistoricalPreparedTransition`
- `MultiplePreparedTransitions`
- `PreparedNotImmediateChild`
- `AnchorIntentMissing`
- `AnchorIntentBindingMismatch`
- `CommittedTransitionWithoutConfirmedAnchor`
- `ReceiptReauthenticationFailed`
- `ExternalRequestConflict`
- `UnexplainedExternalAdvance`
- `ProviderHistoryProvenanceMismatch`
- `ActivationTicketProvenanceMismatch`
- `AuthorityDescriptorMismatch`
- `MigrationProvenanceMismatch`
- `EpochExhausted`

These are fail-closed startup outcomes. None authorizes repair by itself.

## Side-effect prohibition

During `verify_startup()` and `plan_recovery()` the following are forbidden:

- INSERT/UPDATE/DELETE/DDL in SQLite;
- creation of missing tables/triggers;
- bootstrap installation or provider-history normalization;
- provider increment/activation prepare/commit/release/abort;
- LAB-080 intent confirmation writes;
- provenance PREPARED->COMMITTED mutation;
- cached-head update;
- migration execution;
- authority upgrade;
- worker endpoint creation/delegation.

An executable implementation should enforce this with a read-only SQLite connection where practical plus behavioral tests that snapshot DB/provider state before and after every verifier failure class.

## Restart/open ordering

Broker restart order is frozen as:

1. construct retained authority graph;
2. open database for verification without ordinary-startup repair;
3. verify initialization provenance;
4. verify exact schema/storage definitions;
5. traverse and authenticate full provenance chain;
6. verify provider-generation / migration / activation / authority event-specific commitments;
7. classify at most one PREPARED child;
8. collect only the exact external evidence requested;
9. create a pure RecoveryPlan;
10. if plan is NONE, open normal runtime only after terminal external-anchor continuity is verified;
11. if plan is actionable, execute it through LAB-080/LAB-091/LAB-087 gates, then restart verification from step 1;
12. delegate LAB-093 worker endpoints only after a clean no-recovery VerifyResult.

Recovery is therefore never interleaved with partial verification.

## RED-first verifier/planner matrix

Freeze before production implementation:

1. clean initialized DB -> VerifyResult, no plan;
2. verification leaves DB byte/logical state unchanged;
3. verification leaves provider state unchanged;
4. missing provenance table after initialization -> fail closed, no CREATE;
5. altered table/trigger definition -> fail closed;
6. wrong logical DB identity -> fail;
7. wrong initialization certificate -> fail;
8. malformed canonical event -> fail;
9. malformed canonical link -> fail;
10. digest/bytes mismatch -> fail;
11. TEXT/REAL/bool numeric confusion -> fail;
12. second genesis -> fail;
13. epoch gap -> fail;
14. sibling link fork -> fail;
15. sibling transition fork -> fail;
16. wrong parent digest -> fail;
17. orphan reachable link -> fail;
18. COMMITTED transition beyond head -> fail;
19. cached head rollback -> fail;
20. head points through PREPARED -> fail;
21. historical PREPARED -> fail;
22. two PREPARED transitions -> fail;
23. PREPARED wrong parent -> fail;
24. PREPARED missing event -> fail;
25. PREPARED missing link -> fail;
26. PREPARED missing LAB-080 intent -> fail;
27. PREPARED intent wrong request id -> fail;
28. PREPARED intent wrong position -> fail;
29. PREPARED intent wrong commitment -> fail;
30. local PREPARED + provider unchanged/request absent -> exact retry plan only;
31. local PREPARED + exact request reconciles committed -> confirm-then-commit plan only;
32. local PREPARED + unexplained provider advance -> fail;
33. local PREPARED + conflicting request reuse -> fail;
34. local CONFIRMED + exact receipt reauth -> commit plan only;
35. local CONFIRMED + receipt reauth failure -> fail;
36. local CONFIRMED + mutated receipt binding -> fail;
37. provider event mutates authority digest -> illegal delta fail;
38. migration event mutates provider head -> illegal delta fail;
39. authority event mutates schema digest -> illegal delta fail;
40. deleted historical activation commitment -> fail;
41. coherently rebound historical activation ticket -> fail;
42. retained bootstrap/history strategy rebinding -> fail;
43. activation authority descriptor/version drift -> fail;
44. migration certificate valid bytes but wrong parent link -> fail;
45. stale RecoveryPlan after concurrent head advance -> executor rejects before mutation;
46. recovery success -> complete re-verification required before runtime open;
47. epoch `2^63-1` verifies, but actionable next append is rejected as exhausted;
48. LAB-093 restricted worker cannot invoke verifier with raw writable DB/provider capability.

## Audit conclusions

- Verification and recovery are separate authorities: observing recoverable state does not grant mutation authority.
- The cached local head is an optimization only; authority comes from full canonical parent traversal plus event-specific commitments and LAB-080 external evidence.
- UNKNOWN-after-commit is recoverable only for one exact already-frozen PREPARED transition.
- Ordinary startup never repairs missing provenance/history/schema evidence.
- Every recovery execution is followed by a fresh verification pass; a plan is not a durable truth object.
- This contract composes with LAB-087 sole-writable broker, LAB-091 one-shot DML authorization and LAB-093 least-capability worker delegation.

## Verdict

`PROVENANCE_STARTUP_VERIFIER_RECOVERY_PLANNER_V1_FROZEN`

Production implementation remains blocked on exact executable RED/GREEN capability. LAB-086 remains priority #1.