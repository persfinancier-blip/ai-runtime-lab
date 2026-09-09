# Current Lab State

Last updated: 2026-09-09

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts remain visible: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and PR #165; resumed LAB-086 first.

Current-run capability/state probe:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available;
- PR #165 is confirmed `open` and `draft` at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; no draft/merge-state change was attempted;
- retained prior evidence still says the strict/thaw subgate passed on pinned executable source; remaining LAB-086 gate is the complete LAB-080→086 real-ledger suite, unsafe expected-failure seed, full compileall and final security/reconciliation/conflict audit;
- no supported automated connector-to-local exact-source materialization path was observed, so no large security-critical source closure was manually/model reserialized and no new LAB-086 behavioral/compile PASS is claimed.

Completed the recorded distinct fallback and froze `REPLICA_RECOVERY_RECEIPT_KEY_RECOVERY_CHALLENGE_PROVENANCE_DESTRUCTION_NEGATIVE_SPACE_PQ_SUPPLY_CHAIN_V1_FROZEN` in `research/2026-09-09-replica-recovery-receipt-key-recovery-challenge-provenance-destruction-negative-space-pq-supply-chain-v1.md`, main commit `fd9cc03b83c53310d4b8a666d684437581ba73e4`; #178 comment `5597834518` records the result.

Key decisions:
- replica-audit authority recovery is a new authenticated generation: a compromised incumbent cannot self-issue a clean successor. Recovery requires an independent recovery quorum/policy epoch and monotonic anti-rollback floor; later denominator shrink does not validate an under-quorum historical recovery;
- receipt-log key rollover preserves old promise origin and verification lineage. K1→K2 continuity must bind predecessor checkpoint/ancestry/outstanding-promise frontier and historical witness policy; witness recovery cannot recount old checkpoints or erase observed equivocation;
- confidential challenge assurance now separates secrecy from sampling integrity. Challenge generation binds exact corpus/population, generator/build provenance, selection algorithm, randomness provenance, anti-bias commit ordering and monotonic leakage accounting; `SECRET_CHALLENGE != UNBIASED_CHALLENGE`;
- destruction completeness now proves negative space through a `CopyDomainUniverse` and per-source authenticated scope/epoch. Signed empty backup/snapshot inventories prove absence only inside their authenticated scope; uncovered domain×time cells remain `NEGATIVE_SPACE_UNCOVERED`, and source compromise degrades dependent historical negative claims;
- PQ migration evidence now includes migration/parser/canonicalizer/crypto/verifier supply-chain provenance and authenticated algorithm-negotiation transcripts. A valid PQ signature does not prove a trusted migration implementation; clean re-verification creates a successor generation; stripping a policy-required stronger/PQ offer is downgrade evidence;
- frozen 40-case RED-first matrix across replica authority recovery/rollback, receipt-key/witness recovery, challenge provenance/leakage, destruction negative-space/source compromise, and PQ supply-chain/verifier/negotiation downgrade.

Primary donors: RFC 9162; NIST SP 800-57 Part 1 Rev. 5; SP 800-131A Rev. 2; FIPS 203/204/205; NIST SP 800-227 final; NIST IR 8547 initial public draft.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable in this run due DNS resolution failure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **recovery-quorum membership compromise/rotation and emergency-root survivability + receipt promise frontier anti-omission across key/log migration + challenge randomness-beacon compromise/bias and verifiable sampling + copy-domain universe authority/versioning and topology drift + PQ migration builder/SBOM attestation compromise, negotiation transcript completeness and multi-implementation cross-verification policy**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers independent replica-authority recovery/anti-rollback, receipt-key/witness recovery with promise lineage, challenge-generator provenance/anti-bias/leakage, destruction negative-space/source compromise, and PQ migration supply-chain/verifier/negotiation downgrade boundaries; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
