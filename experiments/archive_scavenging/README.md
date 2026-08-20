# LAB-063 archive scavenging

Reachability comes from authenticated LAB-062 SQL archive-chain state, never filenames. Unreferenced content-addressed files become candidates, survive a durable generation grace period, and are rechecked under a SQL write lock immediately before unlink. UNKNOWN compaction outcomes are reconciled from authoritative SQL state.

Validation includes the isolated mark/sweep matrix plus integration against the real `SignedPrunableHistory`: real `fail_after_archive=True` orphan creation/reclamation, committed-UNKNOWN protection, multi-archive reachability, and a real compaction-vs-GC race. The race invariant is that a committed compaction base never references a missing archive; if GC wins before commit, signed live history remains intact and restartable.

Cleanup is storage reclamation, not forensic erasure, backup retention, secure deletion, remote lifecycle management, or distributed GC.
