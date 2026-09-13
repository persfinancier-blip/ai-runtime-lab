# LAB-099 orchestration source audit after exact-materialization probe

Date: 2026-09-13

## Scope

Resume the exact next action from `state/CURRENT.md`: keep LAB-086 priority first, probe exact materialization for pinned snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`, then fall back to the frozen LAB-099 orchestration closure only if the exact LAB-086 snapshot cannot be materialized.

## Observed runtime capability

A direct local Git materialization was attempted in this run:

```text
git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git /tmp/ai-runtime-lab
fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com
exit 128
```

The failure happened before repository code execution. The GitHub connector can still read the exact pinned commit tree and UTF-8 files, including the LAB-086 manifest and exact PR #186 files, but this runtime still exposes no supported non-model byte bridge from connector reads into the local filesystem. Therefore no new LAB-086 executable/security/compile/conflict PASS and no LAB-099 exact import/SQLite PASS is claimed.

## LAB-086 disposition

The pinned LAB-086 exact-gate manifest remains authoritative at `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. Its remaining gate is unchanged: reconstruct the complete branch-local LAB-080→086 dependency closure and all LAB-086 `test_*.py`, verify every blob, execute normal real-schema tests, execute the unsafe legacy-promotion expected-failure seed separately, run compileall, then perform fresh security/reconciliation and current-main conflict audits. PR #165 remains draft.

## LAB-099 fallback source audit

Because exact byte materialization remained unavailable, this run re-audited the already-frozen orchestration path at PR #186 head `766434563a5ad82a88156687c84de9c9e17b14c6` rather than inventing execution evidence.

Audited exact files included:

- `lab099_confirmed_orchestration_witness.py` blob `71a50df5b5d8c3cece33274d5263f1c4fe0ec27a`;
- `lab099_shared_anchor_prefix_witness.py` blob `079d42b61836294d433170d4aace867e1c03b106`;
- `lab099_confirmed_execution_witness.py` blob `454e76cb3059353d041ba83f81dc11b9eec45b5c`;
- `lab099_precursor_fixture_adapter.py` blob `671ace9ed879a0a1d0c06786b11d2e46fb746de3`;
- `lab099_precursor_fixture_vectors.py` blob `73406169990849327774fc46682747a14222bd9d`;
- `lab099_confirmed_fixture_row_verifier.py` blob `b1324194ef0f9c251ccdc747394d63b7b0a9d68a`;
- `anchor_attestation/protocol.py` blob `15d8b7cf8ff093490ccb75679030d3a0fe41e401`;
- `provider_generation_history/supported.py` blob `8140d6e180c3e97085830b872cea7d87f8433144`.

### Audit conclusions

1. The legitimate prefix builder still creates positions 1..41 only through `SupportedHistoricalSharedAnchorLedger.execute()`; it does not synthesize shared-anchor rows or manually advance `shared_anchor_meta`.
2. The orchestration uses the prefix runtime/provider at the authenticated predecessor tail, installs the frozen PREPARED row, performs the exact request through provider `increment()` and `reconcile_increment()`, constructs a `HistoricalReceipt`, and persists that receipt through the existing provider-history store before CONFIRMED mutation.
3. The CONFIRMED fixture plan remains fail-closed and exact: it only accepts the frozen PREPARED digest and updates a row that matches every authority-relevant field of the independently frozen bridge.
4. The persisted CONFIRMED verifier reconstructs exact PREPARED ancestry, externally reauthenticates the provider result, compares the stable receipt, and binds the row to externally supplied confirmed position/head authority.
5. The orchestration finishes with `HistoricalSharedAnchorLedger.verify_durable()`. The previously found missing historical-receipt persistence defect remains fixed.
6. No new semantic or authority-substitution defect was established in this source audit. This is not executable evidence; the frozen 18-file import closure remains the required next executable gate.

## Decision

Keep `LAB099_EXACT_ORCHESTRATION_IMPORT_CLOSURE_V1_FROZEN` unchanged. Do not add production `activation_reservation_provenance` code until the exact closure is byte-materialized and the orchestration executes, followed by an observed production RED.

## Exact next action

At the next runtime, probe LAB-086 exact materialization once first. If still unavailable, attempt a supported byte-preserving transfer of the already-frozen 18-file LAB-099 closure into local storage. Only if every `git hash-object` matches the manifest should the runtime run compileall and the fresh file-backed SQLite orchestration. Otherwise preserve the source-audit result and do not claim RED/GREEN.