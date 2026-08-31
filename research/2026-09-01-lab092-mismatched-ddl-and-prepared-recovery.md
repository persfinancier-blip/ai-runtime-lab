# LAB-092 mismatched-DDL and PREPARED recovery regressions

Date: 2026-09-01

## Scope

Continued LAB-092 on draft PR #177 without changing LAB-090.

LAB-086 remained first priority, but no supported byte-preserving patch-composition/write bridge was available in this run. A fresh exact checkout attempt for PR #177 also failed before repository execution with `Could not resolve host: github.com`, so no branch-level GREEN is claimed.

## New published regressions

Branch: `lab-092-activation-schema-provenance`

New test file:
`experiments/provider_generation_history/tests/test_activation_schema_provenance_recovery.py`

Current published blob: `f7e69087525f74bc7ed2a8e1d6acbb8bf30b5b40`

Current branch commit for the tightened suite: `5f6d2beda547d4395f7c149b7bd5bbf9ce05f3d9`.

The suite adds three cases:

1. **Unmarked mismatched trigger**
   - start from an exact LAB-090 schema;
   - replace `block_intent_during_provider_activation` with a same-name but mismatched trigger;
   - ordinary LAB-092 startup must fail closed;
   - explicit migration must also fail closed;
   - the mismatched trigger must remain unrepaired.

2. **Post-completion mismatched trigger**
   - perform the explicit migration and confirm provenance;
   - replace the exact trigger with a same-name mismatched trigger;
   - both ordinary startup and explicit migration must fail closed;
   - no automatic repair is permitted after completion provenance exists.

3. **PREPARED completion-marker recovery**
   - create exact activation DDL;
   - reserve the deterministic LAB-092 completion intent without confirming it, leaving the marker `PREPARED`;
   - ordinary startup must raise the specific `ActivationSchemaMigrationRequired` and must leave the marker PREPARED;
   - only `migrate_activation_schema_v1()` may resume/confirm the marker;
   - successful explicit recovery must end with a CONFIRMED marker and verified activation-schema provenance.

The PREPARED regression deliberately asserts the specific migration-required exception rather than `Exception`, preventing unrelated constructor failures from satisfying the test.

## Validation status

Published bytes were written through the normal Contents API and the current file blob is recorded above.

Exact branch unit execution was attempted first via a fresh clone, but DNS failed before any repository code ran. Therefore these regressions are authored/published but not yet observed GREEN against the exact branch head.

## Next highest-value fallback

If exact execution remains unavailable:

1. add a concurrent-writer explicit-migration regression proving no shared-anchor intent can enter between DDL installation and completion-marker reservation/confirmation in a way that creates ambiguous provenance;
2. audit and regress explicit migration while a LAB-090 activation record is unresolved, requiring fail-closed behavior and no completion-marker confirmation if LAB-090's trigger blocks the migration intent;
3. keep PR #177 draft until exact published-head behavioral execution succeeds.
