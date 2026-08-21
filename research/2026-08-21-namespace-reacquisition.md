# LAB-066 — Restart namespace reacquisition

## Result so far
A restart loses LAB-065's held directory FD, so a pathname alone cannot recreate authority. The reference record is authenticated and generation-bound. Linux opaque handle evidence is captured when `name_to_handle_at` supports the filesystem; the current pathname is reauthorized without following symlinks and its handle is compared to the durable record. `st_dev/st_ino` and mount IDs are observations only, not universal persistent identities.

The current runtime can capture handles but cannot prove `open_by_handle_at` because `CAP_DAC_READ_SEARCH` is absent. Therefore a missing/renamed directory with saved handle is classified `UNSUPPORTED_STRONG_REACQUISITION`, never silently rebound by path or bytes. Intentional relocation requires an authenticated migration permit and increments namespace generation.

## Real integration
`SignedPrunableHistory` now persists the continuity row and does not recreate a missing archive directory on restart. Every consequential `require_namespace_authority()` refreshes strong reacquisition instead of trusting a cached startup result. LAB-065 directory-FD acquisition is additionally bound back to the authenticated continuity record's `(st_dev, st_ino)`, closing the swap-between-reacquire-and-open race.

Archive publication receipts now carry `namespace_generation`; artifact and manifest receipts must agree and must still equal the current authenticated generation immediately before SQL commit. A migration after publication therefore fences stale receipts.

LAB-063 scavenging is also inside the authority boundary. On a namespace-capable layer it enumerates, reads and unlinks through one held directory FD, rechecks configured-path binding immediately before unlink, and refuses scan/destruction when continuity cannot be reacquired. This closes the lexical `Path.unlink()` TOCTOU left by a simple pre-operation authority check.

## Remaining proof gate
The implementation is still draft until the exact published PR HEAD is reconstructed from the GitHub connector (direct shell clone currently fails DNS), Git blob identity is checked for executable files, and LAB-066 plus LAB-065/LAB-062/LAB-063 regressions and compileall are actually executed. No merge claim should precede that evidence.

## Boundary
This is local namespace continuity and explicit relocation, not a remote filesystem, mount manager, backup service, cross-host identity protocol, forensic secure erasure, or whole-store rollback protection. Whole-store freshness remains delegated to LAB-034–037.
