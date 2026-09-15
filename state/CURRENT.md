# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue LAB-095/#180 + LAB-096/#181 composition on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187, current head `a0404909bd144f4527ec364fac5b484f40339dea`; keep draft.
- #169 LAB-090: draft PR #175 retained as donor; provider fence primitive and post-SQL durable acknowledgement ordering are now semantically ported to PR #187; pre-ack SQL transaction and restart/historical recovery remain.
- #176 LAB-092: draft PR #177 retained as donor; shared schema, locked provenance/receipt guard, read-only startup gate, explicit migration writer, and focused writer regressions are adapted onto PR #187.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173.

## Last completed step
LAB-086 was probed first. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

Fallback work audited PR #175 coordinator call sites and ported only the post-SQL activation acknowledgement primitive to PR #187 as `experiments/provider_generation_history/activation_coordinator.py`. The isolated mixin preserves `SQL_COMMITTED -> provider COMMITTED_FENCED -> durable exact-ticket COMMITTED -> RELEASED`, reconciles `UnknownOutcome` through provider status, and owns no construction/database/history/schema/receipt authority. Added `tests/test_activation_coordinator_ordering.py` for normal commit, unknown-outcome reconciliation, and wrong-fence fail-closed non-release. Production commit `39c05ee36bf3105a68db657b434bc128a6137db9`; regression/current head `a0404909bd144f4527ec364fac5b484f40339dea`. Durable evidence: `research/2026-09-15-lab090-durable-activation-ack-ordering.md`, main commit `c7b8d77e695fd7c7d5b46b60ebb4ca47091e6784`.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed regressions are coverage, not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 construction-bound history strategy, least-capability public view, and same-transaction receipt guard are source-patched on PR #187 but still need exact repository behavioral gates.
- LAB-090 pre-ack coordinator transaction still needs composition: exact prepare ticket, under-lock tail/unresolved/PREPARED rechecks, atomic `SQL_COMMITTED` ticket + private `_history()._rotate_locked(q, ...)`, then the newly ported acknowledgement primitive.
- LAB-090 restart reconciliation, overlapping-rotation block, and historical unresolved fail-closed handling remain after that transition slice.
- LAB-090 PR #175 and LAB-092 PR #177 remain source-incompatible with LAB-096 if authority-heavy files are selected wholesale. Port semantics only.
- LAB-092 startup/migration writer remains intentionally opt-in until remaining LAB-090 coordinator activation semantics are composed.
- LAB-092 receipt provenance must remain checked through supplied locked `q` inside the receipt transaction; no out-of-transaction precheck.
- Final composition must preserve activation fencing, provenance fail-closed behavior, `CanonicalDatabaseBinding`, construction-bound provider-history strategy, least-capability public inspection, and same-transaction provenance guard.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem; do not manually reserialize the large security-critical closure.

If LAB-086 remains transport-blocked, port the next smallest LAB-090 coordinator slice onto PR #187: prepare the exact activation ticket, then under one `BEGIN IMMEDIATE` re-check no unresolved `SQL_COMMITTED` activation, no PREPARED shared-anchor intent, and unchanged reserved tail; insert the exact `SQL_COMMITTED` activation row and call private `_history()._rotate_locked(q, new, proof)` in that same transaction. On pre-commit failure abort only the exact provider ticket; after SQL commit invoke the already ported `ActivationCoordinatorMixin` acknowledgement path. Add focused regression coverage before expanding into restart/historical recovery.

Composition order: PR #187 structural authority base -> shared `activation_schema.py` -> locked LAB-092 classifier/receipt guard -> read-only startup gate -> explicit migration writer -> focused migration regressions -> LAB-090 provider fence primitive -> LAB-090 durable acknowledgement ordering -> LAB-090 pre-ack SQL transition -> restart/historical recovery -> exact/downstream gates.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB binding implemented; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; source fixes present; exact/downstream validation pending.
- #169 LAB-090 — retained draft; provider fence + durable acknowledgement ported; pre-ack SQL transition is next fallback step.
- #176 LAB-092 — retained draft; migration/startup/provenance layers composed, exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
