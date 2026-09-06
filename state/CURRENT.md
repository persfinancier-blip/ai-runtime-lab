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

Completed the recorded distinct fallback: froze `PROOF_CARRYING_COMPACTION_DEPENDENCY_GRAPH_EVIDENCE_REACHABILITY_GC_SAFETY_V1_FROZEN` in `research/2026-09-06-proof-carrying-compaction-dependency-graph-evidence-reachability-gc-safety-v1.md`, main commit `2c3b994d586414a4a94758967009c11235c76265`; #178 comment `5559497500` records the result.

Key decisions:
- destructive evidence GC is authority-sensitive: delete eligibility comes from authenticated roots, typed content-addressed dependency edges, explicit horizons/holds and a reproducible epoch decision, not age or latest-checkpoint heuristics;
- root set includes consequential verdicts/checkpoints, unresolved challenge/appeal/investigation state, revocation blast-radius revalidation sets, recovery anchors, admitted snapshot/bootstrap anchors and publication grace roots;
- `UNKNOWN != DEAD`; unrooted cycles do not create liveness, while corrupt reverse indexes cannot erase forward reachability;
- every consequential object type has a versioned complete dependency schema; later discovery of a missing material dependency moves the affected historical blast radius to `REVALIDATION_REQUIRED` and roots the required old closure;
- signer/verifier/toolchain/policy revocation can reactivate historical proof closures after ordinary challenge windows; old evidence remains rooted until re-adjudication completes;
- supersession is not deletion authority without a subsumption proof preserving supported verification/recovery semantics;
- archive relocation requires authenticated manifest plus independent post-upload retrieval/content-address verification before hot deletion;
- GC uses explicit epochs, publication grace roots and pre-delete reachability recheck to close publication/compaction races;
- every destructive epoch emits a canonical independently reproducible GC proof bundle recording policy/graph generations, roots, live/candidate sets, horizon evidence, archive receipts and actual deletions;
- explicit 80-case RED-first matrix is frozen across roots/reachability, dependency completeness, horizons/challenges, revocation reactivation, archive safety, supersession, concurrent publication/GC and disaster recovery/historical omission-fraud integrity.

Primary donors: Nix GC roots/reachability, Git prune reachability + expiry, TUF rollback/freeze/trusted-root persistence, and Sigstore/Rekor immutable transparency evidence. Donor mechanisms only; no production compactor/GC engine or behavioral PASS is claimed.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor/patch identities are known, but no supported byte-preserving connector-resource→machine transform/materialization bridge has been observed; large blob connector responses truncate and line-chunk reconstruction would be model-mediated.
- Direct git transport currently fails before repository execution with DNS resolution failure.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper-completeness/bootstrap-compaction/GC contracts rather than creating independent locally-valid authority islands.
- No production omission verdict may treat silence, lookup failure, a missing dense-log inclusion proof, a signed but derivation-unverified subject-map root, an unanchored snapshot, or post-GC absence as cryptographic non-membership/completeness evidence.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze **GC dependency-schema evolution / historical dependency repair / proof-of-complete-mark semantics**. Define how a new verifier can discover that an old object type omitted a material dependency without allowing the new schema to reinterpret history; specify authenticated dependency-repair records, blast-radius derivation, canonical mark proofs that demonstrate every required edge was traversed, cross-verifier disagreement handling, and RED cases for schema downgrade, dependency omission laundering, repaired-edge cycles, stale mark proofs, and revocation concurrent with graph migration.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper-derivation/bootstrap-compaction/proof-carrying-GC contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
