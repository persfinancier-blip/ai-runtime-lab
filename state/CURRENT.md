# Current Lab State

Last updated: 2026-09-09

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts remain visible: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-086 first.

Current-run capability/state probe:
- direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available;
- PR #165 is confirmed `open`, `draft` at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; no draft/merge-state change was attempted;
- retained prior evidence still says the strict/thaw subgate passed on pinned executable source; remaining LAB-086 gate is the complete LAB-080→086 real-ledger suite, unsafe expected-failure seed, full compileall and final security/reconciliation/conflict audit;
- no supported automated connector-to-local exact-source materialization path was observed, so no large security-critical source closure was manually/model reserialized and no new LAB-086 behavioral/compile PASS is claimed.

Completed the recorded distinct fallback and froze `REPLICA_AUTHORITY_RECEIPT_CONFIDENTIAL_CORPUS_ESCROW_FINALITY_ZK_PQ_V1_FROZEN` in `research/2026-09-09-replica-authority-receipt-confidential-corpus-escrow-finality-zk-pq-v1.md`, main commit `2b543c934d0f97eea34d1f515673ac58963e1b6a`; #178 comment `5595705715` records the result.

Key decisions:
- replica independence is an authenticated historical topology claim, not a replica-label count. Relabeling creates a successor epoch; same-generation mapping conflicts are equivocation; concurrent successors are split-brain; historical destructive-domain denominators are never rewritten retroactively;
- `SEND_ATTEMPT != ACCEPTANCE_RECEIPT`: positive no-response/censorship evidence requires an authenticated receipt bound to the exact challenge/nonce/source/deadline plus a precommitted complete collector population. Missing receipt means delivery is unproven; missing collectors means observation is incomplete; neither may be promoted to source withholding;
- confidential semantic-corpus cases may remain hidden, but their committed existence/population cannot be silently omitted. Full-corpus PASS requires exact coverage of the authenticated case commitments plus the policy-required auditor/ZK predicate evidence for hidden decision-relevant cases;
- escrow fork adjudication chooses the prospective winner but does not prove losing-branch disposal. Retired shares must be rejected, prior partial exposure remains monotone, and `DELETION_ATTESTED != ALL_COPIES_UNRECOVERABLE`; destruction assurance must cover the policy-required key/share/backup hierarchy;
- ZK renewal separates statement semantic-equivalence authority from proof-system/circuit/parameter and attestation-key epochs. PQ signatures protect new bindings but do not repair already-untrusted predecessor provenance or prove semantic equivalence; hybrid combiner semantics and downgrade boundaries are explicit;
- frozen 40-case RED-first matrix across replica authority, ingress receipts/collector collusion, confidential-corpus anti-omission, escrow fork retirement/disposal, and ZK/PQ renewal.

Primary donors: RFC 9162 acceptance promise/MMD + consistency model; IETF Roughtime nonce-bound observations; RFC 9901 selective disclosure; NIST SP 800-57/SP 800-88 key lifecycle/sanitization; NIST FIPS 203/204/205 and PQ transition guidance.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable in this run due DNS resolution failure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **replica-domain challenge/audit freshness and false-independence revocation + ingress-receipt transparency/non-inclusion proof + confidential-corpus auditor compromise and re-audit generations + escrow destruction-evidence retention versus privacy/secrets minimization + PQ hybrid-combiner semantics, algorithm deprecation effective-time and long-term renewal of migration attestations**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers authenticated replica-domain authority/split-brain, ingress receipt/collector anti-collusion, confidential-corpus anti-omission, escrow fork adjudication versus disposal assurance, and ZK semantic-equivalence/PQ migration boundaries; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
