# Current Lab State

Last updated: 2026-09-15

## Active objective
LAB-086 remains priority #1: execute the exact asymmetric break-glass history migration gate from authoritative executable pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. When byte-exact materialization remains unavailable, continue LAB-095/#180 + LAB-096/#181 composition on draft PR #187. LAB-099 PREPARED authority waits on LAB-095 completion.

## Active issue / branch / PR
- #163 / LAB-086: draft PR #165; keep draft.
- #180 LAB-095 + #181 LAB-096: branch `lab-095-database-identity-red-intent`, draft PR #187; keep draft.
- #169 LAB-090: draft PR #175 retained as donor; provider fence, pre-ack SQL transition, durable acknowledgement, supported-ledger rotation wiring, and restart/historical recovery are now ported to PR #187.
- #176 LAB-092: draft PR #177 retained as donor; shared schema, locked provenance/receipt guard, read-only startup gate, explicit migration writer, and focused writer regressions are adapted onto PR #187.
- #184 LAB-099: draft PR #186; blocked on LAB-095 completion.

## Last completed step
LAB-086 was probed first. Direct clone failed before repository execution with `Could not resolve host: github.com`, exit 128; no LAB-086 PASS is claimed.

Fallback work ported LAB-090 restart recovery from PR #175 onto PR #187 without restoring donor public provider-history authority. `ActivationCoordinatorMixin._recover_pending_activation()` uses private `_history().current()` and reconciles durable-current `SQL_COMMITTED`/`COMMITTED` against provider `PREPARED`/`COMMITTED_FENCED`/`RELEASED`, rejects premature release and ABSENT reservation, then fails closed if any historical generation remains `SQL_COMMITTED`. It is invoked after runtime/durable-head verification in supported-ledger construction. Branch commits: `ce6bdab3eb3c34a9d9165fad8d3b522197d21527`, `af8a22e520f1a2aab30e72f899aad04b25a07935`. Evidence: `research/2026-09-15-lab090-restart-recovery-port.md`, main commit `a66d026b2957ab46d1876592a8756134b8a316a2`.

## Known failures / blockers
- LAB-086 complete real-ledger gate remains unexecuted because shell DNS cannot resolve GitHub and no supported connector-to-filesystem byte-preserving bridge is exposed.
- Exact PR #187 repository pytest/compileall remains unavailable for the same materialization reason; committed/source-reviewed regressions are not a GREEN claim.
- PRs #165/#172/#173/#175/#177/#186/#187 remain draft until retained exact gates execute.
- LAB-095 complete eight-file no-stub tree still needs same-run reconstruction/hash verification plus execution.
- LAB-096 source fixes still need exact repository behavioral gates.
- LAB-090 restart recovery is source-composed but focused regressions for restart windows/premature release/ABSENT/historical unresolved remain to be added and executed when possible.
- LAB-092 startup/migration remains intentionally opt-in; startup ordering with LAB-090 recovery needs an explicit audit so recovery never queries an uninstalled/unconfirmed activation schema.

## Exact next action
Probe LAB-086 first. Execute its complete gate only if authoritative pin `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` can be placed byte-for-byte into an executable filesystem.

If LAB-086 remains transport-blocked, audit PR #187 constructor ordering against LAB-092 activation-schema classification before adding more behavior. Ensure `_recover_pending_activation()` cannot query `provider_generation_activations` unless the exact LAB-090 schema is classified COMPLETE; preserve explicit migration semantics for absent/unmarked/PREPARED states. Then add focused regressions for SQL_COMMITTED+PREPARED, SQL_COMMITTED+COMMITTED_FENCED, premature RELEASED, ABSENT reservation, and historical unresolved activation. Do not claim GREEN without execution.

## Backlog
- #163 LAB-086 — IN_PROGRESS; exact executable gate pending.
- #180 LAB-095 — IN_PROGRESS; DB binding implemented; exact/downstream gates pending.
- #181 LAB-096 — IN_PROGRESS/COMPOSED ON PR #187; exact/downstream validation pending.
- #169 LAB-090 — restart/historical recovery source-composed; startup-order audit + regressions next.
- #176 LAB-092 — migration/startup/provenance layers composed; exact execution pending.
- #167 LAB-088, #170 LAB-091 — retained draft gates pending.
- #178..185 LAB-093..100 — architecture/security follow-ups.
- #184 LAB-099 — PREPARED authority waits on LAB-095 completion.
