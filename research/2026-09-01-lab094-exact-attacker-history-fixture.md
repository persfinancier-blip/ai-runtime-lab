# LAB-094 exact attacker-history fixture

Date: 2026-09-01
Issue: #179

## Purpose

Turn the source-level bootstrap mutability finding into an exact executable regression plan against the current `experiments/provider_generation_history/protocol.py` schema, without staging a production fix before a real pre-fix RED can execute.

## Exact source facts

`DurableProviderHistory.__init__()` validates the supplied bootstrap, stores it as public mutable `self.bootstrap`, initializes the schema, and then calls `verify_durable()`.

On a fresh DB, `_init()` inserts exactly the construction bootstrap into `provider_generations` and `provider_generation_head`.

`verify_durable()` reconstructs every descriptor from `provider_generations`, verifies each descriptor's content-derived `generation_id`, then checks only that the first durable descriptor equals `self.bootstrap.generation_id`. It then validates transition proofs for later generations and finally requires the durable head to equal the last descriptor.

Therefore a one-generation substituted history is sufficient to isolate the trust-root rebinding defect: no transition row or receipt is required.

## Minimal standalone security reproduction

Use the existing test helper conventions:

- legitimate bootstrap key: `k1 = b'provider-key-1'`;
- legitimate bootstrap: `g1 = GenerationDescriptor('anchor-A', 1, k1.hex())`;
- attacker key: `attacker_key = b'attacker-bootstrap-key'`;
- attacker bootstrap: `attacker_g1 = GenerationDescriptor('anchor-A', 1, attacker_key.hex())`.

Steps:

1. Construct `h = DurableProviderHistory(path, g1)`. This creates and verifies the legitimate one-generation history.
2. Open the same SQLite DB directly and replace the durable history with a self-consistent attacker-rooted one-generation history:
   - `DELETE FROM historical_provider_receipts` (normally already empty; makes fixture independent of future setup changes);
   - `DELETE FROM provider_generation_transitions` (normally already empty);
   - `DELETE FROM provider_generations`;
   - `INSERT INTO provider_generations VALUES(attacker_g1.generation_id, attacker_g1.provider_id, attacker_g1.generation, attacker_g1.verification_key_hex)`;
   - `UPDATE provider_generation_head SET generation_id=attacker_g1.generation_id, generation=1 WHERE singleton=1`;
   - commit.
3. Call `h.verify_durable()` *without rebinding*. Expected: `HistoryRollback('bootstrap generation changed')`. This proves the substituted database is rejected under the construction-time trust root.
4. On the same already-constructed object execute `h.bootstrap = attacker_g1`.
5. Call `h.verify_durable()` again. Current pre-fix expected result: `True`. The attacker descriptor is internally self-consistent, there are no successor transitions to validate, the head matches that descriptor, and the public rebound `self.bootstrap` now equals the substituted first generation.

This is stronger than a mere `AttributeError` test: it demonstrates that public runtime rebinding changes a later authority decision from reject to accept.

## Regression-first test shape

Add a dedicated test, preferably near provider-history audit regressions, with two assertions before any production change:

```python
with self.assertRaises(HistoryRollback):
    h.verify_durable()
h.bootstrap = attacker_g1
self.assertTrue(h.verify_durable())
```

The pre-fix regression is considered reproduced only if that exact reject-then-accept sequence is executed against the exact branch source.

After reproduction, the production fix should make the second stage impossible while preserving read-only introspection. The intended minimal contract remains:

- store construction root in private `_bootstrap`;
- expose `bootstrap` through a getter-only property if callers/tests need inspection;
- make `_init()`, `verify_durable()`, and integrated `_verify_durable_locked()` consume `_bootstrap` rather than a rebindable public authority slot;
- do not broaden this patch into path/DB identity (#180) or caller-owned provider capability (#178).

Post-fix acceptance should prove both:

1. `h.bootstrap = attacker_g1` is rejected (or otherwise cannot alter the retained trust root);
2. `h.verify_durable()` continues to reject the substituted attacker history because the original `g1` remains authoritative.

## Integrated-path extension

The same durable substitution is sufficient for the integrated path because `IntegratedProviderHistory._verify_durable_locked()` performs the same first-descriptor-vs-bootstrap authority comparison. The integrated regression should use the supported ledger/provider-history construction helper already present in LAB-081/LAB-090 tests, obtain the live `provider_history`, perform the same one-generation DB substitution, prove integrated verification rejects under the legitimate bootstrap, then demonstrate the pre-fix accept-after-rebind behavior.

Do not invent a second attacker transition chain unless the one-generation fixture fails to reach the integrated verification path. The one-generation form is deliberately minimal and removes transition-MAC correctness as a confounder.

## Why this fixture is valid

The attacker is not exploiting malformed descriptor content: `GenerationDescriptor.generation_id` is recomputed from the attacker descriptor and matches the stored primary key. The attacker is not exploiting a missing transition: there is only one generation, so no transition is required. The head is internally coherent with the substituted generation. The only reason the legitimate object rejects the DB before rebinding is continuity with its construction-time authenticated bootstrap. Rebinding that exact trust root is therefore the isolated variable.

## Current execution status

No behavioral RED/GREEN is claimed in this run. Direct Git transport was probed first and failed before repository code execution with `Could not resolve host: github.com`; the GitHub connector is available for durable reads/writes but does not provide exact branch checkout/test execution. No LAB-094 production code was staged.

## Next action

At the next run, probe LAB-086 exact publication/execution first. If exact source execution becomes available, execute this standalone LAB-094 regression against pre-fix source before changing production code. Only after observing reject-then-accept should the minimal private-bootstrap fix be staged, followed by standalone + integrated + LAB-081/LAB-090/LAB-092 downstream gates.

If execution remains unavailable and LAB-086 publication remains blocked, move to LAB-095/#180 source-level lifetime DB-identity audit as already directed by `state/CURRENT.md`; do not continue expanding LAB-094 without executable evidence.