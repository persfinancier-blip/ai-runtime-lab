# LAB-063 — crash-safe archive retention

LAB-062 correctly exports archive bytes before SQL prune commit, so a crash can leave valid-looking filesystem orphans. The safe rule is mark from authenticated current compaction state through the complete `previous_archive_id` chain, then sweep only content-addressed names that remain unreachable after a durable grace generation. Reachability is rechecked under the SQL write lock immediately before unlink, so the final destructive decision is serialized against the LAB-062 compaction commit. UNKNOWN outcomes are reconciled by rereading SQL authority. Invalid/substituted content-address pairs fail closed instead of being silently erased.

The first prototype was intentionally not accepted after remote audit because it exercised only a compact fake LAB-062-shaped layer. The corrected slice now uses LAB-062's real `ArchiveManifest` parser and `_verify_manifest_identity()` history binding when operating on `SignedPrunableHistory`, while retaining the fake layer only for isolated algorithm tests.

Observed integration evidence in this run:

- real `compact(..., fail_after_archive=True)` produced an uncommitted content-addressed orphan; after two retention generations it was deleted while the five signed live transitions remained restartable;
- real `compact(..., timeout_after_commit=True)` produced a committed archive which was never classified as a candidate;
- two sequential real compactions left both the current and historical archive reachable through the authenticated `previous_archive_id` chain;
- the real compaction-vs-GC race was repeated 20 times; every run preserved the invariant that an authoritative committed base never referenced missing archive files. If GC wins before the compaction commit, the signed live history remains authoritative and restartable; if compaction wins, the archive is protected by reachability.

The preferred production rule is therefore not "delete old-looking files" but `authenticated mark -> durable grace -> write-locked recheck -> unlink`. File names and directory age are never authority.

This is storage reclamation, not forensic erasure. It does not define legal retention, backup durability, secure deletion, remote object-store lifecycle, distributed garbage collection, or whole-store freshness; whole-store freshness remains delegated to LAB-034–037.

## Newly exposed boundary

LAB-062 `_atomic_file()` fsyncs file contents before `os.replace`, but the experiment has not yet proven parent-directory fsync / power-loss durability for the renamed archive files before SQL commits a reference to them. Process-crash correctness is covered; sudden host/power-loss durability of the filesystem publication boundary remains a separate correctness question.
