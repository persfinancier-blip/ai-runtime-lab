# Atomic provenance append / recovery protocol V1

Date: 2026-09-04
Status: design contract frozen; exact RED/GREEN pending
Related: LAB-080/081, LAB-086/#163, LAB-090/#169, LAB-092/#176, LAB-097/#182, LAB-099/#184, LAB-100/#185

## Objective

Freeze one crash-safe, timeout-after-commit/UNKNOWN-safe protocol that couples:

1. one domain-specific authenticated provenance event;
2. its exact successor `ytim.provenance-chain-link.v1`;
3. the durable authenticated chain-head advancement; and
4. the existing LAB-080 shared/external monotonic-anchor intent.

This is deliberately a design contract only. In this run a fresh `git clone --no-checkout` failed before repository access with `Could not resolve host: github.com`; no exact repository behavioral PASS is claimed and no production source is changed.

## Existing mechanism to reuse

LAB-080 already supplies the correct outer idempotency skeleton:

- `reserve(Intent)` runs under `BEGIN IMMEDIATE`;
- it permits only one unresolved PREPARED shared-anchor intent;
- it allocates exactly `position = predecessor + 1`;
- it derives deterministic `request_id` from position + immutable intent identity/content;
- the PREPARED row and reserved-position advance commit atomically;
- `execute()` uses the same request id for the external provider;
- after timeout/UNKNOWN it can call `reconcile_increment(request_id=...)` and distinguish the exact committed provider result;
- SQL confirmation occurs only after re-authenticating that exact position/request pair.

V1 MUST extend this path. It MUST NOT introduce a second independently advancing external-anchor counter or a second unrelated idempotency namespace for provenance.

## Frozen transition state machine

Every provenance-changing operation is represented by one durable transition record keyed by a deterministic `transition_id` and bound to one reserved LAB-080 anchor intent.

States:

```text
ABSENT
  |
  | SQL transaction A
  v
PREPARED
  |
  | external anchor exact request / reconcile
  v
ANCHORED
  |
  | SQL transaction B
  v
COMMITTED
```

`ANCHORED` may be represented by authenticated LAB-080 receipt evidence rather than a separately writable free-form state flag. A mutable row saying only `ANCHORED` is not authority.

A transition is complete only when all four objects agree:

```text
DomainEvent
ChainLink(parent=current_head, event=DomainEvent)
ChainHead -> ChainLink
SharedAnchorIntent(status=CONFIRMED, payload_digest=TransitionCommitment)
```

## Deterministic transition identity

Define domain:

```text
ytim.provenance-transition-id.v1
```

Fields:

```text
1 logical_database_identity_digest DIGEST32
2 parent_chain_link_digest         DIGEST32
3 parent_epoch                     U64
4 event_kind                       U64
5 event_payload_digest             DIGEST32
6 successor_chain_link_digest      DIGEST32
7 resulting_provider_head_digest   DIGEST32
8 resulting_authority_digest       DIGEST32
9 resulting_schema_state_digest    DIGEST32
10 protocol_version                U64
```

`transition_id = SHA-256(canonical_transition_id_bytes)`.

The LAB-080 intent id is deterministic:

```text
intent_id = "provenance:" + hex(transition_id)
component_id = "provenance-chain"
intent_type = "migration"  # existing LAB-080 vocabulary until a dedicated enum is introduced under executable RED/GREEN
```

The intent payload MUST carry a typed canonical transition commitment, not arbitrary caller JSON. The current LAB-080 JSON `payload_digest` is therefore treated as the outer ledger binding; the security-relevant payload contains exact canonical V1 digests.

Retrying the exact same logical transition reproduces the exact same `transition_id`, intent identity, event digest, successor-link digest and anchor request id. Any changed field creates a different identity and cannot consume the prior PREPARED/CONFIRMED evidence.

## Transaction A — durable PREPARE

Under one `BEGIN IMMEDIATE`, before any external provider mutation:

1. verify construction-bound retained authority graph;
2. verify the complete authenticated provenance chain to current head;
3. require the requested parent digest and epoch equal that current head;
4. verify the domain-specific event payload and allowed state delta;
5. deterministically construct the exact successor chain link in memory;
6. compute `transition_id`;
7. reserve the LAB-080 shared-anchor intent for that exact transition commitment;
8. insert the domain event row as `PREPARED` / non-current evidence;
9. insert the exact successor link as `PREPARED` / non-current evidence;
10. insert/update transition metadata tying event, link and LAB-080 intent together;
11. commit.

Transaction A MUST NOT advance the authenticated chain-head pointer. It MUST NOT release/activate a provider authority. It MUST NOT perform repair based on newly written PREPARED rows.

If Transaction A rolls back, external state is untouched and the operation is ABSENT.

## External anchor phase

After Transaction A commits, execute the already-reserved LAB-080 intent using its deterministic request id.

Possible observations:

- provider returns exact committed observation: proceed;
- timeout/transport failure: classify as UNKNOWN, do not create a second intent;
- retry: reconcile the same request id;
- provider says no such request and authenticated position is still predecessor: transition remains PREPARED and may retry the exact request;
- provider is ahead without the exact request/receipt: fail closed as unexplained advance;
- authenticated receipt binds a different position/request: fail closed.

The external anchor confirms only the exact transition commitment. It does not authorize substituting a different event/link after PREPARE.

## Transaction B — durable COMMIT

Only after re-authenticating the exact LAB-080 receipt, open one `BEGIN IMMEDIATE` and re-read every precondition.

Require:

1. transition row is the exact PREPARED transition;
2. event bytes/digest are unchanged;
3. successor link bytes/digest are unchanged;
4. current chain head is still the transition's exact parent;
5. current epoch is still parent epoch;
6. LAB-080 intent is the exact reserved intent and is externally re-authenticated;
7. no sibling successor exists for the same parent/next epoch;
8. event-specific preconditions still hold;
9. construction-bound authority graph is unchanged except for the exact dimension this event is authorized to transition.

Then atomically:

1. mark event committed/immutable;
2. mark successor link committed/immutable;
3. advance authenticated chain head to `(epoch+1, successor_digest)`;
4. bind the LAB-080 confirmed receipt to the transition;
5. mark transition COMMITTED;
6. commit.

If any predicate differs, roll back with no chain-head advancement.

## Why chain-head advancement is not sufficient by itself

A SQLite `current_chain_head` row is only a cache/index. It is not independent authenticity.

Startup authenticates a current head only when:

- genesis/initialization provenance is valid;
- the complete parent-linked chain is valid;
- the terminal link digest equals the head pointer;
- the corresponding LAB-080 shared-anchor intent is CONFIRMED and re-authenticates at its exact position/request;
- component/shared-anchor continuity proves no authenticated later position was discarded.

Restoring an internally self-consistent older SQLite chain therefore cannot become valid merely by restoring an older head row.

## Restart classification

Startup performs verification before any repair/provider release/worker delegation.

For each transition:

### Case 1 — no event, no link, no reserved intent

Operation never durably started. No repair.

### Case 2 — exact PREPARED event + link + PREPARED LAB-080 intent; provider has no request and remains at predecessor

Safe retry of the exact external request is allowed. No event/link rewriting.

### Case 3 — exact PREPARED event + link + PREPARED local intent; provider reconciliation proves the exact request committed

UNKNOWN-after-commit. Re-authenticate receipt, then Transaction B may deterministically commit the already frozen event/link. It may not recalculate them from mutable current rows.

### Case 4 — exact event/link and LAB-080 intent already CONFIRMED, but local transition/head still PREPARED parent

Crash between external confirmation and Transaction B. Re-authenticate exact receipt; if every Transaction-B predicate still matches, complete exactly once.

### Case 5 — transition COMMITTED + head advanced + LAB-080 CONFIRMED

Idempotent success. Retry returns existing result and creates no new epoch.

### Case 6 — successor link committed/head advanced but exact event payload is missing/mismatched

Corruption. No generic repair.

### Case 7 — event committed but successor link missing/mismatched

Corruption unless independently authenticated PREPARED bytes retained by the transition record prove the exact previously frozen successor. V1 preference is fail closed; do not reconstruct from current state.

### Case 8 — two different successors for same parent/next epoch

Fork/corruption. Never choose by rowid, timestamp or digest ordering.

### Case 9 — external anchor is ahead of local confirmed transition history

Fail closed unless every intervening anchor position is explained by exact CONFIRMED LAB-080 ledger entries. Missing provenance event/link cannot be invented to fill a gap.

### Case 10 — local chain contains a later COMMITTED transition than authenticated external/shared anchor

Fail closed. Local SQLite cannot outrank the external rollback/equivocation anchor.

## Event-specific recovery constraints

The generic protocol controls ordering and idempotency; each event type retains its own stronger rules.

### Provider-generation / LAB-099 activation transition

- provider activation ticket digest is part of the event payload before PREPARE;
- unresolved LAB-090 provider fence remains installed until the exact transition is durably COMMITTED where required by the LAB-090 lifecycle;
- restart must not release/reconstruct the fence before provenance-chain verification;
- a different ticket/fence is a different transition and cannot reuse the original anchor intent.

### LAB-092 migration

- exact repository-owned DDL digests are fixed before PREPARE;
- migration DDL and provenance records must be ordered so startup can classify partial installation without inventing success;
- if DDL side effects cannot be rolled back under the exact SQLite operation, the migration-specific PREPARED record must exist before those effects and recovery may only complete the exact certified DDL state;
- authority/provider-head changes inside migration are forbidden.

### LAB-100 authority transition

- old/new authority descriptors and any unresolved-state handoff digest are fixed before PREPARE;
- the old authority remains authoritative until Transaction B commits the successor chain head;
- restart cannot instantiate the new authority as current merely because its durable state exists.

### LAB-097 initialization

Initialization is a special genesis transaction: no prior shared-anchor provenance transition exists. It must atomically establish logical DB identity/genesis/initialization event/epoch-0 link and the first authenticated external/shared anchor commitment under the same one-time initialization authority. After that, absence of provenance is corruption, never permission to re-bootstrap.

## Repair forbidden conditions

No automatic repair is authorized when any of the following is true:

- event bytes are missing or digest-mismatched;
- successor-link bytes are missing or digest-mismatched;
- parent digest/epoch no longer match;
- two children exist for one parent;
- LAB-080 request identity differs;
- authenticated external provider is ahead without the exact request;
- receipt binding differs;
- construction-bound DB/bootstrap/history/activation authority identity differs;
- schema/provider/authority post-state changed outside the event's authorized dimension;
- canonical parser/type validation fails;
- any recovery would need to derive authenticated bytes from current mutable rows rather than previously committed/prepared canonical bytes.

## Exact idempotency rule

The unit of idempotency is **the full transition commitment**, not an API call name and not an event kind.

Same `transition_id` + exact bytes:

- PREPARED -> resume/reconcile;
- COMMITTED -> return success;
- different content under same semantic caller request -> `IntentConflict` / fail closed.

A new transition after the parent head changes MUST have a different transition id even if its event payload is otherwise identical, because `parent_chain_link_digest` is part of the identity.

## RED-first atomicity/recovery matrix

Freeze before production implementation:

1. normal transition: PREPARE -> exact anchor -> COMMIT;
2. crash before Transaction A commit -> no rows/no anchor change;
3. crash after Transaction A, before provider call -> exact PREPARED retry;
4. timeout before provider commit -> PREPARED retry, no new intent;
5. timeout after provider commit -> reconcile exact request -> COMMIT once;
6. crash after provider commit before local receipt persistence -> recover via reconcile;
7. crash after LAB-080 confirmation before chain-head commit -> exact Transaction-B completion;
8. crash after chain-head commit before caller response -> retry returns same COMMITTED transition;
9. retry same transition cannot create epoch+2;
10. retry changed event bytes under reused caller id -> fail conflict;
11. same event on newer parent -> new transition id;
12. mutated PREPARED event before recovery -> fail unchanged;
13. mutated PREPARED successor link -> fail unchanged;
14. changed current head before Transaction B -> fail unchanged;
15. sibling child inserted before Transaction B -> fail fork;
16. successor link without event -> fail;
17. event without successor -> fail/no generic reconstruction;
18. local head advanced without exact CONFIRMED LAB-080 evidence -> fail;
19. external anchor ahead without exact request -> fail unexplained advance;
20. old locally self-consistent chain restored under newer external anchor -> fail rollback;
21. local chain ahead of external authenticated anchor -> fail;
22. duplicate byte-identical observation is idempotent, not another append;
23. provider-generation event cannot change schema/authority;
24. migration cannot change provider head/authority;
25. authority transition cannot change provider head/schema;
26. LAB-099 ticket one-byte change produces different transition identity and fails old receipt reuse;
27. LAB-092 DDL digest one-byte change fails old receipt reuse;
28. LAB-100 new-authority descriptor one-byte change fails old receipt reuse;
29. restart verifies chain/anchor before provider release/reconciliation writes;
30. LAB-093 restricted worker cannot PREPARE/COMMIT provenance or access raw anchor authority;
31. LAB-087 broker crash/restart preserves exactly-once recovery classification;
32. two concurrent append attempts: one parent wins; loser sees changed head and cannot become sibling;
33. U64 epoch exhaustion fails before PREPARE/provider mutation;
34. malformed canonical integer/text/bool/REAL confusion fails before PREPARE;
35. LAB-080 existing ordinary migration/root/archive intents remain compatible and cannot impersonate a provenance transition because the inner canonical transition commitment/domain differs;
36. full LAB-080/081/086 rollback/UNKNOWN regressions remain green after implementation.

## Implementation boundaries

- one authoritative provenance append coordinator inside the LAB-087 broker;
- reuse LAB-080 request/reconcile semantics rather than wrapping provider calls in a new home-grown retry layer;
- one canonical transition builder computes event/link/transition bytes before Transaction A;
- no generic reflection/RPC for workers;
- no SQLite rowid/time as authority or ordering;
- no same-process security claim against code with direct writable DB/provider handles;
- no production refactor until exact RED tests can run on repository source.

## Open implementation detail intentionally deferred

The current LAB-080 `ALLOWED_INTENT_TYPES` does not yet have a dedicated provenance-transition type. V1 deliberately reuses the existing outer `migration` slot only as a design placeholder while domain separation occurs inside the exact payload commitment. When executable RED/GREEN becomes available, test whether adding a dedicated `provenance_transition` enum is compatible with retained LAB-080/081/086 history. Do not change that enum speculatively in this blocked run.

## Verdict

`ATOMIC_PROVENANCE_APPEND_RECOVERY_V1_FROZEN`

The provenance chain now has a single exactly-once append/recovery model tied to the existing deterministic LAB-080 shared-anchor protocol. PREPARED canonical bytes are frozen before external mutation; timeout-after-commit uses exact request reconciliation; chain-head advancement occurs only after re-authenticated external commitment; restart may complete only the exact previously prepared transition; forks, unexplained external advances, missing provenance bytes and authority rebinding remain fail closed.