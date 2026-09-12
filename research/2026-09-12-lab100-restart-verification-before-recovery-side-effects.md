# LAB-100 — restart verification must precede activation recovery side effects

Date: 2026-09-12
Issue: #185 (composes with #184 / LAB-099)
Status: source-proved ordering finding; exact behavioral RED/GREEN pending

## Finding

On PR #175 head `d9a381dd4607a928cd1315adef6431e239995bc1`, `SupportedHistoricalSharedAnchorLedger.__init__()` performs:

1. `_init_activation_schema()`;
2. `_require_runtime_matches_durable_head()`;
3. `_recover_pending_activation()`;
4. `_verify_activation_records()`.

That order is unsafe relative to the frozen LAB-090/LAB-100 restart contract. Recovery can mutate the external provider and coordinator SQLite before all activation-history evidence has been validated.

For a current durable activation row in `SQL_COMMITTED`, `_recover_pending_activation()` may call `_commit_or_reconcile_activation()`. That path can:

- call `provider.commit_activation(ticket)` (external/provider-side state mutation);
- call `_mark_activation_committed(ticket)` (SQLite mutation from `SQL_COMMITTED` to `COMMITTED`);
- call `_release_committed_activation()` / `provider.release_activation(ticket)` (external fence removal).

Only after those actions does startup call `_verify_activation_records()`, which can reject a different historical activation row for missing generation linkage, generation-identity mismatch, invalid expected position/fence/status, activation-id mismatch, or historical unresolved state.

Therefore a database with one recoverable current activation plus separately tampered historical activation evidence can cause startup to make irreversible/relevant recovery mutations and only then fail verification.

## Why this matters

The frozen construction/restart contract requires retained authority and provenance verification before unresolved LAB-090 activation reconciliation. LAB-099 also requires historical activation-ticket tampering to fail closed before provider/SQLite mutation. The current source order does not satisfy either requirement.

This is distinct from the existing arbitrary-subclass finding: even an otherwise trusted exact activation authority should not be allowed to perform recovery side effects until durable activation provenance/history is accepted.

## Minimal regression-first case

Construct a valid multi-generation history with:

- current generation activation row `SQL_COMMITTED` and provider-side status `PREPARED` or `COMMITTED_FENCED`;
- at least one older `COMMITTED` activation row;
- coherently tamper the older row so `_verify_activation_records()` rejects it (LAB-099 can use expected-position/fence/activation-id rebinding).

On restart, assert before the fix:

- constructor ultimately raises `HistoricalVerificationError`;
- but current provider activation state and/or current SQLite activation status changed before the error.

Post-fix requirement:

- historical/provenance verification rejects the database before `provider.commit_activation`, `provider.release_activation`, or activation-status SQLite mutation;
- provider and SQLite activation state remain byte/semantically unchanged on the rejected startup.

## Implementation constraint

Simply moving the existing structural `_verify_activation_records()` call before `_recover_pending_activation()` is necessary but not the complete LAB-100/LAB-099 fix. The final startup sequence must place all retained-authority and authenticated activation-ticket provenance checks (LAB-097..099) before recovery side effects.

Target order:

1. initialize/validate schema without semantic recovery;
2. authenticate retained authority graph and exact activation-authority descriptor;
3. validate provider-generation head and provider-owned restart invariants;
4. verify every activation record plus authenticated ticket/transition provenance;
5. only then reconcile current unresolved activation;
6. re-verify durable state after reconciliation as needed;
7. open worker-facing/delegated surfaces last.

## Source evidence

- PR #175 `supported.py`: constructor calls `_recover_pending_activation()` before `_verify_activation_records()`.
- `_recover_pending_activation()` can invoke `_commit_or_reconcile_activation()` for `SQL_COMMITTED`.
- `_commit_or_reconcile_activation()` performs provider commit, SQLite acknowledgement, and provider release.
- `_verify_activation_records()` is the later loop that rejects malformed/tampered historical activation records.
- Frozen `research/2026-09-04-lab090-lab100-activation-authority-construction-restart-api.md` explicitly requires provenance checks before recovery writes.

Python's `typing.final` is not a runtime enforcement mechanism, so sealing/trust admission must remain an actual runtime construction/registration boundary rather than a type-hint-only control.

## Verdict

`LAB100_RESTART_VERIFY_BEFORE_RECOVER_SIDE_EFFECTS_REQUIRED`

No production code changed in this step because exact PR source execution remains unavailable in this runtime. Direct Git transport was re-probed and failed before repository execution with `Could not resolve host: github.com`; no behavioral PASS/FAIL is claimed.