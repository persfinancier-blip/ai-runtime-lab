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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected live open issues and open draft PRs. GitHub connector is healthy. PR #165 remains open/draft at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.

Re-probed LAB-086 direct transport in this runtime: `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab` failed before repository access with `Could not resolve host: github.com` (exit 128). Connector exposes repository bytes and normal Contents writes but still no supported machine operation observed in this run that consumes exact predecessor bytes + retained unified patch and emits transformed bytes. `strict_fence.py` was not model-reserialized/mutated; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `MANUAL_RECONCILIATION_CANONICAL_CASE_EVIDENCE_VERIFIER_STATE_MACHINE_V1_FROZEN` in `research/2026-09-05-manual-reconciliation-canonical-case-evidence-schema-verifier-state-machine-v1.md`, main commit `fc268e30c997cdbb3937dc15526511e1df52ddf8`; #178 comment `5550823607` records the result.

Key decisions: manual reconciliation objects use one canonical V1 encoding and domain-separated immutable digests; `ReconciliationCaseV1`, evidence-source capability declarations, imported evidence, deterministic assessments, reviewer decisions, resolution decisions and redaction overlays are separate immutable object types. Evidence strength is capped by a versioned source capability covering retention/consistency/scope; missing evidence is never absence proof and repeated weak negatives never promote by count. Corrections are append-only supersessions. Terminal verdicts remain only `COMMITTED`, `NOT_COMMITTED`, `UNRESOLVED`; no state can free the original application key/provider token or create resend authority. Authoritative appends use case-head CAS plus the existing LAB-097..100 global provenance/recovery protocol. Redaction is presentation-only and cannot change verifier inputs. A 72-case RED-first matrix is frozen. No production code or behavioral PASS is claimed.

Primary donors recorded in the artifact: RFC 8785 JSON Canonicalization Scheme; RFC 8949 deterministic CBOR as a future-format donor only; NIST SP 800-53 Rev.5 AU controls; NIST SP 800-92 log-management/retention concepts.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade, session/request/effect registry, application-idempotency/result delivery, authenticated retention/archive/DR/escrow/re-root/epoch/provider-capability/UNKNOWN-oracle/manual-resolution contracts, including the new canonical case/evidence verifier schema; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-re-root cutover or manual consequential re-attempt may be activated without the required explicit product/security/business authorization bound to the exact payload/effect under the frozen contracts.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze a **manual-reconciliation source-capability revocation / evidence-compromise / verdict-challenge lifecycle contract**. Define how a later-discovered compromised source, overstated retention/consistency declaration, provider drift, revoked reviewer/authorizer credential, or corrupted sealed artifact invalidates future trust in affected evidence without deleting it; how historical assessments/verdicts are marked challenged and re-evaluated through append-only supersession; whether `COMMITTED` versus `NOT_COMMITTED` receive asymmetric fail-closed treatment; exact propagation into global provenance/startup/delegation; and the boundary beyond which automation must stop and require security-owner adjudication. The lifecycle must never rewrite the old effect, reuse its provider token/application key, or convert a challenged verdict into resend authority.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; façade/session/request/effect/registry/application-idempotency/install-retention/bounded-capacity/archive/DR/escrow/human-reroot/post-reroot/client/provider-capability/UNKNOWN-oracle/manual-resolution/canonical-evidence-verifier contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
