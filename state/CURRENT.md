# Current Lab State

Last updated: 2026-09-08

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected active PRs and #178; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto36` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; connector reports `mergeable=false`;
- no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `RETENTION_DOMAIN_ATTESTATION_CHALLENGE_ERASURE_ARCHIVE_CRYPTO_AGILITY_V1_FROZEN` in `research/2026-09-08-retention-domain-attestation-challenge-erasure-archive-crypto-agility-v1.md`, main commit `fac3631e5bdfa607f244b93de9c6b2b75886c58c`; #178 comment `5587543467` records the result.

Key decisions:
- a signed retention/destructive-domain attestation is evidence about provenance, not proof that independence exists; no single attester may define the denominator and self-certify all members as independent;
- attester compromise causes append-only current-reliance re-appraisal and cannot erase historical receipts; threshold-compromised attestation authority cannot self-bootstrap a trusted successor;
- `SUCCESSFUL_STORAGE_CHALLENGE != GOVERNANCE_INDEPENDENCE_PROVEN`: nonce/retrievability challenges prove bounded possession/liveness and can expose contradictions, but cannot prove absence of hidden common operator/account/credential/KMS/upstream control;
- asymmetric credential-disable/recovery drills are stronger positive evidence for discovering shared destructive/control dependencies than passive endpoint diversity;
- destructive-domain assurance is provenance-vector based; endpoint/key/region rotation does not create new independence and unknown provenance remains `INDEPENDENCE_UNKNOWN`;
- erasure-coded archive storage preserves exhaustive-prefix omission semantics only when any policy-valid `k` fragments reconstruct byte-exact canonical prefix bytes and the result verifies against independently retained checkpoint/root + reconstruction manifest;
- `N_FRAGMENTS != N_INDEPENDENT_DESTRUCTIVE_DOMAINS`; k-of-n survivability must be evaluated over destructive domains, not node/share count;
- reconstruction metadata, source checkpoint, parser/predicate definition, encryption material and long-term evidence have separate survivability denominators and must not collapse into a single reconstruction root;
- long-term omission evidence follows RFC 4998-style renewal: signature/timestamp ageing can use timestamp/evidence renewal, while weakened content-hash/tree binding requires hash-tree renewal over archived data/evidence while the old binding is still trustworthy;
- post-break rehash without an independently trusted pre-break binding cannot recreate historical authenticity; algorithm/attester compromise reopens current reliance without rewriting history;
- frozen a 48-case RED-first matrix covering attestation lifecycle, hidden common control/challenges, erasure reconstruction/survivability and long-term crypto agility.

Primary donors: RFC 4998 Evidence Record Syntax; NIST CSWP 39-upd1 crypto agility; NIST SP 800-131A Rev.2 algorithm transition guidance; Tahoe-LAFS k-of-N erasure coding plus Merkle/content-integrity mechanisms.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, hidden-rowid collision/sentinel, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **independence-evidence registry lifecycle / destructive-domain membership admission-retirement / challenge scheduler anti-collusion and unpredictability / archive repair without denominator laundering / evidence-renewal authority compromise and PQ/hybrid migration ordering**. Define who may add/remove a destructive domain from the trusted denominator without laundering a failed member, how random challenges remain unpredictable when scheduler/verifier may collude with storage operators, how erasure-code repair chooses replacement domains without silently collapsing independence, how renewal-TSA/authority compromise is handled recursively, and how PQ/hybrid migration is ordered so classical evidence is not relied on beyond its acceptable window.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability through retention-domain-attestation/hidden-common-control-challenge/erasure-archive-survivability/long-term-crypto-agility contracts frozen; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
