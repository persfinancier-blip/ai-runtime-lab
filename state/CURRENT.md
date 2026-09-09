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

Completed the recorded distinct fallback and froze `BUDGET_LEASE_WITNESS_RETIREMENT_BEACON_ATTESTATION_CONFIDENTIAL_DELETION_PQ_RESUMPTION_V1_FROZEN` in `research/2026-09-09-budget-lease-witness-retirement-beacon-attestation-confidential-deletion-pq-resumption-v1.md`, main commit `3c1093c18e5bd5322965fe6a80fcda37db173b34`; #178 comment `5602584487` records the result.

Key decisions:
- replicated lease state does not make every replica clock authoritative for security-budget expiry. Partitioned reclaim must preserve global unit conservation; ambiguous clock/expiry authority fails closed, while preallocated partition shards are valid only when fixed before partition and globally bounded;
- witness/log retirement freezes future authority but does not dispose of predecessor audit evidence. Historical verification must survive offline using archived checkpoint/inclusion/consistency/trust-root lineage, with survivability counted by independent archive domains rather than copy count;
- signed beacon dependency attestations prove statements by an attestor, not actual independence. Attestor roots are versioned/revocable; compromise degrades affected generations and successor re-signing without independent remeasurement is reendorsement, not re-audit;
- confidential evidence uses separate payload, commitment, selective-proof and disposition objects. Redaction/deletion is append-only lifecycle evidence: `PAYLOAD_DELETED != AUDIT_EVENT_DELETED`; if deletion removes material required for exact re-audit, the historical record must say so rather than preserve a reproducibility claim;
- TLS/PQ resumption requires more than ticket decryption: current service identity, ticket-key/replication generation, current crypto-policy epoch and authenticated freshness must authorize the resumed consequential use. Cross-cluster ticket-key replication expands a compromise domain; stricter current PQ/hybrid policy forces a compliant fresh handshake or fail-closed;
- frozen 40-case RED-first matrix across lease/clock authority, witness retirement/archive loss, beacon attestation compromise/revocation, confidential deletion/redaction, and PQ/TLS resumption lifecycle.

Primary donors: etcd lease/API guarantees; RFC 9162; Sigstore Rekor sharding/monitoring and TUF-style root freshness/revocation; NIST IR 8213 randomness-beacon security considerations; SLSA verifier/provenance trust boundaries; NIST SP 800-53/800-171 audit protection/retention; W3C BBS selective disclosure; RFC 9846, RFC 9325 and RFC 9813 TLS resumption/ticket lifecycle; NIST PQC project and IR 8547 transition vocabulary. IR 8213/8547 cited material is draft-status evidence.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- Direct container Git/raw transport is unavailable in this run due DNS resolution failure.
- Connector can read/write repository content, but no supported automated connector-to-local materialization path for the full exact executable closure was observed; manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **lease reallocation under delayed/duplicated expiry notifications and quorum leadership change + historical witness proof-format/crypto migration without losing offline verifiability + beacon dependency-graph transitive closure/hidden common-control discovery + confidential commitment-key/pepper destruction and dictionary/privacy leakage after payload deletion + PQ resumption ticket theft/replay-cache behavior under partitions and asymmetric client/server upgrade rollout**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers distributed budget lease/clock authority, witness retirement/archive survivability, beacon dependency-attestation revocation, confidential payload disposition without history corruption, and PQ/TLS resumption across cluster/identity/policy transitions; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
