# LAB-066 — Restart namespace reacquisition

## Result
A restart loses LAB-065's held directory FD, so a pathname alone cannot recreate authority. The durable record is authenticated and generation-bound. Linux opaque handle evidence is captured when `name_to_handle_at` supports the filesystem; the configured pathname is reopened without following symlinks and compared to the durable object identity. `st_dev/st_ino` and mount IDs remain observations, not universal persistent identities.

The observed runtime can capture opaque handles but `open_by_handle_at` lacks the required `CAP_DAC_READ_SEARCH`; therefore a missing pathname with saved handle fails closed as `UNSUPPORTED_STRONG_REACQUISITION` rather than silently trusting path or bytes. The protocol nevertheless has an explicit `DETACHED_OBJECT_FOUND` classification when strong handle reopen is available and proves the saved directory object.

## Real integration
`SignedPrunableHistory` persists the continuity row and never recreates a missing authoritative archive directory on restart. Every consequential `require_namespace_authority()` refreshes strong reacquisition instead of treating startup success as a lease. LAB-065 directory-FD acquisition is bound back to the authenticated continuity record's `(st_dev, st_ino)`, closing the swap-between-reacquire-and-open race.

Archive publication receipts carry `namespace_generation`; artifact and manifest receipts must agree and must still equal the current authenticated generation before SQL commit. Migration after publication fences stale receipts.

LAB-063 scavenging is inside the same authority boundary. On a namespace-capable layer it enumerates, reads and unlinks through one held directory FD, rechecks configured-path binding before unlink, and refuses scan/destruction when continuity cannot be reacquired. This removes the lexical `Path.unlink()` TOCTOU left by a simple pre-operation check.

Authenticated relocation advances generation through exact predecessor/generation CAS. Before that CAS, the complete reachable committed archive chain is read and verified through the old held dirfd, durably copied and verified in the new held dirfd, and only then is the continuity record advanced under the same SQL write-serialization boundary used by compaction commit. A crash before CAS leaves redundant destination copies but preserves old authority; the old namespace is not automatically erased.

## Audit fixes
The separate audit found and corrected four cross-layer issues:
1. cached restart reacquisition was incorrectly usable as a long-lived lease;
2. scavenger authority checks still left a lexical-path unlink TOCTOU;
3. a newly acquired dirfd was not explicitly tied back to the authenticated continuity object;
4. relocation initially stranded already committed archives in the old namespace and would have broken forensic archive-chain audit.

Two regression tests also had stale expectations after the stronger fail-closed path moved errors earlier; they were updated to assert the stronger refusal rather than a specific later exception class.

## Validation
Direct shell clone was re-probed and still failed DNS resolution for `github.com`, so exact branch bytes were reconstructed through the GitHub connector. Reconstructed executable files were checked with `git hash-object` against GitHub blob SHA before execution.

Observed corrected regression result: **58/58 tests passed** across LAB-066 pure/integration, LAB-065 namespace tests/integration, LAB-062 signed-history compaction, and LAB-063 signed scavenging integration. `compileall` over the involved experiment packages also passed. The unsafe path+bytes design remains demonstrated by the corrected suite: byte-identical replacement is accepted by the unsafe baseline but rejected by the continuity protocol.

## Boundary
This is local namespace continuity and explicit relocation, not a remote filesystem, mount manager, backup service, cross-host identity protocol, forensic secure erasure, or whole-store rollback protection. Whole-store freshness remains delegated to LAB-034–037. A migrated-away namespace can contain redundant or crash-debris copies; retiring/scavenging those detached generations requires a separate authenticated lifecycle rather than reusing current-generation authority.
