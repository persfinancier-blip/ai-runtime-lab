# LAB-097..099 — authenticated initialization + activation provenance contract

Date: 2026-09-04
Status: DESIGN/REGRESSION CONTRACT FROZEN; exact RED/GREEN pending
Issues: #182 LAB-097, #183 LAB-098, #184 LAB-099

## Scope

Reconcile three deletion/rebinding findings into one provenance model instead of repairing each mutable table independently:

- LAB-097: complete or partial provider-history deletion can be mistaken for first initialization and silently re-bootstrap authority.
- LAB-098: deletion of a LAB-090 activation row can erase required handoff/recovery evidence while authenticated generation history remains.
- LAB-099: a historical activation row can remain present but have authority-relevant ticket fields coherently rebound because transition evidence does not authenticate the original ticket.

This contract composes with the already frozen LAB-092 migration-provenance design and LAB-094..096 construction-bound retained-authority graph. It does not supersede LAB-086.

## Source facts rechecked

On LAB-090 draft head `d9a381dd4607a928cd1315adef6431e239995bc1`:

1. `provider_generation_activations` stores `activation_id`, `new_generation_id`, `provider_id`, `generation`, `expected_position`, `fence`, `status`.
2. `_recover_pending_activation()` asks for the row of the current durable generation and returns immediately if it is absent.
3. `_verify_activation_records()` validates rows that exist, but does not derive a required row set from authenticated provider-generation transitions.
4. Historical activation validation is structural. `activation_id` is deterministic from generation descriptor + expected position, so an attacker who rewrites `expected_position` can recompute a matching id; `fence` is only checked as a positive integer.
5. `rotate_provider()` inserts the activation row and advances provider history in one SQLite transaction, but the authenticated provider-generation transition evidence does not currently commit to the exact activation ticket fields.

Therefore activation-table contents are currently mutable evidence, not independently authenticated provenance.

## Core design decision

Freeze one construction-authenticated provenance chain with three layers:

### 1. Database initialization certificate

A logical database/history instance has a construction-time `InitializationCertificate` whose authenticated identity is outside the mutable provider-history rowset it protects.

Minimum committed fields:

- provenance version/domain;
- canonical logical database identity from the LAB-094..096 retained authority graph;
- bootstrap generation id and canonical descriptor digest;
- provider-history schema/protocol version;
- initialization epoch/nonce generated once at explicit initialization;
- initial authenticated chain root.

The certificate is verified before any provider-history bootstrap/head/history write on restart. Absence is permitted only on an explicitly classified pristine database with no evidence of prior initialization. Ordinary restart must never infer "first initialization" solely from empty provider-history tables or `COUNT(*) == 0`.

Do not store a self-authenticating marker only in the same deletable SQLite row family. The certificate must be authenticated by the retained construction authority already required by LAB-092/LAB-094..096, or by an equivalent external/parent authenticated record whose loss is independently detectable.

### 2. Authenticated provider-generation transition record

Every non-bootstrap provider-generation transition contributes an authenticated canonical transition record to the provider-history chain.

In addition to old/new generation identity and existing transition proof fields, the LAB-090-governed transition MUST commit to an `activation_ticket_digest` over a canonical, domain-separated serialization of all authority-relevant activation fields:

`provider_id, generation, new_generation_id, expected_position, activation_id, fence, activation_protocol_version`.

The digest belongs to authenticated transition/handoff evidence, not only to `provider_generation_activations`.

This makes the authenticated generation transition the provenance source for both LAB-098 presence and LAB-099 ticket binding.

### 3. Activation row as recoverable operational state, not provenance root

`provider_generation_activations` remains useful for crash recovery and status (`SQL_COMMITTED`/`COMMITTED`), but it is no longer allowed to prove its own necessity or contents.

At verification/restart:

- derive the exact set of required LAB-090 activation records from authenticated generation transitions;
- require exactly one activation row per governed non-bootstrap transition;
- canonicalize its ticket and require its digest to equal the authenticated transition's `activation_ticket_digest`;
- reject extra activation rows that do not correspond to an authenticated transition;
- only after this provenance pass may current pending activation recovery query provider state or mutate SQLite/provider state.

No missing activation row may be reconstructed from current runtime/provider state.

## Startup ordering invariant

Supported construction/restart must be strictly read/verify before repair/mutation:

1. bind the frozen LAB-094..096 `RetainedAuthorityGraph` (canonical DB identity, bootstrap root, history strategy);
2. classify DB as explicit pristine-initialization candidate or existing initialized DB without mutating provider-history/activation state;
3. authenticate `InitializationCertificate` / migration provenance (LAB-092 composition);
4. verify provider-generation chain and transition authenticity from the retained bootstrap root;
5. derive required activation-ticket digests from authenticated transitions;
6. verify activation schema provenance and exact required activation rows/digests;
7. verify runtime provider/head compatibility;
8. only then run pending activation reconciliation/release or other supported recovery writes.

Any failure in steps 1-7 is fail-closed and leaves SQLite/provider state unchanged.

## First-initialization rule

There are exactly two supported states:

- **PRISTINE/UNINITIALIZED:** explicit classifier proves the database has no retained product identity/provenance, no provider-history generations/head/transitions/receipts, no LAB-090 activation rows, and no LAB-092 migration completion evidence. Only an explicit initialization operation may create the initialization certificate + bootstrap state atomically according to the construction contract.
- **INITIALIZED:** an authenticated initialization certificate exists and must validate. Missing provider-history rows, head, transitions, receipts, activation schema/rows, or required authenticated evidence are corruption/tampering, never a signal to reinitialize.

Ambiguous state is corruption, not pristine.

## Why this closes the three issues

### LAB-097

Complete provider-history deletion no longer converts an initialized DB into an empty-head bootstrap path. The retained initialization certificate/logical DB identity says the DB was already initialized, so missing generations/head/transitions fail before `_init()` can reinstall g1.

### LAB-098

Required activation rows are derived from authenticated transitions. Deleting a current or historical row creates a cardinality/provenance mismatch and fails before `_recover_pending_activation()` can return early or before the trigger absence can be treated as safe.

### LAB-099

A present activation row must match the transition-authenticated canonical ticket digest. Independent mutation of `expected_position`, `activation_id`, `fence`, provider/generation identity, or coherent multi-field rebinding changes the digest and fails.

## Interaction with LAB-092

LAB-092 activation-schema migration provenance and this contract must share one construction-time provenance domain rather than creating independent mutable "completed" markers.

The initialization certificate commits to the provider-history protocol/schema generation. A schema migration is an authenticated transition of that construction provenance state. A database that claims migration completion but lacks/mismatches the required activation schema fails closed; a database that was already initialized cannot become "legacy pristine" by deleting the migration marker/table.

## Interaction with LAB-094..096

The `InitializationCertificate` is verified against the frozen construction-bound `RetainedAuthorityGraph`:

- database identity must be the canonical retained DB identity;
- bootstrap root must be the retained bootstrap root;
- verification must use the retained audited provider-history strategy;
- caller mutation/rebinding of `path`, `bootstrap`, or `provider_history` cannot select a different provenance universe.

This is one lifetime authority graph; do not implement three separate underscore/property patches plus an unrelated initialization marker.

## Canonicalization requirements

Before production code, freeze one byte-level canonical serialization for authenticated transition and activation-ticket digests:

- explicit domain/version tag;
- length-delimited UTF-8 strings or another unambiguous canonical encoding;
- integers encoded canonically (no bool acceptance, no alternate textual/SQLite numeric representations);
- all fields type-checked before hashing/signature verification;
- no JSON implementation-dependent ordering/number coercion;
- digest/signature verification performed before trusting any field for authority decisions.

This must compose with LAB-092's serialization-bound redesign rather than introducing a second incompatible encoding.

## Combined RED-first regression matrix

Freeze these cases before implementation. All post-fix tamper cases must fail before provider/SQLite mutation and preserve tampered bytes/state for audit.

### Initialization / LAB-097

1. true pristine DB -> explicit initialize succeeds once.
2. true pristine DB -> ordinary restart does not silently initialize if explicit init is required by the supported surface.
3. valid g1 -> g2 -> delete all provider history/head/transition/receipt rows, retain DB identity/certificate -> fail closed, no g1 rewrite.
4. delete only head -> fail closed.
5. delete current generation row -> fail closed.
6. delete historical generation row -> fail closed.
7. delete transition row -> fail closed.
8. delete historical receipt required by current protocol -> existing historical-evidence rule still fails closed.
9. delete initialization certificate while other initialized evidence remains -> fail closed, not pristine.
10. copy provider-history rows into different logical DB identity -> fail closed under LAB-095/LAB-094..096 binding.
11. valid restart with untouched state -> PASS.

### Activation presence / LAB-098

12. valid g1 -> g2; delete current g2 activation row -> fail closed.
13. same deletion while provider remains PREPARED -> fail closed before provider reconciliation/mutation.
14. same deletion while provider is COMMITTED_FENCED -> fail closed before release.
15. valid g1 -> g2 -> g3; delete historical g2 COMMITTED activation row -> fail closed.
16. duplicate activation rows for one authenticated transition (where schema manipulation makes this representable) -> fail closed.
17. extra activation row with no authenticated transition -> fail closed.
18. bootstrap generation has no activation ticket when protocol says bootstrap is ungated -> PASS; do not demand fabricated bootstrap activation provenance.

### Activation ticket binding / LAB-099

19. mutate historical `expected_position` only -> fail closed.
20. mutate `activation_id` only -> fail closed.
21. mutate `fence` only -> fail closed.
22. mutate provider id/generation while keeping structurally valid descriptor relation -> fail closed.
23. coherent rewrite of expected_position + recomputed deterministic activation_id + positive fence -> fail closed.
24. preserve activation row but tamper authenticated transition ticket digest -> fail closed under transition authentication.
25. replay g2 activation row/ticket digest onto g3 transition -> fail closed through new-generation/domain binding.
26. numeric-type confusion (`1` vs `1.0`, bool, text numeric if SQLite coercion permits storage) -> fail closed before digest comparison.
27. valid historical committed activation after later generation becomes current -> PASS.

### Cross-contract composition

28. delete LAB-092 migration completion provenance but leave installed activation DDL -> fail closed according to migration contract, not reclassify pristine.
29. delete activation table after authenticated migration completion -> fail closed before reinstall.
30. rebind retained bootstrap root after construction -> LAB-094 failure before provenance verification proceeds.
31. rebind logical database path/identity -> LAB-095 failure.
32. replace provider-history strategy -> LAB-096 failure.
33. LAB-090 timeout-after-commit/UNKNOWN with intact authenticated ticket -> existing recovery semantics remain PASS.
34. restart with current SQL_COMMITTED activation and exact authenticated ticket -> reconcile using provider state only after provenance verification.
35. restart with COMMITTED_FENCED exact ticket -> release only after durable/authenticated ticket match.
36. LAB-080/LAB-081 normal reserve/execute/verify flows remain unchanged after successful startup verification.
37. LAB-087 restricted worker cannot access/rewrite initialization certificate, writable DB, activation rowset or raw provider through LAB-093 façade.
38. LAB-093 value-only ENTRY/VERIFY_DURABLE surfaces do not expose provenance-authority objects.

## Implementation boundary when execution returns

Do not write production code until exact repository REDs can be run. When executable source becomes available:

1. add the combined regressions at supported constructor/restart abstraction level;
2. observe LAB-097/098/099 REDs on the retained exact branch stack;
3. implement one coherent provenance mechanism, not three aliases/markers;
4. run LAB-090/LAB-092 plus LAB-094..096 composition regressions;
5. run LAB-080/081, LAB-087/LAB-093 compatibility, compileall and security audit;
6. keep any PR draft until all exact gates are observed.

## Current verdict

`LAB097_LAB099_AUTHENTICATED_PROVENANCE_CONTRACT_FROZEN`

This is a source-grounded design/regression result only. Direct git transport was re-probed in this run and failed before repository access with `Could not resolve host: github.com`; no exact branch behavioral PASS is claimed.
