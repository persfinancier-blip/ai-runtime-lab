# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current connector read confirms `open`, `draft=true`, `mergeable=false`. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues, open PRs, branches, and PR #165; resumed LAB-086 first.

Current-run capability/state:
- Direct exact-source transport was re-probed with local `git clone --no-checkout` and failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained byte-exact gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `WITNESS_REPLAY_ADAPTIVE_MUTATION_PRIVACY_DELEGATION_RETENTION_QUORUM_PQ_DNS_CONVERGENCE_V1_FROZEN` in `research/2026-09-10-witness-replay-adaptive-mutation-privacy-delegation-retention-quorum-pq-dns-convergence-v1.md`, main commit `c48a79115a7dea8bf1111ee085a503912e080802`; #178 comment `5610077785` records the result.

Key decisions:
- `VALID_OLD_ACKNOWLEDGEMENT != CURRENT_REOPEN_AUTHORITY`: reopen/finalize acknowledgements bind predecessor and successor digests, witness membership/quorum epoch, acknowledgement key generation, role, transition id, policy generation and freshness. Replay across proposal, membership, key or policy epoch is rejected; post-compromise successor keys do not retroactively repair degraded predecessor assurance.
- `ADAPTIVE_MUTATION_FINDS_NO_BUG != COVERAGE_COMPLETE`: authenticated test claims separate deterministic corpus root, mutation operators, adaptive search algorithm, seeds/RNG commitments where relevant, search budget/stopping rule, oracle provenance, semantic coverage floor and excluded families. Silent operator retirement is prohibited; shared build/control planes do not count as independent verification domains.
- `PRIVACY_BUDGET_DELEGATED != PRIVACY_BUDGET_MULTIPLIED`: parent/child disclosure authority is conserved across delegation, transfer, credential rotation, subject split/merge and restore. Unknown lineage or global spend state blocks consequential disclosure as `PRIVACY_BUDGET_STATE_UNKNOWN` rather than resetting allowance.
- `N_TIME_SOURCES_AGREE != N_INDEPENDENT_TIME_AUTHORITIES`: retention time quorum counts transitive upstream/network/operator/KMS/recovery failure domains. Leap-second ambiguity, wall-clock rollback, VM/database restore or time-config rollback cannot reset an already observed monotonic destructive-action floor.
- `DNSSEC_VALID_ROUTE != CURRENT_RESUMPTION_ROUTE_AUTHORITY`: DNSSEC-valid cached SVCB/ECH state during rollover is authenticated historical routing evidence, not automatic current TLS/PQ resumption authority. Resolver disagreement is explicit; weakest-answer fallback is forbidden for required security capability; route convergence does not by itself reauthorize an incompatible old ticket.
- Frozen 40-case RED-first matrix across witness replay/compromise, adaptive mutation coverage, privacy delegation/split-merge, retention time quorum, and PQ/ECH/SVCB DNS convergence.

Primary donors: RFC 9162; SLSA reproducibility guidance; NIST SP 800-226; NIST authenticated Internet time/leap-second guidance; RFC 9460; RFC 6781; RFC 9849.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read exact pinned blobs but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **witness acknowledgement nonce-store rollback/GC and compromised-key recovery bridges + adaptive mutation adversarial reward/oracle collusion and metamorphic differential checks + privacy-budget delegation revocation/race and cross-purpose composition + retention time-quorum membership rotation, holdover/drift and authenticated epoch transitions + PQ/ECH/SVCB route-convergence proofs under resolver cache poisoning recovery, DNSSEC emergency rollover and session-ticket cache eviction**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers witness acknowledgement replay/key compromise, adaptive mutation coverage, privacy delegation/split-merge conservation, retention time-source independence, and PQ/ECH/SVCB DNS route convergence; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
