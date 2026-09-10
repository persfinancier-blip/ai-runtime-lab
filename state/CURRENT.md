# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current connector read confirms `open`, `draft=true`, `mergeable=false`. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues, PRs and branches; resumed LAB-086 first.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained byte-exact gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `CHECKPOINT_CONFLICTSET_SEQUENTIAL_SELECTION_PRIVACY_ORPHAN_RETENTION_OMISSION_PQ_TICKET_ANCESTRY_V1_FROZEN` in `research/2026-09-10-checkpoint-conflictset-sequential-selection-privacy-orphan-retention-omission-pq-ticket-ancestry-v1.md`, main commit `ede147e776af261ce8f48e5571deb870da4b5905`; #178 comment `5612986115` records the result.

Key decisions:
- `ADJUDICATION_CONTAINS_ALL_KNOWN_HEADS != ADJUDICATION_PROVES_NO_UNKNOWN_CONFLICTING_HEAD_EXISTS`: successor adjudication commits to the canonical known conflict set plus observation cutoff; later-discovered conflicts append new evidence. Successor-root compromise/replay requires a new authenticated recovery bridge and cannot clean predecessor equivocation.
- `PER_CANDIDATE_STOPPING_RULE_VALID != SELECTED_CANDIDATE_INFERENCE_VALID`: adaptive flaky-reducer search is ranking evidence only. A selected candidate receives a fresh predeclared independent confirmation budget; confirmation outcomes cannot be used to replace the candidate without reopening search/evidence accounting.
- `TRANSFER_ACK_MISSING != DESTINATION_CREDIT_ABSENT`: orphaned privacy escrow is not reclaimed on timeout. Destination must be proven non-credited at a current epoch or globally fenced for that transfer id before a new source allocation generation is created; possible disclosure remains charged/unknown.
- `RECEIPT_INCLUSION_PROVEN != EVENT_COVERAGE_COMPLETE`: present valid receipts do not prove omission-free retention history. Reconciliation requires gap-free authenticated coverage for every destructive-capable authority, or independent evidence that an authority was fenced for the uncovered interval.
- `CHILD_TICKET_IS_FRESH != TICKET_ANCESTRY_IS_CURRENT`: ticket descendants inherit ancestry/revocation lifetime floors. Late edges remain `RESUMPTION_QUARANTINED` until ticket-key/revocation/identity/ECH/PQ/backend policy floors are current; 0-RTT additionally requires current replay authority. ECH rejection/public-name authentication never grants origin ticket authority.
- Frozen 40-case RED-first matrix across conflict-set/successor-root recovery, multiple-candidate reducer selection, orphan privacy escrow, retention omission coverage and PQ/ECH ticket ancestry/late-edge admission.

Primary donors: RFC 9162; NIST SP 800-226; RFC 8446; RFC 9849.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read exact pinned blobs but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **checkpoint conflict discovery completeness under censored/gossip-partitioned observers and successor adjudication co-signing + valid post-selection inference/holdout reuse boundaries for flaky reducers + privacy orphan-reclamation authority compromise and reconciliation-root replay + retention writer-inventory completeness across membership changes + PQ/ECH ticket ancestry after certificate/PQ policy rotation, late descendant issuance and cross-region revocation-floor divergence**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers known-vs-universal conflict-set completeness, post-selection confirmation for flaky reducers, double-ownership-safe privacy escrow reclamation, omission-aware retention receipt coverage, and bounded PQ/ECH ticket ancestry/late-edge admission; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
