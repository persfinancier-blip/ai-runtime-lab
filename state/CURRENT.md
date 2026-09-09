# Current Lab State

Last updated: 2026-09-09

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-086 first.

Current-run capability/state probe:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available;
- PR #165 is confirmed `open`, `draft`, `mergeable=false` at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; no draft/merge-state change was attempted;
- retained prior evidence still says the strict/thaw subgate passed 31/31 distinct tests + compileall on pinned executable source; remaining LAB-086 gate is the complete LAB-080→086 real-ledger suite, unsafe expected-failure seed, full compileall and final security/reconciliation/conflict audit;
- no supported automated connector-to-local exact-source materialization path was observed, so no large security-critical source closure was manually/model reserialized and no new LAB-086 behavioral/compile PASS is claimed.

Completed the recorded distinct fallback and froze `CHECKPOINT_TIME_PROOFCLOSURE_ESCROW_ZK_RENEWAL_V1_FROZEN` in `research/2026-09-09-checkpoint-time-proofclosure-escrow-zk-renewal-v1.md`, main commit `b2c4034f8c14f330456220af64cafeb4b2bd3a70`; #178 comment `5594790935` records the result.

Key decisions:
- historical checkpoint assurance is evaluated against the exact witness/log policy epoch and original denominator; later witness retirement, compromise or quorum reduction cannot retroactively shrink historical quorum requirements;
- a survivable checkpoint package retains exact signed checkpoint bytes, historical policy/denominator, key/hash epochs and enough consistency ancestry/material to independently reproduce append-only continuity. A digest alone is insufficient;
- checkpoint GC requires positive authenticated dependency-closure evidence against a reproducible complete source frontier; empty lookup is never proof of zero dependencies and concurrent admission invalidates stale GC authorization;
- time-authority compromise creates a successor epoch rather than rewriting the old denominator. Populations/aggregation rules are committed before observing responses; authenticated intervals crossing an independently adjudicated compromise boundary remain ambiguous/fail-closed for consequential use;
- proof-closure parser/generator migration creates immutable interpreter/proof generations and uses a versioned canonical semantic corpus. Reproducible bytes/build relation are not semantic equivalence, and decision-relevant interpretation differences require explicit policy/equivalence adjudication;
- escrow share refresh is epoch-atomic and distinct from membership/threshold reconfiguration. Concurrent activated successors from one predecessor form `ESCROW_EPOCH_FORK`; no last-write-wins, no cross-epoch share mixing without explicit scheme proof, and refresh cannot erase prior compromise evidence;
- ZK parameter archives must preserve retrievable/verifiable ceremony transcript material, not only a digest. Contribution count is not contributor-independence evidence. A successor SRS/proof system protects successor proofs only; a recursive proof that merely proves an old proof verified still inherits the old assumptions and is not full renewal of the original statement;
- frozen 40-case RED-first matrix across checkpoint anti-GC, time-authority recovery, semantic parser/generator migration, escrow concurrency, and ZK transcript/parameter renewal.

Primary donors: RFC 9162; IETF Roughtime `draft-ietf-ntp-roughtime-19`; SLSA provenance/reproducibility guidance; Ethereum KZG ceremony/transcript; NIST threshold cryptography.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable in this run due DNS resolution failure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **checkpoint-package replica independence and positive recovery after archive-domain loss + time-source query/response censorship and challenge-delivery completeness + canonical semantic-corpus anti-omission/equivocation authority + escrow fork detection under partition/rejoin and partial share exposure + ZK transcript chunk/manifests cross-storage recovery and proof-renewal downgrade detection**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers checkpoint archival denominator/positive anti-GC, time-authority compromise recovery, semantic parser/generator migration corpus, escrow refresh concurrency/fork adjudication, and ZK transcript/parameter renewal; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
