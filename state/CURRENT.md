# Current Lab State

Last updated: 2026-09-05

## Active objective
LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to authenticated cutoff + Ed25519 public-only history without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165; live PR head remains `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- Authoritative pending lineage: predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; retained hidden-rowid patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; required composed target blob `b78e7c98e35138719f77c482c7f1aab36b702de7`.
- Draft/IN_PROGRESS stack remains open: LAB-088/#167 PR #172; LAB-090/#169 PR #175; LAB-091/#170 PR #173; LAB-092/#176 PR #177.
- Frozen design follow-ups: LAB-093/#178; LAB-094..096/#179..181; LAB-097..099/#182..184; LAB-100/#185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs. Connector remains healthy and the draft stack remains open.

LAB-086 was probed first. A potentially useful route was tested: the connector can read the exact Git blob for predecessor `d4a6a40f...`, and PR #165's `strict_fence.py` at head `ee210a...` is observable through `fetch_file`. However, no supported machine bridge in this runtime can transfer those exact connector-returned bytes into a local patch engine or Contents API replacement payload without model reserialization. Direct raw/container materialization was also unavailable. Security-critical `strict_fence.py` therefore remains untouched; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `PROVIDER_SEMANTIC_REQUEST_EXTRACTOR_POST_SIGNING_EQUIVALENCE_ATTESTATION_V1_FROZEN` in `research/2026-09-05-provider-semantic-request-extractor-post-signing-equivalence-attestation-v1.md`, main commit `3c67424bb466c9191d71b895e3876060f2897fca`; #178 comment `5553127560` records the result.

Key decisions: replay compatibility becomes executable evidence. A provider/adapter-specific extractor derives one canonical authority-relevant semantic request from both the immutable replay capsule and the final post-signing/pre-I/O request; domain-separated digests must match immediately before I/O. Unknown/unclassified fields, parser ambiguity, middleware/config/build drift, unobservable lazy signing, unsupported one-pass streaming, or semantic mismatch remove retry/mutation authority. The contract covers endpoint/account/region scope, ordered/duplicate query semantics, semantic/auth/transport header classes, JSON/forms, multipart, content encodings, streaming/chunking, presigned URLs, protobuf schema/unknown-field behavior, SDK defaults and credential rotation. Each admitted adapter generation needs an authenticated directional extractor declaration plus signed positive/negative golden fixtures; an 80-case RED-first matrix is frozen. No production code or behavioral PASS is claimed.

Primary donors recorded: AWS SigV4 canonical-request construction and volatile-header guidance; RFC 9110 HTTP representation/content-coding semantics; RFC 7578 multipart framing/part semantics; Protocol Buffers documentation explicitly stating deterministic serialization is not canonical across builds/schema evolution and generic fingerprinting is unsafe with unknown fields.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade, session/request/effect registry, application-idempotency/result delivery, authenticated retention/archive/DR/escrow/re-root/epoch/provider-capability/UNKNOWN-oracle/manual-resolution/canonical-evidence/challenge/quarantine/authority-manifest/effective-authority-lease/retry-authority/replay-capsule/semantic-extractor contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-reroot cutover, re-admission after trust discontinuity, or manual consequential re-attempt may be activated without required explicit product/security/business authorization bound to the exact payload/effect.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze a **final-request freeze / transport interposition integrity + lazy-signing admission contract**. Define the exact handoff between post-signing semantic attestation and external I/O so no middleware, serializer, redirect handler, retry layer, HTTP client, gRPC interceptor, proxy selector or lazy signer can mutate authority-relevant semantics after PASS. Define immutable request representations, transport-hook placement, redirect policy, connection/proxy/DNS boundaries, one-pass streaming rejection, attestation-to-send sequence/CAS, crash semantics, and signed conformance fixtures proving post-attestation mutation is impossible or detected. Keep read-only/offline until executable RED/GREEN exists.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; façade/session/request/effect/registry/application-idempotency/install-retention/bounded-capacity/archive/DR/escrow/human-reroot/post-reroot/client/provider-capability/UNKNOWN-oracle/manual-resolution/canonical-evidence/challenge/quarantine/authority-manifest/effective-authority-lease/retry-authorization/replay-capsule/semantic-extractor contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
