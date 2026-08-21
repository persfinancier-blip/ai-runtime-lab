# LAB-067 — Authenticated namespace retirement

LAB-066 intentionally leaves the old namespace untouched after relocation. That ordering is correct for crash safety but creates a new authority problem: current-generation scavenging must not silently gain authority to erase historical namespace objects.

The first reference slice separates three decisions: (1) successor continuity must be current and fully audited, (2) an authenticated retirement permit must bind the exact old/new record IDs, generations, archive-chain commitment and policy generation, and (3) the old object must be strongly reacquired immediately before destructive cleanup. Missing or unsupported strong reacquisition remains non-destructive.

A retirement receipt is idempotent and generation/watermark bound. The unsafe baseline demonstrates that pathname-only cleanup can delete a current namespace.

## Current boundary

This slice is deliberately not yet integrated into real `SignedPrunableHistory` / LAB-063. Completion still requires durable lineage/retirement state in the real SQL store, strong reacquisition of the superseded LAB-066 continuity object, verification of the full reachable archive chain in the successor namespace, restart/crash semantics, and current-generation protection under the real scavenger boundary.

This work is storage reclamation only. It is not forensic erasure, backup retention, remote object-store GC, distributed consensus, or whole-store rollback freshness.
