# LAB-095 production authority/blob audit — 2026-09-15

## Scope

Continuation of #180 on draft PR #187 at head `c69eb116e78ac85b4983ddb0499131210ddcacc9`. LAB-086 was probed first in this run; direct `git clone --no-checkout` failed before repository execution with `Could not resolve host: github.com` (exit 128), so no LAB-086 PASS or exact repository GREEN is claimed.

This pass prioritized connector-visible production database-binding/identity files and remaining public/rebindable path or provider-history strategy authority.

## Exact connector-visible branch blobs

The following files were fetched directly at PR #187 head and their Git blob identities recorded by the Contents API:

- `experiments/database_binding.py` — `c6bf05b3a5579e076142300aefbc9d785cc6354a`
- `experiments/provider_generation_history/database_identity.py` — `bac58a48c576001370144cc10cfab8e0cfd129e3`
- `experiments/provider_generation_history/database_identity_migration.py` — `c4d1db46b8b64fec116dcfef8bb05e1e7a7b875e`
- `experiments/provider_generation_history/integration.py` — `83399d3d184ae61bcfb50a749c11a348e835f428`
- `experiments/provider_generation_history/supported.py` — `a1615cb7b793d6602db4406f0bdccb31ef5fba45`

These are branch blob identities, not locally reconstructed hashes; byte-for-byte executable materialization remains unavailable in this runtime.

## Authority audit

### Database path

`CanonicalDatabaseBinding` canonicalizes the first assigned path and rejects subsequent assignment to both public `path` and private `_canonical_database_path`. PR #187 applies that binding at the supported shared-ledger boundary and to `CoordinatorOnlyProviderHistory`. The concrete supported historical ledger constructs the history strategy from the same constructor path, then initializes the supported shared ledger from that path. No later supported path setter is exposed in the inspected production files.

The explicit LAB-095 migration canonicalizes `ledger.path` and `history.path`, rejects divergence, then uses that canonical path for its SQLite writer. Because the intended supported objects expose construction-bound paths, the migration does not introduce a new supported rebindable path authority. The migration functions remain generic Python call surfaces, however, so callers can technically pass unsupported objects with mutable `path`; that is an explicit migration API boundary rather than runtime supported-ledger authority. Do not broaden this into a supported constructor path without exact-type/binding review.

### Provider-history strategy

`SupportedHistoricalSharedAnchorLedger` stores the mutable implementation in private `_provider_history`, rejects rebinding of both `_provider_history` and public `provider_history`, and exposes only `ProviderHistoryInspectionView`. The view permits `current`, verification, receipt inspection, and static transition construction; it does not expose rotation or a writable path. `CoordinatorOnlyProviderHistory.rotate()` rejects direct rotation. Production mutation continues through the concrete ledger's private `_history()` path and coordinator-owned transition primitives.

No remaining public provider-history strategy replacement path was found in the inspected PR #187 production files.

### Legacy base class remains intentionally broader

`HistoricalSharedAnchorLedger` in `integration.py` still assigns public `provider_history = IntegratedProviderHistory(...)` and its `_history()` fallback reads that public attribute. This is legacy LAB-081 behavior. The supported concrete class does not invoke that constructor; it installs `CoordinatorOnlyProviderHistory` itself and calls `SupportedSharedAnchorLedger.__init__` directly. Therefore this broader legacy surface is not evidence of a rebindable strategy in the inspected supported concrete path, but downstream code must continue to instantiate `SupportedHistoricalSharedAnchorLedger`, not the legacy base, when LAB-095/LAB-096 guarantees are required.

## Result

Source audit found no new production path/strategy authority defect requiring a patch in this slice. Five production branch blobs are now explicitly pinned for later same-run reconstruction/hash comparison. Exact pytest/compileall and the complete eight-file reconstruction gate remain pending because connector-visible bytes cannot currently be placed into an executable filesystem byte-for-byte.

## Next

After the mandatory LAB-086 probe, continue the LAB-095 eight-file closure by pinning the remaining reference/regression file blob identities from PR #187 and comparing their imports/authority assumptions against the five production blobs above. If exact materialization becomes available, reconstruct all retained files at PR head, verify blob/hash identity before execution, then run the LAB-095 focused/downstream gates. Do not claim GREEN from source inspection alone.
