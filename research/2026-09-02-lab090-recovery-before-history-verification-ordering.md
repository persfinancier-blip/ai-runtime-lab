# LAB-090 restart recovery ordering audit

Date: 2026-09-02

## Finding

The current draft PR #175 constructor orders activation recovery before full activation-history verification:

```python
self._init_activation_schema()
self._require_runtime_matches_durable_head()
self._recover_pending_activation()
self._verify_activation_records()
```

`_recover_pending_activation()` is not read-only. Depending on the durable current activation row and provider status it can:

- call `provider.commit_activation(ticket)`;
- update the durable activation row from `SQL_COMMITTED` to `COMMITTED` via `_mark_activation_committed()`;
- call `provider.release_activation(ticket)`, removing the external activation fence.

Only after those effects does `_verify_activation_records()` inspect the complete durable activation history and reject malformed/orphaned/non-integral/inconsistent historical rows.

## Why this matters

A restart against a database whose *current* activation row is locally reconcilable but whose *other* activation history is invalid can therefore mutate coordinator/provider state before the constructor discovers that the database as a whole is unacceptable.

The important case is `SQL_COMMITTED`: restart may commit the provider activation, durably acknowledge it as `COMMITTED`, and release the external fence, then fail construction because a different historical activation row violates verification. That weakens fail-closed startup semantics: rejected durable state has already caused externally consequential recovery effects.

Even for an already-`COMMITTED` current row, releasing a still-installed provider fence before validating the complete history means a failed startup can leave the external provider less fenced than it was at entry.

This is distinct from LAB-092/#176 schema-installation provenance. The table and trigger may both be authentic and present; the defect is recovery-side-effect ordering relative to full historical verification.

## Required regression-first contract

Before changing production code, add an executable restart regression with all of these properties:

1. create a valid current generation with a current activation row that is recoverable (`SQL_COMMITTED` is the strongest case);
2. preserve matching provider-owned activation state so recovery would otherwise commit/release the ticket;
3. corrupt or inject a *different historical activation row* in a way that `_verify_activation_records()` rejects (for example an orphan reference or invalid historical numeric ticket value);
4. restart the supported ledger;
5. assert construction fails **without** changing the current durable activation status and **without** committing/releasing the provider activation fence.

A second case should cover a current `COMMITTED_FENCED` provider state plus durable `COMMITTED`: historical verification failure must not release that fence.

## Implementation direction

Prefer a side-effect-free preflight that validates the complete activation relation before `_recover_pending_activation()` is allowed to call provider mutation APIs or update durable activation status. Re-check any facts that can change across the recovery boundary as needed; do not treat an early verification snapshot as serializing the external provider.

The final constructor should preserve the invariant:

> no external activation mutation or durable recovery mutation occurs until every durable fact required to trust that recovery has passed fail-closed verification.

## Evidence basis

Source-level audit of PR #175 diff, especially `SupportedHistoricalSharedAnchorLedger.__init__`, `_recover_pending_activation`, `_commit_or_reconcile_activation`, `_mark_activation_committed`, `_release_committed_activation`, and `_verify_activation_records`.

No behavioral PASS/FAIL is claimed in this run because exact source execution remains unavailable. This note defines the regression that must be executed before production changes.
