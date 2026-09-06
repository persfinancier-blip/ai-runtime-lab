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

Re-probed direct source execution with `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git`; it again failed before repository execution with `Could not resolve host: github.com` (exit 128). No security-critical source mutation was attempted and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `COMPATIBILITY_ADJUDICATOR_TRUST_ROOT_VERIFIER_DIVERSITY_REVOCATION_EQUIVOCATION_V1_FROZEN` in `research/2026-09-06-compatibility-adjudicator-trust-root-verifier-diversity-revocation-equivocation-v1.md`, main commit `dcd868e9774dcc693ca22a0d228fcd7106b4e410`; #178 comment `5557404151` records the result.

Key decisions:
- a cryptographically valid adjudicator signature is necessary but insufficient; every adjudicator is a content-addressed generation with explicit capability scope, semantic/toolchain/dependency lineage, and current trust-root authorization;
- verifier-trust metadata advances on a monotonic authenticated frontier; trust-root rotation is dual-authorized by old+new root thresholds and stale/rollback restore is archival only;
- verifier diversity is obligation-specific semantic/dependency independence, not process/container/key/vendor count; common-mode critical dependencies collapse threshold domains;
- threshold arithmetic occurs only after capability/freshness/revocation/quarantine/diversity filtering;
- revocation and quarantine preserve evidence, remove admission authority, and compute blast radius over signer/key/semantic-lineage/dependency/oracle/toolchain/proof references; affected compatibility edges become `REVALIDATION_REQUIRED` when remaining independent threshold is not sound;
- contradictory valid attestations for the same canonical adjudication key are durable equivocation evidence, immediately quarantine the adjudicator generation, and can never be resolved by majority vote, latest-wins or selecting the favorable verdict;
- contradictory authenticated trust-root/frontier views are a split-view trust-plane failure; local signed consistency is insufficient after split-view evidence exists;
- fixed implementations receive new adjudicator generations rather than being “unrevoked”; key/toolchain compromise recovery requires fresh root authorization, blast-radius revalidation and preserved compromise/equivocation history;
- explicit 80-case RED-first matrix is frozen across root identity/rotation, adjudicator scope, semantic diversity collapse, threshold arithmetic, revocation blast radius, equivocation, split-view monitoring, recovery, historical frontier and downgrade/substitution pressure.

Primary donors: TUF threshold root rotation/rollback mechanics, Sigstore trust-root/transparency separation, RFC 9162 split-view/gossip threat model, and SLSA configured-root verification. These are donor mechanisms only; no production trust-plane implementation or behavioral compatibility PASS is claimed.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor/patch identities are known, but no supported byte-preserving connector-resource→machine transform/materialization bridge has been observed; large blob connector responses truncate and line-chunk reconstruction would be model-mediated.
- Direct git transport currently fails before repository execution with DNS resolution failure.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade and retained session/request/effect/idempotency/retention/archive/DR/escrow/reroot/provider-capability/UNKNOWN/manual-resolution/evidence/challenge/quarantine/authority/retry/replay/transport-observer/capacity-compaction/archive/privacy-minimization/policy-compiler/evidence-schema-registry/model-normalization/model-semantic-diff/fixture-proof/oracle-independence/proof-reproducibility/adjudicator-trust contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-reroot cutover, re-admission after trust discontinuity, manual consequential re-attempt, retention/privacy exception, plaintext-expanding evidence-policy upgrade or provider evidence-schema widening may be activated without required explicit product/security/business/legal authority bound to the exact decision.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze a **compatibility trust-frontier witness / split-view gossip / checkpoint-consistency contract**. Define independent witness identities/capabilities and diversity; canonical signed trust-frontier checkpoints; ancestry/consistency proofs across frontier advances; multi-channel checkpoint gossip and split-view detection; freeze/withholding detection without treating one distribution endpoint as authoritative; witness quorum degradation/revocation; offline/air-gapped catch-up; recovery after detected fork; and RED cases for forked checkpoints, stale gossip, common-mode witnesses, partial partitions, archive replay, withheld updates and compromised witness keys.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; provider evidence/privacy/policy/schema/model-normalization/model-semantic-diff/fixture-proof/oracle-independence/proof-reproducibility/adjudicator-trust contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
