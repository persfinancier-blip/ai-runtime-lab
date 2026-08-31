# LAB-092 trigger-deletion and partial-DDL regressions

Date: 2026-08-31

## Context

LAB-086 remains priority #1, but the current GitHub interface still exposes no supported byte-preserving patch-composition/write operation for the exact `strict_fence.py` predecessor + retained patch contract. Direct git transport was re-probed in this run and failed before repository execution with `Could not resolve host: github.com`. Per `state/CURRENT.md`, LAB-092 is therefore the allowed fallback while exact execution is unavailable.

## Change

Draft PR #177 / branch `lab-092-activation-schema-provenance` was extended at commit `86d501cb2879a684c72201ae94f348a2931ee0a4`.

Published test file:

- path: `experiments/provider_generation_history/tests/test_activation_schema_provenance.py`
- blob: `17f37a6a34dfc8caf26ee37a7e019afc6a744fc4`

Two regressions were added without changing LAB-090 source:

1. **Confirmed migration + trigger-only deletion**
   - perform legitimate explicit migration;
   - delete only `block_intent_during_provider_activation`;
   - ordinary startup must raise `HistoricalVerificationError`;
   - repeated explicit migration must also raise;
   - the trigger must remain absent, proving no silent repair.

2. **Unmarked partial activation DDL**
   - retain the exact `provider_generation_activations` table but remove the trigger before any provenance marker exists;
   - ordinary startup and explicit migration must both fail closed;
   - the exact table remains and the trigger remains absent, proving the ambiguous partial state is not auto-healed.

## Evidence actually observed

- GitHub Contents API update succeeded and returned commit `86d501cb2879a684c72201ae94f348a2931ee0a4`, blob `17f37a6a34dfc8caf26ee37a7e019afc6a744fc4`.
- The published file was re-fetched from branch `lab-092-activation-schema-provenance`; both intended regressions are present in the returned bytes.
- Exact branch unittest execution was attempted first through a fresh git clone, but network resolution failed before any repository code executed: `Could not resolve host: github.com`.
- Therefore this run does **not** claim branch-level RED/GREEN or full-suite PASS.

## Audit conclusion

The new tests strengthen the intended LAB-092 contract at two important ambiguity boundaries: post-confirmation loss of only the guard trigger, and a pre-marker partial installation. Both states must be treated as evidence requiring fail-closed handling rather than as permission to repair schema automatically.

The remaining regression matrix is unchanged: PREPARED-marker recovery, mismatched DDL definitions, concurrent-writer behavior during explicit migration, and interaction with unresolved LAB-090 activation records.
