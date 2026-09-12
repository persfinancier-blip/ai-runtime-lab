# LAB-099 — provider activation provenance atomic state machine

Date: 2026-09-12
Status: SOURCE-COMPOSED STATE MACHINE FROZEN; exact RED/GREEN pending
Related: LAB-080/081, LAB-090/#169 PR #175, LAB-092/#176 PR #177, LAB-097/#182, LAB-098/#183, LAB-099/#184, LAB-100/#185

## Objective

Pin the smallest crash-safe ordering for the separate V2 provider-transition provenance event frozen in `2026-09-12-lab099-versioned-transition-provenance-storage-seam.md`, using the actual LAB-090 PR #175 transaction boundaries and the already-frozen `ATOMIC_PROVENANCE_APPEND_RECOVERY_V1_FROZEN` contract.

No production code is changed in this run. Exact repository execution remains unavailable because direct git transport fails before repository execution with `Could not resolve host: github.com`; this is source-composed design evidence only.

## Source facts that constrain the ordering

PR #175 currently performs provider rotation in this order:

1. derive `expected_position` from `shared_anchor_meta`;
2. derive deterministic `activation_id` from successor generation + expected position;
3. call `provider.prepare_activation(...)`;
4. validate the returned exact `ActivationTicket` and require provider status `PREPARED`;
5. under one `BEGIN IMMEDIATE`, insert `provider_generation_activations(..., SQL_COMMITTED)`, call `_rotate_locked()` (generation row + transition row + head advance), and commit;
6. call provider `commit_activation()` / reconcile UNKNOWN;
7. persist activation `COMMITTED` acknowledgement;
8. release the provider fence.

The provider-side `prepare_activation()` is already idempotent for the same deterministic `activation_id`: if the id is already committed or pending with the same expected position, it returns the retained exact ticket rather than allocating a new fence. If another activation is pending or the same id is rebound to another position, it fails.

The V2 LAB-099 event, however, must authenticate the exact activation ticket digest, including the provider-assigned `fence`. Therefore the final V2 event bytes cannot exist before the first successful `prepare_activation()`.

This conflicts with a literal application of the generic provenance rule "Transaction A before any external provider mutation". The provider-generation event needs a provider-specific precursor that authorizes the reversible/idempotent prepare call without pretending the final ticket already exists.

## Decision: authenticated reservation precursor + frozen V2 transition

Introduce a distinct **activation reservation precursor** whose bytes can be authenticated before provider mutation, followed by the final V2 provider-transition provenance event after the exact ticket exists.

The precursor is not the provider-generation transition and does not advance provider history, provenance-chain head, or external/shared anchor. It only authorizes one deterministic idempotent activation reservation against the current authenticated parent.

Minimum precursor commitment semantics:

```text
ytim.provider-activation-reservation.v1

logical_database_identity_digest
parent_chain_link_digest
parent_epoch
old_generation_id
new_generation_id
provider_id
new_generation
expected_position
activation_id
activation_protocol_version
transition_protocol_version
```

The precursor must be authenticated by the retained transition authorities required for the successor handoff (under the lab's current symmetric-key model, both old and new generation authority proofs or an equivalent already-frozen handoff authenticator). A plain mutable SQLite row is insufficient: startup must never call `prepare_activation()` merely because an unauthenticated local row asks it to.

`activation_id` remains deterministic from the requested successor + expected position. The precursor does **not** contain `fence`, because only the provider may assign it.

## Frozen provider-specific state machine

```text
ABSENT
  |
  | Tx R: authenticate + persist exact reservation precursor
  v
RESERVATION_AUTHENTICATED
  |
  | idempotent external prepare_activation(activation_id, expected_position)
  v
PROVIDER_PREPARED
  |
  | Tx A: freeze exact ticket + V2 event + successor chain link + LAB-080 intent
  v
PROVENANCE_PREPARED
  |
  | LAB-080 exact external anchor execute/reconcile
  v
ANCHOR_CONFIRMED
  |
  | Tx B: atomically advance provider history + provenance head + activation SQL state
  v
SQL_COMMITTED
  |
  | provider commit/reconcile UNKNOWN, still fenced
  v
PROVIDER_COMMITTED_FENCED
  |
  | persist exact-ticket COMMITTED acknowledgement
  v
ACK_COMMITTED
  |
  | release exact provider fence
  v
RELEASED
```

`PROVIDER_PREPARED`, `ANCHOR_CONFIRMED`, `PROVIDER_COMMITTED_FENCED`, and `RELEASED` are not trusted because of free-form local status flags. They are classifications derived from authenticated provider/LAB-080 observations plus the exact retained canonical bytes.

## Tx R — reservation precursor, before provider mutation

Under one `BEGIN IMMEDIATE` and before `prepare_activation()`:

1. verify retained logical DB/bootstrap/history/strategy authority and complete provenance chain;
2. require no unresolved governed provider rotation for the current parent;
3. require no unresolved shared-anchor PREPARED intent;
4. read current provider generation head and shared-anchor `reserved_position` under the same serialization boundary;
5. validate the requested successor and existing legacy transition proof structurally;
6. derive the deterministic `activation_id` from exact successor + exact expected position;
7. construct and authenticate the exact reservation precursor against the current provenance parent/epoch;
8. persist the precursor as non-current `PREPARED` evidence;
9. commit.

Tx R MUST NOT change `provider_generations`, `provider_generation_transitions`, `provider_generation_head`, provenance-chain head, or LAB-080 reserved position. It MUST NOT install an activation row that can be mistaken for a completed transition.

If Tx R rolls back, no external mutation is authorized.

## Provider prepare phase

After Tx R commits, call only:

```text
prepare_activation(
    expected_position=<precursor.expected_position>,
    activation_id=<precursor.activation_id>,
)
```

The returned exact ticket must match the precursor's provider/new-generation/expected-position/activation-id fields and pass strict type checks. The provider-assigned positive `fence` is then canonicalized into the frozen LAB-099 ticket digest.

A timeout/UNKNOWN during a real remote prepare must be reconciled by retrying/reconciling the **same activation id**. It must never allocate a different id or infer a new fence locally. PR #175's in-process provider already has the required same-id idempotency property.

## Tx A — freeze exact V2 bytes, but do not advance authority

After obtaining the exact ticket, under one `BEGIN IMMEDIATE`:

1. re-verify Tx R precursor bytes/authenticators and current parent/epoch;
2. re-read shared-anchor tail and require it still equals precursor/ticket `expected_position`;
3. require the provider generation head is still the precursor's old generation;
4. require no sibling reservation/transition exists for this parent/successor;
5. canonicalize the exact ticket and compute the frozen LAB-099 activation-ticket digest;
6. construct/authenticate the separate V2 provider-transition provenance event covering that digest;
7. deterministically construct the exact successor provenance-chain link;
8. derive the full provenance `transition_id` from the exact event/link/current parent;
9. reserve the LAB-080 provenance intent for that exact transition commitment;
10. persist the exact activation ticket row in a PREPARED/non-current form tied one-to-one to the V2 event;
11. persist exact V2 event + successor link + transition metadata as PREPARED;
12. commit.

Tx A still MUST NOT advance `provider_generation_head` or provenance-chain head. This removes the current PR #175 property where provider history becomes current before the transition has any authenticated provenance-chain commitment.

If Tx A fails after provider prepare, the provider fence remains intentionally installed. Restart may continue only from the authenticated Tx R precursor and must recover the same provider ticket by same-id prepare/reconcile; it may not mint V2 bytes from unrelated current rows.

## External LAB-080 anchor phase

Execute/reconcile the exact LAB-080 intent reserved in Tx A. Reuse the generic `ATOMIC_PROVENANCE_APPEND_RECOVERY_V1_FROZEN` rules:

- exact request id only;
- timeout/UNKNOWN -> reconcile exact request;
- ahead without exact request/receipt -> fail closed;
- changed event/ticket/link bytes -> cannot reuse the prior anchor evidence.

The provider activation fence remains PREPARED throughout this phase, so no ordinary provider increment/effect may cross the candidate activation boundary.

## Tx B — one SQLite commit makes the successor locally current

Only after re-authenticating the exact LAB-080 receipt, execute one `BEGIN IMMEDIATE` that re-verifies all Tx R/Tx A predicates and then atomically:

1. insert/confirm the successor generation descriptor;
2. insert/confirm the legacy structural `provider_generation_transitions` projection;
3. advance `provider_generation_head` from exact old generation to exact successor;
4. mark the exact V2 provider-transition event and successor chain link committed/immutable;
5. advance authenticated provenance-chain head to the exact successor link;
6. bind the exact LAB-080 confirmed receipt to the provenance transition;
7. move the exact activation row from PREPARED to the durable `SQL_COMMITTED` recovery class;
8. mark the transition COMMITTED at the provenance layer;
9. commit.

These authority changes must be one SQLite transaction. There must be no durable state where the provider head is new while the authenticated provenance head is old, or vice versa.

This is the central correction to the current LAB-090 transaction boundary: the legacy provider-generation rows remain a structural projection, but their head advance is synchronized with V2 provenance-chain commitment rather than occurring before it.

## Provider commit / acknowledgement / release

After Tx B commits, reuse LAB-090's existing external ordering:

1. `commit_activation(exact_ticket)`; on UNKNOWN, reconcile exact ticket status;
2. require `COMMITTED_FENCED`;
3. persist the exact activation acknowledgement `COMMITTED`;
4. only after that durable acknowledgement call `release_activation(exact_ticket)`;
5. require `RELEASED`.

Crash after Tx B but before provider commit is recoverable because the exact ticket bytes are already authenticated and durable, the successor is locally/provenance-current, and the provider fence remains installed.

Crash after provider commit but before local acknowledgement is recoverable by exact ticket status reconciliation. Crash after acknowledgement but before release is recoverable by exact release of the retained ticket.

## Restart classification

Startup remains verification-first and performs no provider calls until retained authority/provenance/history cardinality and ticket digests have been authenticated.

### R0 — no precursor

No rotation is authorized. Never probe/prepare a provider from inferred current rows.

### R1 — authenticated precursor, no frozen V2 event

The only allowed external recovery action is same-id `prepare_activation()`/prepare reconciliation using the exact precursor. The returned ticket must match all precursor fields; then Tx A may freeze those exact returned bytes.

### R2 — precursor + exact PREPARED V2 event/link/activation + PREPARED LAB-080 intent

Do not call a different prepare. Reconcile provider reservation against the exact retained ticket and execute/reconcile the exact LAB-080 intent.

### R3 — LAB-080 exact commitment confirmed, Tx B not committed

Re-authenticate all bytes and current parent; execute Tx B once. No reconstruction from current mutable tables.

### R4 — Tx B committed, provider status PREPARED

Commit exact activation ticket, retaining fence until durable acknowledgement.

### R5 — Tx B committed, provider `COMMITTED_FENCED`, activation SQL `SQL_COMMITTED`

Persist exact acknowledgement, then release.

### R6 — activation acknowledgement COMMITTED, provider still fenced

Release exact ticket idempotently.

### R7 — provider reservation exists but no authenticated precursor

Fail closed. This is an orphan external fence; do not manufacture local authority/provenance from it. Operational remediation requires independently authenticated evidence.

### R8 — V2 event/activation exists without authenticated precursor or legacy transition/head changes exist before Tx B

Fail closed as partial/corrupt state. Do not normalize it into a completed transition.

## Why not persist the V2 event only after provider prepare with no precursor?

A crash immediately after provider prepare would leave a provider-owned fence but no durable local evidence proving which requested successor/parent authorized it. Although the current deterministic activation id can make same-id prepare idempotent, startup would have to infer the request from mutable generation/activation state or scan provider internals. That violates the frozen rule against reconstructing authenticated transition bytes from current mutable state.

The authenticated precursor is therefore the minimum extra durable object needed to make the pre-ticket external side effect recoverable without granting it transition authority.

## Why not put `fence=0` or a wildcard into the final event before prepare?

That would authenticate a different semantic object than the exact provider ticket. Updating the event after prepare would either mutate authenticated bytes or require a second signature whose relationship to the first event is ambiguous. The precursor deliberately has a narrower type/domain: it authorizes one reservation request, while the V2 transition event authenticates the exact returned authority-bearing ticket.

## Composition with LAB-100

Tx R must validate provider/verifier authority pairing **before** the first provider mutation. An exact authenticated precursor cannot make an unrelated `FencedActivationProvider` safe: the runtime provider instance/capability used for prepare must be the trusted provider authority for the successor descriptor. Therefore the LAB-100 pairing regression remains a prerequisite to executing the prepare phase.

Likewise, startup must verify all historical activation/V2 evidence before entering any R1-R6 recovery mutation, preserving the LAB-100 verify-before-recover finding.

## RED-first additions for this ordering

When exact execution is available, add before production refactor:

1. crash before Tx R commit -> no provider prepare/fence;
2. Tx R committed, crash before prepare -> restart performs exact same-id prepare only;
3. provider prepare succeeds, crash before Tx A -> restart recovers same exact ticket/fence from authenticated precursor;
4. provider has pending reservation but precursor missing/tampered -> fail without local repair/head change;
5. Tx A rollback after provider prepare -> fence stays installed; exact precursor recovery resumes;
6. Tx A committed, ticket/event/link one-byte tamper -> fail before LAB-080/provider/head mutation;
7. LAB-080 UNKNOWN after commit -> exact request reconcile, no sibling transition;
8. crash after anchor confirmation before Tx B -> exact Tx B completion;
9. Tx B atomically advances both provider head and provenance head; injected crash cannot expose one advanced without the other;
10. crash after Tx B before provider commit -> exact-ticket recovery commits provider while still fenced;
11. provider commit UNKNOWN -> exact status reconcile; no re-prepare/new fence;
12. crash after provider commit before activation acknowledgement -> acknowledge exact ticket then release;
13. crash after acknowledgement before release -> exact release only;
14. unrelated provider paired with successor verifier -> reject before Tx R/prepare mutation;
15. historical V2 tamper plus current recoverable state -> reject before all R1-R6 provider/SQLite mutations;
16. changed `expected_position` after Tx R -> Tx A fails and original fence remains recoverable only under original precursor;
17. changed parent chain head after Tx R -> Tx A fails; precursor cannot be rebound to new parent;
18. same successor attempted from a newer parent -> new precursor/transition identities required;
19. legacy LAB-090 activation rows without precursor/V2 provenance remain `LEGACY_LAB090_UNATTESTED`; never synthesize precursor/event from them;
20. full LAB-080/081/090/092/097..100 restart/UNKNOWN regressions remain green.

## Implementation boundary

Do not implement this production state machine until exact repository RED execution is available. The important source-level result is the ordering correction and the identification of the authenticated reservation precursor as the missing bridge between "event bytes must be frozen before authority mutation" and "the exact ticket digest is unknowable before provider-assigned fence allocation".

The first executable patch should add REDs for cases 1-6 and 9-15 before introducing any new schema.

## Verdict

`AUTHENTICATED_ACTIVATION_RESERVATION_PRECURSOR_AND_ATOMIC_V2_COMMIT_V1_FROZEN`

For LAB-099, the final authenticated transition cannot safely precede provider prepare because the exact fence is not yet known, and provider prepare cannot safely precede all durable authenticated intent because crash would orphan an unprovable fence. The minimal sound composition is: authenticate a narrow reservation precursor -> idempotently obtain the exact provider ticket -> freeze V2 event/link/anchor intent -> externally anchor it -> atomically advance provider head and provenance head -> provider commit -> durable acknowledgement -> release.