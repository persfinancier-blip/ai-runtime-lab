# LAB-094/095/096 retained-authority closure inventory — 2026-09-16

## Runtime observation

LAB-086 was probed first in this run. A direct `git clone https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 executable PASS and no exact PR #187 pytest/compileall GREEN are claimed.

## PR #187 closure inventory

Audited branch: `lab-095-database-identity-red-intent`, head observed at `5bfdbdbd64d2281206b1c3d1e9a00db8bdbd4057`.

Current connector-observed blobs relevant to the retained-authority closure:

- `experiments/database_binding.py` — `c6bf05b3a5579e076142300aefbc9d785cc6354a`
- `experiments/provider_generation_history/database_identity.py` — `bac58a48c576001370144cc10cfab8e0cfd129e3`
- `experiments/provider_generation_history/database_identity_migration.py` — `c4d1db46b8b64fec116dcfef8bb05e1e7a7b875e`
- `experiments/provider_generation_history/integration.py` — `83399d3d184ae61bcfb50a749c11a348e835f428`
- `experiments/provider_generation_history/supported.py` — `0c645593a86efa5a1990dd4f13775e6fcfbc2272`
- `experiments/shared_anchor_intent_ledger/supported.py` — `b16fda1fd1f47ab3f333af6ac94190d6135dcf64`
- `experiments/provider_generation_history/tests/test_provider_history_capability_surface.py` — `1ef1583b86d6d4287e5a018fc1ff95cce25f1f7b`

The prior closure inventory must therefore treat `supported.py` and the capability-surface regression as changed after the bootstrap-root fix; stale hashes from before commits `40f97cb...` / `5bfdbdb...` are not acceptable execution evidence.

## Retained-authority audit result

For the supported historical ledger graph, the three repository-owned retained authorities identified by #179/#180/#181 are now source-bound:

1. **Bootstrap trust root (#179 / LAB-094).** `CoordinatorOnlyProviderHistory.bootstrap` is backed by private `_bootstrap_generation`; both public and private-slot rebinding are rejected after first assignment. `_verify_durable_locked()` continues consuming `self.bootstrap`, which now resolves to that construction-bound slot.
2. **Canonical database path (#180 / LAB-095).** `CanonicalDatabaseBinding` canonicalizes the first path assignment and rejects later `path` or `_canonical_database_path` rebinding. Both `SupportedSharedAnchorLedger` and `CoordinatorOnlyProviderHistory` inherit this binding, so ledger/history connection and classifier paths share construction-bound sources of truth.
3. **Provider-history strategy (#181 / LAB-096).** `SupportedHistoricalSharedAnchorLedger` stores exact `CoordinatorOnlyProviderHistory` in private `_provider_history`, rejects public/private strategy rebinding, exposes only `ProviderHistoryInspectionView`, and inherited internal calls resolve through `_history()` to the private strategy.

No additional repository-owned retained authority of the same class was found in the inspected production surfaces. `attested` remains mutable/reachable, but it is explicitly the caller-owned external provider capability tracked separately by LAB-093/#178; rotation intentionally replaces the runtime attested capability after durable activation. It must not be silently folded into LAB-094/095/096 without resolving #178's ownership contract.

## Exact executable gates required before #179/#180/#181 can leave draft

At minimum, materialize the exact PR #187 closure and run:

### Focused retained-authority / identity gates

- `pytest -q experiments/provider_generation_history/tests/test_provider_history_capability_surface.py`
- `pytest -q experiments/provider_generation_history/tests/test_database_path_binding.py`
- `pytest -q experiments/provider_generation_history/tests/test_database_binding_object_new_surface.py`
- `pytest -q experiments/provider_generation_history/tests/test_database_identity.py`
- `pytest -q experiments/provider_generation_history/tests/test_database_identity_audit.py`
- `pytest -q experiments/provider_generation_history/tests/test_database_identity_migration.py`
- `pytest -q experiments/provider_generation_history/tests/test_database_identity_migration_recovery.py`
- `pytest -q experiments/provider_generation_history/tests/test_database_identity_orphan_intent_classifier.py`
- `pytest -q experiments/provider_generation_history/tests/test_database_identity_rotation_reauthentication.py`
- `pytest -q experiments/provider_generation_history/tests/test_audit_regressions.py`
- `pytest -q experiments/provider_generation_history/tests/test_store_receipt_guard_hook.py`

### Composed LAB-090/LAB-092/LAB-101 and integration gates

- `pytest -q experiments/provider_generation_history/tests/test_activation_fence_composed.py`
- `pytest -q experiments/provider_generation_history/test_activation_schema_startup.py`
- `pytest -q experiments/provider_generation_history/tests/test_activation_schema_contract.py`
- `pytest -q experiments/provider_generation_history/tests/test_activation_schema_provenance_guard.py`
- `pytest -q tests/test_activation_coordinator_ordering.py`
- `pytest -q tests/test_activation_restart_recovery.py`
- `pytest -q tests/test_activation_schema_explicit_bootstrap.py`
- `pytest -q tests/test_activation_schema_explicit_bootstrap_failures.py`
- `pytest -q tests/test_activation_schema_migration_writer.py`
- `pytest -q tests/test_activation_transition_ordering.py`
- `pytest -q tests/test_supported_activation_wiring.py`
- `pytest -q experiments/provider_generation_history/tests/test_integration.py`

### Downstream LAB-080/LAB-081 baselines

Repository history and current main-tree discovery now pin the downstream suites instead of leaving them implicit.

LAB-080 merged evidence (#152) identifies the primary, restart, and supported suites; current main exposes the same three test files. Run:

- `pytest -q experiments/shared_anchor_intent_ledger/tests/test_protocol.py`
- `pytest -q experiments/shared_anchor_intent_ledger/tests/test_restart_rollback.py`
- `pytest -q experiments/shared_anchor_intent_ledger/tests/test_supported.py`

Also preserve the LAB-080 unsafe control as an expected failure, not as a normal GREEN gate:

- `python -m unittest experiments.shared_anchor_intent_ledger.tests.unsafe_monotonic_expected_failure -v` — expected to fail by design.

LAB-081 merged evidence (#154) states that its provider-generation continuity/integration suite was validated together with LAB-080. Current main exposes these LAB-081 test files; run all four explicitly:

- `pytest -q experiments/provider_generation_history/tests/test_protocol.py`
- `pytest -q experiments/provider_generation_history/tests/test_standalone_audit.py`
- `pytest -q experiments/provider_generation_history/tests/test_audit_regressions.py`
- `pytest -q experiments/provider_generation_history/tests/test_integration.py`

The latter two overlap the focused/composed list above; they need not be executed twice in one exact-tree run, but the closure record must count their observed result toward both the LAB-095/096 and LAB-081 downstream gates.

### Complete repository / syntax gate

After the focused, composed, LAB-080, and LAB-081 gates pass on the exact PR #187 tree, run the complete repository test suite and `python -m compileall` over the repository Python surfaces. Record the exact commands and observed counts from the materialized tree. Do not infer those results from connector source inspection.

## Decision

Source-level closure for LAB-094/095/096 is coherent enough to stop broadening the patch. The remaining blocker is executable evidence, not another speculative authority rewrite. Keep PR #187 draft until exact materialization permits hash verification plus the focused/composed/downstream gates above. If execution finds a defect, fix it at the failing abstraction boundary and re-run; do not infer GREEN from this audit.
