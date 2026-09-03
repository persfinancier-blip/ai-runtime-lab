# LAB-091 — fresh reentrancy and supported write-surface audit

Date: 2026-09-04
Issue: #170
Candidate: draft PR #173, branch `lab/091-mutable-shared-anchor-writer`

## Scope

Fresh static audit only. No exact-source behavioral execution is claimed in this run because direct Git/source materialization remained unavailable (`git ls-remote` failed before repository access with `Could not resolve host: github.com`).

The audit targets the remaining LAB-091 item: reentrancy plus legacy/alternate supported write surfaces.

## Exact files inspected

- `experiments/mutable_shared_anchor_writer/operation_permit.py` blob `637784a5cb61a024a1df3e0e983887b6d0a838be`
- `experiments/mutable_shared_anchor_writer/operation_scoped_integration.py` blob `577979b1c3643c6232fd76cccd942429214542ca`
- `experiments/mutable_shared_anchor_writer/convergent_operation_scoped.py` blob `f93e67f8140782aec824fb4057832d568c761712`
- `experiments/mutable_shared_anchor_writer/state_machine_operation_scoped.py` blob `b359a9a191ea9632e97c227193b3bde886f904dc`
- `experiments/mutable_shared_anchor_writer/history_bound_operation_scoped.py` blob `5f3192d9266551c0805e600bf149684e0082dd89`
- `experiments/mutable_shared_anchor_writer/full_operation_guards.py` blob `6ff1f5eedac80c524163a7e78ea03cd1f0460742`
- `experiments/mutable_shared_anchor_writer/cross_table_guards.py` blob `f76809e067d9d92aa0e7c96145c282757e1fbf0b`
- `experiments/mutable_shared_anchor_writer/history_binding_guards.py` blob `adb586f953816574a4f4f7380aace7305cf088b8`
- `experiments/mutable_shared_anchor_writer/adoption_trigger_surface.py` blob `4f36f7eb12d4fd0839880292cbda9c1108a7c5ba`

## Findings

### 1. One-shot permit does not survive successful use, statement failure, rollback, or transaction exit

`lab091_consume_permit()` compares the exact `(kind, identity, old_value, new_value)` tuple and clears `_lab091_permit` before the row mutation executes. `one_shot_permit()` rejects nesting and clears any unused/error-path permit in `finally`. `_write_txn()` rejects a stale permit before `BEGIN IMMEDIATE`, refuses commit with an unused permit, and clears the field on both exception and final exit.

Static verdict: no permit reuse/reentrancy bypass found in the inspected supported paths.

### 2. Network/provider work is outside SQL permit scope

The inspected `execute`, `_reauthenticate`, and `verify_component` paths obtain authenticated provider observations before opening the individual `one_shot_permit` that authorizes consequential DML. The permit encloses only the exact INSERT/UPDATE statement that must consume it.

Static verdict: no network call was found executing while a LAB-091 one-shot mutation permit is live.

### 3. Consequential supported writes are individually permitted

The inspected supported surface issues separate exact permits for:

- intent PREPARED insertion;
- singleton meta tail update;
- provider receipt insertion;
- PREPARED -> CONFIRMED transition;
- component watermark insert/update.

The confirmation convergence override keeps the same exact permit boundary and treats an already-confirmed identical winner as convergence rather than granting a second mutation.

Static verdict: no inspected consequential DML path bypasses the one-shot permit primitive.

### 4. Same-name persisted-trigger substitution is repaired before trigger-surface acceptance

A names-only trigger inventory would be insufficient if an attacker could preseed an expected trigger name with different SQL. In this candidate, however, all expected v2/v3/v4 trigger namespaces are explicitly `DROP TRIGGER IF EXISTS` and recreated inside the constructor's writer transaction before `validate_protected_trigger_surface()` is called. Therefore a persisted same-name body is replaced, while an extra differently named trigger on a protected table is rejected by the subsequent surface check.

Static verdict: the obvious same-name preseed bypass does not survive the final constructor sequence.

### 5. Final supported constructor owns restart/adoption hardening

`SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger._install_guards()` holds `BEGIN IMMEDIATE`, reruns inherited durable verification, installs v2/v3/v4 guards, validates trigger surface/schema domains/foreign keys/extra columns/collations/index collations, validates existing mutable rows, and commits only after those checks. Its `_init()` routes through the restart-safe initializer rather than LAB-080's historical `INSERT OR IGNORE` replay.

Static verdict: legacy/restart adoption is not silently routed through the earlier weaker `_install_guards()` implementations on the final class.

## Fresh audit verdict

**PASS — static reentrancy / supported-write-surface audit only.**

No new static authority bypass was found in the exact inspected candidate files. This closes only the fresh static re-audit portion of LAB-091's remaining gate.

It does **not** establish the remaining behavioral/integration requirements:

1. exact-source execution against real LAB-080/LAB-082 dependencies;
2. two-worker/crash semantics through the final supported class;
3. timeout-after-commit / UNKNOWN reconciliation through the final supported class;
4. LAB-087 restricted-worker composition;
5. full regression/compile evidence on exact candidate bytes.

PR #173 must remain draft until those gates actually execute and pass.
