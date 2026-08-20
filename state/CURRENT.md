# Current Lab State

Last updated: 2026-08-20

## Active objective

Extend the authenticated multi-replica root+bundle boundary from “detect divergence once complete views meet” to durable gossip/exchange evidence that can distinguish partition/delay, stale or selectively frozen views, and actual split-view evidence without false equivocation claims from silence alone.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-052.
- Completed Issue #99 / LAB-052.
- LAB-052 branch: `lab/052-bundle-replica-convergence`.
- LAB-052 PR: #100.
- LAB-052 merge SHA: `7e064ee74d599d4905820cae7552630757b6e4a3`.
- Active next: Issue #101 / LAB-053 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-052 built a deterministic authenticated root+bundle replica model. Replicas validate complete root/bundle event continuity, persist a durable head/history watermark, catch up only when the candidate is an authenticated strict extension, reject shorter rollback input for current service, and emit split-view evidence for incomparable authenticated histories. Duplicate/conflicting replica identities cannot inflate evidence quorum. The model explicitly demonstrates that two locally valid forks can exist while replicas are isolated; detection begins only when independent views meet, so the result is not presented as consensus or fork prevention.

A separate audit found and fixed a lineage-authorization defect: the first version accepted a successor root signed by any known registry root key. The corrected model additionally requires the successor signer to be authorized by the predecessor authority.

## Evidence produced

- `experiments/ctv2_bundle_replica_convergence/`
- `research/2026-08-20-bundle-replica-convergence.md`
- Corrected deterministic suite: 14/14 passed.
- Unsafe isolated-replica baseline failed as expected: two incompatible locally authenticated forks were both accepted before comparison.
- `python -m compileall -q experiments/ctv2_bundle_replica_convergence` passed.
- Remote Git blob identities for the executable protocol, corrected tests, unsafe seed, and README matched the locally executed files.
- `compare_commits` before integration: ahead by 5, behind by 0, exactly five new files.
- PR #100 remote patch-audited and squash-merged as `7e064ee74d599d4905820cae7552630757b6e4a3`.
- Primary external donors: RFC 9162 split-view/gossip boundary and TUF monotonic rollback/continuity rules.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- PR creation/merge endpoints can occasionally be externally blocked before execution; the repository's audited Contents API fallback remains valid for small conflict-free file-scoped changes.
- LAB-052 does not provide Byzantine consensus, leader election, quorum commit, reliable gossip delivery, or partition-tolerant liveness.
- Silence/non-delivery alone is not evidence of split view. An isolated fork can remain undetected indefinitely if independent views never cross a comparison path.
- HMAC remains a deterministic reference authenticator, not production key custody/HSM behavior.

## Exact next action

Start Issue #101 / LAB-053. Build `experiments/ctv2_bundle_gossip_evidence/` on LAB-052 identities. Persist authenticated peer/view observations with stable observation identity and last-seen watermarks. Classify timely catch-up, missing/delayed exchange (`UNKNOWN/PARTITIONED`), authenticated stale view after independently observed newer same-lineage evidence (`FREEZE_SUSPECTED`), and incomparable authenticated histories (`SPLIT_VIEW`). Replayed/duplicate exchange records must not refresh evidence; restart must preserve peer observation state; trusted-clock rollback must fail closed. Include an unsafe timeout-means-equivocation baseline. Do not build a production gossip network or consensus protocol.

## Backlog

- #101 / LAB-053 — gossip evidence durability and partition/freeze classification — READY.
- Reliable gossip transport, Byzantine consensus, and fork prevention remain out of scope unless LAB-053 evidence makes them the next correctness bottleneck.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
