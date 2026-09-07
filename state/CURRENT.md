# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 remains open at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; GitHub currently reports `mergeable=false`; do not change draft/merge status without the exact retained gate.
- Other open draft/IN_PROGRESS PRs retained from current repository state: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected open issues and active PRs. PR #165 remains open/draft at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, `mergeable=false`, and still requires the full exact branch execution gate before ready/merge.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto11` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available;
- therefore no new LAB-086 behavioral/compile PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `ORACLE_DECISION_ANTI_EQUIVOCATION_PUBLICATION_TRANSPARENCY_APPEAL_FINALITY_FORK_RECONCILIATION_V1_FROZEN` in `research/2026-09-07-oracle-decision-anti-equivocation-publication-transparency-appeal-finality-fork-reconciliation-v1.md`, main commit `32c9bc65eac9367511d9c7adc9f779e571d06e46`; #178 comment `5572009205` records the result.

Key decisions:
- stable oracle decision slot is `(case_digest, semantic_profile_digest, oracle_generation, adjudication_generation)`; same-signer conflicting payloads in one slot are `ADJUDICATOR_EQUIVOCATION_PROVEN` and cannot be resolved by LWW/time/database order;
- two incompatible decisions for one slot that each satisfy the historical threshold/independence policy are `THRESHOLD_DECISION_EQUIVOCATION_PROVEN`, even if their signer sets differ;
- appeals never mutate/reuse the challenged decision slot; they append a new adjudication generation plus explicit supersession linkage while retaining challenged evidence;
- oracle decisions, threshold closures, dissent/conflicts, appeals, policy rotations, key-status/compromise statements and fraud proofs share one append-only `OraclePublicationLogV1` authority namespace;
- signed inclusion/Merkle root is insufficient for global non-equivocation because a log may present split views; authoritative checkpoints require external witnesses that retain prior state and verify append-only consistency;
- `PublicationWitnessPolicyV1` must define a fault model, claim-relevant independence domains and fork-intersecting acceptance quorums; arbitrary numeric `m-of-n` is insufficient;
- for homogeneous threshold policies, any two q-of-n quorums intersect by at least `2q-n`; acceptance policy must ensure the guaranteed intersection exceeds the tolerated equivocating witness budget in relevant failure domains (e.g. `n=3f+1,q=2f+1` gives at least `f+1` intersection);
- conflicting signature-valid checkpoints without valid append-only consistency are `PUBLICATION_FORK_PROVEN`; if both satisfy witness policy, normal finalization stops as `WITNESS_QUORUM_SAFETY_FAILURE_PROVEN` pending explicit reconciliation;
- offline verification can prove a historical non-rollback prefix only; without freshness evidence it must return `CURRENT_STATUS_UNKNOWN_OFFLINE`, not current finality;
- finality is split into publication, procedural appeal, semantic-conflict and historical-trust dimensions; `FINAL_FOR_POLICY_GENERATION` requires every policy-required dimension;
- later appeal, contradiction or compromise evidence adds/supersedes state but never erases old signed/publication evidence;
- publication/witness policy rotations are themselves append-only authority events and cannot reset an inconvenient fork/frontier;
- fork reconciliation requires explicit governance and preservation of all branches; longest-chain, newest timestamp, current endpoint majority or operator preference are forbidden automatic rules;
- introduced `DecisionSlotV1`, `OracleAppealV1`, `OraclePublicationEntryV1`, `OraclePublicationCheckpointV1`, `PublicationWitnessPolicyV1`, `PublicationFrontierV1`, `OracleFinalityProofV1`, `PublicationForkReconciliationV1`, 10 fraud proofs and an 80-case RED-first matrix.

Primary donors: RFC 9162 CT append-only/view-consistency auditing; RFC 9942/9943 COSE receipts + append-only/non-equivocating/replayable VDS; transparency-dev/C2SP stateful checkpoint witnesses/cosignatures; RFC 2026 appeal governance.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 implementation must compose capability inventory/delegation/revocation/lease/handoff/provider-fence/portable-receipt/historical-trust/archive-capture/archive-durability/verifier-durability/conformance-corpus/oracle-independence/oracle-governance/oracle-publication contracts with LAB-087 isolation. It must not treat current trust state, adapter assertions, one-region readback, session consistency, eventual convergence, timestamps alone, a single authentic receipt, quiet periods, archive-builder-selected Merkle roots, WORM/object existence, source-only retention, mutable package/runtime identity, corpus pass rate, code coverage, parser majority vote, verifier-generated expected outputs, mutable standards text, numeric reviewer threshold alone, current reviewer membership, unresolved normative majority vote, a raw threshold signature, an unwitnessed Merkle root, an old valid offline checkpoint, or longest-chain fork selection as global proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **publication witness key lifecycle / witness-policy rotation / witness-history archival and bootstrap semantics**. Define how a new/offline verifier safely acquires its initial trusted publication frontier without claiming more than TOFU; how witness key retirement/compromise with known vs unknown effective time changes historical checkpoint trust; how old/new witness sets and quorum-intersection safety compose across rotations; how log/witness decommission preserves independently replayable checkpoints, consistency proofs, keys and policies; and how a verifier distinguishes authorized trust-root/bootstrap migration from rollback or fork laundering.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration/provenance contracts frozen; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability delegation + descendant revocation + D2 lease + issuer handoff + external-provider fence + portable receipt + historical trust + archival capture/completeness + archive durability/custody/restore-verifiability + hermetic verifier durability + scoped verifier conformance/differential-equivalence + oracle-independence/provenance + oracle-governance/threshold/normative-conflict + oracle anti-equivocation/publication/appeal/fork-reconciliation contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
