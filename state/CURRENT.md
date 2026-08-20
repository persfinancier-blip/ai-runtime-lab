# Current Lab State

Last updated: 2026-08-20

## Active objective

LAB-062 — integrate LAB-061 authenticated pruning/archive semantics directly with the real LAB-059/060 threshold-authenticated transition/checkpoint stack, proving compaction does not weaken signed-history verification.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-061.
- Completed Issue #113 / LAB-061.
- Merged PR #114 / LAB-061 as `22a0604c18100db1c79980d069ff2d4b4c0763d4`.
- Next: Issue #115 / LAB-062 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-061 built and integrated a deterministic local history-compaction reference model. A current authenticated checkpoint authorizes pruning. Exact canonical archive bytes and a content-addressed manifest are written/fsynced first; then one SQLite `BEGIN IMMEDIATE` transaction revalidates the checkpoint/archive, records the new compacted live-history base, registers archive metadata, and deletes the checkpointed prefix. Normal restart uses authenticated base + retained suffix; forensic archive audit separately recomputes archive SHA-256 and the cumulative prefix commitment.

Two audit defects were found and fixed before merge: (1) substituted archive `history_id` initially survived normal restart, so manifest content identity and current history binding are now recomputed; (2) compacted base initially trusted derived fields without re-verifying the persisted checkpoint, so restart now verifies exact checkpoint content/signature and base binding.

## Evidence produced

- `experiments/transition_history_pruning/core.py`
- `experiments/transition_history_pruning/live.py`
- `experiments/transition_history_pruning/compaction.py`
- `experiments/transition_history_pruning/protocol.py`
- `experiments/transition_history_pruning/tests/test_protocol.py`
- `experiments/transition_history_pruning/tests/unsafe_delete_first_expected_failure.py`
- `experiments/transition_history_pruning/README.md`
- `research/2026-08-20-authenticated-history-pruning.md`
- Corrected exact-source deterministic suite: 16/16 passed.
- Unsafe delete-first seed: failed as expected because restartability was destroyed.
- Compileall: passed.
- Remote/local Git blob identities matched for executable/test sources.
- Branch audit before merge: ahead 8 / behind 0; only new LAB-061 paths.
- PR #114 remote patch-audited and squash-merged as `22a0604c18100db1c79980d069ff2d4b4c0763d4`.

## Known blockers / constraints

- No active blocker.
- LAB-061 intentionally isolates compaction/archive semantics with a reduced transition model; it must not replace LAB-059/060 threshold-signature proof verification in production integration.
- Archive bytes are not runtime authority; missing/tampered archive bytes fail closed on explicit forensic audit. The SQL manifest and authenticated checkpoint remain part of the live restart boundary.
- SQL row deletion is not forensic erasure.
- Whole-store rollback/freshness remains delegated to LAB-034–037 external monotonic-anchor work.
- Local compaction is not distributed consensus or fork prevention.

## Exact next action

Start Issue #115 / LAB-062. Extend the existing LAB-059/060 signed-history/checkpoint implementation rather than duplicating it. Build a real threshold-signed root/recovery chain, checkpoint a fully verified prefix, apply LAB-061 archive+atomic-prune semantics, then restart from compacted base + retained suffix while reusing the same threshold-signature/payload/digest verification for every retained transition. Forensic archive audit must replay the same historical proof rules. Inject corrupted retained/archive signatures, payload/digest substitution, suffix gaps, checkpoint/base substitution, crash-before/inside-commit and timeout-after-commit. Prove second compaction after new signed transitions and terminal equivalence with full unpruned replay.

## Backlog

- #115 / LAB-062 — threshold-authenticated compaction integration and signed-history conformance — READY.
- Archive retention/orphan scavenging after successful compaction — candidate only after LAB-062 proves proof-preserving integration.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
