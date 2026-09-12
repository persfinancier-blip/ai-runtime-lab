# LAB-099 — activation reservation precursor relation / DDL cutover contract

Date: 2026-09-12
Status: SOURCE/SCHEMA CONTRACT FROZEN; exact RED/GREEN pending
Related: LAB-090/#169 PR #175, LAB-092/#176 PR #177, LAB-097/#182, LAB-098/#183, LAB-099/#184, LAB-100/#185

## Objective

Pin the minimum persisted relation, DDL ownership and legacy classification rules for the already-frozen `ytim.provider-activation-reservation.v1` precursor without allowing ordinary startup to manufacture missing provenance or silently bless existing LAB-090 activation rows.

No production precursor code is added here. Direct exact repository execution remains unavailable in this run because `git clone --no-checkout` failed before repository code execution with `Could not resolve host: github.com`.

## Source facts

1. PR #175 ordinary LAB-090 startup currently calls `_init_activation_schema()` and uses `CREATE TABLE IF NOT EXISTS` / `CREATE TRIGGER IF NOT EXISTS` before recovery. LAB-092 exists precisely because that pattern cannot distinguish first installation from post-install deletion.
2. PR #177 replaces that behavior for the activation table/trigger with an explicit migration protocol: classify first, never auto-install missing governed DDL during ordinary startup, atomically install exact DDL plus a deterministic PREPARED migration marker, externally confirm that marker, then require exact DDL + CONFIRMED provenance on restart.
3. LAB-097 separately freezes the rule that complete authority-state absence must not be treated as proof of freshness. Startup may not reconstruct missing history before verification.
4. LAB-099 already freezes a precursor that must be durably authenticated by predecessor + successor authorities and committed before the first provider `prepare_activation()` mutation. Its identity contains the logical DB identity, exact provenance parent/epoch, old/new generation identity, successor provider identity/key id, exact shared-anchor position, deterministic `activation_id`, and protocol version.
5. The later V2 provider-transition provenance event authenticates the exact returned activation ticket, including provider-assigned `fence`. Existing LAB-090 activation rows have no such authenticated ticket commitment and are explicitly `LEGACY_LAB090_UNATTESTED` rather than auto-upgradeable.
6. The precursor necessarily exists before the provider-generation transition is committed. Therefore a precursor row cannot require an already-existing `provider_generation_transitions` parent row as an insertion precondition without breaking the frozen ordering.

## Decision

`PROVIDER_ACTIVATION_RESERVATION_RELATION_DDL_CUTOVER_V1_FROZEN`

Use a dedicated pre-transition relation, illustratively `provider_activation_reservations`, whose rows are immutable authenticated precursor evidence. The relation is installed only by an explicit authenticated schema/cutover migration path; ordinary startup never creates or repairs it.

### 1. Minimum row semantics

Exact SQL spelling remains implementation-gated until executable REDs are available, but each persisted V1 row must carry at least:

```text
activation_id                         PRIMARY KEY
logical_database_identity_digest      DIGEST32 NOT NULL
parent_chain_link_digest              DIGEST32 NOT NULL
parent_chain_epoch                    U64 NOT NULL
old_generation_id                     TEXT NOT NULL
new_generation_id                     TEXT NOT NULL
provider_id                           TEXT NOT NULL
new_provider_generation               U64 NOT NULL
new_provider_verification_key_id      TEXT NOT NULL
expected_position                     U64 NOT NULL
reservation_protocol_version          U64 NOT NULL
old_authenticator                     BYTES NOT NULL
new_authenticator                     BYTES NOT NULL
```

The stored authenticators are over the canonical `ytim.provider-activation-reservation.v1` bytes/digest, not over a SQL-row serialization and not over a mutable-row self-hash.

`fence` is intentionally absent: it does not exist until provider prepare and belongs to the subsequent authenticated V2 ticket/transition event.

### 2. Required uniqueness

The database must reject both forms of fork before provider mutation:

- more than one row for the same `activation_id`;
- more than one semantically distinct reservation under one authenticated current provenance parent.

Minimum uniqueness therefore is:

```text
PRIMARY KEY (activation_id)
UNIQUE (
  logical_database_identity_digest,
  parent_chain_link_digest,
  parent_chain_epoch
)
```

The second constraint is intentional even if `activation_id` is deterministic. It makes the one-reservation-per-authenticated-parent rule a database invariant rather than a caller convention.

The relation must not use timestamps, rowid ordering, `MAX()`, or “latest wins” to resolve siblings.

### 3. No mandatory transition foreign key at precursor insertion

Do **not** require `new_generation_id` to reference an already-persisted `provider_generation_transitions` row when Tx R inserts the precursor.

Frozen ordering is:

```text
verify current authenticated parent/head
-> persist authenticated precursor (Tx R)
-> provider prepare_activation()
-> obtain exact ticket/fence
-> build authenticated V2 transition event
-> atomically persist governed transition/activation/V2 provenance state
```

The transition does not exist at Tx R time. Requiring it first would either invert the security ordering or force provider mutation before durable authorization.

Instead, later V2 commit/verification must establish the one-to-one composition:

- precursor `activation_id/new_generation_id` -> exactly one governed V2 transition event;
- V2 transition event -> the exact precursor that authorized its provider prepare;
- V2 ticket digest -> exactly one activation row under LAB-098/LAB-099 rules.

A future deferred relationship may be added only if it preserves this ordering and exact crash semantics; it is not required for V1 correctness.

### 4. DDL owner and installation protocol

The precursor relation follows the LAB-092 provenance pattern, not PR #175 ordinary-startup auto-DDL.

Ordinary constructor/startup behavior:

1. classify the precursor-schema/cutover state **before** provider recovery or SQLite repair;
2. if the authenticated cutover says precursor V1 is required, require the exact relation definition already present;
3. missing, partial or definition-mismatched governed DDL fails closed;
4. never run `CREATE TABLE IF NOT EXISTS` to normalize a missing governed relation.

Explicit migration behavior:

1. bind the LAB-094..096 construction authority graph / logical DB identity;
2. verify existing provider-generation/shared-anchor history before mutation;
3. require a state that is actually eligible for migration (see classification below);
4. `BEGIN IMMEDIATE`;
5. install the exact precursor relation if absent;
6. re-read `sqlite_master` and require exact expected definition;
7. persist the deterministic authenticated schema/cutover PREPARED marker in the same transaction;
8. commit;
9. perform the existing external/authenticated marker confirmation path;
10. subsequent startup requires exact relation + CONFIRMED cutover provenance.

DDL and PREPARED cutover provenance therefore share one SQLite commit, matching the source-proved LAB-092 installation model. External confirmation remains a separate recoverable step.

### 5. Cutover classes

Startup/migration must distinguish at least these classes. Names are illustrative; semantics are mandatory.

#### `PRECURSOR_LEGACY_ELIGIBLE`

Provider/shared-anchor history is authenticated as pre-LAB-090 or otherwise explicitly outside precursor governance; there are no historical LAB-090 activation rows whose original ticket provenance would need to be invented.

Only this class may enter the explicit relation-install/cutover path.

#### `PRECURSOR_DDL_PREPARED`

Exact precursor relation exists and the authenticated cutover marker is PREPARED/unconfirmed. Ordinary startup does not continue into provider recovery. The explicit migration/reconciliation path may finish confirmation after re-verifying history, exact DDL and current authority.

#### `PRECURSOR_V1_COMPLETE`

Exact relation exists and authenticated cutover provenance is CONFIRMED. Ordinary startup may continue only after relation/cardinality/authenticator verification and the broader verify-before-recover sequence.

#### `LEGACY_LAB090_UNATTESTED`

LAB-090 activation state/history already exists, but there is no independently authenticated precursor/V2 ticket provenance proving the original pre-prepare authorization/ticket bytes.

This state is **not migration-eligible**. Creating the precursor table and deriving rows/authenticators/digests from current mutable activation/history rows would retroactively bless potentially rewritten evidence. Fail closed before provider recovery/mutation.

#### `PRECURSOR_PROVENANCE_LOST_OR_MISMATCHED`

Authenticated cutover says precursor V1 was installed/required, but the relation is absent, partial or definition-mismatched. Fail closed. Never recreate/repair automatically.

### 6. Relation absence is not freshness

Relation absence by itself proves nothing.

The explicit migration decision must come from already-authenticated retained history/cutover state, composed with LAB-097. In particular:

- empty/missing provider-history rows cannot be used to infer a fresh DB;
- a plain local UUID/marker inside the same replaceable SQLite file is not sufficient authority;
- existing LAB-090 rows cannot be used as the source of truth for synthesizing precursor authenticators.

This preserves the construction-bound root/database/history identity contract rather than introducing a second self-asserted bootstrap path.

### 7. Startup verification order

For a precursor-governed database, the minimum order before any provider `commit/release/abort/prepare` recovery side effect is:

1. bind retained root/database/history strategy;
2. authenticate initialization and schema/cutover provenance;
3. require exact precursor relation definition;
4. verify provider-generation structural history from retained root;
5. verify provenance-chain parent/epoch continuity;
6. verify every retained precursor canonical identity + both authenticators;
7. reject duplicate/forked parent or activation identities;
8. verify required V2 transition-provenance cardinality;
9. verify LAB-098 activation-row presence and LAB-099 exact ticket digest binding;
10. verify runtime provider/head pairing;
11. only then enter activation recovery.

This composes directly with the already-recorded LAB-100 verify-before-recover finding.

## Minimum RED-first matrix

Before production implementation, require at least these cases:

1. eligible legacy DB + ordinary startup + missing precursor relation -> migration-required, no DDL written;
2. eligible legacy DB + explicit migration -> exact relation + PREPARED cutover marker are atomic;
3. crash after atomic DDL/PREPARED commit but before external confirmation -> ordinary startup blocks; explicit migration can re-verify and confirm;
4. confirmed precursor cutover + relation deleted -> fail closed before provider recovery; relation remains absent;
5. confirmed precursor cutover + relation definition changed -> fail closed before provider recovery;
6. confirmed precursor cutover + only one required column/constraint missing -> fail closed; no auto-repair;
7. two different precursors for one `(logical DB identity,parent link,parent epoch)` -> database/restart rejection before provider mutation;
8. same `activation_id` with different precursor contents -> primary-key/immutable-evidence rejection;
9. identical same-parent/same-id retry -> idempotent observation of the retained row, not a second authorization;
10. precursor insert attempted against a non-current parent/head -> reject inside Tx R;
11. parent/head changes after precursor commit and before prepare -> old precursor loses mutation authority; no new row chosen by timestamp;
12. existing LAB-090 activation row(s) + no precursor relation/cutover -> classify `LEGACY_LAB090_UNATTESTED`, do not install-and-bless;
13. existing LAB-090 rows + newly created empty precursor relation but no authenticated cutover -> still untrusted/fail closed;
14. deletion of all provider-history rows plus missing precursor relation -> LAB-097 fail-closed, not “fresh migration”;
15. precursor relation exists but cutover marker absent on a DB known to contain governed V2 history -> fail closed;
16. PREPARED precursor-schema marker + mismatched/missing DDL -> fail closed, no confirmation;
17. post-cutover valid precursor has no corresponding V2 transition after parent/head has advanced -> orphan/fork failure, no replay;
18. V2 transition references an activation id with no precursor -> fail before activation recovery;
19. precursor copied to another logical DB identity -> authenticator/identity rejection;
20. current recoverable activation + separately broken precursor/schema/cutover evidence -> failure occurs before current provider or SQLite recovery mutation.

## Implementation seam when exact execution returns

Implement tests first, then the smallest coherent schema layer:

1. add exact precursor DDL constant + `sqlite_master` definition verifier;
2. add read-only classifier that never creates DDL;
3. add explicit migration method using the LAB-092 DDL+PREPARED/CONFIRMED pattern;
4. add Tx R insertion with both uniqueness constraints and exact parent/head recheck;
5. add immutable row/authenticator verification before any provider mutation/recovery;
6. compose with V2 transition-provenance and LAB-098 anti-joins;
7. only after REDs execute, wire rotation/restart production ordering.

Do not implement this as ordinary-startup `CREATE TABLE IF NOT EXISTS`, an unauthenticated local migration flag, an FK that forces transition persistence before precursor authorization, or a backfill from existing LAB-090 activation rows.

## Verdict

`PROVIDER_ACTIVATION_RESERVATION_RELATION_DDL_CUTOVER_V1_FROZEN`

The precursor is a distinct pre-transition authenticated authority object. Its relation is explicitly migrated and provenance-bound, unique by activation id and authenticated parent, never auto-created on governed startup, and never retroactively synthesized from legacy LAB-090 rows.
