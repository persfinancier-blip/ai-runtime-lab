# Capability Planner Reference Prototype

LAB-008 standard-library prototype for per-run capability negotiation and safe fallback planning.

## Core contract

1. Observe capabilities in the current run rather than inheriting them from prior runs.
2. Version both observations and requirements.
3. Attach freshness (`observed_at` + `ttl`) and evidence references to observations.
4. Separate **hard requirements** from **preferences**.
5. Reject any candidate that fails a hard requirement before scoring preferences.
6. Rank remaining candidates deterministically.
7. Emit rejection reasons, selected evidence references, and a stable explanation hash.

A route that is faster or higher priority can never compensate for violating a hard safety/correctness property.

## Run

From repository root:

```bash
python -m unittest discover -s experiments/capability_planner/tests -v
python -m compileall -q experiments/capability_planner
```

## Seeded matrix

- preferred path available;
- preferred path unavailable, safe equivalent fallback available;
- stale observation;
- unsafe fallback with attractive priority;
- deterministic tie-breaking;
- no viable path;
- stable explanation identity.

## Integration boundaries

The planner is not durable run state and is not an evidence ledger. A LAB-005 run may store the chosen `explanation_id`/route as continuation state; LAB-007 may store the observation/evidence records used by the planner. The planner consumes those facts and produces a decision.

## Non-goals

No plugin marketplace, workflow engine, credential broker, distributed probe service, or automatic authorization escalation is implemented here.
