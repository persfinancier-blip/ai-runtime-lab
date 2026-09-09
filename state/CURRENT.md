# Current Lab State

Last updated: 2026-09-09

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current connector read confirms `open`, `draft=true`, `mergeable=false`. Keep draft and do not merge without the exact retained gate.
- Other open drafts remain: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`, the LAB-086 exact gate manifest, and PR #165; resumed LAB-086 first.

Current-run capability/state:
- Direct exact-source transport was re-probed with `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` and failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- The exact manifest at `research/2026-08-27-lab086-exact-gate-manifest.md` reconfirms pinned executable/test snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` and requires each reconstructed file to match its pinned Git blob via `git hash-object` before execution.
- Connector retrieval of pinned source was positively probed: `experiments/asymmetric_break_glass_history/strict_fence.py` at the pinned commit is readable as exact base64/UTF-8 connector content. The connector, however, exposes no supported direct materialization primitive into the local executor in this run. Manual/model reserialization of the large security-critical closure remains disallowed because it would weaken the retained byte-exact gate.
- Therefore the complete LAB-080→086 closure still has not been materialized/executed locally in this run. No new LAB-086 behavioral/unsafe-seed/compileall PASS is claimed.
- PR #165 remains open/draft/mergeable=false; no draft/merge state was changed.

Completed the recorded distinct fallback and froze `WITNESS_ANTI_CAPTURE_VERIFIER_POISON_SCHEMA_INTERSECTION_RETENTION_SPLIT_PQ_SVCB_V1_FROZEN` in `research/2026-09-09-witness-anti-capture-verifier-poison-schema-intersection-retention-split-pq-svcb-v1.md`, main commit `df2f215e1e7eba44ea60ef0406c34683723ab605`; #178 comment `5608230364` records the result.

Key decisions:
- `SUCCESSOR_QUORUM_AVAILABLE != SUCCESSOR_QUORUM_LEGITIMATE`: witness recovery binds predecessor generation/root, proposed membership, denominator, threshold and activation boundary before observing successor availability; successor agreement cannot retroactively repair degraded predecessor history.
- `CORPUS_HASH_MATCHES != CORPUS_TRUSTWORTHY`: reproducible verifier corpora bind generator source/dependencies, oracle/version, coverage commitments, build provenance and corpus generation; reproducibility alone does not defeat deterministic poisoning or correlated builders/caches.
- `EACH_DISCLOSURE_UNLINKABLE != DISCLOSURE_SEQUENCE_UNLINKABLE`: privacy-preserving schema gossip needs a sequence/window disclosure budget against adaptive intersection; mandatory security/common-control edges remain verifiable or the result is `INSUFFICIENT_DISCLOSURE`, never invented independence.
- `VALID_HOLD_SIGNATURE != CURRENT_HOLD_AUTHORITY`: hold/release/revocation/authority rollover are versioned lifecycle events; conflicting valid current-generation views yield `RETENTION_AUTHORITY_SPLIT_VIEW` and destructive deletion fails closed. Runtime does not infer legal authority.
- `SAME_ORIGIN_NAME != SAME_RESUMPTION_AUTHORITY`: DNS HTTPS/SVCB or multi-CDN routing continuity does not imply continuity of ticket authority, ECH/backend identity, anti-replay ownership, or PQ/hybrid policy. Failover may allow a fresh compliant handshake while unsafe resumption/0-RTT remains rejected.
- Frozen 40-case RED-first matrix across witness recovery anti-capture, verifier-corpus poisoning, schema-gossip intersection privacy, retention authority split-view, and PQ/ECH multi-CDN resumption.

Primary donors: RFC 9162; SLSA v1.2/v1.1; W3C Data Integrity BBS Cryptosuites; NIST SP 800-53 AU-11; RFC 9460; RFC 9849; RFC 9846/TLS 1.3.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read exact pinned blobs but this run has no supported connector-to-local-filesystem materialization primitive. Manual/model byte reconstruction of the large closure is prohibited by the retained gate.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe for a **supported non-model materialization path** for the pinned connector bytes at `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` (for example, any newly available connector file download/mount/resource-to-file operation). If available, reconstruct the manifest-listed implementation closure plus every `test_*.py` under `experiments/asymmetric_break_glass_history/tests` and the pinned LAB-085 fixture helper; verify every local file with `git hash-object` against the pinned tree/blob SHA before import; execute every normal LAB-086 real-schema test; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not spend another run manually copying connector payloads into the executor: that violates the retained exact-source discipline. If no supported non-model materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **witness recovery split-brain activation/finalization + verifier corpus semantic-coverage mutation testing and oracle compromise recovery + privacy-budget composition across schema-gossip verifiers + retention authority timestamp/freshness and offline-root recovery + PQ/ECH/SVCB downgrade resistance under DNS cache poisoning, authenticated DNS transitions and heterogeneous client capability rollout**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers witness anti-capture recovery, corpus provenance/poisoning, sequence-level schema-gossip privacy, retention authority split-view and PQ/ECH multi-CDN resumption; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
