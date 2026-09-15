# LAB-095 identity-rotation composition audit — 2026-09-15

## Runtime observation
LAB-086 was probed first with `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git`; the shell failed before repository execution with `Could not resolve host: github.com` (exit 128). No executable GREEN is claimed.

## Concrete stale composition found
PR #187 `experiments/provider_generation_history/tests/test_database_identity_rotation_reauthentication.py` still instantiated `SupportedHistoricalSharedAnchorLedger` directly on a fresh database and used plain `SignedAnchorProvider` objects for a rotation.

That is stale against the composed contracts:
- LAB-092 ordinary supported startup requires activation-schema provenance `COMPLETE`;
- LAB-101 provides the explicit fresh/pre-LAB-092 bootstrap path `migrate_activation_schema_v1()`;
- LAB-090 supported rotation requires `FencedActivationProvider`.

## Adaptation
Updated the regression to:
1. bootstrap the fresh DB through `migrate_activation_schema_v1()`;
2. use fenced generation-1 and generation-2 providers;
3. account for the authenticated activation-schema migration consuming provider position 1;
4. expect the database-identity receipt at generation 1 / position 2;
5. start the generation-2 candidate at durable tail 2 before rotation.

The original security assertion is preserved: after rotation and loss of generation-1 live availability, complete database identity must reauthenticate from the historical receipt; deleting that historical receipt must fail closed.

Branch commit: `4eec30809ea0e6203146b9b0274014ec0aae3a3e`.

## Validation status
Source/composition audit only. Exact repository pytest/compileall remains unavailable because no byte-preserving connector-to-executable-filesystem bridge is exposed in this run. Do not count this as executable GREEN.

## Next action
After the mandatory LAB-086 probe, continue scanning PR #187 tests for direct fresh/pre-LAB-092 `SupportedHistoricalSharedAnchorLedger` construction and non-fenced rotation providers. Fix only concrete stale composition, preserving the intended security assertions.
