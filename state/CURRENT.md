# Current Lab State

Last updated: 2026-09-06

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; live head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack remains open: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues/PRs and PR #165. PR #165 remains open/draft on `ee210a47221b6df53f3518aa3af74f76c5b0122b`; its own remaining gate still requires the strict/thaw published subgate plus complete LAB-080→086 real-ledger execution before ready/merge.

Re-probed direct source execution with `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git`; it failed before repository execution with `Could not resolve host: github.com` (exit 128).

Re-evaluated a potential byte-safe LAB-086 publication fallback. The GitHub connector can expose exact repository/blob content, including base64, but large exact blob responses are truncated at the connector response boundary and there is no observed supported connector-resource→container materialization primitive. `fetch_file` line-range reads can expose text incrementally, but reconstructing a security-critical file through model-mediated concatenation would violate the retained byte-preserving gate. Therefore `strict_fence.py` remains untouched and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `COMPATIBILITY_PROOF_REPRODUCIBILITY_DETERMINISTIC_BUNDLE_INDEPENDENT_ADJUDICATION_V1_FROZEN` in `research/2026-09-06-compatibility-proof-reproducibility-deterministic-bundle-independent-adjudication-v1.md`, main commit `0196a729d6d9118e4c50e530ffac2f1153effc9e`; #178 comment `5557148415` records the result.

Key decisions:
- consequential compatibility admission requires a closed canonical proof bundle reproducible by a second verifier without invoking candidate codegen or fetching undeclared mutable dependencies;
- bundle identity binds exact source/target models, semantic diff, impact cone, policy/schema generations, fixture/mutant/oracle/verifier generations, deterministic seed domains, complete obligations and historical/frontier evidence;
- randomness is allowed only via recorded domain-separated seeds with PRNG algorithm/version bound to generation identity; traversal/order/time/locale/environment drift cannot be ambient semantic inputs;
- producer and adjudicator independently reconstruct obligation sets/results; material disagreement yields fail-closed `ADJUDICATION_DISAGREEMENT`, never majority vote, favorable-verdict selection, obligation dropping or rerun-new-seed until PASS;
- process/container separation is not semantic independence when both verifiers share the disputed generator/oracle lineage;
- signatures/timestamps/transparency prove bundle integrity/existence/time, not truth of the compatibility claim;
- provider-observed nondeterministic relations replay authenticated durable observations and independently justified invariants; they are not silently re-issued to manufacture determinism;
- stale but internally valid proof bundles lose admission authority after authenticated registry/global frontier advancement while remaining archival evidence;
- explicit 80-case RED-first matrix is frozen across bundle closure/canonicalization, deterministic generation, toolchain identity/independence, adjudication disagreement, provider-observed evidence, stale replay/frontier and attestation separation.

Primary donors: SLSA provenance and verified-reproducibility independence, Sigstore offline verification bundles, and TUF rollback/snapshot monotonic-state mechanics. These are donor mechanisms only; LAB's compatibility authority remains stricter and frontier-bound. No production proof-bundle compiler/adjudicator or behavioral compatibility PASS is claimed.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor/patch identities are known, but no supported byte-preserving connector-resource→machine transform/materialization bridge has been observed in this run; large blob connector responses truncate and line-chunk reconstruction would be model-mediated.
- Direct git transport currently fails before repository execution with DNS resolution failure.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade and retained session/request/effect/idempotency/retention/archive/DR/escrow/reroot/provider-capability/UNKNOWN/manual-resolution/evidence/challenge/quarantine/authority/retry/replay/transport-observer/capacity-compaction/archive/privacy-minimization/policy-compiler/evidence-schema-registry/model-normalization/model-semantic-diff/fixture-proof/oracle-independence/proof-reproducibility contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-reroot cutover, re-admission after trust discontinuity, manual consequential re-attempt, retention/privacy exception, plaintext-expanding evidence-policy upgrade or provider evidence-schema widening may be activated without required explicit product/security/business/legal authority bound to the exact decision.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze a **compatibility adjudicator trust-root / verifier-diversity / revocation and proof-equivocation contract**. Define authenticated identities and capability scopes for producer/adjudicator implementations; require diversity claims to commit to independently maintained semantic lineage rather than process count; define revocation/quarantine after verifier compromise or common-mode oracle defect; bind every adjudication attestation to a monotonic verifier-trust frontier; detect two contradictory valid attestations for the same `(bundle_id, frontier, adjudicator_generation)` as equivocation; define recovery/re-admission after verifier-key/toolchain compromise; freeze RED cases for shared transitive semantic dependencies disguised as diversity, revoked verifier replay, stale trust roots, split-view trust metadata, contradictory attestations, threshold/quorum degradation, key rotation, verifier rollback and archive restore.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; provider evidence/privacy/policy/schema/model-normalization/model-semantic-diff/fixture-proof/oracle-independence/proof-reproducibility contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
