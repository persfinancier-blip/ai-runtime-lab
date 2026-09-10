# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current connector inspection shows `open`, `draft=true`, `mergeable=false`. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and active PRs; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `OBSERVER_DOMAIN_ATTESTATION_HOLDOUT_COMPACTION_PRIVACY_SCOPE_OVERLAP_RETENTION_REPLICA_FENCE_TICKET_RETIREMENT_V1_FROZEN` in `research/2026-09-10-observer-domain-attestation-holdout-compaction-privacy-scope-overlap-retention-replica-fence-ticket-retirement-v1.md`, main commit `3057874b6f96f962a453bf963f5db8ea3787943b`; #178 comment `5617849829` records the result.

Key decisions:
- `MEMBER_ID_UNIQUE != FAILURE_DOMAIN_INDEPENDENT` and `ATTESTATION_SIGNATURE_VALID != ATTESTATION_ROOT_CURRENT`: observer quorum independence is computed from authenticated stable authority/failure-domain lineage, with a monotonic attestation-root generation. New ids/keys or stale domain assertions do not restore independence after compromise/rollback.
- `COMPACT_PROVENANCE_ROOT != FRESH_HOLDOUT` and `SYNTHETIC_ROWS_DIFFER != INFORMATION_INDEPENDENT`: reusable-holdout compaction may GC raw DAG nodes only after an authenticated successor root preserves dataset/generator/controller/disclosure ancestry and freshness; rollback, synthetic derivation or renaming cannot reset exposure.
- `SCOPE_IDS_DIFFER != SUBJECT_SETS_DISJOINT`: privacy accounting follows semantic subject-set/data lineage. Split/merge operations conserve capacity and carry charged/reserved/unknown ancestry; ambiguous overlap composes conservatively rather than creating fresh budget.
- `PROXY_ACK_CURRENT != REPLICA_FENCE_CURRENT`: destructive retention operations carry monotonic policy/delegation/operation/proxy/replica/resource fences and are revalidated at the final resource replica. Rejoin/rollback or timeout after possible effect cannot authorize blind replay.
- `NEW_CERT_OR_DC_OR_PQ_KEY != OLD_RESUMPTION_AUTHORITY_RETIRED`: TLS/PQ/ECH/DC recovery requires durable ticket-retirement acknowledgements from every eligible regional spend authority; late/rolled-back regions remain resumption-quarantined, and descendant/re-encrypted tickets preserve unresolved ancestry.
- Frozen 40-case RED-first matrix across those five domains.

Primary donors: RFC 9162; Generic/Reusable Holdout work; NIST SP 800-226; RFC 8446; RFC 9345; RFC 9325.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **observer domain-attestation issuer compromise/cross-signing and lineage-merge semantics + authenticated holdout compact-root completeness/GC proof and restoration after lost provenance nodes + privacy scope equivalence under probabilistic identity resolution and subject migration + retention multi-replica effect reconciliation/anti-replay after partial success + PQ/ECH/DC ticket-retirement quorum changes during region membership churn, including old-key erasure evidence and bounded ancestry lifetime**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers authenticated observer failure-domain lineage, rollback-resistant compact holdout provenance, semantic privacy-scope overlap, multi-hop resource/replica fencing, and durable regional ticket-retirement convergence after certificate/DC/PQ/ECH recovery; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
