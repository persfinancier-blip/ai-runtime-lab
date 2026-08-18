# Durable Run-State Reference Prototype

Standard-library Python prototype for LAB-005.

## Protocol in one sentence

Persist intent before a non-trivial side effect, attach a stable idempotency key, version every checkpoint, issue monotonically increasing fencing tokens to new attempts, and reconcile an unknown outcome against durable external evidence before retrying.

## State fields

- `schema_version` — compatibility boundary; unsupported snapshots are rejected.
- `run_id` / `work_id` — stable identity of run and logical work item.
- `generation` — optimistic checkpoint version; stale writers cannot overwrite newer state.
- `fence` — monotonic attempt ownership token; stale workers are rejected by the external-effect simulator.
- `attempt` — number of claims/resumptions.
- `phase` — `NEW`, `EFFECT_INTENT_RECORDED`, `EFFECT_UNKNOWN`, `EFFECT_CONFIRMED`, `DONE`.
- `effect_key` — stable idempotency key for the logical side effect.
- `effect_receipt` — durable proof returned/recovered from the external system.
- `payload` — reconstructable task inputs needed to execute the current step.
- `evidence` — references/receipts only; this is not a full audit ledger.

## Checkpoint rule

For non-idempotent or externally visible work:

1. persist `EFFECT_INTENT_RECORDED` + stable `effect_key`;
2. execute the side effect using idempotency/fencing if the external system supports it;
3. if success is observed, persist `EFFECT_CONFIRMED` + receipt;
4. if transport fails after possible commit, persist `EFFECT_UNKNOWN`;
5. on resume, query/reconcile using the same idempotency identity before retrying;
6. only mark `DONE` after confirmed evidence exists.

## Run

```bash
python -m unittest discover -s experiments/durable_run_state/tests -p 'test_*.py' -v
```

The deliberately unsafe baseline is kept outside normal discovery:

```bash
python -m unittest experiments.durable_run_state.tests.unsafe_seed_expected_failure
```

It is expected to fail because a timeout-after-commit followed by a naive retry increments the external counter twice.

## Non-goals

This prototype is not a workflow engine, message broker, database, distributed lock service, or conversational memory system. It only demonstrates the minimum correctness contract around durable execution state and external side effects.
