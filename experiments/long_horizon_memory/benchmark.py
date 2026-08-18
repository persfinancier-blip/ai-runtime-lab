from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Memory:
    id: str
    time: int
    subject: str
    predicate: str
    value: str
    text: str
    provenance: str
    supersedes: str | None = None
    invalidated: bool = False
    causes: tuple[str, ...] = ()
    objective: str | None = None


@dataclass(frozen=True)
class Case:
    name: str
    query: str
    memories: tuple[Memory, ...]
    expected_ids: frozenset[str]
    stale_ids: frozenset[str]


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", text.lower()))


def recency(case: Case, k: int = 3) -> list[str]:
    return [m.id for m in sorted(case.memories, key=lambda m: m.time, reverse=True)[:k]]


def similarity(case: Case, k: int = 3) -> list[str]:
    query = _tokens(case.query)
    scored: list[tuple[float, int, str]] = []
    for memory in case.memories:
        candidate = _tokens(
            " ".join((memory.text, memory.subject, memory.predicate, memory.value))
        )
        score = len(query & candidate) / (len(query | candidate) or 1)
        scored.append((score, memory.time, memory.id))
    return [row[2] for row in sorted(scored, reverse=True)[:k]]


def typed_temporal_graph(case: Case, k: int = 3) -> list[str]:
    superseded = {m.supersedes for m in case.memories if m.supersedes}
    live = [
        m
        for m in case.memories
        if not m.invalidated and m.id not in superseded
    ]
    query = _tokens(case.query)
    seeds: list[Memory] = []
    for memory in live:
        fields = _tokens(
            " ".join(
                (
                    memory.subject,
                    memory.predicate,
                    memory.value,
                    memory.text,
                    memory.objective or "",
                )
            )
        )
        if query & fields:
            seeds.append(memory)

    by_id = {m.id: m for m in case.memories}
    result: list[str] = []
    seen: set[str] = set()
    for memory in sorted(seeds, key=lambda m: m.time, reverse=True):
        if memory.id not in seen:
            result.append(memory.id)
            seen.add(memory.id)
        for cause_id in memory.causes:
            cause = by_id.get(cause_id)
            if (
                cause
                and not cause.invalidated
                and cause.id not in superseded
                and cause.id not in seen
            ):
                result.append(cause.id)
                seen.add(cause.id)
        if len(result) >= k:
            break
    return result[:k]


def bounded_hybrid(case: Case, k: int = 3) -> list[str]:
    graph_candidates = typed_temporal_graph(case, k=5)
    similarity_candidates = similarity(case, k=5)
    superseded = {m.supersedes for m in case.memories if m.supersedes}
    invalid = {m.id for m in case.memories if m.invalidated}
    forbidden = superseded | invalid

    result: list[str] = []
    for candidate in graph_candidates + similarity_candidates:
        if candidate not in forbidden and candidate not in result:
            result.append(candidate)
        if len(result) >= k:
            break
    return result


def corpus() -> tuple[Case, ...]:
    cases: list[Case] = []
    cases.append(
        Case(
            "supersession",
            "What is the current deployment region?",
            (
                Memory("m1", 1, "deployment", "region", "us-east", "Deployment region is us-east.", "config-v1"),
                Memory("m2", 2, "deployment", "region", "eu-west", "Deployment region changed to eu-west.", "config-v2", supersedes="m1"),
                Memory("d1", 3, "marketing", "region", "us-east", "Campaign targets us-east region.", "campaign"),
            ),
            frozenset({"m2"}),
            frozenset({"m1"}),
        )
    )
    cases.append(
        Case(
            "distractor",
            "Which database does the billing service use?",
            (
                Memory("m3", 1, "billing", "database", "postgres", "Billing service uses postgres.", "architecture"),
                Memory("d2", 4, "analytics", "database", "clickhouse", "Analytics database is clickhouse.", "architecture"),
                Memory("d3", 5, "docs", "database", "sqlite", "Docs example uses sqlite database.", "docs"),
            ),
            frozenset({"m3"}),
            frozenset(),
        )
    )
    cases.append(
        Case(
            "causal_chain",
            "Why is checkout retry disabled?",
            (
                Memory("c1", 1, "payments", "incident", "duplicate_charge", "Duplicate charges occurred during retries.", "incident"),
                Memory("c2", 2, "checkout", "retry", "disabled", "Checkout retry was disabled because of duplicate charges.", "decision", causes=("c1",)),
                Memory("d4", 3, "checkout", "timeout", "30s", "Checkout timeout is 30s.", "config"),
            ),
            frozenset({"c1", "c2"}),
            frozenset(),
        )
    )
    cases.append(
        Case(
            "objective_change",
            "What is the current optimization objective for search?",
            (
                Memory("o1", 1, "search", "objective", "latency", "Optimize search for latency.", "goal-v1", objective="latency"),
                Memory("o2", 3, "search", "objective", "conversion", "Objective changed: optimize search for conversion.", "goal-v2", supersedes="o1", objective="conversion"),
                Memory("d5", 4, "search", "latency", "120ms", "Search latency is 120ms.", "metric"),
            ),
            frozenset({"o2"}),
            frozenset({"o1"}),
        )
    )
    cases.append(
        Case(
            "provenance_conflict",
            "What is the approved refund limit?",
            (
                Memory("p1", 1, "refund", "limit", "100", "Draft says refund limit is 100.", "draft", invalidated=True),
                Memory("p2", 2, "refund", "limit", "50", "Approved policy sets refund limit to 50.", "policy-approved"),
                Memory("d6", 3, "refund", "limit", "100", "Chat mentions refund limit 100.", "chat"),
            ),
            frozenset({"p2"}),
            frozenset({"p1"}),
        )
    )

    long_history: list[Memory] = [
        Memory("lh0", 1, "warehouse", "carrier", "DHL", "Warehouse carrier is DHL.", "ops-v1")
    ]
    for index in range(2, 22):
        long_history.append(
            Memory(
                f"lh{index}",
                index,
                f"noise{index}",
                "status",
                f"value{index}",
                f"Noise event {index} status value{index}.",
                "noise",
            )
        )
    long_history.append(
        Memory("lh22", 22, "warehouse", "carrier", "UPS", "Warehouse carrier changed to UPS.", "ops-v2", supersedes="lh0")
    )
    for index in range(23, 28):
        long_history.append(
            Memory(f"lh{index}", index, f"noise{index}", "status", f"value{index}", f"Recent noise event {index}.", "noise")
        )
    cases.append(
        Case(
            "long_horizon_noise",
            "What is the current warehouse carrier?",
            tuple(long_history),
            frozenset({"lh22"}),
            frozenset({"lh0"}),
        )
    )
    return tuple(cases)


Strategy = Callable[[Case, int], list[str]]
STRATEGIES: dict[str, Strategy] = {
    "recency": recency,
    "similarity": similarity,
    "typed_temporal_graph": typed_temporal_graph,
    "bounded_hybrid": bounded_hybrid,
}


def evaluate(strategy: Strategy, cases: tuple[Case, ...] | None = None, k: int = 3) -> dict:
    cases = cases or corpus()
    rows = []
    for case in cases:
        selected = strategy(case, k)
        selected_set = set(selected)
        current_causal_recall = len(selected_set & case.expected_ids) / len(case.expected_ids)
        stale_intrusion = len(selected_set & case.stale_ids) / (len(selected) or 1)
        rows.append(
            {
                "case": case.name,
                "selected": selected,
                "current_causal_recall": current_causal_recall,
                "stale_intrusion": stale_intrusion,
            }
        )
    return {
        "mean_current_causal_recall": sum(row["current_causal_recall"] for row in rows) / len(rows),
        "mean_stale_intrusion": sum(row["stale_intrusion"] for row in rows) / len(rows),
        "rows": rows,
    }


def run_all() -> dict[str, dict]:
    return {name: evaluate(strategy) for name, strategy in STRATEGIES.items()}


if __name__ == "__main__":
    import json

    print(json.dumps(run_all(), indent=2, sort_keys=True))
