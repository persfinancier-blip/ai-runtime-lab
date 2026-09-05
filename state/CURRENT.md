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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected live open issues and draft PRs. GitHub connector is healthy.

Re-probed LAB-086 direct transport in this runtime: `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository access with `Could not resolve host: github.com` (exit 128). Connector exposes repository bytes and normal Contents writes but still no supported machine operation that consumes exact predecessor bytes + retained unified patch and emits transformed bytes. `strict_fence.py` was not model-reserialized/mutated; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `EXTERNAL_PROVIDER_IDEMPOTENCY_CAPABILITY_EVIDENCE_CONFORMANCE_LIFECYCLE_V1_FROZEN` in `research/2026-09-05-external-provider-idempotency-capability-evidence-conformance-lifecycle-v1.md`, main commit `7ba8233662fb2e50550e1c0370acaa4d1b661415`; #178 comment `5549921242` records the result.

Key decisions: provider idempotency is an exact, immutable, authenticated capability evidence generation rather than a boolean feature flag. Evidence binds provider/service/operation/API/account/scope/adapter/config/effect class/token construction and explicitly classifies token syntax, normalization, truncation, scope, changed-payload behavior, retention, concurrent duplicates, UNKNOWN/outcome-query semantics, deletion/recreation behavior, error taxonomy and outcome identity. Official documentation establishes declared semantics; safe provider probes establish only observed semantics for the tested environment/time. Contradiction enters `DRIFT_SUSPECTED` and blocks new effects. Evidence expiry or provider/adapter/account/API/config drift also blocks new admission. Existing operations never migrate to a successor capability record: provider token, payload identity and evidence generation remain pinned; after the historically proven safe resend deadline they become query-only or fail-closed/manual reconciliation, never a fresh side effect. Canary/drill probes must be sandbox/synthetic/reversible/non-consequential. A 64-case RED-first matrix is frozen. The contract composes with LAB-093/LAB-100 and post-re-root epoch work but cannot authorize a production cutover.

Research donors recorded in the artifact: current IETF HTTPAPI Idempotency-Key Internet-Draft -07; AWS EC2/EBS/ECS operation-specific client-token semantics (including ECS RunTask TTL/scope); Google Cloud Storage conditional-idempotency/precondition semantics.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade, session revocation/re-entry, request/effect boundary, durable request/effect registry, application idempotency/result delivery, authenticated install/retention, bounded-growth/resource-exhaustion, consumed-key archival/checkpoint, authenticated archive retrieval, archive manifest/index/replica lifecycle, archive-loss/DR authority, DR checkpoint-escrow/root recovery, DR escrow issuance/rotation/policy lifecycle, human re-root ceremony, post-re-root trust/effect epoch migration, epoch-aware client/API + external cutover adapter, and external-provider idempotency capability evidence/conformance lifecycle contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-re-root cutover may be activated without explicit human-owner product/security authorization bound to the exact loss/cutover payload.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen canonical encoder/chain/atomic-append/storage/verifier/evidence/recovery/broker/session/request/registry/application-idempotency/install-retention/capacity/archive/retrieval/lifecycle/DR/escrow/human-reroot/post-reroot-epoch/client-negotiation/adapter/provider-capability-evidence contracts and execute LAB-090/LAB-100, LAB-092, LAB-094..096 and LAB-097..099 RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze an **external provider UNKNOWN-outcome reconciliation oracle contract**. Define what qualifies as an authoritative query independent of an idempotent resend, how request/token/resource/operation identities are bound before first provider I/O, how `NOT_FOUND`, `PENDING`, `COMMITTED`, ambiguous/stale reads and eventual consistency are distinguished, how polling/reconciliation expires, how provider query semantics are versioned in the capability evidence record, and when an operation must enter permanent manual reconciliation instead of resending. It must compose with LAB-093 request/effect registry, application idempotency, external-adapter/capability-evidence contracts and may not create a new provider request identity to resolve UNKNOWN.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; façade/session/request/effect/registry/application-idempotency/install-retention/bounded-capacity/archive/checkpoint/retrieval/lifecycle/archive-loss-DR/escrow-root-recovery/escrow-lifecycle/human-reroot/post-reroot-epoch/client-negotiation/external-adapter/provider-idempotency-evidence contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
