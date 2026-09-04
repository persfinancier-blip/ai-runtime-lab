# LAB-094..096 — construction-bound retained-authority graph contract

Date: 2026-09-04
Status: architecture/source evidence only; exact RED/GREEN pending
Related: #179 LAB-094, #180 LAB-095, #181 LAB-096, with boundary relation to #178 LAB-093

## Question

Should the provider-history bootstrap root, logical database identity/path, and provider-history strategy/capability be patched independently, or treated as one lifetime authority graph owned by a supported ledger construction?

## Source facts

Current `DurableProviderHistory.__init__()` validates the bootstrap and then retains two public mutable authority-bearing references:

- `self.path = str(path)` — consumed by `_con()` for every later provider-history read/write;
- `self.bootstrap = bootstrap` — consumed by `verify_durable()` to decide whether the first durable generation is the authenticated root.

Current `HistoricalSharedAnchorLedger.__init__()` separately constructs and retains another public mutable authority-bearing reference:

- `self.provider_history = IntegratedProviderHistory(path, bootstrap)`.

The LAB-080 base ledger separately stores its own `self.path = str(path)` and every `_con()` opens that selected path.

After construction, supported LAB-081 operations dispatch authority decisions through all three retained references:

- `reserve()` opens the ledger-selected DB and calls `provider_history._current_locked(q)` on that already-open connection;
- `rotate_provider()` opens the ledger-selected DB and calls `provider_history._rotate_locked(q, ...)`;
- `_require_runtime_matches_durable_head()` and `_runtime_matches_entry()` call `provider_history.current()`, which reopens the history object's own path;
- `_reauthenticate()` calls `provider_history.load_receipt()` / `store_receipt()`, which also reopen the history object's path;
- `verify_durable()` opens the ledger-selected DB and dispatches `provider_history._verify_durable_locked(q)` / `_load_receipt_locked(q)`;
- `_verify_durable_locked()` compares the first durable generation against `self.bootstrap.generation_id`.

Therefore `path`, `bootstrap`, and `provider_history` are not independent implementation details. They jointly select:

1. **which durable database is authoritative**;
2. **which root authenticates provider-generation history**;
3. **which strategy implementation interprets and mutates that history**.

A fix that hides only one public attribute can leave split authority through the others.

## Concrete split-authority schedules to freeze as RED

### A. LAB-094 root rebinding

1. Construct a valid history/ledger against DB A with bootstrap root R1.
2. Replace public `bootstrap` with R2 after construction.
3. Substitute/rollback durable history so its first generation matches R2 rather than R1.
4. Call supported durable verification.

Pre-fix property: the live object's verification root is chosen by mutable post-construction state rather than by the successful construction that established trust.

### B. LAB-095 database rebinding

1. Construct against DB A and complete verification.
2. Rebind ledger path to DB B.
3. Keep `provider_history.path` at A, or also rebind it independently.
4. Invoke supported reserve/verify/receipt flows.

Pre-fix property: different methods can consume different durable authority domains. Locked history helpers may read DB B through the ledger-opened `q`, while ordinary `current()/load_receipt()/store_receipt()` may reopen DB A through the history object's own path.

A DB B whose current head superficially matches the runtime is especially important: `_current_locked(q)` is not equivalent to full construction-time `verify_durable()` of B.

### C. LAB-096 strategy replacement

1. Construct a supported ledger with the audited `IntegratedProviderHistory`.
2. Replace public `ledger.provider_history` with a permissive/fake strategy, or with a legitimate history object bound to DB B.
3. Invoke supported reserve/rotate/verify/re-authentication flows.

Pre-fix property: security-relevant behavior is dynamically dispatched through a caller-replaceable strategy slot after the construction that supposedly established authority.

The legitimate DB-A-ledger + DB-B-history-object case is required; the proof must not depend only on arbitrary monkeypatching.

## Decision — one construction-bound authority graph

Treat the following as a single lifetime object established atomically by supported construction/restart:

```
RetainedAuthorityGraph
  database_identity
  bootstrap_root
  provider_history_strategy
```

The graph is conceptually immutable after successful construction. Supported operations do not rediscover or accept replacements for any of its members.

### 1. Canonical database identity

Construction canonicalizes the requested database target once and stores a private canonical identity used by **all** connections and classifiers for the lifetime of the object.

Minimum V1 contract:

- one private canonical path/source of truth, not independent ledger/history public paths;
- every `_con()` for ledger and provider-history use the same canonical source;
- locked helpers accept only a connection opened from that same construction-bound identity;
- no supported post-construction path setter/rebind operation;
- if a future rebind/move operation is needed, it is a new fully verified construction/migration protocol, never attribute assignment.

Path-string equality alone is not a complete hostile-filesystem identity proof. Under the accepted LAB-087 sole-writer/process/filesystem boundary, V1 may treat a canonical absolute path plus broker-owned namespace/confinement as the logical DB identity. If stronger inode/file-handle identity is later required, it belongs at the LAB-087 broker boundary, not as ad-hoc comparisons inside every ledger method.

### 2. Bootstrap root

Construction validates the bootstrap once and stores an immutable/private root identity sufficient for all later history verification.

Minimum V1 contract:

- later verification never consults a caller-rebindable public `bootstrap` authority slot;
- a read-only descriptor/value copy may be exposed for introspection, but replacing it cannot affect verification;
- restart must receive/derive the expected root through the supported construction contract and verify the durable first generation before ordinary operation.

### 3. Provider-history strategy

The audited history implementation used by the ledger is construction-bound private state.

Minimum V1 contract:

- ledger internal reserve/rotate/current/receipt/verify paths all dispatch through the same private strategy instance;
- no public writable strategy slot participates in authority decisions;
- if public introspection is needed, expose a value-only/read-only view, not `_current_locked`, `_rotate_locked`, receipt storage, or verification helpers;
- custom strategy implementations are not implicitly trusted by duck typing. A future extension point requires an explicit trusted adapter/capability contract and its own authority proof.

## Construction/restart boundary

A supported construction or broker restart must establish the graph in this order before exposing the ledger capability:

1. Resolve and retain the canonical DB identity under the LAB-087 broker-owned filesystem/process boundary.
2. Validate and retain the expected bootstrap root.
3. Instantiate the exact audited provider-history strategy bound to the same canonical DB identity and retained root.
4. Initialize only according to the separate first-install/deletion-provenance rules (LAB-097/LAB-092 remain relevant; absence is not automatically proof of freshness).
5. Run full durable provider-history verification against the retained bootstrap root.
6. Run supported shared-anchor / activation / provenance durable verification for the composed ledger.
7. Verify runtime provider identity against the verified durable head.
8. Only then publish/delegate the supported ledger or LAB-093 value-only broker façade.

A worker restart under LAB-093 reconstructs only its delegation endpoint. It must not reconstruct or choose a new retained-authority graph. A broker restart reconstructs and fully verifies the graph before issuing new endpoints.

## Scope relation to LAB-093

LAB-093 and LAB-094..096 are complementary, not duplicates.

- LAB-093: what capability a lower-trust consumer receives. It should receive no live ledger/provider-history object.
- LAB-094..096: whether the broker-owned/supported ledger itself can internally change its retained authority graph after construction.

A LAB-093 process boundary does not justify keeping mutable authority aliases inside the broker object; conversely, private aliases alone do not create a security boundary against same-process introspection. The intended composition is:

`construction-bound private authority graph inside broker` + `closed value-only LAB-093 endpoint outside broker`.

## RED-first combined regression matrix

Do not implement production changes until exact executable source is available. Freeze these regressions first:

1. bootstrap public-slot rebinding changes verification root pre-fix;
2. substituted/rollback history + rebound root is accepted or reaches the wrong verifier pre-fix;
3. post-fix public/introspection bootstrap mutation cannot affect verification;
4. ledger path A -> B rebinding causes a supported DB-B operation pre-fix;
5. history path A -> B rebinding changes ordinary `current()`/receipt behavior pre-fix;
6. ledger path B + history path A demonstrates locked-vs-reopened split authority;
7. ledger path A + history path B demonstrates the converse split;
8. DB B has matching current head but invalid earlier continuity; current-head equality must not substitute for full construction verification;
9. fake/permissive `provider_history` replacement changes an authority decision pre-fix;
10. legitimate `IntegratedProviderHistory(DB B)` replacement changes/splits authority pre-fix;
11. post-fix replacement of any public compatibility/introspection attribute cannot affect internal authority decisions;
12. every internal ledger/history connection resolves the same canonical construction identity;
13. reserve uses the bound strategy/root/database only;
14. rotate uses the bound strategy/root/database only;
15. current/runtime-head matching uses the bound strategy/root/database only;
16. historical receipt load/store/verify uses the bound strategy/root/database only;
17. `verify_durable()` uses the bound strategy/root/database only;
18. restart with same canonical DB + expected root succeeds after full verification;
19. restart pointed at another DB, even with matching head, performs fresh full construction verification and fails on invalid continuity;
20. attempted post-construction database move/rebind has no supported mutation path;
21. LAB-097 complete-history deletion remains fail-closed rather than being hidden by construction refactor;
22. LAB-092 activation-schema provenance semantics remain unchanged/fail-closed;
23. LAB-090 provider activation/current-head behavior remains compatible;
24. LAB-080 shared-ledger reserve/execute/verify focused regressions remain compatible;
25. LAB-081 provider-history rotation/historical-receipt focused regressions remain compatible;
26. LAB-087 restricted-worker composition still exposes no writable DB/path capability;
27. LAB-093 façade can operate while worker has no reachable graph object;
28. compile/static audit confirms no security-relevant method reads legacy public `path`, `bootstrap`, or `provider_history` slots.

## Implementation shape to test when execution returns

Prefer a minimal refactor rather than three independent wrappers:

- introduce one private construction-bound authority container or equivalent private final fields;
- make base ledger/history connection helpers consume the same canonical DB identity;
- make history verification consume the retained root;
- make ledger history dispatch consume the retained audited strategy;
- optionally leave compatibility properties that return immutable/value-only views, but no setter and no security-relevant read path through those views.

Do not claim Python underscore/frozen dataclass state is by itself a hostile same-process security boundary. The claim is supported-API correctness/authority stability inside the LAB-087 broker trust domain. The hostile lower-trust boundary remains LAB-087/LAB-093 process isolation.

## Verdict

`LAB094_LAB096_RETAINED_AUTHORITY_GRAPH_CONTRACT_FROZEN`

The three issues should remain individually trackable for regression provenance, but implementation should be one coherent construction/restart-bound change unless exact RED evidence disproves one of the interactions above.
