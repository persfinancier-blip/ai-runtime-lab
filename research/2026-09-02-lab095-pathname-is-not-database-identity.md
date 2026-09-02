# LAB-095 — pathname immutability is not database identity

Date: 2026-09-02

## Scope

Follow-up source audit for #180 / LAB-095. This note strengthens the existing finding; it does not create a new issue.

## Finding

Making the current public `path` attribute private/read-only is necessary but not sufficient to bind a supported ledger/provider-history object to one database for its lifetime.

`SharedAnchorLedger._con()` opens a fresh SQLite connection from the stored pathname on every operation. Therefore the authority actually consumed by later operations is "whatever database object this pathname resolves to at open time", not necessarily the database that was verified during construction.

A lifetime-stable Python string such as `/state/ledger.db` does not make that target lifetime-stable. The filesystem mapping can change while the string remains identical, for example by replacing/renaming the file between operations or by changing a symlink target. A newly opened `sqlite3.connect(path)` can consequently reach DB B after construction verified DB A, even if application code cannot reassign the stored pathname.

This is the same security/correctness class already tracked by LAB-095: a supported capability can be redirected to a different durable authority without a fresh full construction/verification boundary. It is stronger than the current public-attribute regression because a `_path` + read-only property fix alone would still leave the underlying rebinding route.

## Source relationship

- `experiments/shared_anchor_intent_ledger/protocol.py`: constructor stores a pathname and `_con()` executes `sqlite3.connect(self.path, ...)` for each operation.
- `experiments/provider_generation_history/protocol.py`: provider history independently retains the same style of pathname state.
- composed historical ledger operations pass freshly opened ledger connections into provider-history helpers, so whichever file the pathname resolves to at that moment becomes the effective durable authority.

## Required contract refinement

LAB-095 should bind an object to a **database identity**, not merely an immutable path string.

A correct fix should use one canonical source of truth and prove that every fresh connection still addresses the database accepted at construction. Candidate mechanisms, to evaluate during implementation:

1. Persist a strong database-instance identifier in authenticated/verified durable metadata and verify it on every newly opened connection before any authority decision or mutation.
2. Retain a construction-opened connection/handle when concurrency and lifecycle constraints permit, avoiding pathname re-resolution; this requires careful SQLite threading/process semantics and is not assumed to be the preferred design.
3. If filesystem identity is used, it must account for portability and replacement semantics; pathname canonicalization alone (`resolve`, absolute path, normalized string) is not sufficient because the resolved object can still be replaced later.

The durable database-instance identifier is currently the least surprising architecture because the system already has explicit authenticated durable-state verification and frequently reopens SQLite connections.

## Regression-first extension

In addition to the already specified DB-A -> public `path` -> DB-B rebinding regression, add a same-path substitution case:

1. Construct and fully verify the supported ledger/history object against DB A at pathname P.
2. Without changing any Python attribute, arrange that P subsequently resolves to DB B (for a platform-neutral test this can be modeled with an atomic file replacement while no connection is held, or an equivalent indirection fixture).
3. DB B should superficially satisfy current-head/runtime identity but fail full trusted history/bootstrap continuity.
4. Pre-fix: demonstrate a supported operation opens B through the unchanged pathname and reaches an authority decision/mutation path that construction never verified.
5. Post-fix: the first fresh connection to B must fail closed on database-instance identity before reserve/execute/rotate/verify mutation or trust decisions.
6. Confirm ordinary reopen of the original DB A still works.

The test should avoid relying only on symlink behavior so it remains meaningful on platforms where symlink privileges or rename semantics differ.

## Non-goals

- This does not require treating every pathname alias/hardlink to the same database as a different authority. The desired identity is the accepted database instance/history, not the spelling of its path.
- Do not fix this by merely calling `Path.resolve()` once.
- Do not add a second independent identity source in ledger and provider history; that would preserve split-authority risk.

## Status

Source-level contract refinement only. No behavioral RED/GREEN is claimed in this run because exact repository execution is unavailable. Production code should remain unstaged until the existing LAB-095 pre-fix regression and this same-path substitution regression can be executed, or an equivalently strong auditable execution path becomes available.
