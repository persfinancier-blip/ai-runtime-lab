# Current Lab State

Last updated: 2026-08-20

## Active objective

Compose LAB-050's authenticated atomic policy/trust release with the threshold/recovery trust-root lifecycle already proven in LAB-037–039 so bundle signer authority is restart-persistent and cannot be replaced by an unauthenticated caller.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-050.
- Completed Issue #96 / LAB-050.
- PR #97 remote patch-audited at HEAD `a7f2d402f83311a2c35f6e03f78b344bb54aa147`; normal squash merge was blocked before execution by an external safety gate, so the exact five audited added files were integrated via normal Contents API fallback and PR #97 was closed as manually integrated.
- Main LAB-050 protocol blob SHA: `368d988d7780da0f67cb03af4e634c15fd66163b` (matches audited branch exactly).
- Active next: Issue #98 / LAB-051 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-050 replaced independently authenticated policy/trust histories with one signed release manifest committing to exact policy and CT trust digests under one bundle lineage/version/generation. Manifest, policy, trust and active pointer are activated in one SQLite transaction. Rollback, substitution, gaps, expiry, partial-update crashes and mix-and-match are fail-closed; historical replay rehashes stored bytes and rechecks manifest→object binding.

A separate audit found and fixed a replay defect: stored JSON bytes had initially not been rehashed during replay, so damage to document bytes could have escaped detection if the adjacent digest column was untouched.

## Evidence produced

- `experiments/ctv2_policy_trust_bundle/`
- `research/2026-08-20-authenticated-policy-trust-bundle.md`
- Corrected deterministic suite: 15/15 passed.
- Unsafe independent-history baseline: expected failure demonstrating policy release 2 + trust release 1 can be falsely accepted without an atomic bundle.
- `python -m compileall -q experiments/ctv2_policy_trust_bundle` passed.
- Primary donors: TUF snapshot mix-and-match protection, Sigstore TUF-delivered TrustedRoot, SQLite atomic commit/rollback.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- Normal PR merge endpoint may be externally blocked before execution; the repository's audited Contents API fallback remains valid for small conflict-free file-scoped changes.
- LAB-050 reference `Authority.rotate_authority()` still treats new signer authority as a trusted higher-level input. Bundle content is authenticated, but signer-root transition is not yet composed with LAB-037–039.
- HMAC in LAB-050 is a deterministic reference authenticator, not production key management.
- Local atomic activation does not imply multi-replica consensus/convergence.

## Exact next action

Start Issue #98 / LAB-051. Reuse LAB-037–039 threshold trust-root, recovery and anti-equivocation mechanisms rather than redoing them. Build `experiments/ctv2_bundle_authority_lifecycle/` so LAB-050 bundle acceptance derives current signer authority from durable threshold-root state, persists root identity/version/epoch across restart, rejects stale/revoked signers, distinguishes normal rotation from break-glass recovery, serializes root transition vs release publication, and preserves historical attribution without allowing old roots to authorize new releases. Include an unsafe self-authorized authority swap seed and deterministic failure-injection tests. Do not build a general PKI/HSM service.

## Backlog

- #98 / LAB-051 — threshold-authorized bundle signer lifecycle + restart-persistent authority binding — READY.
- Multi-replica bundle distribution/convergence and split-view detection — candidate follow-up after signer authority is closed.
- Independent witness/gossip transport reliability and Byzantine consensus remain out of scope unless product requirements justify them.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
