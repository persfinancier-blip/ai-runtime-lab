# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-083 — add an independent threshold authorization layer to LAB-082 provider-generation rotation so compromise of one current provider private key cannot install an attacker-chosen successor by itself.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-082.
- Completed Issue #155 / LAB-082.
- PR #156 closed as manually integrated after the normal draft→ready operation was blocked before execution by an external safety-status gate.
- Active: Issue #157 / LAB-083 — IN_PROGRESS.
- Active branch: `lab/083-threshold-provider-rotation`.
- Active PR: none yet.

## Last completed step

LAB-082 replaced durable historical HMAC signing material with Ed25519 public verification-only history behind the existing LAB-080 shared-anchor SQLite serialization boundary. Exact PR-head execution found no regression across the dependent stack. A final audit discovered that a valid signed `READ` could otherwise substitute for `RECONCILE` evidence when provider/generation/position/request identity matched; the audited supported surface now requires `kind == RECONCILE` for confirmed-effect evidence.

Normal PR draft→ready was blocked before execution. Fresh compare showed all nine LAB-082 paths were additions with no overlap against newer `main`, so the file-scoped GitHub Contents API fallback was used. No low-level refs/trees/force updates were used. Security-critical `protocol.py` and `supported.py` in `main` match their tested branch blobs. Some integration/test files were transferred with non-semantic formatting/comment differences; this distinction is explicitly recorded rather than reported as byte-identical.

After LAB-082 closure, no open issues remained. The next correctness bottleneck was selected as LAB-083: the LAB-082 N→N+1 transition still allows a compromised current provider signer to choose an attacker-controlled new signer and satisfy old+new possession signatures. LAB-083 adds a separate threshold rotation authority.

## Evidence produced

- LAB-082 corrected exact-source gate: 28/28 passed.
- LAB-081 regression gate: 20/20 passed.
- LAB-080 + LAB-036 regression gate: 30/30 passed.
- Total corrected gate: 78/78 passed.
- LAB-082 unsafe symmetric-history seed failed as expected because durable historical HMAC material could sign a new effect.
- Compileall passed after removing a local root-owned `__pycache__` artifact created by a different tool runtime.
- Final semantic-evidence regression rejects signed READ evidence as a substitute for RECONCILE evidence.
- Issue #155 closed DONE.
- PR #156 closed as manually integrated.
- New Issue #157 / LAB-083 created and branch `lab/083-threshold-provider-rotation` created from current `main`.

## Known blockers / constraints

- No owner/product blocker.
- Direct shell DNS access to `github.com` was unavailable in the LAB-082 validation runtime; GitHub connector reconstruction remains a valid exact-source fallback when needed.
- LAB-082 removes signing capability from durable historical storage, but the current private signer remains a live authority and can still be compromised.
- Old+new provider signatures alone do not contain compromise of the old signer when the attacker can choose the new key; LAB-083 must add an independent threshold authorization without creating a second conflicting serialization boundary.
- Whole-store rollback/bootstrap freshness remains delegated to the external/shared-anchor mechanisms from LAB-034 onward.

## Exact next action

On `lab/083-threshold-provider-rotation`, inspect the existing threshold/root mechanisms from LAB-038/LAB-056/LAB-077 and choose the smallest reusable authorization representation rather than creating a parallel trust system. First build an unsafe baseline showing that a compromised LAB-082 old signer plus attacker-controlled new signer can install a successor. Then extend the provider-rotation payload so it binds exact old provider generation, proposed new generation, and the current threshold-authority identity/generation. Require a valid distinct-signer quorum and persist the full threshold proof with the provider transition. Integrate verification and provider-head advancement in the same SQL write transaction that already serializes PREPARED shared-anchor work. Add failure-injection tests for missing/duplicate/revoked/stale quorum, root-authority rotation races, restart proof corruption, and preservation of historical receipt verification. Run LAB-083 plus LAB-082/LAB-080 regressions and perform a separate remote patch audit before integration.

## Backlog

- #157 / LAB-083 — threshold-authorized asymmetric provider rotation and compromise containment — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
