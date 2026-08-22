# LAB-079 — Migration checkpoint monotonic-anchor composition

LAB-078 authenticates the legacy→threshold migration inside SQLite, but a complete restore of a pre-migration database can erase both checkpoint and local evidence while remaining internally valid. LAB-079 therefore composes, rather than replaces, the LAB-034–037 boundary.

The implementation reuses LAB-036 authenticated provider observations/catch-up semantics. The local registry DB stores a monotonically increasing migration binding sequence plus the exact checkpoint identity/cutoff/terminal authority digest. The external anchor stores the corresponding position. Consequential restart requires exact equality and a fresh authenticated observation. If the DB is restored behind the external position, rollback is detected. If SQL committed but anchor did not advance, migration remains non-consequential until catch-up. Timeout-after-anchor-commit uses the same stable request identity for reconciliation and cannot double-advance.

A higher unexplained external position fails closed in this slice rather than being treated as harmless. A future shared-ledger composition may authorize later positions only by proving every intervening intent.
