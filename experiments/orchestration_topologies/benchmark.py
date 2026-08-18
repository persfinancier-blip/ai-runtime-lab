from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field, asdict
from typing import Literal

Topology = Literal["single", "manager", "peer"]

@dataclass(frozen=True)
class Evidence:
    eid: str
    key: str
    value: str
    version: int
    current_version: int
    valid: bool = True
    authoritative: bool = False

    @property
    def stale(self) -> bool:
        return self.version != self.current_version

@dataclass(frozen=True)
class Event:
    work_id: str
    evidence: Evidence | None = None
    fail_once: bool = False

@dataclass(frozen=True)
class Scenario:
    name: str
    expected: dict[str, str]
    events: tuple[Event, ...]
    context_budget: int = 4

def ev(eid, key, value, version=1, current=1, authoritative=False, work_id=None):
    return Event(work_id or eid, Evidence(eid, key, value, version, current, True, authoritative))

SCENARIOS = (
    Scenario("simple", {"a": "A"}, (ev("e1", "a", "A"),), 4),
    Scenario(
        "decomposable_context_pressure",
        {"a": "A", "b": "B", "c": "C"},
        (ev("e1", "a", "A"), ev("e2", "b", "B"), ev("e3", "c", "C")),
        2,
    ),
    Scenario(
        "stale_specialist",
        {"a": "A2"},
        (ev("e1", "a", "A1", 1, 2), ev("e2", "a", "A2", 2, 2)),
        4,
    ),
    Scenario(
        "duplicate_handoff",
        {"a": "A"},
        (ev("e1", "a", "A", work_id="w1"), ev("e1-dup", "a", "A", work_id="w1")),
        4,
    ),
    Scenario(
        "conflicting_evidence",
        {"a": "GOOD"},
        (
            ev("e1", "a", "BAD"),
            ev("e2", "a", "GOOD"),
            ev("e3", "a", "GOOD", authoritative=True),
        ),
        4,
    ),
    Scenario(
        "worker_failure",
        {"a": "A"},
        (Event("w1", ev("tmp", "a", "A").evidence, fail_once=True),),
        4,
    ),
    Scenario("overhead_dominates", {"a": "A"}, (ev("e1", "a", "A"),), 4),
)

@dataclass
class Metrics:
    scenario: str
    topology: Topology
    correct: bool = False
    messages: int = 0
    coordination_steps: int = 0
    work_calls: int = 0
    duplicate_deliveries: int = 0
    stale_context_events: int = 0
    failures_contained: int = 0
    recoveries: int = 0
    surfaced_evidence: int = 0
    notes: list[str] = field(default_factory=list)

    @property
    def cost(self) -> int:
        return self.messages + self.coordination_steps + self.work_calls

def _verify(expected: dict[str, str], evidence: list[Evidence]) -> bool:
    by_key: dict[str, list[Evidence]] = {}
    for item in evidence:
        if not item.valid or item.stale:
            continue
        by_key.setdefault(item.key, []).append(item)

    for key, wanted in expected.items():
        candidates = by_key.get(key, [])
        if not candidates:
            return False
        authoritative = [item for item in candidates if item.authoritative]
        chosen = authoritative[-1] if authoritative else candidates[-1]
        if chosen.value != wanted:
            return False
        values = {item.value for item in candidates}
        if len(values) > 1 and not authoritative:
            return False
    return True

def _execute_event(event: Event, seen_work: set[str], metrics: Metrics) -> Evidence | None:
    if event.work_id in seen_work:
        metrics.duplicate_deliveries += 1
        return None
    seen_work.add(event.work_id)
    metrics.work_calls += 1
    if event.fail_once:
        metrics.recoveries += 1
        metrics.failures_contained += 1
        metrics.work_calls += 1
    return event.evidence

def run_scenario(scenario: Scenario, topology: Topology) -> Metrics:
    metrics = Metrics(scenario.name, topology)
    seen_work: set[str] = set()

    if topology == "single":
        context: deque[Evidence] = deque(maxlen=scenario.context_budget)
        for event in scenario.events:
            item = _execute_event(event, seen_work, metrics)
            if item is not None:
                if item.stale:
                    metrics.stale_context_events += 1
                context.append(item)
        surfaced = list(context)
        metrics.coordination_steps = 1

    elif topology == "manager":
        isolated: dict[str, Evidence] = {}
        for event in scenario.events:
            metrics.messages += 2
            metrics.coordination_steps += 1
            item = _execute_event(event, seen_work, metrics)
            if item is None:
                continue
            if item.stale:
                metrics.failures_contained += 1
                continue
            isolated[item.eid] = item
        surfaced = list(isolated.values())
        metrics.coordination_steps += 1

    elif topology == "peer":
        context = deque(maxlen=scenario.context_budget)
        metrics.messages += 1
        metrics.coordination_steps += 1
        for index, event in enumerate(scenario.events):
            if index:
                metrics.messages += 1
                metrics.coordination_steps += 1
            item = _execute_event(event, seen_work, metrics)
            if item is not None:
                if item.stale:
                    metrics.stale_context_events += 1
                context.append(item)
        surfaced = list(context)
        metrics.coordination_steps += 1

    else:
        raise ValueError(topology)

    metrics.surfaced_evidence = len(surfaced)
    metrics.correct = _verify(scenario.expected, surfaced)
    if topology != "single" and len(scenario.events) == 1:
        metrics.notes.append("agent boundary added coordination without additional information")
    return metrics

def benchmark() -> list[Metrics]:
    return [run_scenario(scenario, topology) for scenario in SCENARIOS for topology in ("single", "manager", "peer")]

def aggregate(rows: list[Metrics]) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {}
    for topology in ("single", "manager", "peer"):
        selected = [row for row in rows if row.topology == topology]
        output[topology] = {
            "correct_rate": sum(row.correct for row in selected) / len(selected),
            "mean_cost": sum(row.cost for row in selected) / len(selected),
            "messages": sum(row.messages for row in selected),
            "work_calls": sum(row.work_calls for row in selected),
            "duplicate_deliveries": sum(row.duplicate_deliveries for row in selected),
            "stale_context_events": sum(row.stale_context_events for row in selected),
            "failures_contained": sum(row.failures_contained for row in selected),
            "recoveries": sum(row.recoveries for row in selected),
        }
    return output

if __name__ == "__main__":
    import json

    rows = benchmark()
    print(json.dumps({"aggregate": aggregate(rows), "rows": [asdict(row) | {"cost": row.cost} for row in rows]}, indent=2))
