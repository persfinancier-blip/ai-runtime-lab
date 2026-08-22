# LAB-075 sink registry binding

Authenticated registry entries bind logical sink identity to a stable adapter profile digest, canonical endpoint origin, operation profile, and exact predecessor entry digest. New requests bind the exact registry entry in the same SQL authority database.

A rotated successor may reconcile an old UNKNOWN only when it directly names the historical entry digest. It may never re-execute that old reservation. CONFIRMED remains receipt-only.

The reference `adapter_digest` is a declared stable profile identity. Production integration should bind signed build/artifact identity. LAB-022–025 remain responsible for transport/DNS/TLS/proxy enforcement.
