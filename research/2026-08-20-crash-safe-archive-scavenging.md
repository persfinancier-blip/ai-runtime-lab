# LAB-063 — crash-safe archive retention

LAB-062 correctly exports archive bytes before SQL prune commit, so a crash can leave valid-looking filesystem orphans. The safe rule is mark from authenticated current compaction state through the complete `previous_archive_id` chain, then sweep only content-addressed names that remain unreachable after a durable grace generation. Reachability is rechecked under the write lock immediately before unlink, so a compaction commit cannot race the final decision. UNKNOWN outcomes are reconciled by rereading SQL authority. Invalid/substituted content-address pairs fail closed instead of being silently erased.

This is storage reclamation, not forensic erasure. It does not define legal retention, backup durability, secure deletion, remote object-store lifecycle, distributed garbage collection, or whole-store freshness; whole-store freshness remains delegated to LAB-034–037.
