# Current Lab State

Last updated: 2026-09-08

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-086 first.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-auto11` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes and web research remain available;
- PR #165 remains open/draft at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; connector reports `mergeable=false`;
- no new LAB-086 behavioral/compile PASS is claimed and no draft/merge state was changed.

Completed the recorded distinct fallback and froze `REGISTRY_RECOVERY_TRANSPARENCY_RANDOMNESS_FALLBACK_REPAIR_MANIFEST_VERIFIER_PROVENANCE_V1_FROZEN` in `research/2026-09-08-registry-recovery-transparency-randomness-fallback-repair-manifest-verifier-provenance-v1.md`, main commit `3242ee97a8dc334a6cf7ca2e1855fde868dfb3da`; #178 comment `5589794363` records the result.

Key decisions:
- valid authority generation, transparent publication, witness observation and latestness are separate assurance classes;
- registry/recovery authority cannot be the sole source of truth for its own compromise/successor; independently authorized + transparently published later generations can make an older still-valid generation provably stale;
- same lineage/generation + different authenticated digest is equivocation, never LWW/newest/fastest-mirror resolution;
- challenge population is committed before randomness; fallback must be versioned and declared before commitment, with no post-value subset selection or same-epoch reselection after withholding;
- beacon endpoint/key count does not equal independent beacon/control-domain count; resharing that preserves a chain key does not itself prove unchanged administrative independence;
- repair manifests are immutable, predecessor/CAS-linked and require configured transparency/witness publication before authoritative finality; witnessed publication does not prove semantic reconstructability/independence;
- verifier process/binary count != implementation diversity; provenance separately tracks source lineage, parser/canonicalizer, crypto implementation, toolchain, build control and runtime domains;
- independent reproducible byte equality corroborates build inputs but does not prove source/parser/crypto correctness or implementation independence;
- late common-mode provenance disclosure re-appraises current verifier-diversity assurance without erasing historical evidence;
- frozen 64-case RED-first matrix across authority transparency/recovery, randomness fallback, repair-manifest equivocation/offline catch-up and PQ verifier provenance/diversity.

Primary donors: TUF root continuity/freeze semantics; RFC 9162 transparency consistency/auditing; drand threshold beacon/resharing; SLSA verified-reproducible independence guidance; Reproducible Builds byte/hash comparison.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, hidden-rowid collision/sentinel, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **transparency-log/witness authority lifecycle and cross-log anchoring + randomness-fallback anti-bias composition under partial compromise + repair-manifest semantic attestation quorum + verifier-provenance attestation authority/revocation**. Define how transparency/witness sets themselves rotate/recover without circular self-trust; when cross-log anchoring gives positive equivocation/suppression evidence versus merely more replicas; which multi-beacon combination rules remain unbiased when some contributors can selectively withhold after learning their values; how semantic repair attestations are independently reproduced/adjudicated rather than merely cosigned; and who is allowed to issue/revoke verifier provenance attestations without letting a verifier certify its own independence.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability through registry/recovery transparency, randomness fallback, repair-manifest witnessing and verifier-provenance contracts frozen; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
