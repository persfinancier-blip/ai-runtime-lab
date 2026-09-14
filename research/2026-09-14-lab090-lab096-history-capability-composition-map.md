# LAB-090 + LAB-095/LAB-096 provider-history capability composition map

Date: 2026-09-14

## Scope

This audit classifies every provider-history call site introduced or retained by LAB-090 PR #175 against the LAB-095/LAB-096 contract on draft PR #187.

The composed contract is stricter than either branch in isolation:

1. the ledger and provider-history strategy are construction-bound to one canonical database path;
2. the live `CoordinatorOnlyProviderHistory` strategy is private and cannot be replaced after construction;
3. public `provider_history` is a least-capability inspection view only;
4. internal coordinator operations that need locked helpers or mutation authority must use `_history()`;
5. LAB-090 activation ordering/fencing must remain unchanged: provider PREPARED fence -> SQL generation/activation commit -> provider COMMITTED_FENCED -> durable SQL acknowledgement -> exact-ticket release.

## Current-run transport observation

The mandatory LAB-086 executable probe was attempted first:

```text
git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git
fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com
exit 128
```

No LAB-086 PASS is claimed. The failure happened before repository code execution.

## Exact branch sources audited

- LAB-090 PR #175 head: `d9a381dd4607a928cd1315adef6431e239995bc1`
  - `experiments/provider_generation_history/supported.py`
  - `experiments/provider_generation_history/integration.py`
- LAB-095/LAB-096 PR #187 head: `0a14492c280c0fa6ed60ae20c8ea9f04144ade7a`
  - `experiments/provider_generation_history/supported.py`
  - `experiments/provider_generation_history/integration.py`

PR #187 already supplies the required internal abstraction:

```python
def _history(self) -> IntegratedProviderHistory:
    try:
        return object.__getattribute__(self, "_provider_history")
    except AttributeError:
        return object.__getattribute__(self, "provider_history")
```

Supported LAB-096 ledgers bind an exact `CoordinatorOnlyProviderHistory` into `_provider_history`; public `provider_history` returns only `ProviderHistoryInspectionView`.

## LAB-090 call-site classification

### Construction

LAB-090 currently does:

```python
self.provider_history = CoordinatorOnlyProviderHistory(path, bootstrap)
SupportedSharedAnchorLedger.__init__(self, path, attested)
```

**Composition rule:** preserve this as the one-time construction bind through LAB-096's setter, but preserve LAB-095's class MRO:

```python
class CoordinatorOnlyProviderHistory(CanonicalDatabaseBinding, IntegratedProviderHistory):
    ...
```

Do not replace the history object later. Do not restore LAB-090's older `CoordinatorOnlyProviderHistory(IntegratedProviderHistory)` definition, because that would silently remove canonical DB binding.

### `_recover_pending_activation()`

LAB-090:

```python
durable = self.provider_history.current()
```

Classification: read-only semantically, but internal coordinator state.

**Composed form:** `self._history().current()`.

Reason: using `_history()` keeps all internal security decisions on the construction-bound exact strategy and avoids coupling coordinator internals to the public delegation surface.

### `_verify_activation_records()`

LAB-090:

```python
durable = self.provider_history.current()
```

Classification: read-only semantically, security-sensitive durable verification input.

**Composed form:** `self._history().current()`.

### `rotate_provider()` retry path

LAB-090:

```python
durable = self.provider_history.current()
```

Classification: read-only semantically, but controls whether an activation retry is accepted.

**Composed form:** `self._history().current()`.

### `rotate_provider()` SQL transaction

LAB-090:

```python
self.provider_history._rotate_locked(q, new, proof)
```

Classification: internal authority-changing operation.

**Mandatory composed form:** `self._history()._rotate_locked(q, new, proof)`.

This call must never go through public `provider_history`; the LAB-096 inspection view intentionally does not expose `_rotate_locked`.

### `_stored_receipt()`

LAB-090:

```python
receipt = self.provider_history._load_receipt_locked(q, entry.request_id)
```

Classification: transaction-internal locked helper.

**Mandatory composed form:** `self._history()._load_receipt_locked(q, entry.request_id)`.

### `_reauthenticate()` current-head decision

LAB-090:

```python
durable = self.provider_history.current()
```

Classification: read-only semantically, but decides whether fresh external reconciliation is permitted.

**Composed form:** `self._history().current()`.

### `_reauthenticate()` receipt persistence

LAB-090:

```python
binding = self.provider_history.store_receipt(receipt)
```

Classification: authority-adjacent durable mutation.

**Mandatory composed form:** `self._history().store_receipt(receipt)`.

The public LAB-096 inspection view intentionally omits `store_receipt`.

## Base LAB-081 interaction

PR #175 also modifies `integration.py` by adding a runtime-vs-durable generation check inside `reserve()`. In the final composed tree that new check must be preserved, but the PR #187 version of `integration.py` must remain the structural base because it has already migrated inherited provider-history access to `_history()`.

Therefore conflict resolution must be semantic, not whole-file selection:

- retain PR #187 `_history()` helper and all `_history()` dispatches;
- retain LAB-090's additional `runtime = self._descriptor_from_attested(self.attested)` generation equality check in `reserve()`;
- do not accept PR #175 `integration.py` wholesale, because it restores direct live `provider_history` authority access.

## Required final class/capability shape

The final LAB-090 + LAB-095/LAB-096 composition should have exactly one live history strategy:

```text
SupportedHistoricalSharedAnchorLedger
  public provider_history -> ProviderHistoryInspectionView (read-only delegation surface)
  private _provider_history -> CoordinatorOnlyProviderHistory
      MRO includes CanonicalDatabaseBinding
      exact canonical DB path is construction-bound
      locked helpers + receipt mutation + rotation are coordinator-internal only
```

Internal ledger paths use `_history()` for both reads and mutations. External callers may inspect current/durable history and receipts through the public view, but cannot obtain `_con`, `_rotate_locked`, `_load_receipt_locked`, `store_receipt`, path/bootstrap mutation, or live-strategy replacement authority.

## Activation ordering that must not change during conflict resolution

The following LAB-090 invariants are independent of the history-capability refactor and must be retained exactly:

1. candidate provider `prepare_activation()` installs the external fence before the authoritative SQL rotation;
2. the SQL transaction rechecks unresolved activations, PREPARED intents, and the exact reserved tail;
3. the same SQL commit stores the activation ticket and generation rotation;
4. provider `commit_activation()` leaves the ticket `COMMITTED_FENCED`;
5. SQLite exact-ticket status is durably advanced to `COMMITTED` before release;
6. only then is the exact provider ticket released;
7. restart reconciliation fails closed for premature release, lost reservation, invalid historical unresolved activation, or ticket mismatch.

Replacing `self.provider_history` with `_history()` at the classified call sites does not alter this ordering.

## Conflict-resolution checklist

Before a composed branch can claim GREEN:

- [ ] `CoordinatorOnlyProviderHistory` keeps `CanonicalDatabaseBinding` in its MRO.
- [ ] only construction performs the initial provider-history strategy bind.
- [ ] no post-construction `provider_history` or `_provider_history` replacement exists.
- [ ] all LAB-090 internal provider-history calls dispatch through `_history()`.
- [ ] public `provider_history` still exposes only the inspection view.
- [ ] LAB-090 activation table/trigger schema verification remains intact.
- [ ] LAB-090 provider fencing and acknowledgement ordering remains intact.
- [ ] LAB-090 runtime-vs-durable head check added to `reserve()` remains intact.
- [ ] LAB-092 provenance composition is resolved without replacing the live history strategy.
- [ ] exact PR #187 capability/path-binding tests execute.
- [ ] LAB-090 focused stale-candidate, external-advance, UNKNOWN, restart, overlapping-rotation, historical-retry, premature-release and historical-unresolved regressions execute on the composed tree.

## Decision

No independent patch is applied to PR #175 in this run. Its branch does not contain LAB-096's `_history()`/private-strategy infrastructure, so rewriting call sites there in isolation would either fail or duplicate the composition mechanism. The safe next implementation point is a composed branch/tree based on PR #187 semantics, carrying LAB-090 activation behavior across conflict resolution.

No full behavioral GREEN is claimed in this run because a byte-preserving exact repository tree could not be materialized into the executable filesystem.