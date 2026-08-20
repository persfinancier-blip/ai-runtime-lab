# Current Lab State

Last updated: 2026-08-20

## Active objective

Remove the remaining cross-observer wall-clock trust assumption from gossip freeze attribution by replacing it with authenticated causal ordering/sequence evidence and explicit observer-credibility/quorum rules.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-053.
- Completed Issue #101 / LAB-053.
- LAB-053 branch: `lab/053-gossip-evidence`.
- LAB-053 PR: #102.
- LAB-053 merge SHA: `e0edca297d80c96fccca5a1ded7a948ce3520bd2`.
- Active next: Issue #103 / LAB-054 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-053 built durable observer-signed gossip evidence over LAB-052-style authenticated histories. It distinguishes fresh current state, ordinary missing/delayed exchange (`UNKNOWN_PARTITIONED`), an older authenticated prefix served after independently observed newer same-lineage evidence (`FREEZE_SUSPECTED`), and incompatible authenticated histories (`SPLIT_VIEW`). Silence/timeout alone never becomes equivocation evidence. Duplicate replay of the same signed view does not refresh freshness. Restart preserves observations and trusted-clock rollback fails closed.

A separate audit found and fixed a consequential evidence-authority defect: persisted incident labels were initially trusted during classification, so storage corruption could fabricate `SPLIT_VIEW`. The final implementation verifies observer-signed observations and deterministically rebuilds incident attribution from those observations before consequential classification.

## Evidence produced

- `experiments/ctv2_bundle_gossip_evidence/`
- `research/2026-08-20-gossip-evidence-partition-freeze.md`
- Corrected exact published-source suite: 13/13 passed.
- `python -m compileall -q experiments/ctv2_bundle_gossip_evidence` passed.
- Unsafe timeout=>split baseline failed as expected.
- Published protocol blob matched locally executed source: `0dbf7e1228f3cba61bb0bb069c88a9b229b810b8`.
- Published corrected test blob matched locally executed source: `c0caed5f0a3328cdc38c3fc0bb513275ef3cbeb8`.
- PR #102 remote patch-audited and squash-merged as `e0edca297d80c96fccca5a1ded7a948ce3520bd2`.
- Primary donors: RFC 9162 asynchronous/split-view boundary, TUF freeze/rollback semantics, transparency-dev witness/C2SP witness durable checkpoint progression.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- PR creation/merge endpoints can occasionally be externally blocked before execution; audited file-scoped Contents API fallback remains permitted under AGENTS.md.
- LAB-053 uses one trusted aggregator receipt clock. Observer signatures authenticate authorship, not independent wall-clock truth; distributed cross-observer ordering is therefore the next correctness gap.
- Silence/non-delivery remains unknowable availability state, not proof of malice.
- Reliable gossip delivery, Byzantine consensus, and fork prevention remain out of scope.

## Exact next action

Start Issue #103 / LAB-054. Build `experiments/ctv2_bundle_causal_gossip/` so freeze suspicion is derived from authenticated causal sequence/predecessor evidence rather than cross-observer wall-clock ordering. Test observer replay/rollback, observer fork/equivocation, malicious timestamp manipulation, duplicate identity/quorum inflation, independent corroboration, restart watermarks, and continued UNKNOWN classification for partitions. Keep causal detection/attribution separate from consensus or reliable delivery.

## Backlog

- #103 / LAB-054 — causal gossip ordering and observer-credibility conformance — READY.
- Reliable gossip transport, Byzantine consensus, and fork prevention remain out of scope unless evidence makes them the next correctness bottleneck.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
