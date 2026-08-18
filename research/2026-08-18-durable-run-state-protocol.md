# Durable Run-State Protocol — donor comparison and experiment

Date: 2026-08-18  
Issue: #8 / LAB-005  
Branch: `lab/005-durable-run-state`

## Research question

What is the smallest durable state and transition contract that lets an autonomous agent resume after process/session loss without duplicating external side effects, accepting stale state, or allowing an obsolete worker to keep mutating the run?

## Donor mechanisms

### 1. OpenAI Agents SDK — serialized `RunState`

Primary sources:
- https://openai.github.io/openai-agents-python/ref/run_state/
- https://github.com/openai/openai-agents-python/blob/main/.agents/references/runstate-schema.md

Transferable mechanisms:
- `RunState` is an explicit serializable pause/resume boundary rather than an implicit reconstruction from chat history.
- The snapshot carries continuation-critical execution context, interruptions/approval state and runtime metadata.
- Serialization is compatibility-sensitive: state is schema-versioned and unsupported newer versions are rejected rather than silently interpreted.
- Context serialization is conservative; non-serializable context needs an explicit reconstruction path.
- Secret-bearing trace material is not persisted by default.

Implication: durable execution state needs an explicit schema/version boundary and should persist continuation-critical data, not arbitrary in-memory objects or secrets.

### 2. LangGraph — checkpoints, pending writes, replay

Primary sources:
- https://docs.langchain.com/oss/python/langgraph/persistence
- https://github.com/langchain-ai/docs/blob/main/src/oss/langgraph/persistence.mdx

Transferable mechanisms:
- checkpoints are explicit execution-boundary snapshots;
- pending writes can preserve successful task outputs inside a partially failed super-step;
- replay skips work before a checkpoint but re-executes later nodes, including external requests, so replay is not automatically side-effect safe;
- checkpointed run/thread state and long-term stores are distinct concepts.

Implication: replayable regions containing side effects need idempotency/reconciliation in addition to checkpointing.

### 3. AWS Durable Execution — retry semantics and idempotency

Primary source:
- https://docs.aws.amazon.com/durable-execution/patterns/best-practices/idempotency/

Transferable mechanisms:
- replay/retry can execute an operation more than once;
- at-least-once is appropriate for idempotent work;
- at-most-once per attempt avoids automatic re-execution after interruption but does not create global exactly-once semantics across retries;
- non-idempotent external side effects need explicit reconciliation/no-retry semantics.

Implication: `UNKNOWN` outcome is a first-class state. Timeout after an effect may mean “committed but unobserved”, so resume must reconcile by stable identity before retrying.

### Supporting reference: Temporal

Primary source:
- https://docs.temporal.io/

Temporal reinforces the architectural split between durable workflow progress and side-effecting activities: process loss should not lose orchestration state, while replay-sensitive code and external effects require explicit execution semantics.

## Synthesized minimal protocol

### Durable state

- schema/protocol version;
- stable run/work identity;
- optimistic generation/version;
- ownership/fencing token and attempt identity;
- current phase;
- stable idempotency identity for any prepared side effect;
- side-effect status including `UNKNOWN` and receipt when available;
- deterministic/reconstructable inputs for the current step;
- evidence references required to justify terminal success.

### Reconstructable rather than embedded

- large source documents/repository content addressable by stable reference;
- versioned tool definitions;
- derived summaries reproducible from durable evidence.

### Concepts that must stay distinct

**Conversational memory** records prior discussion/preferences and may influence planning, but it is not authoritative proof that a side effect committed.

**Evidence/audit records** record observations, tests and external acknowledgements; they are provenance-oriented and should outlive one attempt.

**Durable run state** records where execution is, who owns it, which effect is pending/unknown/confirmed, and what action is safe next.

## Transition model

```text
NEW
  -> claim(fence++)
  -> EFFECT_INTENT_RECORDED  [persist idempotency key before effect]
      -> EFFECT_CONFIRMED    [receipt observed]
      -> EFFECT_UNKNOWN      [possible commit, result unobserved]

EFFECT_UNKNOWN / EFFECT_INTENT_RECORDED
  -> reconcile(effect_key)
      -> EFFECT_CONFIRMED       [external receipt exists]
      -> EFFECT_INTENT_RECORDED [no receipt; retry with same key]

EFFECT_CONFIRMED -> DONE
```

Every state write uses optimistic `generation`; every new attempt increments `fence`. The external-effect simulator rejects a lower fence than the latest registered owner.

## Failure-injection experiment

Prototype: `experiments/durable_run_state/`

### Seeded unsafe design

A deliberately unsafe counter commits an increment, raises a timeout, then naively retries without idempotency. The safety test expected one effect but observed two:

```text
AssertionError: 2 != 1 : unsafe retry duplicated the external side effect
FAILED (failures=1)
```

The failing baseline is retained as `tests/unsafe_seed_expected_failure.py` outside normal passing discovery.

### Corrected protocol

Local command executed:

```bash
python -m unittest discover -s experiments/durable_run_state/tests -p 'test_*.py' -v
```

Observed result: **8 tests passed**.

Covered scenarios:
1. clean checkpoint -> fresh process object -> resume;
2. duplicate delivery -> no repeated effect;
3. unsupported schema -> hard rejection;
4. crash after durable intent but before external effect -> safe retry;
5. timeout after committed external effect -> `UNKNOWN` then reconciliation without duplicate;
6. retry/lost confirmation after successful effect -> same idempotency receipt, no duplicate;
7. stale worker -> fencing rejects external mutation;
8. stale checkpoint generation -> optimistic version check rejects overwrite.

`python -m compileall -q experiments` also completed successfully.

## Findings

1. Checkpointing alone is insufficient when replay can reissue external calls.
2. `UNKNOWN` is distinct from success and failure; it means reconcile before retry.
3. Exactly-once should not be assumed. The useful primitive is durable intent + idempotency/reconciliation + evidence.
4. Schema version and state generation solve different problems: compatibility versus stale writes.
5. Fencing is different from optimistic versioning: generation protects the checkpoint store; fencing protects external actions from obsolete owners.
6. Durable run state should stay small and authoritative; large context should be referenced/reconstructed where safe.

## Integration implications

A future production implementation should preserve these concepts independent of storage technology:
- `run_id`, `work_id`, `attempt_id`;
- `protocol/schema_version`;
- monotonic checkpoint `generation`;
- monotonic owner `fence`/lease epoch;
- durable side-effect intent + stable idempotency key;
- side-effect status including `UNKNOWN`;
- reconciliation adapter for externally visible effects;
- evidence receipt/reference before terminal success;
- atomic/transactional persistence or compare-and-swap equivalent.

A SQL implementation can implement generation/fence checks with conditional row updates; external adapters should transmit idempotency/fencing material wherever supported.

## Non-goals

- no general DAG/workflow scheduler;
- no multi-agent routing;
- no vector/conversational-memory architecture;
- no distributed consensus implementation;
- no claim that JSON files are production storage;
- no claim of universal exactly-once side effects.

## Stop-condition assessment

Three donor families were compared and the prototype passes the required failure matrix after demonstrating the unsafe baseline failure. Remaining work is repository audit/integration, not broader research.
