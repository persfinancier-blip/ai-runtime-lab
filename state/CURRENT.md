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

Completed the recorded distinct fallback: froze `DEPENDENCY_REPAIR_AUTHORITY_MATERIALITY_ADJUDICATION_SEMANTIC_EDGE_TAXONOMY_V1_FROZEN` in `research/2026-09-06-dependency-repair-authority-materiality-adjudication-semantic-edge-taxonomy-v1.md`, main commit `fcb62d243e8605875d72f6bd25ddb24c3f8404a9`; #178 comment `5560196888` records the result.

Key decisions:
- dependency existence/reporting, semantic classification, materiality adjudication, repair registration, and destructive GC authority are separate powers;
- edge taxonomy separates `E0_AUDIT_PROVENANCE`, `E1_REPRODUCIBILITY_INPUT`, `E2_VERIFICATION_DEPENDENCY`, `E3_RECOVERY_DEPENDENCY`, `E4_AUTHORITY_CONTINUITY`, explicit external `E5_LEGAL_OR_OWNER_HOLD`, and authenticated `E_NEG_NON_MATERIAL`;
- reports alone never become permanent GC roots;
- consequential `E2+` materiality requires independent evidence and cannot rely solely on the same material semantic extractor/oracle lineage whose omission triggered repair;
- repair authority is namespace/class scoped and cannot manufacture owner/legal holds or wildcard-retain arbitrary history;
- downgrades can authorize future deletion and therefore require authenticated evidence, blast-radius calculation, no unresolved challenge/disagreement/revalidation, frozen current frontiers, and a fresh GC mark;
- `E4` cannot be weakened by age or simple supersession; authenticated subsumption must preserve every still-supported historical authority-continuity path;
- revocation/compromise re-roots affected closures as `REVALIDATION_REQUIRED` and invalidates pre-revocation destructive marks;
- conflicting authenticated decisions enter `MATERIALITY_DISAGREEMENT`; retain the strongest implicated closure until current-policy resolution;
- explicit 80-case RED-first matrix is frozen across role/scope separation, taxonomy semantics, independent materiality evidence, anti-pinning, upgrades/downgrades, revocation, conflicts/diversity, GC races and disaster recovery.

Primary donor mechanisms: Nix GC roots/reachability, Git prune/gc reachability+grace/concurrency semantics, TUF scoped threshold/revocable authority, and in-toto/SLSA provenance separation. Donor mechanisms only; no production repair/GC implementation or behavioral PASS is claimed.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor/patch identities are known, but no supported byte-preserving connector-resource→machine transform/materialization bridge has been observed; large blob connector responses truncate and line-chunk reconstruction would be model-mediated.
- Direct git transport currently fails before repository execution with DNS resolution failure.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper-completeness/bootstrap-compaction/GC/schema-repair/materiality contracts rather than creating independent locally-valid authority islands.
- No production omission verdict may treat silence, lookup failure, a missing dense-log inclusion proof, a signed but derivation-unverified subject-map root, an unanchored snapshot, or post-GC absence as cryptographic non-membership/completeness evidence.
- No repair report/provenance annotation may become destructive-GC retention authority without authenticated current-policy materiality adjudication.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze **semantic-equivalence substitution / minimal-retention witness / dependency-class portability semantics**. Define when an exact retained object may be replaced by a content-addressed semantic equivalent without weakening `E1/E2/E3` guarantees, require independent equivalence proofs bound to verifier/recovery versions, prevent lossy canonicalization from laundering material differences, specify substitution revocation and fallback to original evidence, and freeze RED cases for false equivalence, verifier-version drift, recovery-only data loss, hash-identical-but-context-invalid reuse, and malicious “smaller substitute” retention downgrades.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper-derivation/bootstrap-compaction/proof-carrying-GC/schema-repair/materiality contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
