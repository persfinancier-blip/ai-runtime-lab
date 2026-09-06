# Current Lab State

Last updated: 2026-09-07

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending hidden-rowid lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack remains open: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues, open PRs and repository branches. PR #165 remains the highest-priority unfinished task.

Re-probed the exact LAB-086 capability in this run:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- connector read/write remains available but no supported byte-preserving machine transform from exact predecessor+patch bytes to the exact candidate has been observed;
- manual/model reserialization of security-critical `strict_fence.py` remains prohibited;
- therefore `strict_fence.py` was not mutated and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `CAUSAL_TRANSACTION_MANIFEST_EMISSION_COMPLETENESS_UNDECLARED_EDGE_FRAUD_PROOF_PRODUCER_PATH_BINDING_V1_FROZEN` in `research/2026-09-07-causal-transaction-manifest-emission-completeness-undeclared-edge-fraud-proof-producer-path-binding-v1.md`, main commit `8186b936c1226120cf67197085bab697afd36a98`; #178 comment `5562593521` records the result.

Key decisions:
- consequential effects become federated-barrier visible only when a canonical manifest and the effect are bound on the same authenticated transaction/authority path;
- signed producer metadata alone is not completeness evidence; completeness requires a closed-world operation schema, declaration enforcement at effect release, independent required-slot derivation/verification and reconciliation where independently observable;
- effect and manifest cross-bind by digest/stable identity; participant/outgoing-edge commitments are canonical exact sets;
- deterministic delayed consequences are declared at source commit and remain in-flight obligations until authenticated completion/cancellation;
- `UndeclaredEdgeFraudProofV1` uses authenticated source effect+manifest, destination evidence, schema causality rule and exact non-membership to prove `OMITTED_MATERIAL_EDGE_PROVEN`;
- proven omission makes dependent finalization/GC authority stale, roots affected closure and is repaired additively rather than rewriting history;
- producer+reporter common-mode extraction is not independent completeness assurance;
- schema evolution that discovers a new material edge class triggers historical coverage/repair; scan gaps are `UNKNOWN`;
- explicit 80-case RED-first matrix frozen across binding, required slots, atomicity, delayed effects, participant transactions, independent reconciliation, schema repair and GC/recovery.

Primary donors: Apache Kafka transaction producer-id/epoch + participant protocol; PostgreSQL transactional logical-decoding messages; in-toto signed materials/products metadata and its explicit non-completeness for artifacts not recorded.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- Exact predecessor + retained patch remain readable through connector history, but no supported byte-preserving composition bridge has been observed.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen authority/evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper/bootstrap-compaction/GC/schema-repair/materiality/substitution/verifier-agility/sunset-refresh/concurrent-inventory/federated-barrier/producer-manifest contracts instead of creating locally valid authority islands.
- New audit risk: producer-path completeness depends on the closed-world manifest schema itself being trustworthy and independently reviewable. A buggy/malicious schema generation can omit a material declaration slot and make producer+verifier agree on an incomplete universe.

## Exact next action
LAB-086 first: probe only for a genuinely supported byte-preserving machine transform/materialization path that consumes exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is **manifest-schema authority / declaration-slot compiler / schema-completeness proof semantics**. Define who may publish a closed-world effect schema; how operation kinds map deterministically to required participant/causal/recovery slots; how independent implementations can verify schema completeness without sharing the producer's buggy extractor; how schema generations are authenticated, reviewed, rolled forward/revoked and coverage-scanned; and how a late-discovered missing slot yields a compact schema-omission fraud proof and bounded historical repair rather than silently legitimizing incomplete manifests. Freeze executable RED cases for malicious/buggy schema, aliasing/ambiguous operation kinds, generated-code drift, downgrade, partial rollout and concurrent schema rotation.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; producer-bound causal/transaction manifest completeness and undeclared-edge fraud-proof contract now frozen in addition to prior evidence/GC/substitution/verifier-agility/sunset-refresh/concurrent-inventory/federated-barrier contracts; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
