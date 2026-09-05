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
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs. LAB-086 remains first priority and the draft stack is unchanged.

Probed LAB-086 first in this runtime with a real `git clone --no-checkout`. Git transport again failed before repository access with `Could not resolve host: github.com` (exit 128). The connector remains readable/writable, but no supported machine bridge was observed that can consume exact connector-returned predecessor bytes plus the retained patch and mechanically emit the byte-verified composed target without model reserialization. Security-critical `strict_fence.py` therefore remains untouched; no new LAB-086 behavioral PASS is claimed.

Completed the recorded distinct fallback: froze `FINAL_REQUEST_FREEZE_TRANSPORT_INTERPOSITION_INTEGRITY_LAZY_SIGNING_V1_FROZEN` in `research/2026-09-05-final-request-freeze-transport-interposition-integrity-lazy-signing-v1.md`, main commit `0762867468a2b2b2f23995323b132c7636fb593b`; #178 comment `5553467186` records the result.

Key decisions: a provider-semantic equivalence PASS is insufficient while any layer closer to the network can still mutate or duplicate a consequential request. `FrozenFinalRequestV1` binds the exact attested request to a network-adjacent `FinalSendGateDeclarationV1`; one durable `TransportAttemptV1` CAS binds exactly one frozen request to one transport attempt. Consequential redirects are denied by default; hidden SDK retries/transparent retries/gRPC hedging are forbidden unless every wire attempt is authority-visible and proven same-provider-identity safe. Lazy signing after freeze is allowed only for declared `AUTH_REFRESHABLE` fields followed by final semantic re-observation. Proxies/service meshes/endpoint resolvers that can rewrite semantics belong inside the authority dependency surface. Generic one-pass streaming is not admitted where equality is knowable only after provider-visible bytes leave the process. Crash/timeout after `SEND_STARTED` remains UNKNOWN-safe and cannot mint new SEND authority. An 80-case RED-first matrix is frozen. No production code or behavioral PASS is claimed.

Primary donors recorded: RFC 9110 redirect semantics; gRPC interceptor order/network-near guidance; AWS SDK for Go v2 staged request middleware; AWS SDK retry behavior.

## Known failures / blockers
- LAB-086 remains priority #1. Do not manually/model-reserialize security-critical `strict_fence.py`.
- Exact predecessor and retained patch bytes are observable through the connector, but no supported byte-preserving transform/materialization bridge to a Contents API replacement has been observed.
- Direct git transport in this run failed before repository access with DNS resolution failure.
- Normal Contents API requires complete replacement text and is not a predecessor+patch transform.
- Authoritative lineage remains `d4a6a40f...` + `61841b58...` -> `b78e7c98...`.
- Keep PRs #165/#172/#173/#175/#177 draft until retained exact gates execute.
- LAB-088 still needs supported integration + LAB-084/085/086 downstream execution.
- LAB-091 still needs real LAB-080/LAB-082 integration, two-worker/crash, timeout-after-commit/UNKNOWN, LAB-087 composition and full exact regressions.
- LAB-090/LAB-100, LAB-092 and LAB-097..099 must use the frozen shared canonical V1 encoding, parent-linked chain, atomic append/recovery protocol, durable SQL storage, verifier/planner, external evidence continuity, recovery executor and finite broker startup machine; no independent locally-valid provenance islands.
- LAB-093 must implement the frozen least-capability façade, session/request/effect registry, application-idempotency/result delivery, authenticated retention/archive/DR/escrow/re-root/epoch/provider-capability/UNKNOWN-oracle/manual-resolution/canonical-evidence/challenge/quarantine/authority-manifest/effective-authority-lease/retry-authority/replay-capsule/semantic-extractor/final-request-freeze contracts; production implementation waits for executable RED/GREEN.
- LAB-093..100 production implementation waits for exact executable RED/GREEN.
- No production post-reroot cutover, re-admission after trust discontinuity, or manual consequential re-attempt may be activated without required explicit product/security/business authorization bound to the exact payload/effect.

## Exact next action
LAB-086 first: probe only for a genuinely supported machine transform/materialization path that can consume the exact connector-returned predecessor blob plus retained patch bytes without model reserialization.

If such a bridge appears: mechanically reconstruct predecessor and require Git blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`; apply only patch blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`; require candidate blob `b78e7c98e35138719f77c482c7f1aab36b702de7`; publish through normal Contents API; re-fetch/hash-verify; then execute hidden-rowid + receipt-NULL + alternate-UNIQUE regressions, strict/thaw subgate, LAB-080→086 real-ledger gate, unsafe legacy-promotion seed, compileall and final audit.

If exact source execution becomes available first: run LAB-088 supported/downstream gates, LAB-091 full supported-surface gates, then implement tests first for the frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

If neither capability appears: next distinct evidence task is to freeze a **transport-attempt egress observation / first-I/O proof + ambiguity classifier contract**. Define the evidence required to distinguish `FAILED_BEFORE_IO` from `UNKNOWN` at the final send boundary across HTTP/1.1, HTTP/2, gRPC, proxies and TLS; specify what socket/client-library callbacks are trustworthy enough, how partial writes/connection reuse/proxy acceptance are classified, how durable `SEND_STARTED` composes with first-byte/first-frame evidence, and why absence of a response or local exception is never proof of zero provider-visible I/O. Include exact conformance fixtures for pre-I/O failure, partial write, reused connection, proxy-forward ambiguity, HTTP/2 stream reset, TLS failure, cancellation and crash. Keep read-only/offline until executable RED/GREEN exists.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact hidden-rowid publication/full gate pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; activation authority + canonical/global provenance/recovery contracts frozen; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; migration bound to retained authority graph + global provenance/recovery contracts; exact RED/full gate pending.
- #178 / LAB-093 — READY; façade/session/request/effect/registry/application-idempotency/install-retention/bounded-capacity/archive/DR/escrow/human-reroot/post-reroot/client/provider-capability/UNKNOWN-oracle/manual-resolution/canonical-evidence/challenge/quarantine/authority-manifest/effective-authority-lease/retry-authorization/replay-capsule/semantic-extractor/final-request-freeze contracts frozen; exact RED/GREEN pending.
- #179..181 / LAB-094..096 — READY; unified retained-authority graph + RED matrix frozen.
- #182..184 / LAB-097..099 — READY; authenticated provenance/global chain/recovery contracts frozen.
- #185 / LAB-100 — READY; sealed/registered activation authority + construction/restart/upgrade/global provenance/recovery contracts frozen.
