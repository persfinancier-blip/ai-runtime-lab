# LAB-095 downstream constructor/binding conflict audit

Date: 2026-09-14

## Scope

Connector-side static/security audit performed because the current run exposes no supported byte-preserving GitHub-connector -> executable-filesystem materialization bridge. No executable GREEN is claimed here.

Reviewed:

- LAB-095 PR #187 head `835a81914c5234e68ef436e30c9837331d262432`:
  - `experiments/database_binding.py`
  - `experiments/shared_anchor_intent_ledger/supported.py`
  - `experiments/provider_generation_history/supported.py`
  - inherited `SharedAnchorLedger` / `DurableProviderHistory` constructors
- LAB-090 retained PR #175 `experiments/provider_generation_history/supported.py`
- LAB-092 retained PR #177 `experiments/provider_generation_history/activation_schema_provenance.py`

## Findings

### 1. LAB-095 first-bind behavior composes with inherited constructors

`CanonicalDatabaseBinding` intercepts the first `self.path = ...` and stores a canonicalized path in `_canonical_database_path`; later public `path` and ordinary private-slot reassignment are rejected.

`SupportedSharedAnchorLedger(CanonicalDatabaseBinding, SharedAnchorLedger)` is therefore compatible with `SharedAnchorLedger.__init__`, whose existing first path assignment becomes the canonical bind.

`CoordinatorOnlyProviderHistory(CanonicalDatabaseBinding, IntegratedProviderHistory)` is likewise compatible with inherited `DurableProviderHistory.__init__`, whose existing first path assignment becomes the canonical bind.

No repeated constructor assignment was found in these inherited initialization paths.

### 2. LAB-092 object.__new__ helper surfaces remain compatible with LAB-095

LAB-092 deliberately constructs limited reservation/provenance helper surfaces through `object.__new__` and then assigns `ledger.path` / `history.path` exactly once before use. Under the LAB-095 MRO these become first canonical binds rather than rebinding attempts.

`_bind_live_provider_history_provenance()` similarly creates a fresh `_ProvenanceBoundCoordinatorOnlyProviderHistory` instance and performs exactly one path assignment copied from the already-bound live history object.

No static path-rebinding bypass or duplicate assignment was identified in these helper constructors.

### 3. Security-sensitive merge conflict remains real

LAB-090's retained `supported.py` defines:

`class CoordinatorOnlyProviderHistory(IntegratedProviderHistory)`

whereas LAB-095 requires:

`class CoordinatorOnlyProviderHistory(CanonicalDatabaseBinding, IntegratedProviderHistory)`

LAB-090 also carries the activation-fencing implementation in the same file. Therefore an eventual branch integration that chooses the LAB-090 version wholesale would silently remove physical DB lifetime binding from provider-history operations while retaining apparently valid activation behavior.

Required conflict resolution is additive, not choose-one-side:

- preserve LAB-090 activation fencing/recovery behavior;
- preserve LAB-095 `CanonicalDatabaseBinding` import and MRO on `CoordinatorOnlyProviderHistory`;
- preserve LAB-095 binding on `SupportedSharedAnchorLedger`;
- retain LAB-092 `object.__new__` helper first-bind semantics;
- execute the DB-A -> DB-B regression plus LAB-090/LAB-092 downstream gates after the merged tree can be materialized byte-exactly.

### 4. Current PR state

Fresh PR #187 API read reports `mergeable=true`, `rebaseable=true`, `mergeable_state=clean`; this does not replace downstream cross-branch conflict/security testing because LAB-090/LAB-092 remain separate retained drafts rather than changes on main.

## Decision

No production patch is justified from this static pass: the audited LAB-092 constructors are compatible with the LAB-095 first-bind contract, and the known risk is an integration/conflict-resolution requirement rather than a defect in PR #187 itself.

Keep PR #187 draft. Do not claim downstream GREEN until exact execution is possible.

## Exact next action

Priority remains LAB-086 exact gate if a new supported byte-preserving materialization path appears. Otherwise, for LAB-095, materialize the focused 8-file no-stub closure in one executable runtime, require same-run 8/8 `git hash-object` matches, run `compileall` and recovery/confirmed-finalize/locked-custody tests under `TMPDIR=/dev/shm`, then execute DB-A -> DB-B and the LAB-080/LAB-081/LAB-090/LAB-092 downstream conflict/security gate with the binding-preserving MRO above.
