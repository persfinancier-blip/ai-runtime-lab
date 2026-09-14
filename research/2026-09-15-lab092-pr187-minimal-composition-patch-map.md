# LAB-092 -> PR #187 minimal composition patch map

Date: 2026-09-15

## Scope

This note records the smallest safe LAB-092 composition slice after re-reading:

- PR #187 `experiments/provider_generation_history/supported.py` at blob `c478f7e8676b09a2b891f1e1eafd36e0b77224ca`;
- PR #177 `experiments/provider_generation_history/activation_schema_provenance.py` at blob `396b67a46686f6df23584b1b366824c1b7ac1886`;
- PR #175 LAB-090 activation DDL/constants in `supported.py`.

No behavioral GREEN is claimed here. Direct Git transport was probed first in this run and failed before repository execution with `Could not resolve host: github.com`, exit 128.

## Finding

A safe LAB-092 composition cannot yet be copied as a local one-file production slice onto PR #187 because PR #177's provenance classifier is coupled to LAB-090 activation relation constants and exact DDL (`_ACTIVATION_TABLE_NAME`, `_ACTIVATION_TABLE_SQL`, `_ACTIVATION_TRIGGER_NAME`, `_ACTIVATION_TRIGGER_SQL`, `_normalized_sql`) that do not exist on the PR #187 authority base.

Copying the full PR #177 module now would therefore either:

1. duplicate LAB-090 schema authority into LAB-092, or
2. require wholesale LAB-090 `supported.py` conflict resolution, which would reintroduce the public/live `provider_history` authority paths already removed by LAB-095/LAB-096.

Per the durable handoff, the safe action is a concrete patch map rather than a large security-critical copy.

## Exact composition map

### 1. Keep PR #187 as the structural authority base

Retain unchanged:

- `CanonicalDatabaseBinding` on supported ledger/history objects;
- private construction-bound `_provider_history`;
- public `ProviderHistoryInspectionView` only;
- internal `_history()` authority path;
- ledger-owned `_store_receipt()` transaction;
- `_guard_receipt_persistence_locked(q)` before history verification/insert in that same `BEGIN IMMEDIATE` transaction.

LAB-092 must not add `_bind_live_provider_history_provenance()` and must not replace `provider_history` or `_provider_history` after construction.

### 2. Move LAB-090 activation schema definitions into a shared non-authority helper before composing LAB-092

The following exact schema-definition-only items currently live in PR #175 `supported.py` and are required by LAB-092 classification:

- `_ACTIVATION_TABLE_NAME`;
- `_ACTIVATION_TABLE_SQL`;
- `_ACTIVATION_TRIGGER_NAME`;
- `_ACTIVATION_TRIGGER_SQL`;
- `_normalized_sql`.

They should have one canonical production owner imported by both the LAB-090 coordinator implementation and LAB-092 provenance classifier. This extraction must not move mutation/rotation authority, only immutable schema constants plus SQL normalization.

Until that extraction is composed, do not duplicate those definitions in a new LAB-092-on-#187 module.

### 3. LAB-092 confirmation/history checks must use private history

PR #177 call sites that currently use public/live history must become:

- `_verify_confirmation_authority`: `ledger._history()._verify_durable_locked(q)`;
- `_install_and_reserve_prepared`: `ledger._history()._verify_durable_locked(q)`;
- any current/durable history reads used for security decisions: `ledger._history()` rather than `ledger.provider_history`.

The public inspection view remains suitable only for non-authority inspection APIs.

### 4. Receipt provenance enforcement belongs in `_guard_receipt_persistence_locked(q)`

`ProvenancedHistoricalSharedAnchorLedger` should override:

```python
def _guard_receipt_persistence_locked(self, q):
    super()._guard_receipt_persistence_locked(q)
    if _classify_locked(q) != "COMPLETE":
        raise HistoricalVerificationError("activation schema provenance is incomplete")
```

The classifier used by this hook must read exact activation DDL and the exact migration marker through the supplied `q`; it must not open a second connection. This preserves the PR #187 same-transaction check -> verify -> compare/insert -> commit sequence and closes the previously identified TOCTOU window.

A path-opening `_classify(path)` may remain for startup/migration entry decisions, but receipt persistence must use a locked-connection classifier variant.

### 5. `_reservation_surface()` may remain one-time construction only

The migration-only construction shape remains compatible with LAB-095 if it performs exactly one canonical path bind and exactly one exact private-history installation on a fresh `object.__new__` ledger.

Required shape on PR #187 authority base:

```python
ledger = object.__new__(ProvenancedHistoricalSharedAnchorLedger-or-compatible-supported-type)
ledger.path = path
ledger.attested = attested
history = object.__new__(CoordinatorOnlyProviderHistory)
history.path = path
history.bootstrap = bootstrap
ledger.provider_history = history  # first and only installation
```

No later assignment to `ledger.provider_history` or `ledger._provider_history` is permitted.

### 6. LAB-090 behavior must be ported semantically, not by whole-file selection

When LAB-090 is composed after the LAB-092 provenance layer, preserve its external activation ordering:

provider PREPARED -> SQL generation/activation commit -> provider COMMITTED_FENCED -> durable exact-ticket acknowledgement -> exact-ticket release.

At every LAB-090 internal history call site use PR #187 `_history()` for locked/current authority operations. Do not restore the PR #175 public mutable history topology.

## Minimal next code slice

The next safe production change is **not** a copied LAB-092 module. It is the schema-definition extraction described in step 2, because that removes the non-local dependency while keeping authority boundaries unchanged. After that extraction, a small LAB-092 provenance classifier/guard can be added on PR #187 with file-scoped conflict checking and exact syntax/hash verification.

## Validation status

Observed this run:

- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` -> DNS failure, exit 128, before repository execution;
- PR #187 source re-read from GitHub connector;
- PR #177 provenance source re-read from GitHub connector;
- PR #175 activation constants/DDL source re-read from GitHub connector.

Not executed and not claimed GREEN:

- exact repository compile/test closure;
- LAB-092 behavioral migration tests on PR #187;
- downstream LAB-090/LAB-081 gates.
