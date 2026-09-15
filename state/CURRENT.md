# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue LAB-095/#180 + LAB-096/#181 composition on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187, current head `2d285a639527584503fce79b40fdf8fed8f8f636`; keep draft.
- #169 LAB-090: draft PR #175 retained as donor; provider-owned activation fence primitive is now semantically ported to PR #187; coordinator persistence/recovery remains.
- #176 LAB-092: draft PR #177 retained as donor; shared schema, locked provenance/receipt guard, read-only startup gate, explicit migration writer, and focused writer regressions are adapted onto PR #187.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173.

## Last completed step
LAB-086 was probed first. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

Fallback work ported the smallest LAB-090 provider-owned activation fencing semantic slice from PR #175 onto PR #187 as new `experiments/provider_generation_history/activation.py`; LAB-090 `supported.py`/`integration.py` were not selected. The primitive provides exact-position prepare, monotonic provider-owned fence tickets, PREPARED/COMMITTED_FENCED blocking of ordinary increment, exact-ticket release, unknown-commit reconciliation, and provider-state persistence across coordinator reconstruction. It has no ledger/database/history/receipt authority.

Added `tests/test_activation_fence_composed.py` covering fence-before-release, stale candidate/wrong ticket fail-closed, and UnknownOutcome + restart fence persistence. Exact repository execution is not claimed because connector bytes still cannot be materialized byte-for-byte into the executable filesystem. Branch production commit `c93cb6f7113d39d6437805eb58b95b1108cc7106`; test/current head `2d285a639527584503fce79b40fdf8fed8f8f636`. Durable evidence: `research/2026-09-15-lab090-provider-fence-semantic-port.md`, main commit `3c8e71cf2d6e897d7d0351658719cefc95f53168`.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed regressions are coverage, not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 construction-bound history strategy, least-capability public view, and same-transaction receipt guard are source-patched on PR #187 but still need exact repository behavioral gates.
- LAB-090 coordinator activation persistence/recovery semantics still need composition: SQL_COMMITTED/COMMITTED acknowledgement ordering, restart reconciliation, overlapping-rotation block, historical unresolved fail-closed handling.
- LAB-090 PR #175 and LAB-092 PR #177 remain source-incompatible with LAB-096 if authority-heavy files are selected wholesale. Port semantics only.
- LAB-092 startup/migration writer remains intentionally opt-in until remaining LAB-090 coordinator activation semantics are composed.
- LAB-092 receipt provenance must remain checked through supplied locked `q` inside the receipt transaction; no out-of-transaction precheck.
- Final composition must preserve activation fencing, provenance fail-closed behavior, `CanonicalDatabaseBinding`, construction-bound provider-history strategy, least-capability public inspection, and same-transaction provenance guard.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem; do not manually reserialize the large security-critical closure.

If LAB-086 remains transport-blocked, inspect LAB-090 PR #175 coordinator activation persistence/recovery call sites and port the smallest next semantic slice onto PR #187: exact activation-ticket durable record plus SQL_COMMITTED -> provider COMMITTED_FENCED -> durable COMMITTED -> exact-ticket release ordering. Route all locked history authority through private `_history()`, preserve canonical DB binding/construction-bound history strategy, and keep LAB-092 provenance checks inside caller-owned transactions. Add focused regression coverage before expanding into restart/historical recovery.

Composition order: PR #187 structural authority base -> shared `activation_schema.py` -> locked LAB-092 classifier/receipt guard -> read-only startup gate -> explicit migration writer -> focused migration regressions -> LAB-090 provider fence primitive -> LAB-090 coordinator activation persistence/ack ordering -> restart/historical recovery -> exact/downstream gates.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB binding implemented; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; source fixes present; exact/downstream validation pending.
- #169 LAB-090 — retained draft; provider fence primitive ported, coordinator persistence/recovery is next fallback step.
- #176 LAB-092 — retained draft; migration/startup/provenance layers composed, exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
