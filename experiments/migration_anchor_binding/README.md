# LAB-079 — migration checkpoint ↔ monotonic anchor binding

This experiment composes LAB-078 migration identity with the existing LAB-036 authenticated monotonic-anchor catch-up surface. The migration SQLite DB keeps the local sequence/binding; the external provider keeps the monotonic position. A whole-store rollback rewinds the DB sequence but cannot rewind the external position, so restart fails closed.

States are intentionally two-phase: a LAB-078 checkpoint may exist while its anchor binding is `PENDING`. It becomes consequential only after authenticated catch-up confirms the exact migration identity. `UNKNOWN` anchor outcomes are reconciled by the stable request identity already supplied by LAB-036.

This is rollback detection/catch-up, not distributed consensus, backup durability, or a new anchor trust root.
