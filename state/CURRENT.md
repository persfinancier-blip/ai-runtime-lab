# Current Lab State

Last updated: 2026-09-05

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; live PR head rechecked this run: `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack remains open: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected live open issues and all open draft PRs. GitHub connector is healthy. PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.

Re-probed LAB-086 direct transport in this runtime: `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository access with `Could not resolve host: github.com` (exit 128). Connector exposes repository bytes and normal Contents writes but still no supported machine operation observed in this run that consumes exact predecessor bytes + retained unified patch and emits transformed bytes. `strict_fence.py` was not model-reserialized/mutated; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `MANUAL_RECONCILIATION_SOURCE_CAPABILITY_REVOCATION_EVIDENCE_COMPROMISE_VERDICT_CHALLENGE_V1_FROZEN` in `research/2026-09-05-manual-reconciliation-source-capability-revocation-evidence-compromise-verdict-challenge-v1.md`, main commit `85ec536f6543c6efd63f74d41a5498af43ba3725`; #178 comment `5551127146` records the result.

Key decisions: revocation/challenge is append-only and never deletes historical evidence/assessments/reviews/verdicts; typed challenges cover source compromise/capability overstatement/provider drift/artifact corruption/reviewer-authorizer revocation/global-provenance failure. Propagation is dependency-graph based from capability/credential through evidence, assessment, review and resolution. Time-bounded compromise is honored only when independently evidenced, otherwise the whole authority generation is challenged. `NOT_COMMITTED` is intentionally asymmetric: loss of any required strong-negative predicate immediately suspends its current authority and can never create resend/MISS/retry authority. Challenged `COMMITTED` is conservatively treated as potentially committed; application key/provider token remain consumed and automatic resend is forbidden. Root/provenance compromise, irreconcilable authoritative conflict, insufficient surviving independent quorum or threshold-downgrade pressure stop automation and require security-owner adjudication. A 64-case RED-first matrix is frozen. No production code or behavioral PASS is claimed.

Primary donors recorded in the artifact: RFC 6962 append-only/consistency model; Sigstore/TUF compromise-time revocation, monitoring and root-recovery patterns; NIST SP 800-53/53A AU-family audit integrity and assessment concepts.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade, session/request/effect registry, application-idempotency/result delivery, authenticated retention/archive/DR/escrow/re-root/epoch/provider-capability/UNKNOWN-oracle/manual-resolution/canonical-evidence/challenge contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-re-root cutover or manual consequential re-attempt may be activated without the required explicit product/security/business authorization bound to the exact payload/effect under the frozen contracts.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze a **challenge blast-radius quarantine / effect-class re-admission contract**. Define how a source/verdict/provenance challenge maps to affected provider/effect classes and in-flight UNKNOWN cases; how startup and delegation derive a minimal quarantine set rather than globally stopping unrelated work; how quarantine generations are authenticated and rollback-resistant; how read-only reconciliation may continue while send/mutation authority is removed; and the exact evidence/quorum/drill required to re-admit an effect class after capability replacement or challenge resolution. Re-admission must never revive old request identities, clear historical consumed keys, or bypass the already-frozen product/security/business authorization boundaries after trust discontinuity.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; façade/session/request/effect/registry/application-idempotency/install-retention/bounded-capacity/archive/DR/escrow/human-reroot/post-reroot/client/provider-capability/UNKNOWN-oracle/manual-resolution/canonical-evidence/challenge contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
