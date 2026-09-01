# LAB-092 public return-value / descriptor authority audit — negative

Date: 2026-09-01
Issue: #176 / LAB-092
Branch reviewed: `lab-092-activation-schema-provenance`
PR reviewed: #177, head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, base LAB-090 `d9a381dd4607a928cd1315adef6431e239995bc1`

## Question

After the already-fixed post-construction provenance-deletion paths (`reserve`/`execute`, `rotate_provider`, mutation-capable `verify_component`, and public `provider_history.store_receipt`), does any remaining ledger-owned public return value, descriptor/key surface, or non-underscore history/ledger API expose a mutable authority object that can change durable receipts, activation state, migration provenance, provider history, or watermarks without re-checking LAB-092 provenance?

## Source audit

### Ledger return values

`SharedAnchorLedger.reserve()` / `execute()` / `entry()` return `LedgerEntry`. `LedgerEntry` is a `@dataclass(frozen=True)` containing scalar/string fields only. It has no mutation method or live connection/provider handle.

`watermark()` and `verify_component()` return integers. `verify_activation_schema_provenance()` returns `True`.

`rotate_provider()` returns the supplied `GenerationDescriptor`; `migrate_activation_schema_v1()` returns a new ledger instance whose mutation-capable public paths are the LAB-092 guarded surface.

### Provider-history return values and descriptors

`GenerationDescriptor`, `TransitionProof`, and `HistoricalReceipt` are all `@dataclass(frozen=True)`. `GenerationDescriptor.key` returns immutable `bytes`; `.descriptor` constructs and returns a new dictionary rather than a live internal authority object.

`provider_history.current()` / `require_current()` return a frozen `GenerationDescriptor`; `load_receipt()` / `verify_receipt()` return a frozen `HistoricalReceipt`; `make_transition()` returns a frozen `TransitionProof`.

The only non-underscore provider-history API that persists durable state is `store_receipt()`, and LAB-092 already replaces the live public history handle with `_ProvenanceBoundCoordinatorOnlyProviderHistory`, whose `store_receipt()` requires `_classify(path) == "COMPLETE"` before delegating to the inherited write.

`CoordinatorOnlyProviderHistory.rotate()` is fail-closed and redirects rotation authority to the ledger coordinator.

### Activation return objects

`ActivationTicket` is `@dataclass(frozen=True)`. The activation provider and its mutable `ActivationState` remain reachable only through the caller-owned `AttestedCatchup` / provider capability already separated into LAB-093/#178; the current audit intentionally does not redefine that lower-layer ownership boundary.

### Input caveat

`Intent` is frozen but contains a caller-owned mutable `dict` payload. This does not create a returned ledger-owned authority handle: the durable ledger stores only the validated payload digest, and returned `LedgerEntry` objects contain that digest rather than the payload object.

## Result

No new concrete LAB-092 mutation-before-provenance-validation path was found on the audited ledger-owned return/descriptor/non-underscore surfaces.

The remaining public values are immutable value objects or scalars, and the one remaining public history writer (`store_receipt`) is already provenance-bound. Adding a regression or wrapper here would therefore invent a stronger contract without a demonstrated violation.

## Execution observation

LAB-086 was probed first as required. Fresh local `git clone https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository code execution with `Could not resolve host: github.com`. No LAB-086 mutation or manual/model reserialization was attempted.

No behavioral test PASS is claimed in this audit; this is a source-level negative capability audit. PR #177 remains draft and GitHub currently reports it mergeable, with exact behavioral/full execution still pending.

## Next search surface

If exact execution and LAB-086 byte-preserving publication remain unavailable, inspect public object attributes that are ledger-owned references rather than returned immutable values (`path`, `provider_history.bootstrap`, and other rebinding-capable state) only for a concrete supported-API privilege amplification. Do not treat arbitrary Python attribute reassignment as a security defect unless the repository contract makes that surface supported or a reachable method returns/uses it in a way that bypasses an authority invariant.
