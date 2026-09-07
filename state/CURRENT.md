# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 remains open at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; GitHub currently reports `mergeable=false`; do not change draft/merge status without the exact retained gate.
- Other open draft/IN_PROGRESS PRs observed: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; re-inspected open issues/PRs and PR #165. PR #165 remains open/draft at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b` and still requires the full exact branch execution gate before ready/merge.

Current-run capability probe:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-run17` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- GitHub connector reads/writes remain available;
- therefore no new LAB-086 behavioral/compile PASS is claimed and PR #165 remains draft.

Completed the recorded distinct fallback and froze `VERIFIER_CONFORMANCE_CORPUS_PARSER_DIFFERENTIAL_SCOPED_EQUIVALENCE_V1_FROZEN` in `research/2026-09-07-verifier-conformance-corpus-parser-differential-semantic-equivalence-v1.md`, main commit `6c4b659298c33cf31788a5bbf87ff4e8d3cd9e20`; #178 comment `5569842599` records the result.

Key decisions:
- `CORPUS_AGREEMENT != UNIVERSAL_EQUIVALENCE`; finite replay evidence can justify only scoped semantic equivalence bound to an exact `VerifierSemanticProfileV1`, schemas, crypto suites, corpus root, generator root and coverage manifest;
- verifier migration compares parse accept/reject, normalized semantic-object digest, canonical bytes, crypto result, historical-trust result, final verdict and error/resource class; final-boolean agreement alone is insufficient;
- semantic coverage is first-class and conjunctive: every supported grammar production, normative serialization/canonicalization rule, authority-binding field and applicable crypto suite must map to cases or authenticated `NOT_APPLICABLE` evidence; implementation line/branch coverage is advisory only;
- grammar-derived adversarial generation and metamorphic relations cover duplicate/unknown fields, ordering, canonical/non-canonical encodings, Unicode/numeric/length/depth boundaries, idempotence and signature/canonical binding;
- differential fuzzing is a discovery mechanism, not a truth oracle; majority vote is prohibited for authority semantics and every disagreement becomes a retained minimized regression;
- unresolved parser/spec ambiguity, unavailable required vector families, missing canonical-byte comparison, generator/corpus provenance gaps or skipped historical cases yield `UNKNOWN_EQUIVALENCE`;
- exact generator source/binary, grammar, seeds, mutation operators, minimizer and produced-case root are archived as `GeneratorProvenanceV1` so adversarial generation cannot drift silently;
- applicable version-pinned Wycheproof-style crypto vectors are imported, but local authority-binding mutations remain mandatory;
- introduced `VerifierSemanticProfileV1`, `ConformanceCorpusManifestV1`, `CorpusCoverageManifestV1`, `GeneratorProvenanceV1`, `DifferentialExecutionProofV1`, `SemanticDivergenceV1`, `ScopedSemanticEquivalenceProofV1` and omission/self-oracle/boolean-only/majority-vote/profile-shrink/generator-drift fraud proofs;
- added an 80-case RED-first matrix covering parser ambiguity, canonicalization, deterministic binary/CBOR semantics where applicable, schema/version, authority binding, crypto, differential behavior and generator/metamorphic/replay fraud.

Primary donors: RFC 8785 JSON Canonicalization Scheme; RFC 8949 deterministic CBOR encoding; Project Wycheproof; Language-theoretic Security; USENIX Security 2025 ZipDiff semantic-gap differential fuzzing; NDSS DiffCSP.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- PR #165 must remain draft until branch-local dependency-blob verification, retained strict/thaw subgate, real-schema LAB-086 tests, compileall, unsafe expected-failure seed, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-088 still needs supported-integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 implementation must compose capability inventory/delegation/revocation/lease/handoff/provider-fence/portable-receipt/historical-trust/archive-capture/archive-durability/verifier-durability/conformance-corpus contracts with LAB-087 isolation. It must not treat current trust state, adapter assertions, one-region readback, session consistency, eventual convergence, timestamps alone, a single authentic receipt, a quiet period, archive-builder-selected Merkle root, WORM replication, object existence, source-only retention, package lockfiles, container tags/digests alone, provider durability claims, corpus pass rate, code coverage, or parser majority vote as global completeness/durability/verifiability/equivalence proof.

## Exact next action
LAB-086 first: if exact branch source execution becomes available, check out/reconstruct current PR head `ee210a47221b6df53f3518aa3af74f76c5b0122b`, verify exact branch-local source/blob lineage, then execute the retained strict/thaw subgate (alternate-UNIQUE, primary-key/history/proof replacement, NULL identities, minimal thaw, conflict algorithms), compileall, exact branch-local LAB-080→086 dependency-blob verification, every normal LAB-086 real-schema test, unsafe legacy-promotion expected-failure seed, and final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **conformance-corpus oracle independence / expected-verdict provenance / specification-ambiguity adjudication semantics**. Define how expected outcomes are authenticated without circularly trusting verifier N, verifier N+1, or one mutable parser/spec interpretation; define normative-source inventory, multi-review/policy-generation provenance, treatment of standards errata, conflicting independent implementations, historical-vs-current semantics, and fail-closed rules when no independently justified oracle exists. Distinguish “historically accepted by N” from “normatively valid under profile P”, and forbid later errata/policy changes from silently rewriting a signed historical replay truth set.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact full executable gate + conflict audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration/provenance contracts frozen; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability delegation + descendant revocation + D2 lease + issuer handoff + external-provider fence + portable receipt + historical trust + archival capture/completeness + archive durability/custody/restore-verifiability + hermetic verifier durability + scoped verifier conformance/differential-equivalence contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; retained-authority graph contracts frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; activation implementation/capability authority contracts frozen.
