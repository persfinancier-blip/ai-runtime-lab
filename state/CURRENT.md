# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 remains open at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; do not change draft/merge status without the exact retained gate.
- The alternate-UNIQUE `strict_fence.py` fix is already published byte-exact: commit `05d8e75a636818afcb32e085d464c9fa9171dea5`, blob `eb2198354d222ad0ad6b7d751bf5c649157b6b36`. Do not redo that publication task.
- Other open draft/IN_PROGRESS PRs observed: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected current open PR state and PR #165. PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b` and retains the full exact branch execution gate before ready/merge.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-run15` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available;
- therefore no new LAB-086 behavioral/compile PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `ARCHIVE_REPLICA_DURABILITY_INDEPENDENT_CUSTODY_CORRELATED_LOSS_RESTORE_VERIFIABILITY_V1_FROZEN` in `research/2026-09-07-archive-replica-durability-independent-custody-correlated-loss-restore-verifiability-v1.md`, main commit `284c100f96f132a003bb1a317891da842e00e6bb`; #178 comment `5568431961` records the result.

Key decisions:
- `FINAL_ARCHIVE_CLOSED` proves archive semantic/causal closure but does not authorize destructive GC by itself; destructive archive dependency requires a distinct current `ARCHIVE_DURABILITY_CLOSED` proof;
- replication is not independent custody: failure domains must be modeled independently for geography, provider, account/tenant, admin authority, KMS/key custody, billing/account lifecycle, retention administration, software and legal/commercial exposure;
- WORM/Object Lock/Vault Lock protects retained versions but does not prove recoverability, key survivability or independent administration;
- introduced `ArchiveReplicaManifestV1`, `ArchiveReplicaSetV1`, `FailureDomainMatrixV1`, `KeyRecoveryBindingV1`, `ArchiveGenerationWitnessV1`, `ArchiveRestoreDrillV1`, `RestoreFreshnessPolicyV1` and `ArchiveDurabilityProofV1`;
- every authoritative replica must bind to the same immutable archive seal/root; same-generation different roots prove equivocation; an authentic older generation contradicting an external monotonic witness is rollback;
- at least one monotonic generation witness must be outside any single replica's mutable authority for high-assurance anti-rollback;
- existence checks, provider inventory/checksum status and proof-of-retrievability sampling are useful signals but do not replace a periodic full isolated restore;
- a full restore drill must recover exact authoritative bytes through the declared independent key/custody path, recompute seal/root, rerun archive completeness verification and rerun historical-trust verification without live-provider assumptions;
- topology/key/policy/provider/verifier changes invalidate restore freshness and require re-drill;
- old archive generation may not be destructively GC'd until its successor has itself reached replica durability + restore verification closure;
- default high-assurance topology target is >=3 restore-capable copies/equivalent threshold set, >=2 admin custody domains, >=2 geographic domains, >=1 non-bypassable WORM copy, independent restore path, single-key/admin-loss-tolerant recovery, external monotonic witness and a fresh non-primary full restore;
- added an 80-case RED-first matrix spanning replica identity, custody correlation, WORM/rollback/equivocation, key durability, restore semantics, erasure coding, renewal/migration and crash/fraud.

Primary donors: AWS S3 Object Lock/Replication; AWS Backup Vault Lock; AWS Backup logically air-gapped vault + cross-account restore/multi-party approval; AWS Backup Restore Testing; Google Cloud Bucket Lock; Azure Immutable Blob Storage.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution, not `strict_fence.py` publication.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 implementation must compose capability inventory/delegation/revocation/lease/handoff/provider-fence/portable-receipt/historical-trust/archive-capture/archive-durability contracts with LAB-087 isolation. It must not treat current trust state, adapter assertions, one-region readback, session consistency, eventual convergence, timestamps alone, a single authentic receipt, a quiet period, archive-builder-selected Merkle root, WORM replication, object existence, or provider durability claims as global completeness/durability proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify expected `strict_fence.py` blob lineage includes `eb2198354d222ad0ad6b7d751bf5c649157b6b36`, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **archive restore verifier reproducibility / hermetic verifier supply-chain / executable-obsolescence semantics**. Define how a historical archive remains verifiable when package registries, mutable container tags, language runtimes, CPU/ABI assumptions, signing infrastructure or build tooling disappear or become untrusted; specify the minimal hermetic verifier bundle, source/build/dependency provenance, reproducible-build or independently verifiable binary requirements, emulator/runtime fallback, verifier semantic-generation migration, crypto-agility boundaries, periodic replay drills, and the distinction between `BYTES_RETRIEVABLE` and `EVIDENCE_VERIFIABLE` over long retention.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; publication fixed; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration/provenance contracts frozen; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability delegation + descendant revocation + D2 lease + issuer handoff + external-provider fence + portable receipt + historical trust + archival capture/completeness + archive durability/custody/restore-verifiability contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
