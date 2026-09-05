# Current Lab State

Last updated: 2026-09-05

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; branch `lab/086-asymmetric-break-glass-history`; observed head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected live open issues and PRs. GitHub connector is healthy.

Re-probed LAB-086 direct transport in this runtime: `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository access with `Could not resolve host: github.com` (exit 128). Connector exposes repository bytes and normal Contents writes but no supported machine operation that consumes exact predecessor bytes + retained unified patch and emits transformed bytes. `strict_fence.py` was not model-reserialized/mutated; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `EPOCH_AWARE_CLIENT_API_NEGOTIATION_EXTERNAL_CUTOVER_ADAPTER_V1_FROZEN` in `research/2026-09-05-epoch-aware-client-api-negotiation-external-cutover-adapter-v1.md`, main commit `8280289a65004535b1bdd829172d926319a3f595`; #178 comment `5549596144` records the result.

Key decisions: after a trust discontinuity, missing/legacy epoch fields fail before application-idempotency lookup or provider I/O; clients must explicitly name and acknowledge exact `wire_version + trust_epoch_id + effect_namespace_id`; retries remain pinned to the epoch where the application key was first bound and old UNKNOWN cannot be cloned into a new epoch. Canonical provider request identity includes trust/effect epoch and is durably bound before provider I/O. Adapter capability evidence must cover the provider's real token scope, normalization, truncation, retention/expiry, changed-payload behavior and UNKNOWN outcome-query semantics. Local prefixing is not sufficient if provider transformation can collapse identities. Final provider-token collisions fail closed in a durable UNIQUE mapping before provider I/O. Provider idempotency must either cover the runtime retry horizon, expose an independently queryable authoritative outcome, or force permanent fail-closed/manual reconciliation before an unsafe resend. A provider/adapter unable to prove safe epoch domain separation permanently blocks that effect class after discontinuity. Negotiation never grants cutover authority. A 64-case RED-first matrix is frozen.

Research donors: archived IETF HTTPAPI Idempotency-Key draft -07 (treated as work-in-progress/expired design donor, not normative authority); AWS EBS and Cloud Control documented client-token retry semantics. Provider-specific retention/scope/normalization remain evidence requirements rather than assumptions.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade, session revocation/re-entry, request/effect boundary, durable request/effect registry, application idempotency/result delivery, authenticated install/retention, bounded-growth/resource-exhaustion, consumed-key archival/checkpoint, authenticated archive retrieval, archive manifest/index/replica lifecycle, archive-loss/DR authority, DR checkpoint-escrow/root recovery, DR escrow issuance/rotation/policy lifecycle, human re-root ceremony, post-re-root trust/effect epoch migration, and epoch-aware client/API + external cutover adapter contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-re-root cutover may be activated without explicit human-owner product/security authorization bound to the exact loss/cutover payload.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen canonical encoder/chain/atomic-append/storage/verifier/evidence/recovery/broker/session/request/registry/application-idempotency/install-retention/capacity/archive/retrieval/lifecycle/DR/escrow/human-reroot/post-reroot-epoch/client-negotiation/adapter contracts and execute LAB-090/LAB-100, LAB-092, LAB-094..096 and LAB-097..099 RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze an **external provider idempotency capability evidence + conformance lifecycle contract**. Define how provider semantics are sourced and authenticated, how documentation versus observed probes are ranked, how token normalization/scope/retention/UNKNOWN properties become versioned capability evidence, how evidence expires or is invalidated when provider behavior/adapters/accounts change, safe no-side-effect canary/drill requirements, and how capability drift blocks new effects without changing already-bound retry identities. This must compose with LAB-093/LAB-100 and may not authorize production cutover.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; façade/session/request/effect/registry/application-idempotency/install-retention/bounded-capacity/archive/checkpoint/retrieval/lifecycle/archive-loss-DR/escrow-root-recovery/escrow-lifecycle/human-reroot/post-reroot-epoch/client-negotiation/external-adapter contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
