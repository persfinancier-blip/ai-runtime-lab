# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; do not change draft/merge status without the exact retained gate.
- GitHub read paths disagreed during this run on `mergeable` for #165 (`get_pr_info=false`, recent-PR listing=true). Treat mergeability as control-plane-observation uncertainty, not readiness; retained execution gate is authoritative.
- Other open draft/IN_PROGRESS PRs observed: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected open PR state and PR #165 exact head.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto12` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- therefore no new LAB-086 behavioral/compile PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `PUBLICATION_WITNESS_KEY_LIFECYCLE_POLICY_ROTATION_HISTORY_ARCHIVAL_BOOTSTRAP_V1_FROZEN` in `research/2026-09-07-publication-witness-key-lifecycle-policy-rotation-history-archival-bootstrap-v1.md`, commit `d111f9f2aee776d960730484f22d62998ca6aa91`; #178 comment `5572714218` records the result.

Key decisions:
- network first-use is discovery only; TOFU must remain explicitly local and cannot be inflated into independent/global trust;
- `VALID_COSIGNATURE != TRUSTED_WITNESS_HISTORY != CURRENT_PUBLICATION_FINALITY`;
- witness historical trust is event-time indexed: planned retirement is non-retroactive; known effective compromise can bound invalid history; unknown compromise start yields `UNKNOWN_WITNESS_HISTORICAL_TRUST` when quorum safety depends on the key;
- witness anti-equivocation requires durable monotonic checkpoint state; state loss/rollback requires `RECOVERY_REQUIRED_NO_COSIGN`, never restart from size zero;
- normal witness-policy rotation requires predecessor-policy authorization + successor-policy acceptance over one canonical transition;
- policy rotation must prove cross-policy anti-fork safety; disjoint immediate cutover without sufficient overlap, joint epoch, or independent monotonic bridge is unsafe and can launder a fork;
- old witness policies/keys/checkpoints/key-status statements and losing fork branches are historical evidence and survive rotation/decommission;
- offline verification establishes only a witnessed historical frontier unless separate freshness evidence exists;
- log/witness key rotation, rename, account move or infrastructure migration cannot reset the publication authority namespace or erase prior fork/rollback evidence;
- introduced `PublicationBootstrapV1`, `WitnessKeyHistoryV1`, `WitnessPolicyRotationV1`, `WitnessDurableStateV1`, `WitnessHistoryArchiveV1`, 10 fraud/contradiction proof classes and an 80-case RED-first matrix.

Primary donors: C2SP `tlog-witness` v1.0.0 stateful/atomic consistency enforcement; TUF predecessor+successor root-threshold migration; RFC 9162/CT split-view consistency auditing; Sigstore explicit versioned TUF-root bootstrap/continuity.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 exact implementation must compose all frozen capability/delegation/revocation/lease/handoff/provider-fence/receipt/historical-trust/archive/verifier/conformance/oracle/publication/witness contracts with LAB-087 isolation; none of the design freezes substitute for executable proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **publication witness recovery quorum / lost-state disaster recovery / anti-cloning and simultaneous-active-witness semantics**. Define how a witness recovers after durable checkpoint-state loss without accepting size zero; how recovery state is authorized from independent archives, peer witnesses and log consistency evidence; how restored clones are fenced so two instances cannot simultaneously cosign under one witness identity; how lease/fencing and key custody compose with witness recovery; and how recovery proceeds when the purported terminal historical state is disputed or forked.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; publication-witness bootstrap/key-lifecycle/policy-rotation/history-archival contract now also frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
