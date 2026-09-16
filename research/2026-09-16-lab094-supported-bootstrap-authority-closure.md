# LAB-094/LAB-095/LAB-096 supported bootstrap authority closure — 2026-09-16

## Runtime observation

LAB-086 was probed first. `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 or PR #187 executable GREEN is claimed.

## Finding

The frozen retained-authority architecture says bootstrap root, canonical database binding, and provider-history strategy form one construction-bound authority graph. PR #187 already bound the supported canonical path and provider-history strategy, but `CoordinatorOnlyProviderHistory` still inherited `DurableProviderHistory.__init__`, which assigned public mutable `self.bootstrap`, while `IntegratedProviderHistory._verify_durable_locked()` later consumed `self.bootstrap.generation_id` as the authenticated history root.

Therefore an introspecting holder of the supported ledger could reach `ledger._history()` and rebind the retained bootstrap root after construction. The public inspection view correctly hid `bootstrap`, but hiding the alias was not enough because the live strategy remained mutable. This was the remaining LAB-094 prerequisite inside LAB-095/LAB-096 authority closure.

## Change

On branch `lab-095-database-identity-red-intent` / draft PR #187:

- commit `40f97cbcdc46fbe54ac4c2bc0015071902bb9e05` changes `CoordinatorOnlyProviderHistory` so the first inherited `bootstrap` assignment is stored in private `_bootstrap_generation`; subsequent assignment to either `bootstrap` or the private slot raises `AttributeError`;
- commit `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057` extends `test_provider_history_capability_surface.py` to prove both public and private-slot rebinding are rejected and durable verification continues using the original g1 root.

The base `DurableProviderHistory` compatibility surface was intentionally not changed; the enforcement is at the supported composition boundary, matching the canonical-path and strategy-binding approach already on PR #187.

## Audit

The setter remains compatible with the inherited constructor: `bootstrap.validate()` runs before `self.bootstrap = bootstrap`, and the first assignment is accepted. Later `IntegratedProviderHistory._verify_durable_locked()` reads the property and therefore resolves the construction-bound private value. `CanonicalDatabaseBinding.__setattr__` remains in the MRO for path enforcement because the subclass forwards all non-bootstrap assignments through `super().__setattr__`.

No exact repository execution was possible in this runtime, so these commits are source-audited but not counted as GREEN.

## Next gate

Reconcile the LAB-095 closure/hash inventory including the new supported.py/test blobs, then enumerate and eventually execute the exact focused/downstream gates before #180/#181/#179 can leave draft/in-progress status.