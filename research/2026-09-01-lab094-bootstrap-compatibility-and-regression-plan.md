# LAB-094 bootstrap compatibility and regression-first patch plan

Date: 2026-09-01
Issue: #179

## Scope

Source-level audit only. No production code is staged in this run because exact repository source execution is unavailable: a fresh `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` failed before repository code execution with `Could not resolve host: github.com`.

LAB-086 remains priority #1 and was probed first. No LAB-086 source mutation was attempted.

## Finding

`DurableProviderHistory.__init__()` validates the caller-provided `GenerationDescriptor`, then stores it in public mutable `self.bootstrap`. The same object later supplies the authenticated root identity in `verify_durable()` through `self.bootstrap.generation_id`.

`IntegratedProviderHistory._verify_durable_locked()` independently consumes the same public `self.bootstrap.generation_id` as the first-generation trust root for supported LAB-081 ledger verification. `CoordinatorOnlyProviderHistory` and `SupportedHistoricalSharedAnchorLedger` do not override or encapsulate that attribute.

Therefore the rebindable slot is not merely introspection: later supported verification decisions consume it as authority.

## Compatibility surface audit

Default-branch source inspected:

- `experiments/provider_generation_history/protocol.py`
  - constructor assignment: `self.bootstrap = bootstrap`;
  - initialization writes the first durable generation/head from `self.bootstrap`;
  - `verify_durable()` compares the first durable descriptor to `self.bootstrap.generation_id`.
- `experiments/provider_generation_history/integration.py`
  - `_verify_durable_locked()` compares the first durable descriptor to `self.bootstrap.generation_id`;
  - supported ledger verification calls this locked verifier.
- `experiments/provider_generation_history/supported.py`
  - `CoordinatorOnlyProviderHistory` only blocks direct `rotate()`;
  - no bootstrap override/property/assignment exists;
  - supported ledger constructs `CoordinatorOnlyProviderHistory(path, bootstrap)` directly.
- Existing tests in `experiments/provider_generation_history/tests/` use construction-time bootstrap values; no inspected test requires assigning `history.bootstrap` after construction.

No separate supported compatibility requirement for mutable bootstrap rebinding was found.

## Minimal implementation contract

Do not broaden LAB-094 into path immutability (#180) or caller-owned provider capability encapsulation (#178).

Preferred minimal change in `DurableProviderHistory`:

1. After `bootstrap.validate()`, retain the descriptor in private state, e.g. `self._bootstrap = bootstrap`.
2. Expose `bootstrap` only as a read-only property returning `self._bootstrap`, preserving ordinary introspection/equality behavior.
3. Make every trust decision consume `_bootstrap` directly, not a public setter/rebindable slot:
   - `_init()` initial generation/head creation;
   - `verify_durable()` first-generation trust-root comparison;
   - `IntegratedProviderHistory._verify_durable_locked()` first-generation comparison.
4. Do not add a setter.
5. Do not introduce a generalized `__setattr__` freeze: that would silently change unrelated runtime fields and broaden the authority model.

Because `GenerationDescriptor` is already `@dataclass(frozen=True)`, returning the descriptor itself through the read-only property does not expose mutable descriptor fields.

## Exact regression-first plan

Add a focused standalone regression near `test_protocol.py` or a dedicated `test_bootstrap_trust_root.py`:

1. Create DB A with legitimate bootstrap `g1` and, optionally, rotate to `g2` to prove normal history remains valid.
2. Capture a distinct valid descriptor `attacker_g1` (same provider/generation number is acceptable, different verification key => different `generation_id`).
3. Pre-fix reproduction must demonstrate that `history.bootstrap = attacker_g1` is currently accepted as ordinary attribute rebinding.
4. Substitute the durable first-generation history/head/transition material with a self-consistent attacker-rooted history sufficient that verification would fail against original `g1` but can pass when authority is switched to `attacker_g1`.
5. Assert pre-fix `verify_durable()` accepts the substituted history only after bootstrap rebinding. This is the required RED/security reproduction; do not count a mere `AttributeError` expectation as reproduction.
6. Apply the minimal private/read-only implementation.
7. Post-fix, assert assignment to `history.bootstrap` fails and the same substituted durable history still raises `HistoryRollback`/historical-verification failure because original construction root remains authoritative.
8. Add the same semantic regression through `SupportedHistoricalSharedAnchorLedger.provider_history.verify_durable()` or ledger `verify_durable()` so the integrated `_verify_durable_locked()` path is covered.

The substitution fixture must preserve enough internal consistency to isolate bootstrap authority: descriptor identities, transition proofs (if present), and head must be self-consistent under the attacker root. Otherwise a different invariant may reject first and the regression will not prove LAB-094.

## Validation gate once exact execution is available

Focused first:

- new standalone bootstrap-rebinding RED on predecessor;
- new standalone bootstrap immutability/rollback GREEN on candidate;
- integrated supported-ledger bootstrap regression;
- complete `experiments/provider_generation_history/tests`;
- compileall for provider-generation-history package.

Then downstream compatibility before integration:

- LAB-081 supported integration;
- LAB-090 exact focused/integration gates on its reconciled base;
- LAB-092 four provenance-deletion regressions plus full focused gate on its reconciled base;
- explicit branch/base reconciliation immediately before integration.

## Audit conclusion

LAB-094 is sufficiently specified for regression-first implementation once exact behavioral execution is available. The source audit found no legitimate mutable-bootstrap compatibility dependency and no need for a wider object-freezing mechanism. Production code should remain unstaged until the pre-fix substituted-history acceptance is actually executed or an equivalently strong auditable execution path becomes available.
