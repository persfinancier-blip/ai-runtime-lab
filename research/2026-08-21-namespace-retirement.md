# LAB-067 — Authenticated namespace retirement

LAB-066 intentionally leaves the old namespace untouched after relocation. That ordering is correct for crash safety but creates a new authority problem: current-generation scavenging must not silently gain authority to erase historical namespace objects.

The reference model separates three decisions: (1) successor continuity must be current and fully audited, (2) an authenticated retirement permit must bind the exact old/new record IDs, generations, archive-chain commitment and policy generation, and (3) the old object must be strongly reacquired immediately before destructive cleanup. Missing, replaced, or unsupported strong reacquisition remains non-destructive.

## Real SignedPrunableHistory integration

The draft PR now integrates this boundary with LAB-066 `SignedPrunableHistory` and LAB-063 rather than leaving it as an isolated model.

- Before LAB-066's continuity migration is attempted, a durable PREPARED migration intent stores the authenticated predecessor record and exact migration permit.
- If the continuity CAS commits but the process dies before lineage finalization, restart reconciles that PREPARED intent against the authenticated current continuity row and repairs the exact predecessor→successor link.
- The predecessor becomes `RETIRED_PENDING`; the successor remains `ACTIVE`. A second migration is rejected while a predecessor is still pending, preventing hidden multi-generation retirement backlog.
- Retirement permits are issued only after the full currently reachable signed archive chain has been audited in the successor namespace. The permit binds that exact chain commitment plus current policy generation.
- Destructive cleanup opens the exact superseded namespace object with LAB-066/LAB-065 identity checks, unlinks only content-addressed archive files relative to that held directory FD, and fsyncs the directory. Unknown/replaced/non-regular namespace state fails closed.
- Authorization is persisted before cleanup and terminal receipt/watermark state afterward, making crash-after-authorize and crash-after-cleanup retryable and idempotent.
- LAB-063 continues to enumerate and delete only through the current-generation namespace handle; it never receives implicit authority over superseded generations.

A separate audit found and fixed a crash-gap defect: restart could insert the current successor as a standalone ACTIVE row before reconciling a PREPARED intent, causing `INSERT OR IGNORE` to lose its predecessor. The concrete integration now checks immutable record bytes and explicitly repairs predecessor/status/commitment on reconciliation.

A second audit found that allowing another relocation while an older generation remained `RETIRED_PENDING` could strand that generation outside the one-step permit path. The current protocol therefore serializes relocation with retirement: retire the pending predecessor first, then advance again.

## Evidence status

The earlier isolated authority model passed 10/10 deterministic tests and its pathname-only unsafe seed failed as expected. The real integration adds tests for signed-chain audit, restart receipt persistence, continuity-CAS crash reconciliation, crash-after-authorize, crash-after-cleanup, byte-identical replacement, symlink replacement, unavailable strong reopen, incomplete successor chain, stale policy, current-generation protection, and LAB-063 generation fencing.

Those new exact branch bytes have not yet been executed in this runtime because direct GitHub clone is currently unavailable through DNS. Therefore the PR remains draft and is not completion-eligible until connector-reconstructed exact-source execution and the LAB-066/LAB-063 regression suite pass.

## Boundary

This work is storage reclamation only. Leaving an empty retired directory is intentional: removing the pathname itself without an unlink-by-handle primitive would reintroduce a pathname TOCTOU race. Deletion is not forensic erasure, backup retention, remote object-store GC, distributed consensus, or whole-store rollback freshness. Whole-store rollback freshness remains delegated to LAB-034–037.
