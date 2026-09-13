# LAB-095 — LAB-090/LAB-092 path-binding integration audit

Date: 2026-09-13

## Scope

Source-audit the retained LAB-090 and LAB-092 constructors/helpers against the LAB-095 `CanonicalDatabaseBinding` slice on draft PR #187. This is an integration audit, not a claim that the exact LAB-090/LAB-092 behavioral suites executed in this runtime.

## Runtime observation

LAB-086 remained priority #1 and was probed first. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 gate was weakened and no new LAB-086 PASS is claimed.

## Findings

### 1. LAB-090 repeats the supported constructor pattern in the same file that LAB-095 modifies

LAB-090 PR #175 rewrites `experiments/provider_generation_history/supported.py`. Its `SupportedHistoricalSharedAnchorLedger.__init__()` constructs `CoordinatorOnlyProviderHistory(path, bootstrap)` and then calls `SupportedSharedAnchorLedger.__init__(self, path, attested)`.

LAB-095 PR #187 also modifies that same supported surface by making `CoordinatorOnlyProviderHistory(CanonicalDatabaseBinding, IntegratedProviderHistory)` and by layering the shared-ledger binding below it.

Therefore LAB-095 cannot be considered safely integrated into LAB-090 merely because PR #187 is correct on its own branch. When the retained drafts are eventually reconciled, the LAB-090 version of `supported.py` must preserve the LAB-095 mixin/MRO. Dropping the mixin while conflict-resolving would reopen the original mutable-path finding.

### 2. LAB-092 intentionally constructs reservation surfaces with `object.__new__`

LAB-092 `activation_schema_provenance.py` has two helper patterns that bypass ordinary base constructors:

- `_reservation_surface()` uses `object.__new__(SupportedHistoricalSharedAnchorLedger)`, then performs the first `ledger.path = str(path)` assignment; it separately uses `object.__new__(CoordinatorOnlyProviderHistory)` and performs the first `history.path = str(path)` assignment.
- `_bind_live_provider_history_provenance()` uses `object.__new__(_ProvenanceBoundCoordinatorOnlyProviderHistory)`, assigns the first path from the already-live history object, then installs the replacement helper.

This is not itself a rebinding bypass if the LAB-095 MRO is preserved: `CanonicalDatabaseBinding` deliberately allows exactly one first assignment, canonicalizes it, and rejects subsequent public or private-slot assignment. But this object-construction idiom is security-relevant and needs an executable regression because it does not exercise the normal constructor path.

### 3. Added narrow executable regression for the LAB-092 construction idiom

PR #187 now adds `experiments/provider_generation_history/tests/test_database_binding_object_new_surface.py`.

The test mirrors LAB-092's `object.__new__ + first manual path assignment` pattern using a minimal `CanonicalDatabaseBinding` subclass. It verifies:

1. the uninitialized surface has no readable path;
2. the first manual assignment is canonicalized;
3. a second public `path` assignment is rejected;
4. direct later assignment of `_canonical_database_path` is rejected;
5. the original canonical DB remains selected.

The exact published production binding blob `c6bf05b3a5579e076142300aefbc9d785cc6354a` and exact new test blob `25cd1d53fece40ab71a78ff4838381950505ce0d` were reconstructed in an isolated local package and independently verified with `git hash-object`. The focused unittest executed and passed 1/1.

This is exact evidence for the two-file binding primitive/regression only. It is not a substitute for the retained full LAB-090/LAB-092 dependency closure or DB-A/DB-B regression.

## Decision

Keep PR #187 draft. Treat preservation of `CanonicalDatabaseBinding` in the eventual LAB-090 `supported.py` conflict resolution as a mandatory integration condition. LAB-092's `object.__new__` reservation/replacement helpers are compatible with the one-assignment binding contract, but only when that MRO is present.

## Remaining gates

- LAB-086 exact complete gate still has priority.
- Execute full `test_database_path_binding.py` on the exact repository closure when a safe byte-preserving materialization path exists.
- Before integrating LAB-095 with retained LAB-090/LAB-092 drafts, inspect the resolved MRO and ensure both live ledger and provider-history helper inherit the binding.
- Run LAB-080/LAB-081/LAB-090/LAB-092 focused/downstream behavioral gates.
- Continue LAB-095 migration crash/partial/concurrent/legacy-history regressions.
