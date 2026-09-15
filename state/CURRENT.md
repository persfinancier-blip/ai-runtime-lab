# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue LAB-095/#180 + LAB-096/#181 composition on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187, current head `4174376b6b48459ce62e009c1c44e5ea67ed33fc`; keep draft.
- #169 LAB-090: draft PR #175; activation behavior still must be ported semantically.
- #176 LAB-092: draft PR #177 retained as donor; shared schema, locked provenance/receipt guard, read-only startup gate, explicit migration writer, and focused writer regressions are adapted onto PR #187.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.
- Retained drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173.

## Last completed step
LAB-086 was probed first. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

Fallback work added `tests/test_activation_schema_migration_writer.py` to PR #187. The focused file-backed SQLite harness covers partial DDL fail-closed/no repair; unrelated PREPARED blocking both fresh install and exact migration PREPARED resume; stale runtime generation before DDL installation; exact PREPARED idempotent resume; and CONFIRMED marker with corrupt DDL fail-closed/no repair. An audit caught that the first test slice covered unrelated PREPARED only during resume; the fresh-install variant was added before handoff. No production code changed in this run.

Branch test commit/current head: `4174376b6b48459ce62e009c1c44e5ea67ed33fc`, test blob `58abd5641e32e8626f71226d41a3d844c3f4785a`. Durable evidence: `research/2026-09-15-lab092-migration-writer-focused-regressions.md`, main commit `de940406d1b806339549e71bcad73a26dde33dc6`. PR #187 updated.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; the newly committed migration-writer regressions are coverage, not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 construction-bound history strategy, least-capability public view, and same-transaction receipt guard are source-patched on PR #187 but still need exact repository behavioral gates.
- LAB-090 PR #175 and LAB-092 PR #177 remain source-incompatible with LAB-096 if authority-heavy files are selected wholesale. Port semantics only.
- LAB-092 startup/migration writer remains intentionally opt-in until LAB-090 activation fencing/recovery semantics are composed.
- LAB-092 receipt provenance must remain checked through supplied locked `q` inside the receipt transaction; no out-of-transaction precheck.
- Final composition must preserve activation fencing, provenance fail-closed behavior, `CanonicalDatabaseBinding`, construction-bound provider-history strategy, least-capability public inspection, and same-transaction provenance guard.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem; do not manually reserialize the large security-critical closure.

If LAB-086 remains transport-blocked, inspect LAB-090 PR #175 and port the smallest activation fencing/recovery semantic slice onto PR #187. Preserve private `_history()` locked authority, canonical DB binding, construction-bound history strategy, least-capability public inspection, and same-transaction LAB-092 provenance guard. Do not select PR #175 `supported.py` wholesale. Add focused regression coverage at the same abstraction level before expanding the port.

Composition order: PR #187 structural authority base -> shared `activation_schema.py` -> locked LAB-092 classifier/receipt guard -> read-only startup gate -> explicit migration writer -> focused migration regressions -> LAB-090 activation fencing semantics -> exact/downstream gates.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB binding implemented; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; source fixes present; exact/downstream validation pending.
- #169 LAB-090 — retained draft; activation behavior semantic port is next fallback step.
- #176 LAB-092 — retained draft; focused migration-writer regressions committed, exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
