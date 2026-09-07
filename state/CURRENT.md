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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected open PRs and PR #165. PR #165 remains open/draft and retains the full exact branch execution gate before ready/merge.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-run16` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available;
- therefore no new LAB-086 behavioral/compile PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `ARCHIVE_RESTORE_VERIFIER_REPRODUCIBILITY_HERMETIC_SUPPLY_CHAIN_EXECUTABLE_OBSOLESCENCE_V1_FROZEN` in `research/2026-09-07-archive-restore-verifier-reproducibility-hermetic-supply-chain-executable-obsolescence-v1.md`, main commit `cd22e885bdb296706579e797d003233e477802e7`; #178 comment `5569160165` records the result.

Key decisions:
- `BYTES_RETRIEVABLE` and `EVIDENCE_VERIFIABLE` are distinct closure properties; destructive archive dependency now requires separate current `VERIFIER_DURABILITY_CLOSED` in addition to archive completeness and `ARCHIVE_DURABILITY_CLOSED`;
- historical verifier code/binaries, semantic generation, parser/canonicalizer/schema, crypto parameters, historical trust policy, expected verdict corpus, build inputs and execution substrate are first-class archive objects;
- mutable tags, branches, semver ranges, package-registry resolution and current trust stores are not archival identities; executable/runtime/dependency objects must be selected and verified by immutable digest/size;
- source-only is insufficient unless the complete build closure is archived and independently reproducible; binary/container-only is insufficient unless ISA/ABI/kernel/runtime/emulator assumptions are also preserved and replay-tested;
- OCI digest pinning supports content identity but cannot alone close host execution-substrate assumptions;
- future verifier generation N+1 may not silently reinterpret N-era evidence; migration requires authenticated cross-generation comparison over a frozen historical/adversarial corpus, and N remains retained;
- crypto agility must create a stronger authenticated renewal/migration binding before an old primitive becomes unacceptable; no retroactive closure after an obsolescence gap;
- introduced `HermeticVerifierBundleV1`, `VerifierBuildReproductionProofV1`, `VerifierReplayDrillV1`, `VerifierDurabilityProofV1`, `VerifierGenerationMigrationProofV1` and fraud proofs for hidden dependencies, artifact mismatch, non-reproduction, semantic drift, missing execution substrate and crypto-obsolescence gaps;
- periodic isolated replay must restore from non-primary custody, run without live registries/providers/current trust stores, verify exact bundle bytes, instantiate the native/VM/emulator path, execute positive + adversarial corpus and compare against the frozen expected-verdict root;
- added an 80-case RED-first matrix covering immutable identity, hermetic execution, reproducible build, ABI/emulation, semantic migration, crypto agility, replay/custody and crash/fraud.

Primary donors: Reproducible Builds definition + `SOURCE_DATE_EPOCH`; OCI content descriptor/content-addressability model; QEMU TCG system/user emulation.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution, not `strict_fence.py` publication.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 implementation must compose capability inventory/delegation/revocation/lease/handoff/provider-fence/portable-receipt/historical-trust/archive-capture/archive-durability/verifier-durability contracts with LAB-087 isolation. It must not treat current trust state, adapter assertions, one-region readback, session consistency, eventual convergence, timestamps alone, a single authentic receipt, a quiet period, archive-builder-selected Merkle root, WORM replication, object existence, source-only retention, package lockfiles, container tags/digests alone, or provider durability claims as global completeness/durability/verifiability proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify expected `strict_fence.py` blob lineage includes `eb2198354d222ad0ad6b7d751bf5c649157b6b36`, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **verifier conformance-corpus completeness / parser differential testing / semantic-equivalence proof semantics**. Define how to justify that a frozen replay corpus is strong enough to detect parser/canonicalization/crypto semantic drift rather than merely confirming happy-path compatibility; include grammar-derived adversarial generation, differential execution across verifier generations/implementations, malformed and ambiguous encodings, cryptographic edge cases, coverage/provenance roots, proof that N→N+1 equivalence is scoped rather than universal, and fail-closed `UNKNOWN` rules when corpus coverage cannot justify equivalence.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; publication fixed; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration/provenance contracts frozen; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability delegation + descendant revocation + D2 lease + issuer handoff + external-provider fence + portable receipt + historical trust + archival capture/completeness + archive durability/custody/restore-verifiability + hermetic verifier durability contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
