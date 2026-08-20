# Current Lab State

Last updated: 2026-08-20

## Active objective

Advance from time-aware authenticated CT log eligibility to an authenticated/versioned compliance-policy lifecycle so historical decisions are reproducible against the exact policy generation that governed them, while current/future evaluations cannot downgrade to stale weaker policy.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-048.
- Completed Issue #92 / LAB-048; PR #93 remote patch-audited and squash-merged as `c6eb43653447bdf7bc6916e0dbe4e4ccbecd101e`.
- Active next: Issue #94 / LAB-049 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-048 added authenticated temporal lifecycle/operator intervals over LAB-047 history. Historical mode evaluates lifecycle at evidence time so later retirement/distrust does not retroactively erase earlier attribution; current-policy mode evaluates lifecycle at policy time so old evidence cannot bypass a newer ineligibility transition. Operator identity is always resolved at evidence time. Caller-selected stale snapshots, frozen trust metadata, conflicting temporal events, and future-dated evidence fail closed.

A separate audit fixed two defects before publication: operator changes are now bound to explicit authenticated `operator_since` timestamps rather than inferred snapshot-publication time, and `evidence_time > policy_time` is rejected.

## Evidence produced

- `experiments/ctv2_temporal_log_eligibility/`
- `research/2026-08-20-ctv2-temporal-log-eligibility.md`
- Corrected local deterministic suite: 15/15 passed.
- Unsafe stale-snapshot baseline: expected failure demonstrating a caller-selected old ACTIVE snapshot can bypass later retirement.
- `python -m compileall -q experiments/ctv2_temporal_log_eligibility` passed.
- Exact remote protocol/test/unsafe Git blob SHAs matched the locally executed source.
- PR #93 remote patch audit completed before integration.
- Merge SHA: `c6eb43653447bdf7bc6916e0dbe4e4ccbecd101e`.
- Fresh primary-source recheck: current Chromium CT metadata models timestamped log states and operator history; current Chromium policy resolves operator by timestamp and rejects stale log data; current log-list data uses `start_inclusive`/`end_exclusive` temporal intervals. RFC 9162 leaves concrete client policy local. RFC 5280 was used as a comparison temporal-validity mechanism and explicitly uses inclusive certificate validity endpoints.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- LAB-048 is a reference temporal eligibility policy, not Chrome/browser certificate compliance policy.
- LAB-047 authentication remains upstream authority; LAB-048 does not itself authenticate arbitrary snapshot objects.
- LAB-047's minimal schema did not expose operator-history timestamps, so LAB-048 makes authenticated `operator_since` explicit instead of guessing from current ownership.
- The compliance `Policy` object itself is still an unversioned trusted input. That is now the highest-value correctness gap.

## Exact next action

Start Issue #94 / LAB-049. Research authenticated/versioned policy lifecycle semantics using TUF signed-metadata version/expiry/rollback protections, current Chromium CT configuration/update mechanisms, and one additional primary-source temporal-policy mechanism. Build `experiments/ctv2_temporal_policy_lifecycle/` integrating with LAB-048. The evaluator must derive the authoritative policy snapshot from time, persist exact policy identity/version/generation/effective interval, reject stale-policy downgrade/substitution/mix-and-match, and support deterministic replay of historical decisions without allowing future policy transitions to rewrite them.

## Backlog

- #94 / LAB-049 — authenticated temporal compliance-policy lifecycle and decision replay — READY.
- Independent witness/gossip transport reliability and Byzantine consensus remain intentionally out of scope unless later product requirements justify them.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
