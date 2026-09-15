# LAB-095 integration/wiring call-site audit — 2026-09-16

## Scope

Continuation of #180/#181 composition audit for draft PR #187 after the capability-surface and corrupt-receipt restart adaptations.

Per `AGENTS.md`, LAB-086 was probed first in this run. `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository code execution with `Could not resolve host: github.com`, exit 128. No LAB-086 executable PASS is claimed.

## PR #187 call sites inspected

### `experiments/provider_generation_history/tests/test_integration.py`

This is an actual supported-runtime integration surface. It is already composed correctly:

- fresh databases enter through `migrate_activation_schema_v1()` rather than direct `SupportedHistoricalSharedAnchorLedger(...)` construction;
- providers used for bootstrap and rotation are `FencedActivationProvider`;
- authenticated activation-schema migration is explicitly accounted for as provider position 1;
- the first ordinary intent therefore lands at position 2;
- generation-2 candidates are initialized from the durable current tail;
- restart uses the normal supported constructor only after provenance is COMPLETE;
- PREPARED-vs-rotation and reserve-vs-rotation tests retain fail-closed activation-ticket cleanup assertions.

No stale pre-LAB-092 fresh constructor or non-fenced rotation fixture remains in this file.

### `tests/test_supported_activation_wiring.py`

This file is source-structure validation, not a runtime constructor fixture. It asserts that supported rotation uses `FencedActivationProvider`, private construction-bound `_history()`, pre-ack before durable acknowledgement, and no public `provider_history` strategy substitution. It does not create a fresh database and needs no LAB-101 bootstrap adaptation.

### `experiments/provider_generation_history/test_activation_schema_startup.py`

This is deliberately below the supported-runtime bootstrap boundary. It patches the classifier/startup guard to verify read-only startup classification and constructor ordering. Its temporary SQLite database exists only to prove the path wrapper does not mutate legacy state. Routing it through migration would destroy the property under test.

### `tests/test_activation_restart_recovery.py`

This is also intentionally below supported startup. `_Coordinator` isolates activation recovery semantics and `_seed_complete_schema()` constructs exact COMPLETE provenance directly so recovery cases can be exercised without unrelated provider-history/bootstrap behavior. It already uses `FencedActivationProvider`. No supported fresh-constructor defect exists here.

### `tests/test_activation_schema_explicit_bootstrap.py` and `tests/test_activation_schema_explicit_bootstrap_failures.py`

These are the LAB-101 bootstrap boundary itself. Their use of `SignedAnchorProvider` is intentional: bootstrap confirmation is an ordinary authenticated intent increment, not a provider-generation rotation. Fencing is required by the rotation protocol, not by every ledger increment. These tests do not call `rotate_provider()`. Replacing the provider solely for uniformity would conflate the migration-confirmation contract with LAB-090 rotation fencing.

## Result

No additional stale supported-runtime integration/wiring call site was found in this slice. The remaining direct/manual SQLite construction inspected here is test-boundary-specific and should be preserved.

This is a source audit only. Exact PR #187 pytest/compileall GREEN is not claimed because the repository cannot be byte-exactly materialized into the current executable filesystem.

## Next action

After the mandatory LAB-086 probe, continue LAB-095/LAB-096 authority audit rather than mechanically adapting lower-level fixtures. Prioritize any remaining production or supported-runtime surfaces outside the already inspected PR #187 integration/wiring tests that retain mutable path/history strategy authority. If no such surface remains, reconcile the LAB-095 eight-file closure/hash inventory and enumerate the exact executable gates still required before #180/#181 can leave draft status.
