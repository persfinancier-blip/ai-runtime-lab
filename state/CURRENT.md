# Current Lab State

Last updated: 2026-09-09

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts remain: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues, PRs and branches; resumed LAB-086 first.

Current-run capability/state:
- Direct exact-source transport was re-probed with `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` and failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- The LAB-086 exact manifest confirms connector line-range reconstruction is an accepted byte-exact technique only when every locally reconstructed file matches its pinned Git blob via `git hash-object`; the complete LAB-080→086 closure still has not been materialized/executed in this run.
- No new LAB-086 behavioral/compile PASS is claimed. Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Open PR set remains #165/#172/#173/#175/#177; no draft/merge state was changed.

Completed the recorded distinct fallback and froze `WITNESS_RECOVERY_VERIFIER_PROVENANCE_SCHEMA_PRIVACY_LEGAL_HOLD_PQ_ECH_V1_FROZEN` in `research/2026-09-09-witness-recovery-verifier-provenance-schema-privacy-legal-hold-pq-ech-v1.md`, main commit `a5ca6e739bef1e64d4e4302064fcf657f8e7df75`; #178 comment `5607417927` records the result.

Key decisions:
- `SUCCESSOR_WITNESSES_AGREE != PREDECESSOR_HISTORY_REPAIRED`: witness loss and compromise are separate states; successor generation/threshold/recovery authority are authenticated forward-only state and cannot silently rewrite degraded predecessor history.
- `TWO_VERIFIERS_PASS != TWO_INDEPENDENT_VERIFIERS`: semantic projection assurance requires an immutable test-corpus root plus verifier source/dependency/artifact/build provenance and builder trust-domain lineage; semantic disagreement is fail-closed.
- `SELECTIVE_DISCLOSURE_VERIFIES != COMPLETE_SCHEMA_VIEW_PROVEN`: privacy-preserving schema gossip may use selective disclosure/pseudonymous equality, but mandatory compatibility/security commitments and common-control edges must remain verifiable.
- `DELETION_REQUESTED != DELETION_AUTHORIZED`: an applicable legal/retention hold yields an authenticated `DELETION_DEFERRED_BY_HOLD` lifecycle state, not false completion or generic technical failure. Runtime enforces authenticated policy state but does not infer legal authority.
- `ECH_RETRY_AUTHENTICATED != OLD_RESUMPTION_AUTHORITY_STILL_VALID`: ECH key/config rotation and split termination require current inner SNI/service identity, ALPN, backend/server generation, PQ/hybrid floor and ticket replay/spend authority to be re-evaluated; shared edge keys do not imply shared inner-service authority.
- Frozen 40-case RED-first matrix across witness recovery, verifier provenance/corpus, schema gossip privacy, deletion/hold and PQ/ECH resumption.

Primary donors: RFC 9162; TUF specification; SLSA provenance; W3C Data Integrity BBS Cryptosuites; NIST SP 800-88r2; RFC 9849 ECH; TLS 1.3 resumption guidance.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector line-range reconstruction is viable for byte-exact files only with per-file hash verification, but the full pinned closure/test inventory has not yet been reconstructed in the local executor this run.
- Manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: use the connector line-range reconstruction path against pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; reconstruct the manifest-listed implementation closure plus every `test_*.py` under `experiments/asymmetric_break_glass_history/tests` and the pinned LAB-085 fixture helper, verify every reconstructed file with `git hash-object` against the pinned tree/blob SHA before import, then execute every normal LAB-086 real-schema test. Run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If complete byte-exact materialization still cannot be finished safely in the available run, next distinct evidence task is **witness recovery authority anti-capture and quorum denominator migration + reproducible verifier corpus generation/attestation poisoning + private schema-gossip intersection attacks and unlinkability budget + retention-hold authority revocation/split-view + PQ/ECH resumption state under DNS HTTPS/SVCB rotation, multi-CDN failover and cross-origin ticket reuse**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers witness recovery under loss/compromise, verifier test-corpus/build provenance, privacy-preserving schema gossip, deletion/retention-hold lifecycle and current-context PQ/ECH resumption authorization; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
