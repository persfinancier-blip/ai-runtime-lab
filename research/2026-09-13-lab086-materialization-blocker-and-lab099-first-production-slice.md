# LAB-086 materialization blocker and LAB-099 first production slice

Date: 2026-09-13

## LAB-086 first-priority probe

The exact gate remains pinned to executable commit `1f90830fca21e2f43fc241012cdd34fd187ba96d` by `research/2026-08-27-lab086-exact-gate-manifest.md`.

This run reconstructed the complete LAB-086 test inventory from the pinned Contents API: 29 ordinary `test_*.py` files plus `unsafe_legacy_promotion_expected_failure.py`. The manifest additionally requires the listed implementation closure and the pinned LAB-085 fixture helper.

A fresh direct clone was attempted and again failed before repository execution:

`fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com`

exit 128.

The GitHub connector successfully returns exact UTF-8 file content and pinned blob SHAs, including `test_provider_receipt_null_identity_regression.py` at blob `a66d9ddef2d4a41db937222b875f697c7ff74b75` and `strict_fence.py` at blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`.

The concrete per-run blocker is now narrower than generic network unavailability: there is no supported programmatic byte-stream bridge from connector responses into the local execution filesystem. Manually retyping 50+ source files would not satisfy the byte-exact reconstruction gate and is therefore rejected as an invalid fallback. No full LAB-086 unittest/security/compile/conflict PASS is claimed.

## LAB-099 fallback after observed executable RED

The retained LAB-099 six-case RED had already established that production module `experiments.provider_generation_history.activation_reservation_provenance` was absent. This run added the first production slice on branch `lab-099-precursor-cutover-red-intent`, commit `d40aea8c48efe587b273650a3756ca782ba81472`.

New file:

`experiments/provider_generation_history/activation_reservation_provenance.py`

Published Git blob:

`1e642016c7f3fec258f0e2b7671b763d758f2ff4`

The locally authored exact source passed `python -m py_compile`, and local `git hash-object` was exactly `1e642016c7f3fec258f0e2b7671b763d758f2ff4`, matching GitHub after publication.

### Implemented production semantics

The module does not import `tests/lab099_*` and therefore does not promote fixture vectors into production authority.

It implements:

- `PrecursorCutoverMigrationRequired`;
- `PrecursorCutoverVerificationError`;
- exact precursor-relation V1 identity and normalized-definition digest checking;
- cutover evidence relation shape and one-row checks;
- deterministic `prepared_digest -> anchor_intent_id` cross-binding;
- shared-anchor component/type/status/receipt shape checks;
- read-only `classify_precursor_cutover_v1()` with fail-closed states;
- `PrecursorGovernedHistoricalSharedAnchorLedger` startup gate that rejects ABSENT with explicit migration-required and rejects all non-CONFIRMED corrupt/incomplete states;
- explicit `migrate_precursor_cutover_v1()` and `resume_precursor_cutover_v1()` surfaces that remain fail-closed rather than synthesizing PREPARED/CONFIRMED authority.

### Executed local checks

Because the full repository closure is not locally materialized, import dependencies were replaced only for a narrow classifier execution check with inert stub base classes. The exact production file then executed against fresh SQLite databases and produced:

- no LAB-099 relation/evidence -> `ABSENT`;
- exact frozen precursor DDL without cutover evidence -> `ORPHAN_UNAUTHENTICATED_SCHEMA`;
- same relation name with mismatched DDL -> `CORRUPT_RELATION`.

This narrow classifier check is not claimed as the full six-case repository GREEN.

## Audit / decision

The first production slice intentionally stops before authenticated migration/resume. The prior RED scaffold's exact PREPARED/CONFIRMED test vectors are test authority, not a permissible production source. The next implementation step must derive PREPARED authority from inherited LAB-092 durable state and existing shared-anchor execution primitives, then let the exact six-case RED identify remaining scaffold/production mismatches.

A source audit also predicts that once the production module exists, later RED cases may expose fixture-side gaps that were previously masked by `_future_surface()` failing first. Those must be treated as observed failures when executable materialization is available, not guessed around.
