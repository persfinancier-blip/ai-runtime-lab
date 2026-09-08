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

Completed the recorded distinct fallback and froze `INDEPENDENCE_REGISTRY_AUTHORITY_RECURSION_RANDOMNESS_WITHHOLDING_STALE_REPAIR_PQ_VERIFIER_DIVERSITY_V1_FROZEN` in `research/2026-09-08-independence-registry-compromise-randomness-withholding-stale-repair-pq-verifier-diversity-v1.md`, main commit `d90874ed24558fd5b2d22a65756c8801e4cadf4f`; #178 comment `5589083533` records the result.

Key decisions:
- valid registry signature != trustworthy current registry authority != factual destructive-domain independence; authority compromise reopens current reliance but never erases historical registry generations or shrinks the historical denominator;
- a compromised registry authority cannot self-install a trusted successor; recovery requires separately controlled continuity authority, otherwise same-lineage recovery is unproven/new-lineage rebootstrap is required;
- member re-admission after a compromise interval requires fresh independence evidence; endpoint/key rotation does not inherit independence;
- challenge population must be committed before randomness; randomness withholding may fail a round but cannot authorize same-epoch population recommit/reselection or undeclared scheduler-local fallback randomness;
- repeated contributor withholding is availability/compromise evidence rather than a challenge-target selection knob;
- repair plans bind source manifest/checkpoint, registry/member generation, independence-evidence frontier and crypto policy; both placement and commit revalidate current state and commit is CAS-like against the exact predecessor manifest;
- `>=k` reconstructability and destructive-domain independence are separate success gates; repairing share count under common control yields `RECONSTRUCTABLE_BUT_INDEPENDENCE_DEGRADED`;
- hybrid-required evidence never silently falls back to classical-only/PQ-only because one component verifier is unavailable or compromised;
- verifier process count != implementation diversity; high-assurance PQ verification may require independent implementation families over the exact same canonical payload, while disagreement fails closed;
- algorithm compromise, verifier implementation compromise, parser/canonicalization compromise and key compromise remain separate re-appraisal causes;
- frozen a 48-case RED-first matrix across registry-authority compromise recursion, randomness withholding, stale/concurrent repair and PQ verifier diversity/downgrade.

Primary donors: drand threshold-beacon specification; RFC 9381 VRFs; Tahoe-LAFS k-of-N/repair semantics; current NIST PQC guidance; current IETF PQ/T composite/hybrid signature and anti-downgrade work.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, hidden-rowid collision/sentinel, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **registry/recovery transparency under authority compromise + randomness-beacon set rotation and cross-beacon fallback policy + authoritative repair-manifest publication/witnessing + verifier-attestation provenance and reproducible-build diversity**. Define how relying parties learn that a registry/recovery authority generation was superseded or compromised without trusting that authority alone; how beacon membership/threshold rotation and predeclared multi-beacon fallback avoid withholding-driven downgrade; how repair manifests become append-only/witnessed so a compromised repair coordinator cannot hide a losing/stale generation; and what evidence is sufficient to count two PQ verifiers as genuinely independent implementations rather than nominally different processes around one common parser/library/build chain.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability through registry-compromise/randomness-withholding/stale-repair/PQ-verifier-diversity contracts frozen; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
