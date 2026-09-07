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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and open PRs. PR #165 remains the highest-priority unfinished task and is still draft/open at the recorded head.

Re-probed the exact LAB-086 capability in this run:
- `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository execution with `Could not resolve host: github.com` (exit 128);
- connector read/write remains available but no supported byte-preserving machine transform from exact predecessor+patch bytes to the exact candidate has been observed;
- manual/model reserialization of security-critical `strict_fence.py` remains prohibited;
- therefore `strict_fence.py` was not mutated and no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `SEMANTIC_INVENTORY_AUTHORITY_EFFECT_CAPABILITY_REGISTRATION_LATENT_SIDE_EFFECT_DETECTION_V1_FROZEN` in `research/2026-09-07-semantic-inventory-authority-effect-capability-registration-latent-side-effect-detection-v1.md`, main commit `9489ca92ee16541256a1641d51505abae834806c`; #178 comment `5563334133` records the result.

Key decisions:
- `OperationSemanticInventoryV1` is a projection, not a root of truth; hidden plugin/FFI/provider/dynamic effects must not be able to disappear from both schema and inventory;
- introduced authenticated, monotonic, predecessor-linked `EffectCapabilityInventoryV1` with stable non-reusable semantic capability IDs/classes and explicit runtime/plugin/provider/build activation frontiers;
- consequential capabilities require registration-before-use and binding to a choke point that is either mechanically enforcing-complete or an independently verifiable trusted adapter;
- observability has explicit coverage states: `ENFORCED_COMPLETE`, `OBSERVED_BEST_EFFORT`, `NOT_COVERED`; best-effort telemetry is anomaly evidence and cannot prove no effect occurred;
- plugins, reflection/dynamic dispatch, generated wrappers, FFI/native escape hatches, subprocesses, pre-opened/external handles and delayed work are first-class semantic capabilities rather than invisible implementation details;
- caller-owned provider/client/session ownership is separated from trust; status-returning interfaces are not sufficient when the underlying remote effect is not independently verified;
- delayed scheduling is itself a consequential effect and must commit to eventual capability classes and causal task identity;
- valid `InventoryOmittedCapabilityProofV1` yields `INVENTORY_OMITTED_CAPABILITY_PROVEN`, stales dependent schema-completeness/effect-manifest/federated-finalization/GC authority, re-roots affected E2/E3/E4 closure and requires additive bounded inventory+schema+manifest repair;
- explicit 80-case RED-first matrix frozen across registration, plugin/dynamic paths, FFI/native/process escape, providers/external handles, delayed effects, observation/reconciliation, schema composition and crash/recovery.

Primary donors: Linux seccomp effect interception/discovery, Landlock explicit kernel-object access rights and limitations around pre-opened/special handles, BPF LSM independent runtime hooks, OpenTelemetry producer/message semantic correlation, SLSA trusted-platform provenance and explicit limits of best-effort dependency completeness.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Direct git transport failed in this run before repository execution with DNS resolution failure.
- Exact predecessor + retained patch remain readable through connector history, but no supported byte-preserving composition bridge has been observed.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 remain design-frozen but require exact executable RED/GREEN before production integration.
- LAB-093 production implementation must compose all frozen authority/evidence/privacy/policy/schema/model/proof/adjudicator/trust-frontier/monitoring/non-inclusion/mapper/bootstrap-compaction/GC/schema-repair/materiality/substitution/verifier-agility/sunset-refresh/concurrent-inventory/federated-barrier/producer-manifest/schema-authority/effect-capability-inventory contracts instead of creating locally valid authority islands.
- New audit risk: even with registered capabilities, transitive delegation across process/plugin/task boundaries can broaden authority or sever provenance. Pre-opened descriptors, inherited broker/provider sessions, fork/exec handles and queued task capabilities need exact ancestor/epoch/attenuation semantics.

## Exact next action
LAB-086 first: probe only for a genuinely supported byte-preserving machine transform/materialization path that consumes exact connector-returned predecessor + retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is **capability-envelope transitive delegation / pre-opened-handle provenance / ambient-authority elimination semantics**. Define how registered capabilities cross process/plugin/task boundaries without silently broadening authority; bind inherited/pre-opened descriptors, provider/broker sessions and task credentials to authenticated ancestor, epoch and scope; define attenuation proofs and descendant revocation; distinguish possession from authority; require fork/exec/SCM_RIGHTS/task-queue/provider-session handoff manifests; and show how independently observed effects are attributed to an exact delegated lineage. Freeze RED cases for descriptor passing, inherited FDs, ambient environment credentials, fork/exec, plugin-to-plugin delegation, task queues, provider sessions, attenuation, revocation races, orphaned descendants and runtime recovery.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; effect-capability inventory/latent-side-effect contract now frozen in addition to prior evidence/GC/substitution/verifier-agility/sunset-refresh/concurrent-inventory/federated-barrier/producer-manifest/schema-authority contracts; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
