# LAB-086 live guard presence correction — 2026-08-28

## Observation

Fresh GitHub reads of draft PR #165 at branch `lab/086-asymmetric-break-glass-history`, HEAD `abafb3aabe0276b4a73def343a311b459c818dc8`, identify `experiments/asymmetric_break_glass_history/strict_fence.py` as blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.

The exact live source was then inspected rather than inferring semantics from blob lineage. It already contains both protections that the previous handoff incorrectly described as needing recomposition:

1. provider receipt NULL identity rejection in `_install_provider_receipt_freeze_locked`: `NEW.request_id IS NULL` is included in the insert-deny predicate;
2. alternate provider-generation semantic collision rejection in `_install_thaw_insert_history_collision_fences_locked`: for `asymmetric_provider_generations`, the trigger rejects any existing row with `provider_id IS NEW.provider_id AND generation IS NEW.generation`.

A direct search of the exact live source finds no `rowid` guard. Therefore the current security delta is narrower than the preceding handoff claimed.

## Lineage reconciliation

Commit `05d8e75a636818afcb32e085d464c9fa9171dea5` remains the historical executable alternate-UNIQUE GREEN pin with `strict_fence.py` blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36`. A compare from that commit to current HEAD shows `strict_fence.py` changed by only 7 additions / 3 deletions among later provider-receipt and regression work. Blob inequality alone did not imply loss of the alternate-UNIQUE semantic guard.

The earlier conclusion "current d4a6a40f has lost alternate-UNIQUE protection" is therefore retracted. Exact source semantics win over lineage inference.

## Current candidate rule

The next candidate must start from exact current blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd` and apply only the durable hidden-rowid hardening described by `research/2026-08-28-lab086-hidden-rowid-replace.patch`.

Before publication, require candidate GREEN for all three focused regressions:

- `test_provider_receipt_null_identity_regression.py`;
- `test_thaw_alternate_unique_collision_regression.py`;
- `test_thaw_rowid_collision_regression.py`.

Then run the full strict/thaw conflict subgate and compileall. Existing alternate-UNIQUE and NULL-receipt guards are preservation obligations, not separate patches to reapply.

## Tool/runtime evidence

The GitHub connector can expose the complete added-file PR patch and exact branch source plus blob identity, but this run still lacks an execution-capable byte-preserving checkout path for the complete dependency closure. No new unittest PASS is claimed here.

## Decision

`LIVE_GUARD_PRESENCE_CORRECTED_ROWID_ONLY_DELTA_CONFIRMED`
