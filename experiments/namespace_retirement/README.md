# LAB-067 namespace retirement

A retirement permit is authenticated and binds the predecessor record, successor record, both namespace generations, a fully audited successor archive-chain commitment, and policy generation. Cleanup is allowed only after the successor is still current and the exact old namespace object is strongly reacquired.

The draft integration now extends real LAB-066 `SignedPrunableHistory`: relocation persists a PREPARED intent before continuity migration, restart can repair predecessor→successor lineage after a crash gap, the old generation becomes `RETIRED_PENDING`, authorization is persisted before cleanup, and retirement finishes with an idempotent durable receipt/watermark. LAB-063 remains scoped to the current generation and cannot implicitly delete old-generation files.

A second relocation is rejected while a predecessor is still retirement-pending. This deliberately keeps the authority chain linear until a future design proves a safe multi-generation retirement queue.

Exact-source execution of the new integration plus LAB-066/LAB-063 regressions remains the merge gate. This is storage reclamation, not secure/forensic erasure, backup retention, remote GC, or cross-host object identity.
