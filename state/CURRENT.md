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
- PR #165 was re-read and remains `open`, `draft`, `mergeable=false` at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; no draft/merge-state change was attempted;
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` was re-probed and failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes are available;
- retained prior evidence still says the strict/thaw subgate passed on pinned executable source; remaining LAB-086 gate is complete LAB-080→086 real-ledger execution, unsafe expected-failure seed, full compileall and final security/reconciliation/conflict audit;
- no supported automated connector-to-local exact-source materialization path was observed, so no large security-critical source closure was manually/model reserialized and no new LAB-086 behavioral/compile PASS is claimed.

Completed the recorded distinct fallback and froze `LEASE_PROOF_BEACON_PRIVACY_PQ_PARTITION_V1_FROZEN` in `research/2026-09-09-lease-reallocation-proof-migration-beacon-common-control-confidential-key-destruction-pq-resumption-partitions-v1.md`, main commit `caede8b22eb1cf88fccaaa08acb1c878f2dfd45b`; #178 comment `5603451362` records the result.

Key decisions:
- `EXPIRY_NOTIFICATION != AUTHORITY_TO_REALLOCATE`: delayed/duplicated lease expiry events are observations, not reusable authority. Reallocation is generation-bound and must conserve exactly one live successor across leadership change/partition; ambiguous expiry/ownership fails closed unless a predeclared globally bounded shard protocol proves conservation;
- `NEW_PROOF_FORMAT_VERIFIES != OLD_HISTORY_MIGRATED`: historical witness/log proof or crypto-format migration needs an authenticated predecessor→successor bridge and exact population conservation/completeness. Historical checkpoints remain immutable claims; successor signatures do not rewrite predecessor semantics;
- `N_NAMED_BEACONS != N_INDEPENDENT_FAILURE_DOMAINS`: beacon independence is computed over transitive dependency/common-control graphs including operator, cloud/KMS, time/entropy source, DKG, build signer and emergency governance. Signed dependency claims still require freshness/completeness/independent verification;
- `SECRET_KEY_DESTROYED != COMMITMENT_PRIVACY_PROVEN`: payload, encryption-key, pepper/commitment-key, retained commitment/proof and metadata leakage are separate disposition claims. Low-entropy public commitments can retain offline dictionary leakage after payload deletion; effective wrapped/unwrapped key copies must be accounted for;
- `TICKET_DECRYPTS != CURRENT_SESSION_AUTHORIZED`: TLS/PQ resumption must re-evaluate current service identity and current crypto-policy floor. Partitioned replay-cache ambiguity disables consequential 0-RTT; retry/resumption cannot use a classical predecessor ticket to bypass a stricter current PQ/hybrid minimum;
- frozen 40-case RED-first matrix across lease reallocation, historical proof migration, beacon common-control, confidential key destruction/privacy, and TLS/PQ resumption under partitions/upgrade skew.

Primary donors: etcd failure/lease semantics; RFC 9162; NIST IR 8213 draft; NIST SP 800-63B and SP 800-88r2; OWASP Password Storage; RFC 8446/RFC 9846/RFC 9813.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable in this run due DNS resolution failure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **lease handoff fencing/acknowledgement and stale-owner write suppression + historical proof-migration trust-root compromise and dual-verifier transition windows + privacy-preserving beacon dependency attestations without hiding common-control edges + commitment/key-destruction revocation of derived indexes/caches + PQ resumption single-use ticket/anti-replay ownership across failover, draining and mixed-version clusters**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers generation-safe lease reallocation, historical proof-format/crypto migration, transitive beacon common-control, confidential commitment privacy after key destruction, and PQ/TLS resumption under partition/upgrade skew; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
