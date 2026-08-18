# LAB-009 Metric Separation Audit

Date: 2026-08-18

The first remote patch audit found that the benchmark explicitly measured current/causal recall and stale intrusion, but only represented topical relevance implicitly through the similarity strategy. The issue acceptance criteria require relevance to be distinguishable from causal/current correctness, so the experiment was strengthened before integration.

## Added metric

`experiments/long_horizon_memory/metrics.py` adds `surface_relevance`: the fraction of selected memories sharing any lexical token with the query.

It is intentionally shallow. It does **not** inspect supersession, invalidation, provenance authority, or causal necessity. That makes it a useful control metric for the exact failure mode under study: context can look topically relevant while still being unsafe or stale.

## Observed deterministic result

The similarity strategy produced:

- surface relevance: `0.8888888889`;
- current/causal recall: `1.0`;
- stale intrusion: `0.2222222222`.

Therefore high superficial relevance and perfect required-fact recall did not imply clean/current context: more than one fifth of its selected context was known stale in the seeded cases.

The typed temporal graph retained `1.0` current/causal recall with `0.0` stale intrusion.

Two additional deterministic metric-separation tests passed, bringing the observed LAB-009 validation to 9 tests total (7 core benchmark tests + 2 metric-separation tests).

## Audit conclusion

The strengthened experiment now separates three concepts:

1. **surface relevance** — does retrieved text look related to the query?;
2. **current/causal recall** — are the facts needed for the correct current answer/reasoning chain present?;
3. **stale intrusion** — how much known-invalid/superseded context contaminated the result?

This closes the metric ambiguity found during audit. No broader infrastructure is required for the LAB-009 stop condition.