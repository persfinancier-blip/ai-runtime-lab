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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. PR #165 remains open/draft at `ee210a47221b6df53f3518aa3af74f76c5b0122b`.

Re-probed direct source execution with:

`git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab-probe`

It again failed before repository execution with `Could not resolve host: github.com` (exit 128). No security-critical source mutation was attempted and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `MAPPER_CHECKPOINT_BOOTSTRAP_LATE_AUDITOR_SNAPSHOT_PROVENANCE_COMPACTION_V1_FROZEN` in `research/2026-09-06-mapper-checkpoint-bootstrap-late-auditor-snapshot-provenance-compaction-v1.md`, main commit `ec2925ba72aad1d161adc89f02e27ae6e9932a26`; #178 comment `5559154983` records the result.

Key decisions:
- snapshot/bootstrap is a trust transition, not merely a storage optimization; a latest self-served signed snapshot is not independent authority;
- late auditors may avoid genesis replay only from a retained/admitted anchor plus source consistency, mapper-lineage continuity, trust-frontier continuity, and verified snapshot/retained-evidence manifests;
- a snapshot cannot upgrade an unverified mapper frontier into verified state;
- compaction cannot delete the only evidence needed to reproduce source ancestry, mapper coverage/execution, fraud/equivocation/revocation findings, unresolved promise/challenge windows, or historical omission verdicts;
- admitted fraud evidence is not ordinarily compactable; archive relocation requires authenticated manifest binding plus explicit availability policy;
- pruned source prefixes retain authenticated compact/boundary commitments so the retained suffix remains tied to the original log;
- assurance classes distinguish full replay, anchored replay, anchored snapshot, policy-authorized threshold bootstrap and non-authoritative unanchored snapshots;
- generation migration cannot reinterpret old history; recovery preserves bad snapshots/fraud evidence and creates a new corrected lineage;
- explicit 80-case RED-first matrix is frozen across anchor/ancestry, snapshot reproducibility, skipped-leaf laundering, compaction safety, omission-proof reproducibility, archive availability, late auditors and migration/recovery.

Primary donors: RFC 9162 consistency/auditing, transparency-dev compact ranges, current IETF Key Transparency long-term-state/partition semantics, and Trillian signed-root/range/proof mechanisms. Donor mechanisms only; no production snapshotter/bootstrap verifier/compactor or behavioral PASS is claimed.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor/patch identities are known, but no supported byte-preserving connector-resource→machine transform/materialization bridge has been observed; large blob connector responses truncate and line-chunk reconstruction would be model-mediated.
- Direct git transport currently fails before repository execution with DNS resolution failure.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper-completeness/bootstrap-compaction contracts rather than creating independent locally-valid authority islands.
- No production omission verdict may treat silence, lookup failure, a missing dense-log inclusion proof, a signed but derivation-unverified subject-map root, or an unanchored snapshot as cryptographic non-membership/completeness evidence.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze **proof-carrying compaction dependency graph / evidence reachability / garbage-collection safety semantics**. Define a content-addressed dependency graph from consequential verdicts/checkpoints to every proof object needed for future verification, derive a safe-to-prune set only from authenticated unreachable objects after challenge/revocation/appeal horizons, prevent cyclic/self-asserted reachability from laundering required evidence, and define RED cases for orphaned trust roots, archive loss, later revocation that reactivates historical dependencies, concurrent compaction/publication, and state-loss recovery.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper-derivation/bootstrap-compaction contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
