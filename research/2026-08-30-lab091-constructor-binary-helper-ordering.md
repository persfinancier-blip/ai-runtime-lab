# LAB-091 constructor binary-helper ordering

Date: 2026-08-30

## Finding

The previous identity-collation fix replaced the inherited LAB-082 `IntegratedAsymmetricProviderHistory` only after `super().__init__()` returned from the final LAB-091 class.

That ordering was insufficient. `SupportedMutableAsymmetricSharedAnchorLedger.__init__()` calls `self._install_guards()` and then `self.verify_durable()`. Python dynamic dispatch reaches the final LAB-091 `_install_guards()` while the inherited LAB-082 provider-history helper is still installed. The final `_install_guards()` itself calls `self.verify_durable()` before the final class's `__init__()` resumes.

Therefore first adoption/restart verification could still execute receipt-identity operations through the inherited helper whose request-id predicates use the column default collation. A legacy `TEXT COLLATE NOCASE` receipt identity column with a separate canonical BINARY unique index is an admitted schema shape, so this was a reachable constructor/restart compatibility gap.

## Fix

PR #173 branch `lab/091-mutable-shared-anchor-writer` now upgrades `provider_history` through `_ensure_binary_provider_history()` at the start of final `_install_guards()`, before durable verification. The final `__init__()` calls the same idempotent helper after `super()` as a defensive invariant and then performs the runtime/durable-head match.

Published commits:

- runtime ordering fix: `7de557add95ca877ec843faaaf3977de414c8e20`;
- focused ordering regression: `a9fd1e1422d01088ac34248dd36fc83be0f750f3`.

Post-write PR head was re-fetched as `a9fd1e1422d01088ac34248dd36fc83be0f750f3`.

## Regression

`test_constructor_binary_provider_history_regression.py` constructs the final object without running the full constructor, supplies an inherited-style provider-history placeholder, and invokes the real final `_install_guards()` with guard installers/validators isolated. The test asserts that the binary helper replacement occurs before `verify_durable()` observes `provider_history`.

A local mechanism probe independently confirmed the required ordering (`binary` event before `verify`). This is mechanism evidence only: the exact published branch pytest remains unexecuted because the executable filesystem in this run cannot resolve `raw.githubusercontent.com`. No GitHub Actions/workers were used.

## Security interpretation

This closes the newly identified constructor/restart NOCASE receipt-identity path. It does not complete LAB-091's full gate. Exact branch execution is still required for the identity regression, this constructor regression, timeout/UNKNOWN, process concurrency/crash, receipt-affinity and receipt-collation final-surface tests.

LAB-086 remains priority #1 and remains blocked on the previously recorded requirement for a byte-preserving composition path for the exact retained hidden-rowid patch. No manual/model reserialization of the LAB-086 security-critical file was attempted.
