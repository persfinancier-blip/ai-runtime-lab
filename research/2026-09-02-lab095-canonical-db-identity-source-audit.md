# LAB-095 canonical DB identity — source-level lifetime audit

Date: 2026-09-02
Issue: #180

## Scope

Source-level audit only. No production code is staged in this run because exact branch/source execution is unavailable: direct local Git transport fails before repository code execution with `Could not resolve host: github.com`.

LAB-086 remained priority #1 and was probed first. Its byte-preserving publication/full execution gate is still unavailable, so this run followed the durable fallback in `state/CURRENT.md` and audited LAB-095.

## Facts from current supported composition

### 1. The base shared-anchor ledger retains a public mutable path

`SharedAnchorLedger.__init__()` stores `self.path = str(path)`. `_con()` later opens `sqlite3.connect(self.path, ...)`. All inherited ledger reads/writes that call `_con()` therefore consume the *current value* of the public attribute, not a construction-bound database identity.

### 2. Provider history independently retains another public mutable path

`DurableProviderHistory.__init__()` separately stores `self.path = str(path)`. Its standalone/public methods (`current()`, `verify_durable()`, `store_receipt()`, `load_receipt()`, `verify_receipt()`, standalone `rotate()`) open connections through that independently mutable value.

### 3. Integrated locked helpers do not consult provider-history.path

`HistoricalSharedAnchorLedger.reserve()` opens a connection through the ledger's `_con()` and passes that connection to `provider_history._current_locked(q)`. `_current_locked(q)` reads whichever database the supplied connection already targets. It does **not** reopen `provider_history.path` and does not run full `verify_durable()`.

The same design is intentional for transaction-level atomicity, but it means the connection selected by the ledger path is authoritative for locked history helpers.

### 4. Therefore path divergence has two independent directions

#### A. Rebind `ledger.path`, leave `provider_history.path` unchanged

Ledger-mediated operations can target DB B while standalone provider-history methods still target DB A.

Most importantly, `HistoricalSharedAnchorLedger.reserve()` can mutate DB B after checking only DB B's *current head descriptor* through `_current_locked(q)`. A fresh constructor against DB B would instead run full provider-history verification, including bootstrap continuity.

#### B. Rebind `provider_history.path`, leave `ledger.path` unchanged

Public history operations can target DB B while ledger mutations continue against DB A. For example `provider_history.current()/verify_durable()/store_receipt()` select the history path independently, while ledger `_con()` continues to select the ledger path.

This creates a split-brain object graph: authority/history decisions and receipt persistence can refer to a different durable file from the shared-anchor intents and metadata.

### 5. LAB-092 adds another split check rather than eliminating the split

On the LAB-092 branch, ledger provenance guards call `_classify(self.path)` on the ledger path. The provenance-bound provider-history `store_receipt()` independently calls `_classify(self.path)` on the provider-history path.

If those public attributes diverge, the two guards can validate activation provenance against different databases. This is not a new LAB-092 bug; it is evidence that canonical DB identity belongs below LAB-092, as #180 states.

## Concrete DB-A -> DB-B security/correctness reproduction plan

The smallest strong regression should target LAB-081 first because it isolates the DB identity problem from LAB-090 activation state and LAB-092 provenance.

### Fixture

1. Create DB A normally with bootstrap `g1`, rotate validly to `g2`, and construct a supported `HistoricalSharedAnchorLedger` whose runtime provider is `g2`.
2. Create DB B containing the normal shared-anchor schema plus a superficially current provider head for the *same runtime `g2`*, but with invalid full history relative to bootstrap `g1`.
3. Minimal invalid-history shape for B: `provider_generations` contains only descriptor `g2`; `provider_generation_head` points to `g2`; no authenticated `g1 -> g2` continuity exists.
4. Prove a fresh `IntegratedProviderHistory(DB_B, bootstrap=g1)` / supported ledger construction rejects B because `verify_durable()` sees the first durable generation is not the construction bootstrap.
5. On the already-valid live ledger constructed against A, assign `ledger.path = DB_B` in the pre-fix implementation.
6. Call a supported mutation such as `reserve()` with a fresh intent.

### Pre-fix expected result

`reserve()` opens DB B through the rebound ledger path. `provider_history._current_locked(q)` accepts B's superficially valid current `g2` descriptor because it checks the head row/content but not bootstrap-chain continuity. The intent/tail mutation can therefore commit to a database that fresh supported construction would reject.

This proves the defect is not merely cosmetic attribute mutability: public-state rebinding changes the durable authority target and bypasses construction-time full-history validation.

### Post-fix expected result

The live capability remains bound to DB A for its lifetime. Public assignment must not redirect any supported operation to B. A caller wishing to operate on B must perform a fresh construction, which then rejects B under the existing full verification contract.

## Minimal lifetime contract

The supported ledger/history capability should be bound to one canonical database identity at construction.

Recommended contract:

1. Canonicalize the supplied path once at construction to a stable string/path representation suitable for SQLite connection opening.
2. Retain it in private non-rebindable state (for example `_db_path`).
3. Keep `path` only as a getter-only compatibility/introspection property if callers need it.
4. Make every `_con()` and every schema/provenance classifier consume the same private construction-bound value.
5. Provider history must not retain a separately rebindable authority path. It may retain the same immutable canonical identity for standalone use, but composed construction must assert/effectively guarantee equality with the ledger identity.
6. Transaction-internal history helpers should continue consuming the caller-supplied already-open connection; that is required for atomic composition. Their safety then depends on the connection itself being opened from the canonical immutable ledger identity.
7. Do not mix bootstrap immutability (#179) or caller-owned provider capability encapsulation (#178) into this change.

## Why a generic `__setattr__` freeze is not preferred

The proven invariant concerns retained DB authority/reference identity. Freezing the entire object would silently alter unrelated runtime fields (`attested`, activation/runtime state, future caches) and could conflict with existing provider rotation semantics. A narrow immutable DB identity is the smallest coherent fix.

## Compatibility map for implementation

At minimum audit/change these source surfaces together:

- `experiments/shared_anchor_intent_ledger/protocol.py`
  - constructor DB identity retention;
  - `_con()`;
  - any public `path` compatibility surface.
- `experiments/provider_generation_history/protocol.py`
  - constructor DB identity retention;
  - `_con()`;
  - standalone history API path usage.
- `experiments/provider_generation_history/integration.py`
  - composed construction must guarantee ledger/history canonical identity agreement;
  - locked helpers should remain connection-driven.
- LAB-090 `experiments/provider_generation_history/supported.py`
  - all activation table reads/writes already go through ledger `_con()` and should inherit canonical identity.
- LAB-092 `activation_schema_provenance.py`
  - `_classify(...)`, reservation-surface construction, live provider-history binding, and provenance checks must consume/copy the canonical immutable identity rather than recreate public mutable `path` slots.

## Required regression matrix before integration

1. LAB-081 DB-A -> invalid DB-B ledger-path rebinding reproduction described above: RED pre-fix, GREEN post-fix.
2. Provider-history-path rebinding: public history methods must not be redirectable to B after construction.
3. Composed identity equality: ledger and provider history report/use the same construction-bound canonical DB.
4. Normal file-backed reopen of the same DB remains supported.
5. Relative/`Path` input compatibility is preserved according to the chosen canonicalization rule.
6. LAB-090 activation rotation/restart focused gates.
7. LAB-092 provenance migration/restart/post-deletion regressions, ensuring classifiers and receipt guards cannot diverge onto different DBs.
8. LAB-080/LAB-081 focused/downstream gates.

## Decision

LAB-095 is a real lifetime authority-boundary defect, not merely API cleanliness. The strongest minimal proof is DB B whose current head superficially matches runtime `g2` while its full history is invalid under construction bootstrap `g1`: fresh construction rejects B, but pre-fix ledger path rebinding lets `reserve()` use `_current_locked(q)` and mutate B.

Do not stage production changes until this exact pre-fix reproduction can execute, or an equivalently strong auditable execution path is available. The implementation should then be narrow: immutable canonical DB identity, not a general object freeze.
