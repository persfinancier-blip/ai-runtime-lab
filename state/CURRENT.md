# Current Lab State

Last updated: 2026-09-09

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts remain: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/open PRs and resumed LAB-086 first.

Current-run capability/state:
- PR #165 was re-read and remains `open`, `draft` at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; no draft/merge-state change was attempted;
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` was re-probed and failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes are available;
- retained prior evidence still says the strict/thaw subgate passed on pinned executable source; remaining LAB-086 gate is complete LAB-080→086 real-ledger execution, unsafe expected-failure seed, full compileall and final security/reconciliation/conflict audit;
- no supported automated connector-to-local exact-source materialization path was observed, so no large security-critical source closure was manually/model reserialized and no new LAB-086 behavioral/compile PASS is claimed.

Completed the recorded distinct fallback and froze `LEASE_HANDOFF_PROOF_ROOT_BEACON_PRIVACY_CACHE_REVOCATION_PQ_SINGLE_USE_V1_FROZEN` in `research/2026-09-09-lease-handoff-proof-root-beacon-privacy-cache-revocation-pq-single-use-v1.md`, main commit `a998e3601e482b71effd7b412b003ae15878055c`; #178 comment `5604259503` records the result.

Key decisions:
- `LOCK_RELEASED != OLD_OWNER_UNABLE_TO_WRITE`: stale-owner suppression is a protected-sink invariant. The sink must durably reject generations below its highest accepted fence; predecessor acknowledgement or advisory lock release is not enough.
- `NEW_ROOT_ACCEPTS != PREDECESSOR_HISTORY_REPAIRED`: trust-root compromise degrades affected predecessor history. Successor rotation creates a new generation; independent dual-verifier disagreement during migration fails closed rather than silently choosing one parser/verifier.
- `MINIMIZED_DISCLOSURE != MINIMIZED_DEPENDENCY_GRAPH`: beacon dependency attestations may pseudonymize sensitive infrastructure identifiers but must preserve verifiable common-control relationships and completeness over mandatory dependency classes.
- `PRIMARY_SECRET_DELETED != DERIVED_LOOKUP_AUTHORITY_REVOKED`: secret/key deletion closes over deterministic indexes, caches, materialized views, embeddings/features, queued jobs, replicas/backups and authorization caches. Stale derived state cannot continue consequential lookup/authorization.
- `TICKET_SINGLE_USE_POLICY != SINGLE_GLOBAL_CONSUMPTION`: PQ/TLS resumption requires exactly one globally conserved ticket-spend authority. Failover/draining may replicate decryption keys, but ambiguous ownership disables consequential 0-RTT; old mixed-version nodes cannot bypass a stricter current PQ/hybrid floor.
- frozen 40-case RED-first matrix across stale-owner fencing, proof-root compromise/dual verification, privacy-preserving beacon dependencies, derived-cache revocation, and single-use resumption failover/mixed-version rollout.

Primary donors: Consul session/lock sequencer semantics; etcd Lease API; RFC 9162; Sigstore/TUF trust-root threat model; SLSA provenance; NIST randomness beacon/media sanitization guidance; RFC 9846 TLS 1.3 anti-replay/single-use ticket semantics.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable in this run due DNS resolution failure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **sink-fence generation persistence across storage rollback/restore + dual-verifier canonicalization equivalence and parser differential attacks + beacon dependency-attestation schema evolution/mandatory-field downgrade + deletion tombstone/negative-cache propagation and reintroduction prevention + PQ resumption ticket-authority migration during regional disaster recovery and post-compromise ticket-key rotation**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers protected-sink fencing across lease handoff, proof trust-root compromise/dual verification, privacy-preserving common-control attestations, derived cache/index revocation after secret deletion, and globally single-use PQ/TLS resumption across failover/draining/mixed versions; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
