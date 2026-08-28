# LAB-091 adoption lock envelope — WAL-mode probe

Date: 2026-08-28

## Question

The current LAB-091 first-adoption fix holds `BEGIN IMMEDIATE` on the guard-install connection, re-runs inherited LAB-082 `verify_durable()` through a sibling read connection, then installs v2/v3/v4 guards and validates existing mutable state before commit. The safety argument depends on the writer reservation preventing a lower/legacy connection from changing committed state between verification and guard commit.

A focused follow-up asked whether that property still holds under SQLite WAL mode, where readers and writers have different concurrency behavior than rollback-journal mode.

## Executed probe

A fresh file-backed SQLite database was switched to `PRAGMA journal_mode=WAL`. Three independent connections were opened:

1. connection A acquired `BEGIN IMMEDIATE`;
2. connection B successfully read the committed pre-adoption row while A held the writer reservation;
3. connection C attempted its own `BEGIN IMMEDIATE` followed by an UPDATE and failed with `OperationalError: database is locked`;
4. A installed a `BEFORE UPDATE` guard in the same transaction and committed;
5. C retried after commit and reached the new guard, which rejected the UPDATE with `IntegrityError`;
6. the original row remained unchanged.

Observed output:

```text
journal wal
reader old
writer_blocked OperationalError database is locked
postguard_blocked IntegrityError guarded
final old
```

## Result

The focused mechanism assumption used by `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger._install_guards()` survives WAL mode: `BEGIN IMMEDIATE` permits sibling readers but excludes a competing writer until guard installation commits. After commit, the newly installed trigger governs the next writer.

This supports the existing TOCTOU lock-envelope design and did not establish a new blocker.

## Evidence boundary

This is a standalone SQLite concurrency probe, not an exact-source PASS of the full LAB-080/LAB-082/LAB-091 candidate. PR #173 must remain draft until the real-stack adoption regressions, concurrency/crash/UNKNOWN behavior, LAB-087 composition, reentrancy/legacy-surface audit, and complete integration gate are clean.
