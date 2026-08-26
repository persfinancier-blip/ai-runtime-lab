# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `4d3da21ef2f8c0f782f5ce0146a04aaea0b62251`.
- PR remains draft; exact real-ledger current-head gate is incomplete.
- LAB-088 / Issue #167 is IN_PROGRESS on draft PR #172.
- LAB-091 / Issue #170 is now IN_PROGRESS on branch `lab/091-mutable-shared-anchor-writer`, draft PR #173.

## Last completed step

Resumed LAB-086 first and re-read the current `migration_guard.py`, `strict_fence.py`, `suffix.py`, and `final_supported.py`. No new privilege-escalation/stale-supported-writer blocker was established. Reverse cardinality still covers lower root/provider/threshold evidence before cutoff; post-cutoff public/evidence/current-authority DML surfaces remain behind the least-privilege transaction-scoped fence. The remaining blocker is execution evidence, not a newly identified runtime flaw.

Direct shell/raw GitHub transport was reprobed and still fails. A useful connector capability was confirmed: `fetch_blob` returns complete exact Git blob contents by SHA, so byte-exact LAB-080→086 reconstruction can continue without path/ref ambiguity. The full dependency closure was not completed in this run, so no new LAB-086 PASS is claimed.

While that exact reconstruction remains the primary gate, advanced already-tracked unblocked LAB-091 rather than repeating source audits. Built and published a reference broker-owned mutable-writer boundary for LAB-080/LAB-082 state. A connection-local `lab091_writer_authorized()` predicate is true only inside an audited `BEGIN IMMEDIATE`; triggers permit only fresh reserve + tail CAS, exact `PREPARED -> CONFIRMED`, monotonic watermark advancement and fresh provider-receipt append.

Development testing found an `INSERT OR REPLACE` bypass for an existing receipt. The corrected creation guards reject already-existing intent/request/position/component identities even while the broker writer context is active.

Exact published LAB-091 evidence:
- `protocol.py` blob `f0a3e284823a723a049f32d2ac7603c7997afc72`;
- corrected test blob `1bd08f1b216a7bd8c785812b37514ab223340d6d`;
- corrected suite **11/11 PASS**;
- compileall PASS;
- unsafe raw-DML seed blob `e4c1bc62a102f7bb3ad91c4f2db176a181b87aac` FAILED as intended because unrestricted SQL changed `reserved_position` from 0 to 99.

The LAB-091 negative control also proves the boundary explicitly: a separate unrestricted writable connection can register a spoofed same-name UDF and mutate the DB. Therefore LAB-091 is defense-in-depth on the broker-owned writable handle and depends on merged LAB-087 for the actual process/filesystem sole-writable-handle boundary. Draft PR #173 is reference-only until real LAB-080/LAB-082 integration passes.

## Evidence produced / reconfirmed

LAB-086 cumulative exact lower-stack evidence remains:
- LAB-080 18/18 PASS.
- LAB-082 28/28 PASS.
- LAB-083 24/24 PASS on pre-LAB-088 main source.
- LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS, asymmetric-custody 8/8 PASS, public/final 11/11 PASS.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.
- Current LAB-086 migration guard blob: `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
- Current LAB-086 least-privilege fence blob: `5da01e28a9f813a136d138637f855940f04aab46`.
- Current LAB-086 suffix blob: `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`.
- Current LAB-086 final-supported blob: `ceb7f48a55a931ba9923cac77d4ebf6c4cd2cfec`.

LAB-088 exact evidence remains:
- exact published signer-noise suite 6/6 PASS;
- existing LAB-083 protocol/enablement/strict-type regressions 16/16 PASS on corrected source;
- combined 22/22 PASS + compileall PASS;
- draft PR #172 remains pending supported/downstream compatibility.

LAB-087 is merged/DONE with final exact 14/14 PASS + compileall PASS.

LAB-091 new exact evidence:
- draft PR #173, branch `lab/091-mutable-shared-anchor-writer`;
- protocol `f0a3e284823a723a049f32d2ac7603c7997afc72`;
- tests `1bd08f1b216a7bd8c785812b37514ab223340d6d`;
- corrected 11/11 PASS + compileall PASS;
- unsafe raw-DML seed `e4c1bc62a102f7bb3ad91c4f2db176a181b87aac` FAILED as expected;
- explicit negative control proves a writable connection that can register its own UDF can spoof the SQL predicate, so LAB-087 composition is mandatory.

## Known blockers / constraints

- LAB-086 remaining merge gate: execute `test_pre_cutoff_lower_evidence_cardinality.py`, then the full current-head real-schema migration/suffix/final-supported/security suite from one exact LAB-080→086 dependency closure; run unsafe seed, compileall and final audit.
- Direct shell/raw GitHub transport remains unavailable. GitHub connector reads and exact blob-by-SHA fetch work; file-by-file reconstruction remains the safe execution path.
- PR #165 is substantially diverged from current `main`; do not reconcile/integrate until the complete test/security gate is clean.
- LAB-088 PR #172 must remain draft until supported/downstream regressions pass.
- LAB-091 PR #173 must remain draft until the reference writer is integrated behind the real LAB-080/LAB-082 supported paths. The final supported surface must not expose an unrestricted broker writable connection.
- LAB-091 UDF/triggers are not security against another unrestricted writable SQLite connection; LAB-087 supplies that process/filesystem boundary.
- LAB-090/#169 provider handoff freshness remains a separate correctness follow-up.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Resume LAB-086 as primary. Use connector `fetch_blob` to finish the exact LAB-080→086 dependency closure required by `test_pre_cutoff_lower_evidence_cardinality.py`, verify every executable file by Git blob and execute that real regression.
2. On the same closure execute current `test_suffix.py` and all remaining LAB-086 migration/final-supported/security modules, then unsafe legacy-promotion seed and full compileall.
3. Perform final LAB-086 security audit and branch/main reconciliation only after tests are clean; keep PR #165 draft until then.
4. LAB-091 follow-up: integrate the already exact-tested writer context into actual `SupportedSharedAnchorLedger` / LAB-082 mutation paths, hide the raw writable connection, and add restart/concurrency/UNKNOWN + LAB-087 composition regressions before considering PR #173 ready.
5. LAB-088 follow-up remains supported/downstream regression gate for PR #172.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact current-head real-ledger gate remains primary.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172, exact 22/22 focused/core PASS, supported/downstream gate remains.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173, exact 11/11 reference PASS + unsafe baseline, real LAB-080/LAB-082 integration remains.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
