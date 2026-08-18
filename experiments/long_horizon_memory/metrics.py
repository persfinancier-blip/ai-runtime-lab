from __future__ import annotations

from experiments.long_horizon_memory.benchmark import Case, STRATEGIES, _tokens, corpus


def surface_relevance(strategy_name: str, cases: tuple[Case, ...] | None = None, k: int = 3) -> float:
    """Fraction of selected memories with any lexical overlap with the query.

    This deliberately shallow metric represents topical/surface relevance only. It does
    not know whether a selected memory is current, superseded, invalidated, or causal.
    """
    cases = cases or corpus()
    strategy = STRATEGIES[strategy_name]
    scores: list[float] = []
    for case in cases:
        by_id = {memory.id: memory for memory in case.memories}
        query_tokens = _tokens(case.query)
        for memory_id in strategy(case, k):
            memory = by_id[memory_id]
            candidate_tokens = _tokens(
                " ".join((memory.text, memory.subject, memory.predicate, memory.value))
            )
            scores.append(1.0 if query_tokens & candidate_tokens else 0.0)
    return sum(scores) / len(scores) if scores else 0.0


def surface_relevance_all() -> dict[str, float]:
    return {name: surface_relevance(name) for name in STRATEGIES}


if __name__ == "__main__":
    import json

    print(json.dumps(surface_relevance_all(), indent=2, sort_keys=True))
