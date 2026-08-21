# LAB-067 — Authenticated namespace retirement

LAB-066 intentionally leaves the old namespace untouched after relocation. That ordering is correct for crash safety but creates a new authority problem: current-generation scavenging must not silently gain authority to erase historical namespace objects.

The implemented lifecycle separates three decisions: (1) successor continuity must be current and fully audited, (2) an authenticated retirement permit must bind the exact old/new record IDs, generations, archive-chain commitment and policy generation, and (3) the old object must be strongly reacquired immediately before destructive cleanup. Missing, replaced, or unsupported strong reacquisition remains non-destructive.

## Real SignedPrunableHistory integration

- Before LAB-066's continuity migration is attempted, a durable PREPARED migration intent stores the authenticated predecessor record and exact migration permit.
- If the continuity CAS commits but the process dies before lineage finalization, restart reconciles that PREPARED intent against the authenticated current continuity row and repairs the exact predecessor→successor link.
- The predecessor becomes `RETIRED_PENDING`; the successor remains `ACTIVE`. A second migration is rejected while a predecessor is still pending, preventing hidden multi-generation retirement backlog.
- The SQL predecessor relation is not authority by itself: permit issuance re-verifies the predecessor record and the persisted authenticated LAB-066 migration permit, including its MAC, predecessor ID, successor generation and successor path.
- Retirement permits are issued only after the full currently reachable signed archive chain has been audited in the successor namespace. The permit binds that exact chain commitment plus current policy generation.
- Destructive cleanup opens the exact superseded namespace object with LAB-066/LAB-065 identity checks, unlinks only content-addressed archive files relative to that held directory FD, and fsyncs the directory. Unknown/replaced/non-regular namespace state fails closed.
- Authorization is persisted before cleanup and terminal receipt/watermark state afterward, making crash-after-authorize and crash-after-cleanup retryable and idempotent.
- LAB-063 continues to enumerate and delete only through the current-generation namespace handle; it never receives implicit authority over superseded generations.

## Audit findings fixed before integration

1. **Continuity-CAS crash gap:** restart could insert the current successor as a standalone ACTIVE row before reconciling a PREPARED intent, causing `INSERT OR IGNORE` to lose its predecessor. Reconciliation now verifies immutable record bytes and explicitly repairs predecessor/status/commitment.
2. **Multi-generation backlog:** allowing gen2→gen3 while gen1 remained `RETIRED_PENDING` could strand gen1 outside the one-step permit path. Relocation is serialized with predecessor retirement.
3. **Mutable predecessor relation:** `predecessor_record_id` was initially a mutable SQL column that permit issuance could trust. It is now only a cache/index; authority is re-derived from the persisted authenticated LAB-066 migration permit and continuity records. Regression tests cover both relation substitution and permit tampering.

## Executed evidence

Direct GitHub clone remained unavailable through DNS, so the exact executable branch sources were reconstructed through the GitHub connector and each reconstructed file was checked with `git hash-object` against its GitHub blob SHA before execution.

Observed passing matrix on the published LAB-067 head code:

- LAB-067 real signed-history integration + lineage-authority regressions: **16/16**.
- LAB-062 signed history/compaction regression suite: **15/15**.
- LAB-066 namespace-reacquisition protocol: **11/11**.
- LAB-066 signed-compaction restart/relocation integration: **8/8**.
- LAB-063 scavenger protocol: **9/9**.
- LAB-063 signed-compaction/scavenger integration: **5/5**.
- Total exact regression matrix: **64/64 passed**.
- `python -m compileall -q experiments`: passed.
- Earlier isolated LAB-067 reference suite: 10/10 passed and pathname-only unsafe baseline failed as expected.

Key reconstructed branch blobs included real retirement integration `f3dd566dcf2cee736c532ecbfee751018cd90303`, concrete `SignedPrunableHistory` composition `770f6e2a9c6ccd72eaf6fa40debe2aa1c36d0f23`, real integration tests `92c77e5758f662f4b2f9b1bae259b2e649ae7f52`, lineage tests `6918cdd8f92d6a917d23c8d41b161a20b468cfe7`, LAB-066 integration tests `241d2698669e9d273a6e7e1961f9a379fb7e4ea0`, and LAB-063 signed integration tests `f811739e3e8e2937574a0d29aa32000cc027b405`.

## Boundary

This work is storage reclamation only. Leaving an empty retired directory is intentional: removing the pathname itself without an unlink-by-handle primitive would reintroduce a pathname TOCTOU race. Deletion is not forensic erasure, backup retention, remote object-store GC, distributed consensus, or whole-store rollback freshness. Whole-store rollback freshness remains delegated to LAB-034–037.
