# LAB-092 ledger-owned public-surface closure audit

Date: 2026-09-01

## Scope

Continue the retained-reference/public-surface audit for `ProvenancedHistoricalSharedAnchorLedger` after the concrete post-construction provenance-deletion mutation gaps were already guarded (`reserve`/`execute`, `rotate_provider`, mutation-capable `verify_component`, and public `provider_history.store_receipt`). This pass intentionally excludes caller-owned `attested`/provider capability exposure (#178/LAB-093), provider-history bootstrap trust-root rebinding (#179/LAB-094), and DB path identity rebinding (#180/LAB-095).

## Runtime observation

Fresh local transport probe:

```text
git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD
fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com
```

The failure occurred before repository code execution. No behavioral PASS/FAIL is claimed in this run.

## Exact source audited

- LAB-092 draft head: `81673f8f6e4e0864dfa124735938c40aa28b4f2c`
- LAB-090 base: `d9a381dd4607a928cd1315adef6431e239995bc1`
- `experiments/provider_generation_history/activation_schema_provenance.py`
- `experiments/provider_generation_history/supported.py`
- `experiments/shared_anchor_intent_ledger/protocol.py`
- `experiments/provider_generation_history/protocol.py`

## Findings

### 1. Remaining ledger public methods do not expose a new mutable ledger-owned authority handle

After the existing LAB-092 wrappers, the ordinary non-underscore ledger surface is effectively:

- `reserve()` / inherited `execute()` — mutation-capable and already provenance-gated because `execute()` enters through overridden `reserve()`;
- `rotate_provider()` — mutation-capable and already provenance-gated;
- `verify_component()` — may advance a durable watermark and is already provenance-gated;
- `entry()` — read-only DB lookup returning `LedgerEntry`;
- `watermark()` — read-only scalar lookup;
- `verify_activation_schema_provenance()` — explicitly checks local COMPLETE state before authority/integrity verification; any receipt recovery reached by its final `execute()` uses the provenance-bound provider-history `store_receipt()`;
- `migrate_activation_schema_v1()` — explicit class migration operation, not a post-construction retained capability; its PREPARED/CONFIRMED mutation ordering is intentionally handled by the migration-only reservation surface rather than the live provenance-bound history wrapper.

No additional supported method was found that can mutate durable ledger/provider state after provenance loss without first passing one of the existing guards.

### 2. Returned value objects are immutable/value-like

`entry()` and mutation methods return frozen dataclass/value objects rather than live authority objects:

- `LedgerEntry` is `@dataclass(frozen=True)`;
- `GenerationDescriptor` is `@dataclass(frozen=True)`;
- `HistoricalReceipt` is `@dataclass(frozen=True)`.

Mutating a returned value therefore does not mutate ledger authority or durable state. No new capability wrapper is justified for these return paths.

### 3. `provider_history` remaining public methods are read-only or already blocked

The live LAB-092 history object is `_ProvenanceBoundCoordinatorOnlyProviderHistory`:

- `store_receipt()` is provenance-gated;
- `rotate()` is blocked by `CoordinatorOnlyProviderHistory` and directs callers to ledger coordination;
- `current()`, `verify_durable()`, `require_current()`, `load_receipt()`, `verify_receipt()`, and `make_transition()` are verification/read/value-construction operations and do not directly mutate durable history.

No second LAB-092-only history mutation bypass was found.

## Boundary findings intentionally split out

Three reachable authority/reference concerns remain real but are lower-layer ownership problems rather than new LAB-092 provenance bugs:

1. `ledger.attested` / `ledger.attested.provider` exposes caller-owned runtime mutation capability — #178 / LAB-093.
2. `provider_history.bootstrap` is a mutable retained trust-root slot later consumed by durable verification — #179 / LAB-094.
3. `ledger.path` and `provider_history.path` are independently mutable DB identity slots consumed by supported operations — #180 / LAB-095.

These should not be hidden inside additional LAB-092 wrappers because doing so would change the wrong abstraction boundary and leave lower-layer supported composition inconsistent.

## Decision

The LAB-092 retained-reference/public-surface audit is exhausted for ledger-owned supported non-underscore methods and returned value objects. Do **not** add more LAB-092 regressions or wrappers without a newly demonstrated supported mutation-before-provenance-validation path.

The highest-value source-level follow-up is now LAB-094/#179 (bootstrap trust-root immutability), followed by LAB-095/#180 (canonical DB identity), but regression-first implementation should wait for exact execution unless a separately auditable source-only change can preserve the lower-layer contract without claiming behavioral validation.

## Next action

1. Retry LAB-086 exact byte-preserving publication bridge first.
2. If exact source execution becomes available, run PR #175 and PR #177 behavioral gates before integration.
3. If both remain unavailable, promote LAB-094 architecture/source audit: enumerate every use/write of `bootstrap`, define the smallest lifetime-stable read-only contract, and only then decide whether a source-only patch is sufficiently safe to stage without execution.
