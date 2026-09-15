# LAB-092 explicit atomic migration writer slice — 2026-09-15

## Runtime observation

LAB-086 was probed first. `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

## Implemented fallback

Draft PR #187 received `experiments/provider_generation_history/activation_schema_migration.py`.

The writer is intentionally opt-in and adapts only the `_install_and_reserve_prepared` semantics from LAB-092 PR #177 onto the LAB-095/LAB-096 authority model:

- migration-only reservation surface uses `object.__new__` so an existing legacy database is verified before normal constructors can initialize/repair state;
- canonical ledger path is assigned once;
- exact `CoordinatorOnlyProviderHistory` is installed once through the construction-bound `provider_history` setter;
- no `_bind_live_provider_history_provenance()` and no post-construction `_provider_history` replacement exists;
- one `BEGIN IMMEDIATE` covers durable-history verification, runtime-generation comparison, exact DDL installation, deterministic PREPARED marker insertion, and `shared_anchor_meta` advance;
- locked durable history verification routes through private `ledger._history()`;
- only exact absent DDL or exact table+trigger DDL with ABSENT/PREPARED marker is recoverable;
- partial/mismatched DDL and corrupt marker states fail closed;
- exact CONFIRMED state is read-only/idempotent, but CONFIRMED with damaged DDL fails closed;
- unrelated PREPARED intents are rejected even while resuming the migration's own PREPARED marker;
- stale runtime provider generation is rejected before schema/history mutation.

Initial branch commit `f4ff3713addf71a8f7b95c15afa86c6622e3e07d` was audited immediately. The audit found that the PREPARED-resume early return did not explicitly reject an unrelated second PREPARED row in a corrupted/legacy database. This was fixed before handoff in commit `af4baae16f4f4cc9110f23a1d58cf7dddde534e2`, blob `fd3e676008ca28ff7070559579d76509a79a8262`.

## Validation boundary

The connector-to-filesystem byte-preserving bridge is still unavailable, so exact branch pytest/compileall was not executed and no behavioral GREEN is claimed. Validation this run is source-level conflict/audit plus GitHub Contents write/refetch evidence. The writer must remain opt-in until LAB-090 activation fencing/recovery semantics are ported and exact repository gates execute.

## Next composition step

Add focused regressions around this writer for partial DDL, unrelated PREPARED intent, stale runtime generation, exact PREPARED resume, and CONFIRMED-corrupt DDL. Then port LAB-090 activation fencing semantics without selecting PR #175 authority-heavy `supported.py` wholesale.