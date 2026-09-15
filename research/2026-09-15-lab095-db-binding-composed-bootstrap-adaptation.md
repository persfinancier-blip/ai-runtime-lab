# LAB-095 composed DB-binding regression adaptation — 2026-09-15

## Runtime observation

LAB-086 was probed first with a direct `git clone --no-checkout`. It failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

## Objective

Adapt `experiments/provider_generation_history/tests/test_database_path_binding.py` on draft PR #187 to the LAB-090/LAB-092/LAB-101 composition without weakening the COMPLETE-only startup gate or substituting the legacy historical ledger.

## Source audit

At the prior PR head the regression directly constructed `SupportedHistoricalSharedAnchorLedger` on fresh DB A and used plain `SignedAnchorProvider` for provider rotation. Current production composition instead requires:

- ordinary supported startup sees exact LAB-092 `COMPLETE` provenance before constructor side effects;
- fresh/pre-LAB-090 databases enter through explicit `migrate_activation_schema_v1()`;
- that authenticated migration completion consumes shared-anchor position 1;
- LAB-090 supported rotation requires `FencedActivationProvider` and a candidate whose value equals the current durable tail.

## Change

Updated the regression on branch `lab-095-database-identity-red-intent`:

- DB A is bootstrapped through `migrate_activation_schema_v1()` with a generation-1 `FencedActivationProvider` at value 0;
- first ordinary DB-A intent is therefore position 2;
- generation-2 candidate is a `FencedActivationProvider` at value 2 before rotation;
- post-rotation DB-A-only mutation is expected at position 3;
- the legitimate DB-B strategy-replacement case now independently migrates DB B through the same official entrypoint, leaving its tail at position 1, so the test remains about split authority rather than malformed/fresh DB state;
- private/public path rebinding rejection and DB-B no-mutation assertions are retained;
- private provider-history strategy rebinding rejection is retained.

Branch commits: `c8cc55cee579204f91e0dadef504f93be6ac0e74`, followed by source-audit correction `925a1e2587f1a0685b8fb15e040ebe67100cb703` (descriptor comparison through the inspection view uses value equality, not object identity).

## Validation boundary

The exact repository closure is still not materialized into an executable filesystem in this runtime, so pytest/compileall GREEN is not claimed. Validation in this run is source-level composition audit plus conflict-checked Contents API publication to the existing draft branch.

## Next

Re-fetch/audit the adapted regression against the current PR head and inspect whether the migration bootstrap itself preserves the LAB-095 canonical binding on its migration-only object construction paths. If exact materialization becomes available, verify retained blob identities first and execute the focused DB-binding regression plus LAB-080/LAB-081/LAB-090/LAB-092 downstream gates.
