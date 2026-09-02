# LAB-090 audit: COMMITTED-before-release window

Date: 2026-09-02

## Question

Does PR #175 create a new standalone write-safety defect because `_mark_activation_committed()` changes the SQLite activation row from `SQL_COMMITTED` to `COMMITTED` before `_release_committed_activation()` actually removes the provider-side fence?

The activation trigger blocks `shared_anchor_intents` only while at least one activation row is `SQL_COMMITTED`, so after the durable acknowledgement but before provider release there is a short interval where the SQL trigger no longer blocks inserts while the external provider is still `COMMITTED_FENCED`.

## Source observations

PR #175 head audited: `d9a381dd4607a928cd1315adef6431e239995bc1`.

`SupportedHistoricalSharedAnchorLedger._commit_or_reconcile_activation()` performs:

1. provider commit / reconciliation and requires `COMMITTED_FENCED`;
2. `_mark_activation_committed(ticket)`;
3. `_release_committed_activation(provider, ticket)`.

The activation trigger predicate is `status='SQL_COMMITTED'`, so step 2 removes the SQL-side global insert block before step 3 removes the external provider fence.

`FencedActivationProvider.release_activation()` may still fail after step 2 (for example, if the provider becomes unavailable before release), leaving durable SQLite `COMMITTED` while provider state remains `COMMITTED_FENCED`.

## Supported-surface audit

This window looked like a candidate LAB-090 bug, but on the current supported composition it is not independently reachable as a successful writer bypass:

- the rotating ledger object has not yet rebound `self.attested` to the new provider when release is attempted;
- `HistoricalSharedAnchorLedger.reserve()` on PR #175 checks the runtime provider generation against durable provider history before creating a new intent, so the rotating object's still-old runtime is rejected after the durable head has advanced;
- a freshly constructed ledger using the new provider runs `_recover_pending_activation()` during construction; if the provider is still fenced and release cannot complete, construction fails before the object becomes a usable supported writer;
- a ledger using the old provider fails the durable-head/runtime-generation check;
- a raw same-privilege SQLite writer is outside LAB-090's standalone authority claim and belongs to the LAB-087 sole-writable-handle/process boundary.

Therefore the `COMMITTED -> release` interval is not being opened as a new standalone LAB-090 issue in this run.

## Composition consequence

The window becomes security/correctness relevant if another authority-boundary defect lets a caller bypass those supported-surface assumptions. In particular:

- LAB-093/#178: rebinding/exposure of nested attested/provider capabilities;
- LAB-100/#185: fake/subclass provider implementations, inherited provider identity mutation, or caller-owned mutable activation state.

Future LAB-090/LAB-093/LAB-100 integration regressions should include:

1. durable activation acknowledgement completed (`COMMITTED`);
2. provider release deliberately not completed (`COMMITTED_FENCED`);
3. prove no supported stale/current/rebound ledger path can create or execute a new shared-anchor intent before exact-ticket release/recovery completes.

If a future least-capability refactor permits a preconstructed current-generation writer to survive this interval, either keep the SQL row unresolved until release or add a separate durable release-required status/guard.

## Runtime/tool evidence

Direct Git transport was probed in this run and failed before repository execution with `Could not resolve host: github.com`.

The GitHub connector returned the exact PR #175 `supported.py` source and the exact LAB-086 predecessor/retained-patch blobs, but there is still no supported byte-preserving machine bridge from connector payload to local patch application/hash verification/Contents publication. No production source was mutated and no exact behavioral PASS is claimed.

## Decision

No new issue. Record this as an audited non-standalone window and compose it into existing LAB-093/LAB-100 regression planning rather than duplicating the authority-boundary backlog.
