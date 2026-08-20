# LAB-063 archive scavenging

Reachability comes from authenticated LAB-062 SQL archive-chain state, never filenames. Unreferenced content-addressed files become candidates, survive a durable generation grace period, and are rechecked under a SQL write lock immediately before unlink. UNKNOWN compaction outcomes are reconciled from authoritative SQL state.

Cleanup is storage reclamation, not forensic erasure, backup retention, secure deletion, remote lifecycle management, or distributed GC.
