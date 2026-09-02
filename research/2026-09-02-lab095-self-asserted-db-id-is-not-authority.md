# LAB-095 — a self-asserted SQLite database ID is not sufficient authority binding

Date: 2026-09-02
Issue: #180

## Context

LAB-095 already established two problems:

1. `ledger.path` / `provider_history.path` are publicly rebindable authority references.
2. Making the pathname private/read-only is still insufficient because every `_con()` reopens SQLite by pathname; the same pathname can later resolve to a replacement file.

The previous preferred direction was to evaluate a durable database-instance identifier verified on each fresh connection. This audit tightens that requirement.

## New finding

A database-instance identifier that is merely generated and stored inside the same SQLite database is **self-asserted metadata**, not an authenticated authority binding.

If the supported object opens path `P`, and `P` is replaced with DB B, a check like:

- `SELECT database_instance_id FROM meta`
- compare to a remembered construction-time value

can distinguish an independently-created B only if B has a different ID. It does not establish that the opened file is authorized:

- a copied/cloned DB preserves the same ID;
- an actor able to substitute a writable SQLite file can also construct/copy a file containing the expected unkeyed ID;
- pathname canonicalization, inode/device identity, or a plain UUID describe storage identity but do not prove authenticated ledger/history continuity.

Therefore LAB-095 must not be closed by adding only `_path` + read-only `path`, `Path.resolve()`, inode checks, or an unauthenticated UUID table.

## Existing source mechanisms that can carry authority

`DurableProviderHistory.verify_durable()` already authenticates a stronger logical history identity:

- the first generation must match the retained bootstrap generation ID;
- every generation descriptor is content-addressed;
- each transition must match proofs derived from the old and new generation material;
- the durable head must equal the final authenticated descriptor;
- historical receipts must verify against authenticated generation material.

`HistoricalSharedAnchorLedger.verify_durable()` composes that provider-history verification with ledger contiguity, receipt bindings, PREPARED-tail rules, and component watermarks.

But ordinary mutation paths such as `reserve()` do not run the complete history verifier on each newly-opened target. They call `_current_locked(q)`, which validates the current head descriptor but not bootstrap-to-head continuity. This is why same-path substitution to a superficially matching but invalid-history DB remains possible at source level.

## Required contract refinement

The lifetime binding should be to an **authenticated logical database/history identity**, not merely a filesystem object.

A safe implementation direction must provide one of the following, with equivalent strength:

1. **Full authenticated revalidation on each fresh connection before authority use.**
   - Retain an immutable construction-bound bootstrap/root (LAB-094 must make this actually immutable).
   - Open a raw connection.
   - Before any supported authority decision or mutation on that connection, verify complete provider-history continuity against the retained root and the relevant ledger invariants needed for that operation.
   - Only then expose/use the connection as an authorized ledger connection.
   - Avoid recursive `_con() -> verify_durable() -> _con()` design; split raw connection creation from checked connection admission.

2. **A cheaper authenticated database-instance binding whose authenticity is anchored outside self-asserted SQLite metadata.**
   - For example, bind a database-instance identifier into an already authenticated construction root / transition / external-anchor protocol and protect subsequent uses through the existing writer boundary.
   - The identifier must not be accepted solely because the currently-opened SQLite file says it has that value.

The exact performance/design choice should be made during implementation, but the security criterion is invariant: a replacement DB cannot become authoritative merely by copying or choosing a metadata identifier.

## Clone boundary

A byte-for-byte/current-state clone of an already authenticated DB is logically different from an independently forged invalid-history DB. If the clone preserves the complete authenticated history, it may be indistinguishable at the SQLite-history layer by design; rollback/freshness is delegated to the external monotonic-anchor layer. LAB-095 therefore should not invent inode identity as a cryptographic property. Its responsibility is to prevent a constructed supported capability from silently accepting a different **unauthenticated logical history** through path/file substitution.

## Regression refinement

In addition to the existing DB-A -> same-path DB-B regression:

1. DB A: valid bootstrap g1 -> current g2 history; construct supported ledger successfully.
2. DB B: same pathname after replacement, same superficial current g2 descriptor/head, but missing/corrupt g1 -> g2 continuity.
3. Give DB B any plain `database_instance_id` value equal to A's expected value.
4. Pre-fix/source expectation: shallow current-head / unkeyed-ID checks are insufficient; a mutation path can address B without full construction-equivalent history validation.
5. Post-fix: fail closed before `reserve`, `execute`, `rotate_provider`, receipt mutation, or other authority mutation because the newly-opened target cannot prove the authenticated logical history rooted at the construction-bound bootstrap.

A separate clone case should confirm the fix does not pretend filesystem inode identity is the trust root: a complete authenticated clone is handled by existing external-anchor freshness/reconciliation semantics rather than by a plain-path or UUID test.

## Composition requirements

- LAB-094/#179: bootstrap/root must itself be construction-bound; otherwise per-connection history verification can be redirected by rebinding the root.
- LAB-096/#181: the provider-history strategy used to perform verification must also be construction-bound; otherwise a replacement strategy can make an invalid DB appear valid.
- LAB-093/#178: attested/provider capability encapsulation is orthogonal; do not use external-handle hiding as a substitute for DB/history authentication.
- LAB-087/LAB-091 remain the writable-process / authorized-DML boundaries; LAB-095 should compose with them rather than duplicate them.

## Decision

Update LAB-095 acceptance: **do not accept a self-asserted durable database UUID as sufficient.** The protected object must re-establish authenticated logical-history identity whenever a fresh SQLite target is opened for authority use, or use an equivalently strong externally/authenticated instance binding.

No production code or behavioral PASS is claimed in this run because exact repository execution remains unavailable. This is a source-level contract refinement only.
