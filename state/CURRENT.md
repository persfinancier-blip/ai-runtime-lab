# Current Lab State

Last updated: 2026-08-20

## Active objective

Extend the authenticated root+bundle correctness boundary from one serialized authority store to multi-replica distribution, catch-up, and split-view detection without falsely claiming distributed consensus.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-051.
- Completed Issue #98 / LAB-051.
- LAB-051 branch: `lab/051-bundle-authority-lifecycle`.
- PR creation for LAB-051 was blocked before execution by an external safety-status gate.
- `compare_commits` showed the branch ahead by 5, behind by 0, with exactly five added conflict-free files; the audited file-scoped set was integrated through normal Contents API fallback.
- Main LAB-051 protocol blob SHA: `de8a93e66e75f5be7dea4113ee3f8c34fe7be41e`, matching the branch protocol blob.
- Active next: Issue #99 / LAB-052 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-051 removed LAB-050's unauthenticated `rotate_authority()` trust boundary. Bundle signer keys now live inside a persisted root identity/version/epoch. Every new release binds the exact root digest/version/epoch and is verified against the active root re-read inside the publication transaction. Normal root rotation requires old-root and new-root thresholds; break-glass recovery uses a separately persisted recovery quorum and advances the authority epoch. Historical old releases remain attributable through their old authenticated root but that root cannot authorize new releases.

A separate audit found and fixed two defects before integration: recovery authority was initially caller-supplied after restart, and stored root JSON was initially trusted without rehashing against its durable digest.

## Evidence produced

- `experiments/ctv2_bundle_authority_lifecycle/`
- `research/2026-08-20-bundle-authority-lifecycle.md`
- Corrected deterministic suite: 12/12 passed.
- Real two-thread root-transition vs bundle-publication race serialized correctly at one SQLite write boundary.
- Unsafe self-authorized authority-swap baseline failed as expected.
- `python -m compileall -q experiments/ctv2_bundle_authority_lifecycle` passed.
- Primary external donor: TUF root update continuity requiring threshold authorization from both currently trusted root N and candidate root N+1, followed by durable root persistence.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- PR creation/merge endpoints may be externally blocked before execution; the repository's audited Contents API fallback remains valid for small conflict-free file-scoped changes.
- LAB-051 is a single-node serialization result only. It does not prove multi-replica convergence or consensus.
- HMAC remains a deterministic reference authenticator, not production key custody/HSM behavior.
- One published corrected test file had a Git blob SHA different from the local working test file despite matching observed content, so the run records 12/12 local execution plus remote content audit rather than falsely claiming exact-byte execution for that test file. The main protocol and unsafe seed did match exact Git blob identities.

## Exact next action

Start Issue #99 / LAB-052. Reuse LAB-040 witnessed split-view principles and LAB-050/051 exact root+bundle identities. Build `experiments/ctv2_bundle_replica_convergence/` with deterministic replicas that exchange authenticated heads/history, allow stale catch-up only through valid continuity, detect same-predecessor root or bundle forks, preserve restart watermarks, suppress duplicate replica/witness identities, and distinguish split-view detection/convergence rules from consensus/prevention. Include an unsafe isolated-replica baseline. Do not build a production network service or consensus protocol.

## Backlog

- #99 / LAB-052 — multi-replica root+bundle convergence and split-view detection — READY.
- Independent witness/gossip transport reliability and Byzantine consensus remain out of scope unless evidence makes them the next correctness bottleneck.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
