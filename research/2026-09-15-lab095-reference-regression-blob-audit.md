# LAB-095 reference/regression blob audit — 2026-09-15

## Runtime observation

LAB-086 was probed first with `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git`. The command failed before repository code execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS or exact-repository test GREEN is claimed.

## PR #187 head inspected

Head: `c69eb116e78ac85b4983ddb0499131210ddcacc9` (`lab-095-database-identity-red-intent`).

Previously pinned LAB-095 production blobs remain:

- `experiments/database_binding.py` — `c6bf05b3a5579e076142300aefbc9d785cc6354a`
- `experiments/provider_generation_history/database_identity.py` — `bac58a48c576001370144cc10cfab8e0cfd129e3`
- `experiments/provider_generation_history/database_identity_migration.py` — `c4d1db46b8b64fec116dcfef8bb05e1e7a7b875e`
- `experiments/provider_generation_history/integration.py` — `83399d3d184ae61bcfb50a749c11a348e835f428`
- `experiments/provider_generation_history/supported.py` — `a1615cb7b793d6602db4406f0bdccb31ef5fba45`

Connector-visible LAB-095 reference/regression blobs additionally pinned in this run:

- `experiments/provider_generation_history/tests/lab095_database_identity_reference.py` — `9f02ddf64cff5b245cfa7a58e188ff9792b3eb18`
- `experiments/provider_generation_history/tests/lab095_identity_installation_reference.py` — `eca968573bd5374239507aec58b015fcd1f18869`
- `experiments/provider_generation_history/tests/red_intent_lab095_complete_reauthentication.py` — `347eb94d7d2c601095789c9903dbcbbc24099cd8`
- `experiments/provider_generation_history/tests/red_intent_lab095_confirmed_finalize_reauthentication.py` — `7dcd20dfd24a9439583595bf433f9f696bd870e7`
- `experiments/provider_generation_history/tests/red_intent_lab095_database_identity.py` — `b1499243e8452daadf97fdb9ff97e29a9ce82e28`
- `experiments/provider_generation_history/tests/test_database_path_binding.py` — `9aa68be771e251863b228bcc4fadc5486796254e`

These pins are source/control-plane evidence only. They are not a substitute for byte-exact filesystem reconstruction and execution.

## Composition audit finding

`test_database_path_binding.py` is stale relative to the LAB-090/LAB-092 composition now present on the same PR. It directly constructs `SupportedHistoricalSharedAnchorLedger` on a fresh DB with no explicit LAB-092 activation-schema migration/COMPLETE provenance. The supported constructor now intentionally rejects that startup shape before side effects. The same test also uses plain `SignedAnchorProvider` for rotation, while the composed LAB-090 supported rotation requires `FencedActivationProvider`.

Therefore the DB-A -> DB-B regression currently cannot be counted as an executable LAB-095 gate even after repository materialization without adaptation. This is a test-composition defect, not evidence that the production lifetime binding itself is wrong.

Required adaptation is narrow and must preserve the security assertion:

1. bootstrap DB A through the official explicit `migrate_activation_schema_v1()` path so normal supported construction starts only from exact COMPLETE provenance;
2. use `FencedActivationProvider` for supported rotation;
3. account for the authenticated LAB-092 migration position when constructing the candidate generation/provider and expected positions;
4. retain the original DB-B corruption, public/private path rebinding rejection, construction-bound strategy rejection, and proof that subsequent supported mutation touches DB A only.

Do not bypass the startup gate by manually stamping provenance in the fixture.

## Legacy-authority audit

The inspected LAB-095 reference modules are test-only derivation/state-machine authority and do not silently instantiate legacy `HistoricalSharedAnchorLedger`. The concrete DB-binding regression imports the supported ledger, but its setup predates the composed startup/fencing requirements described above. No justification was found for switching that regression to legacy `HistoricalSharedAnchorLedger`; doing so would weaken the acceptance criterion because LAB-095 explicitly concerns supported guarantees.

## Decision / next action

Keep PR #187 draft. Next, after the mandatory LAB-086 probe, adapt `test_database_path_binding.py` through the official LAB-101/LAB-092 explicit migration entrypoint and LAB-090 fenced-provider semantics. Then audit all position assertions after migration consumes its authenticated anchor position. Exact pytest/compileall remains pending until byte-preserving materialization is available.
