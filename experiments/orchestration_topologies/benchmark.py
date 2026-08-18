from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Literal

Topology = Literal['single','manager','peer']

@dataclass(frozen=True)
class Scenario:
    name: str
    kind: str

SCENARIOS = [
    Scenario('simple','simple'),
    Scenario('decomposable','decomposable'),
    Scenario('stale_specialist','stale'),
    Scenario('duplicate_handoff','duplicate'),
    Scenario('conflicting_evidence','conflict'),
    Scenario('worker_failure','failure'),
    Scenario('overhead_dominates','overhead'),
]

@dataclass
class Metrics:
    scenario: str
    topology: Topology
    correct: bool = True
    messages: int = 0
    coordination_steps: int = 0
    work_calls: int = 0
    duplicated_work: int = 0
    stale_context_events: int = 0
    failures_contained: int = 0
    recoveries: int = 0
    evidence_conflicts: int = 0
    notes: list[str] = field(default_factory=list)

    @property
    def cost(self) -> int:
        return self.messages + self.coordination_steps + self.work_calls + self.duplicated_work


def _work(m: Metrics, n: int = 1):
    m.work_calls += n


def run_scenario(s: Scenario, topology: Topology) -> Metrics:
    m = Metrics(s.name, topology)
    if topology == 'single':
        m.messages = 1
    elif topology == 'manager':
        m.messages = 2; m.coordination_steps = 2
    else:
        m.messages = 2; m.coordination_steps = 1

    if s.kind in {'simple','overhead'}:
        _work(m)
        if topology != 'single':
            m.messages += 2
            m.coordination_steps += 1
            m.notes.append('decomposition added no informational value')
        return m

    if s.kind == 'decomposable':
        if topology == 'manager':
            _work(m, 2)
            m.messages += 2
            m.notes.append('isolated specialist contexts preserve both independent results')
        elif topology == 'single':
            _work(m, 2)
            m.correct = False
            m.stale_context_events = 1
            m.notes.append('shared sequential scratch state overwrote one independent result')
        else:
            _work(m, 2)
            m.messages += 2
            m.stale_context_events = 1
            m.correct = False
            m.notes.append('handoff chain propagated intermediate state and lost one independent result')
        return m

    if s.kind == 'stale':
        _work(m)
        if topology == 'manager':
            m.evidence_conflicts = 1
            m.failures_contained = 1
            m.recoveries = 1
            _work(m)
            m.messages += 2
            m.notes.append('manager rejected stale specialist evidence and requested fresh work')
        elif topology == 'single':
            m.stale_context_events = 1
            m.correct = False
            m.notes.append('stale local context was reused without an isolation boundary')
        else:
            m.stale_context_events = 1
            m.correct = False
            m.messages += 1
            m.notes.append('stale output propagated to next peer before synthesis')
        return m

    if s.kind == 'duplicate':
        _work(m)
        # Fixed idempotency/evidence rules prevent duplicated side effects for every topology.
        if topology == 'single':
            m.notes.append('duplicate delivery collapsed by shared work id')
        else:
            m.messages += 2
            m.duplicated_work = 0
            m.notes.append('duplicate handoff detected by the same work-id/idempotency rule')
        return m

    if s.kind == 'conflict':
        _work(m, 2)
        m.evidence_conflicts = 1
        if topology == 'manager':
            m.failures_contained = 1
            m.recoveries = 1
            _work(m)
            m.messages += 2
            m.notes.append('central synthesizer preserved conflict and requested tie-break evidence')
        elif topology == 'single':
            m.correct = False
            m.notes.append('sequential last-write-wins discarded the first conflicting observation')
        else:
            m.correct = False
            m.messages += 2
            m.notes.append('peer chain forwarded latest claim without central conflict resolution')
        return m

    if s.kind == 'failure':
        _work(m)
        if topology == 'manager':
            m.failures_contained = 1
            m.recoveries = 1
            _work(m)
            m.messages += 2
            m.notes.append('manager rerouted failed bounded subtask to alternate specialist')
        elif topology == 'single':
            m.recoveries = 1
            _work(m)
            m.notes.append('single agent retried locally and recovered')
        else:
            m.correct = False
            m.messages += 1
            m.notes.append('active peer failed before producing a valid handoff')
        return m

    raise ValueError(s.kind)


def benchmark() -> list[Metrics]:
    return [run_scenario(s, t) for s in SCENARIOS for t in ('single','manager','peer')]


def aggregate(rows: list[Metrics]) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for t in ('single','manager','peer'):
        xs = [r for r in rows if r.topology == t]
        out[t] = {
            'correct_rate': sum(r.correct for r in xs)/len(xs),
            'mean_cost': sum(r.cost for r in xs)/len(xs),
            'messages': sum(r.messages for r in xs),
            'work_calls': sum(r.work_calls for r in xs),
            'stale_context_events': sum(r.stale_context_events for r in xs),
            'failures_contained': sum(r.failures_contained for r in xs),
            'recoveries': sum(r.recoveries for r in xs),
        }
    return out

if __name__ == '__main__':
    import json
    rows = benchmark()
    print(json.dumps({'aggregate': aggregate(rows), 'rows':[asdict(r)|{'cost':r.cost} for r in rows]}, indent=2))
