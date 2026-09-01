# LAB-092 retained-reference audit: mutable ledger DB path crosses verification boundary

Date: 2026-09-01

## Context

LAB-086 remains priority #1. In this run direct Git transport was probed again with:

`git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD`

It failed before repository code execution with `Could not resolve host: github.com`. The available GitHub connector still exposes UTF-8 Contents replacement rather than a byte-preserving fetched-bytes + patch composition primitive, so the security-critical LAB-086 `strict_fence.py` was not manually/model reserialized or mutated.

Per `state/CURRENT.md`, fallback work continued the LAB-092 ledger-owned retained-reference audit.

## Finding

A supported shared-anchor/provider-history ledger is not currently lifetime-bound to the database it verified at construction.

`SharedAnchorLedger.__init__()` stores `self.path = str(path)`, and `_con()` later opens SQLite using that public mutable attribute. `DurableProviderHistory.__init__()` independently stores its own public mutable `self.path`.

The important composition detail is in `HistoricalSharedAnchorLedger.reserve()`:

1. it obtains `q = self._con()` using the ledger object's current `self.path`;
2. begins the writer transaction on that connection;
3. calls `self.provider_history._current_locked(q)` using the already-open connection rather than reopening `provider_history.path`;
4. compares the runtime descriptor against that selected database's current head;
5. writes the shared-anchor intent and advances the tail in the selected database.

LAB-092 adds `_require_complete_activation_schema_provenance()`, but that guard only calls `_classify(self.path)`. `_classify()` proves activation DDL/marker shape; it does not perform full provider-history/bootstrap continuity verification for a newly selected database.

Therefore post-construction rebinding of `ledger.path` can redirect later supported authority decisions/mutations to another SQLite file without rerunning the constructor's full durable verification for that target. A superficially matching current provider head is sufficient for the reserve-time `_current_locked()` + runtime equality check even if the target database's full history/bootstrap continuity would fail `verify_durable()`.

This is stronger than an arbitrary attribute-tampering observation because the mutable reference is consumed by supported public methods as the identity of the durable authority store.

## Scope decision

Do not patch LAB-092 only.

The mutable DB identity originates in the LAB-080/LAB-081 base abstractions and affects LAB-090/LAB-092 composition. Opened #180 / LAB-095 to define a lifetime-stable canonical DB identity, prevent ledger/provider-history path divergence, and add a cross-DB rebinding regression.

This is separate from:

- #179 / LAB-094: mutable provider-history bootstrap trust root inside a database;
- #178 / LAB-093: caller-owned `AttestedCatchup` / provider capability exposure.

No LAB-092 code or regression was added in this run because the correct fix belongs below LAB-092.

## Evidence inspected

- `experiments/shared_anchor_intent_ledger/protocol.py`: public mutable `self.path`; `_con()` consumes it.
- `experiments/provider_generation_history/protocol.py`: provider history separately retains public mutable `self.path`.
- `experiments/provider_generation_history/integration.py`: `HistoricalSharedAnchorLedger.reserve()` passes the ledger-selected SQLite connection to `provider_history._current_locked(q)` before mutation.
- `experiments/provider_generation_history/activation_schema_provenance.py`: LAB-092 provenance checks classify `self.path` before inherited mutation.

## Execution status

No behavioral test is claimed in this run. Exact source execution remained unavailable because direct Git transport failed DNS resolution. This finding is a source-level reachable-path audit and has been split into LAB-095 for an executable regression/fix once exact execution is available.
