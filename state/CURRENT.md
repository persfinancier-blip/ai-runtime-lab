# Current Lab State

Last updated: 2026-09-09

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts remain: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and PR #165; resumed LAB-086 first.

Current-run capability/state:
- PR #165 is still `open`, `draft`, `mergeable=false` at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; no draft/merge-state change was attempted.
- Direct exact-source transport was re-probed with `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` and failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available and were used for durable research/state writes.
- No new LAB-086 behavioral/compile PASS is claimed. The complete exact real-ledger closure, unsafe expected-failure seed, compileall and final security/reconciliation/conflict audit still have not executed in this run.

Completed the recorded distinct fallback and froze `FENCE_ROOT_SEMANTIC_SCHEMA_TOMBSTONE_PQ_BINDING_V1_FROZEN` in `research/2026-09-09-fence-root-semantic-schema-tombstone-pq-binding-v1.md`, main commit `383a250e005da055ab7acf029def607920822d22`; #178 comment `5605926004` records the result.

Key decisions:
- `RESTORED_STORAGE != RESTORED_WRITE_AUTHORITY`: snapshot/rollback recovery must preserve or independently re-establish the highest accepted fencing floor; successor floor recovery does not repair uncertainty in compromised predecessor history.
- `VERIFIER_A_ACCEPTS && VERIFIER_B_ACCEPTS != SAME_SEMANTICS`: dual-verifier/hash migration requires equality of canonical semantic projections plus an authenticated H1/H2 bridge. Process count is not verifier independence when parser/canonicalizer/build failure domains are shared.
- `SIGNED_SCHEMA != UNIQUE_SCHEMA_VIEW`: security-schema registries can equivocate with individually valid signatures, so generations need authenticated append-only lineage/cross-view consistency; unknown mandatory/critical fields fail closed rather than downgrade to optional.
- `TOMBSTONE_GCED != REINTRODUCTION_IMPOSSIBLE`: deletion GC requires authenticated witness coverage of the versioned restore/replay-capable copy-domain universe, including backups, queues, derived stores and DR images.
- `TICKET_DECRYPTS != CURRENT_CONNECTION_AUTHORIZED`: TLS/PQ resumption re-evaluates current SNI/server identity, ALPN, authorization/policy epoch and current PQ/hybrid floor. Certificate coverage across two names does not imply shared ticket/application authority.
- Frozen 40-case RED-first matrix across fence-floor recovery, semantic verifier/hash migration, schema split-view, tombstone GC and PQ/TLS resumption binding.

Primary donors: etcd disaster recovery revision bump/mark-compacted; RFC 8785 JCS; RFC 8949 CBOR; RFC 9162 transparency consistency; NIST SP 800-88r2; RFC 9846/RFC 8446 TLS 1.3 resumption/0-RTT; RFC 7301 ALPN.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`. The connector can read/write repository content but does not expose an automated byte-exact connector-to-local materialization path for the complete executable closure.
- Manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe for an automated byte-exact source-materialization path. If available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR-head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **external monotonic fence-floor witness quorum and restore-gap reconstruction + canonical semantic-projection versioning across parser/library deprecation + schema-registry witness/gossip retention and root rollover + tombstone-GC proof survivability after backup-provider retirement + PQ/TLS resumption authorization across ECH/virtual-host routing, ALPN changes and service-mesh ticket-key sharing**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers restore-safe fence floors, semantic projection/hash migration, security-schema split-view, tombstone-GC completeness and current-context PQ/TLS resumption authorization; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
