# Current Lab State

Last updated: 2026-09-09

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts remain: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-086 first.

Current-run capability/state:
- Direct exact-source transport was re-probed with `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` and failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available and were used for durable research/state writes.
- No new LAB-086 behavioral/compile PASS is claimed. The complete exact real-ledger closure, unsafe expected-failure seed, compileall and final security/reconciliation/conflict audit still have not executed in this run.
- Open PR set remains #165/#172/#173/#175/#177; no draft/merge state was changed.

Completed the recorded distinct fallback and froze `FENCE_WITNESS_SEMANTIC_SCHEMA_GOSSIP_TOMBSTONE_PQ_ECH_V1_FROZEN` in `research/2026-09-09-fence-witness-semantic-version-schema-gossip-tombstone-survivability-pq-ech-v1.md`, main commit `04b8f18a89859b73364218e76f5873bad451fb0a`; #178 comment `5606645697` records the result.

Key decisions:
- `RESTORED_LOCAL_FLOOR != PROOF_OF_GLOBAL_FLOOR_CONTINUITY`: restore requires an external monotonic fence-floor witness generation/quorum and explicit restore-gap reconstruction; restored storage cannot silently re-authorize stale fences.
- `CANONICAL_BYTES_V2 != SEMANTIC_EQUIVALENCE_TO_V1`: projection/schema/canonicalizer versions are authenticated state; parser/library/hash migration requires a bridge over predecessor and successor semantic digests, and dual verifiers must agree on meaning rather than merely both return PASS.
- `SIGNED_SCHEMA != GLOBALLY_UNIQUE_SCHEMA_VIEW`: schema registry generations require append-only lineage plus independent witness/gossip retention; conflicting signed heads are permanent split-view evidence and survive root rollover/adjudication.
- `BACKUP_PROVIDER_RETIRED != RESTORE_PATH_PROVEN_DEAD`: tombstone GC requires independently verifiable, versioned copy-domain coverage and proof survivability after provider/control-plane retirement.
- `TICKET_DECRYPTS_AT_EDGE != AUTHORITY_FOR_INNER_SERVICE`: TLS/PQ resumption across ECH/virtual hosts/service meshes must re-bind current inner SNI/service identity, ALPN, backend identity, certificate/server generation, current PQ/hybrid policy and 0-RTT replay/spend authority. Shared ticket keys do not imply shared application authority.
- Frozen 40-case RED-first matrix across external fence witnesses, semantic projection versioning, schema gossip/root rollover, tombstone-GC survivability and PQ/ECH/service-mesh resumption.

Primary donors: etcd disaster recovery revision bump/mark-compacted; RFC 8785 JCS; RFC 9162 Certificate Transparency; NIST SP 800-88r2; RFC 9849 ECH; RFC 9846/RFC 8446 TLS 1.3; RFC 9813 resumption authorization guidance.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`. The connector can read/write repository content but there is still no observed automated byte-exact connector-to-local materialization path for the complete executable closure.
- Manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe for an automated byte-exact source-materialization path. If available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR-head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **external witness quorum recovery under witness loss/compromise + semantic projection test-corpus attestation and verifier-build provenance + schema gossip privacy/selective disclosure + deletion-proof legal-hold/retention-policy conflict resolution + PQ/ECH resumption ticket authority during ECH key rotation, backend migration and split client-facing/inner termination**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers external restore-safe fence witnesses, semantic projection versioning, schema-registry gossip/root rollover, tombstone-GC proof survivability, and current-context PQ/ECH/service-mesh resumption authorization; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
