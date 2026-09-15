# LAB-090 restart recovery focused regressions — 2026-09-15

## Runtime observation

LAB-086 was probed first with direct `git clone --no-checkout`. The operation failed before repository code execution because the shell could not resolve `github.com` (`Could not resolve host: github.com`, exit 128). No LAB-086 PASS is claimed.

## Work performed

Draft PR #187 branch `lab-095-database-identity-red-intent` now contains `tests/test_activation_restart_recovery.py` at commit `2510028d442f775617696d02254d02305e902d8a`.

The fixture creates the exact LAB-092 activation table and trigger DDL, writes the canonical CONFIRMED migration marker from `completion_intent()`, and explicitly proves `classify_activation_schema_provenance_locked(q) == "COMPLETE"` before constructing each recovery scenario.

Focused source-level regressions cover:

1. durable `SQL_COMMITTED` + provider `PREPARED` -> provider commit remains fenced until durable `COMMITTED`, then exact-ticket release;
2. durable `SQL_COMMITTED` + provider `COMMITTED_FENCED` -> durable acknowledgement then release;
3. durable `SQL_COMMITTED` + provider prematurely `RELEASED` -> fail closed;
4. durable `SQL_COMMITTED` + provider `ABSENT` reservation -> fail closed;
5. historical non-current `SQL_COMMITTED` -> fail closed after current-generation reconciliation scope.

## Audit

The first committed fixture seeded the intended COMPLETE objects but did not itself call the provenance classifier. The audit tightened the fixture so every scenario now explicitly proves COMPLETE through the production locked classifier before recovery. This prevents the regression suite from silently drifting away from the LAB-092 startup prerequisite.

The tests exercise the real `FencedActivationProvider` state machine and `ActivationCoordinatorMixin`; only durable history/current-generation lookup is reduced to a minimal private `_history()` stub. No public provider-history authority is introduced.

## Validation limitation

The exact PR #187 repository closure cannot be materialized byte-for-byte into the executable filesystem in this run. Therefore these committed regressions were source-reviewed but not executed, and no pytest/compileall GREEN is claimed.

## Next action

Probe LAB-086 first. If transport remains blocked, audit existing supported-ledger constructor tests for the new explicit LAB-092 migration prerequisite and adapt their setup to install/prove COMPLETE provenance rather than weakening the startup gate. Then inspect the five restart regressions for any compatibility failure exposed by that constructor audit; execute only when exact branch materialization becomes available.
