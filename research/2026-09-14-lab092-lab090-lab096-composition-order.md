# LAB-092 + LAB-090 + LAB-095/LAB-096 composition order

Date: 2026-09-14

## Scope

This audit resolves the concrete source-level composition problem between:

- LAB-090 PR #175 (`lab-090-provider-activation-fencing`, head `d9a381dd4607a928cd1315adef6431e239995bc1`);
- LAB-092 PR #177 (`lab-092-activation-schema-provenance`, head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`);
- LAB-095/LAB-096 PR #187 (`lab-095-database-identity-red-intent`), whose head advanced in this run to `1c77a2ab361e76cb3c89bfb0918cea130899716d`.

LAB-086 remained priority #1 and was probed first. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

## Current LAB-092 conflicts

`activation_schema_provenance.py` on PR #177 contains four authority patterns that cannot be accepted unchanged after LAB-096:

1. `_reservation_surface()` builds a ledger/history pair with `object.__new__`, assigns `ledger.path`, `history.path`, `history.bootstrap`, then installs `ledger.provider_history = history`.
2. `_verify_confirmation_authority()` calls `ledger.provider_history._verify_durable_locked(q)` through the public history handle.
3. `_install_and_reserve_prepared()` likewise calls `ledger.provider_history._verify_durable_locked(q)`.
4. `_bind_live_provider_history_provenance()` creates a replacement `_ProvenanceBoundCoordinatorOnlyProviderHistory` and reassigns `ledger.provider_history` after supported construction.

The fourth item is exactly the whole-object strategy replacement forbidden by LAB-096. On PR #187 the public `provider_history` is now a least-capability `ProviderHistoryInspectionView`, while the live strategy is construction-bound in private `_provider_history`; post-construction replacement must remain impossible.

The first item is not automatically invalid if retained only as an explicit pre-construction migration surface, but it must establish the same one-time canonical DB binding and exact coordinator-history type as the final supported object. It must never become a route for later rebinding or strategy substitution.

## Minimal safe seam added to PR #187

A small file-scoped change was conflict-checked against blob `70c7c7c2515129375de188e575fa04d2c20014f8` and applied through the normal Contents API to `experiments/provider_generation_history/supported.py`.

Branch commit: `1c77a2ab361e76cb3c89bfb0918cea130899716d`.
New blob: `51cb036c555ec4ac4365767e97e6b8675e4ea26f`.

Change:

- add private ledger-owned `_store_receipt(receipt)`;
- default implementation delegates to `self._history().store_receipt(receipt)`;
- `_reauthenticate()` now persists through `self._store_receipt(receipt)` rather than reaching directly into the history strategy.

Reason: LAB-092 needs a last-moment provenance guard immediately before receipt persistence. That guard belongs on the owning ledger, not in a replacement provider-history strategy. A LAB-092 subclass can override `_store_receipt()` to require `COMPLETE` provenance and then call `super()._store_receipt(receipt)`. This preserves the construction-bound exact history strategy and avoids exposing locked/mutation helpers publicly.

Validation actually executed in this run:

- the exact authored replacement `supported.py` was written to the executable filesystem;
- `python -m py_compile /tmp/supported.py` passed;
- local `git hash-object /tmp/supported.py` returned `51cb036c555ec4ac4365767e97e6b8675e4ea26f`;
- post-write GitHub refetch returned the same blob SHA;
- PR #187 head was observed as `1c77a2ab361e76cb3c89bfb0918cea130899716d` and remains open/draft.

This is syntax/blob evidence only. No exact repository behavioral GREEN is claimed.

## Required LAB-092 source adaptation

When LAB-092 is composed onto the PR #187 authority base:

### A. Preserve PR #187 as structural authority base

Keep all of:

- `CanonicalDatabaseBinding` on supported ledger/history objects;
- exact `CoordinatorOnlyProviderHistory` as the construction-bound private strategy;
- `_provider_history` as the single live strategy slot;
- public `ProviderHistoryInspectionView` only;
- internal `_history()` dispatch for locked/current/receipt/rotation operations;
- new private `_store_receipt()` hook for last-moment receipt mutation policy.

Do not select PR #177 or PR #175 `supported.py`/`integration.py` wholesale during conflict resolution.

### B. Remove post-construction strategy replacement

Delete `_ProvenanceBoundCoordinatorOnlyProviderHistory` as a live replacement mechanism and delete `_bind_live_provider_history_provenance()`.

Do not assign `ledger.provider_history = ...` after `SupportedHistoricalSharedAnchorLedger` construction.

### C. Move locked authority calls to the private strategy

Change LAB-092 internal calls:

- `ledger.provider_history._verify_durable_locked(q)` -> `ledger._history()._verify_durable_locked(q)`;
- any future locked/current/receipt/rotation helper -> `ledger._history()` or a narrower ledger-owned private helper.

Public `provider_history` must remain inspection-only and must never be required by internal security logic.

### D. Preserve post-construction provenance-loss receipt fail-closed behavior on the ledger

On `ProvenancedHistoricalSharedAnchorLedger`, override:

```python
def _store_receipt(self, receipt):
    self._require_complete_activation_schema_provenance()
    return super()._store_receipt(receipt)
```

This preserves the purpose of PR #177's `_ProvenanceBoundCoordinatorOnlyProviderHistory.store_receipt()` without swapping the trusted strategy object.

The guard must stay immediately adjacent to receipt persistence. A one-time constructor check is insufficient because LAB-092 explicitly covers post-construction provenance deletion.

### E. Explicit migration reservation surface

`_reservation_surface()` exists because ordinary supported construction cannot auto-install missing LAB-090 schema. Its future composed version may remain constructor-bypassing only if it is tightly scoped to explicit migration and establishes authority once:

- exact `AttestedCatchup` check;
- bootstrap validation;
- one initial canonical path binding for ledger and exact coordinator history;
- one initial exact `CoordinatorOnlyProviderHistory` strategy bind;
- no later strategy replacement;
- no public mutable history capability;
- all locked checks through `_history()`.

Prefer factoring a dedicated private migration constructor/helper over open-ended raw attribute assembly if a small coherent implementation is possible.

### F. Classification path

`_classify(self.path)` is compatible with LAB-095 only when `self.path` is the canonical construction-bound property. Class/classmethod migration entry points that accept a raw path must canonicalize/validate it consistently before constructing retained objects; raw path input must not become post-construction rebinding authority.

## Combined implementation order

The safe composition order is:

1. **LAB-095/LAB-096 structural base first**
   - canonical immutable DB path;
   - construction-bound private exact coordinator history;
   - least-capability public inspection view;
   - `_history()` for internal authority;
   - `_store_receipt()` ledger-owned mutation hook.

2. **LAB-092 provenance semantics second**
   - preserve explicit migration-only schema installation;
   - adapt `_reservation_surface()` to one-time construction-bound authority;
   - replace all public-history locked access with `_history()`;
   - remove `_ProvenanceBoundCoordinatorOnlyProviderHistory` replacement;
   - override `_store_receipt()` on the provenance ledger for immediate pre-persistence `COMPLETE` checking;
   - retain startup read-only classification and confirmed-marker reauthentication;
   - retain post-install table/trigger deletion fail-closed behavior.

3. **LAB-090 activation fencing third**
   - carry activation behavior semantically from PR #175 rather than taking its older whole files;
   - preserve provider PREPARED -> SQL generation/activation commit -> provider COMMITTED_FENCED -> durable exact-ticket SQL acknowledgement -> exact-ticket release;
   - use `_history()` for current/locked rotation/locked receipt operations;
   - retain LAB-090 runtime-vs-durable generation check in `reserve()`;
   - do not reopen public provider-history mutation authority.

4. **Regression composition**
   - LAB-096 strategy-replacement and public-capability regressions;
   - LAB-095 DB-A -> DB-B path and legitimate-history split-authority regression;
   - LAB-092 legacy migration, concurrency, restart-precheck, confirmation bridge, stale runtime, unresolved activation, post-construction marker deletion, and pre-auth history verification regressions;
   - LAB-090 activation race/restart/UNKNOWN/historical-unresolved regressions;
   - retained LAB-081 focused suite.

5. **Only after exact behavioral execution**
   - audit LAB-097/098/099/100 composition;
   - keep #175/#177/#187 draft until exact downstream gates are clean.

## Security invariants that must survive conflict resolution

- one ledger lifetime -> one canonical SQLite database identity;
- one supported ledger -> one construction-bound exact provider-history strategy;
- public history surface is inspection-only;
- locked/internal authority never dispatches through the public view;
- LAB-092 provenance loss blocks receipt persistence at the last mutation boundary;
- LAB-092 ordinary startup never silently repairs missing/mismatched post-install schema;
- LAB-090 provider activation remains fenced until durable exact-ticket acknowledgement;
- no deterministic test vector, caller-supplied nonce/digest, path hash, or same-DB self-asserted UUID substitutes for external authenticated authority.

## Next executable gate

When a supported byte-preserving connector-to-filesystem materialization path becomes available:

1. materialize exact PR #187 head;
2. verify all expected Git blobs;
3. run `compileall`;
4. run LAB-096 capability/replacement tests and LAB-095 DB-binding tests under a journal-capable filesystem (`TMPDIR=/dev/shm` where applicable);
5. compose the LAB-092 adaptation described above and execute its focused suite;
6. layer LAB-090 semantics and execute LAB-081/LAB-090/LAB-092 downstream gates.

Until then, do not claim full behavioral GREEN.
