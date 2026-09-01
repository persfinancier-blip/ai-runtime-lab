# LAB-092 — post-reauthentication recovery race audit

Date: 2026-09-01

## Question

Can provider-history or activation state change after the LAB-092 migration marker has been successfully externally re-authenticated but before the subsequent LAB-090 constructor runs `_recover_pending_activation()`, causing mutation before authority is revalidated?

## Sources inspected

- PR #177 head `7b14fc29217bdf987704d61bfcbc80fba43db1a4`, `experiments/provider_generation_history/activation_schema_provenance.py` blob `35e1adef996640578bf7ade76972680189211bd4`.
- LAB-090 head `d9a381dd4607a928cd1315adef6431e239995bc1`, `experiments/provider_generation_history/supported.py`.
- LAB-081 integration runtime/durable-head checks in `experiments/provider_generation_history/integration.py`.

## Result

No reachable mutation-before-revalidation gap was found in this handoff.

After LAB-092 `confirmation.execute(_completion_intent())` returns a CONFIRMED marker, `ProvenancedHistoricalSharedAnchorLedger` constructs the LAB-090 surface via `super().__init__()`. LAB-090 constructor ordering is:

1. construct provider-history / shared-ledger primitives;
2. `_init_activation_schema()` — dynamically dispatched to the LAB-092 read-only classifier;
3. `_require_runtime_matches_durable_head()`;
4. `_recover_pending_activation()`;
5. `_verify_activation_records()`.

Therefore a concurrent provider generation rotation that commits after marker reauthentication but before LAB-090 recovery changes the durable generation head. The constructor then compares the still-supplied runtime descriptor against that new durable head and raises `CurrentGenerationRequired` before `_recover_pending_activation()` can mutate provider activation state.

A provider activation transition without a generation-head change does not create a bypass. New activation rows are created by LAB-090 rotation in the same SQLite writer transaction as `_rotate_locked()`, so a newly created activation necessarily carries the corresponding durable generation-head mutation. Recovery of an already-existing activation for the current generation can race with another legitimate recovery process, but the LAB-090 recovery transitions are exact-ticket/state checked and are designed to reconcile idempotently across PREPARED / COMMITTED_FENCED / RELEASED states; this is convergence, not authority bypass.

The marker itself no longer leaves a PREPARED shared-anchor intent after successful confirmation, so a subsequent legitimate provider rotation is allowed. That is safe because the constructor's durable-head revalidation occurs before activation recovery.

## Execution observation

A fresh exact checkout was attempted in this run:

`git clone --depth 1 --branch lab-092-activation-schema-provenance https://github.com/persfinancier-blip/ai-runtime-lab.git ...`

It failed before repository code execution with `Could not resolve host: github.com`. No branch-level test PASS is claimed.

## Decision

Close this specific audit question as structurally guarded; no code change is justified without a counterexample. Keep PR #177 draft because exact behavioral execution remains pending.

Next highest-value LAB-092 work while source execution remains unavailable: audit migration/restart composition against LAB-090 activation-record verification for historical COMMITTED rows and ensure provenance verification cannot mask or reorder `_verify_activation_records()` failures. LAB-086 remains priority #1 and must only be published through the exact byte-preserving predecessor+patch contract recorded in `state/CURRENT.md`.
