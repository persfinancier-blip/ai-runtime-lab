from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class Phase(str, Enum):
    NEW = "NEW"
    REPRODUCED = "REPRODUCED"
    PATCHED = "PATCHED"
    VALIDATED = "VALIDATED"
    AUDITED = "AUDITED"
    COMPLETE = "COMPLETE"
    HOLD = "HOLD"
    BLOCKED = "BLOCKED"


class Failure(str, Enum):
    UNREPRODUCED = "unreproduced_bug"
    VALIDATION_FAILED = "validation_failed"
    PARTIAL_FIX = "partial_fix"
    STALE_EVIDENCE = "stale_evidence"
    AUDIT_REGRESSION = "audit_regression"
    NO_SAFE_ROUTE = "no_safe_validation_route"
    MISSING_EVIDENCE = "missing_evidence"


@dataclass(frozen=True)
class Route:
    name: str
    available: bool
    safe: bool
    preference: int


@dataclass(frozen=True)
class Evidence:
    kind: str
    artifact_version: int
    success: bool
    detail: str
    route: str | None = None


@dataclass
class Task:
    task_id: str
    requirements: tuple[str, ...]
    artifact_version: int = 1
    phase: Phase = Phase.NEW
    reproduction_observed: bool = False
    satisfied: set[str] = field(default_factory=set)
    evidence: list[Evidence] = field(default_factory=list)
    failures: list[Failure] = field(default_factory=list)
    failure_history: list[Failure] = field(default_factory=list)
    selected_route: str | None = None

    def add_failure(self, failure: Failure, terminal: Phase = Phase.HOLD) -> None:
        if failure not in self.failures:
            self.failures.append(failure)
        self.failure_history.append(failure)
        self.phase = terminal

    def resolve(self, *failures: Failure) -> None:
        resolved = set(failures)
        self.failures = [f for f in self.failures if f not in resolved]


class EngineeringLoop:
    """Thin lifecycle coordinator; evidence/run-state/capability semantics are explicit boundaries."""

    def reproduce(self, task: Task, *, observed: bool) -> Task:
        task.reproduction_observed = observed
        task.evidence.append(Evidence("reproduction", task.artifact_version, observed, "bug reproduction"))
        if not observed:
            task.add_failure(Failure.UNREPRODUCED)
            return task
        task.phase = Phase.REPRODUCED
        return task

    def patch(self, task: Task, *, satisfies: Iterable[str]) -> Task:
        if task.phase not in {Phase.REPRODUCED, Phase.PATCHED}:
            task.add_failure(Failure.UNREPRODUCED)
            return task
        task.artifact_version += 1
        task.satisfied = set(satisfies)
        task.resolve(Failure.AUDIT_REGRESSION, Failure.VALIDATION_FAILED, Failure.PARTIAL_FIX, Failure.STALE_EVIDENCE, Failure.MISSING_EVIDENCE)
        task.phase = Phase.PATCHED
        return task

    @staticmethod
    def choose_route(routes: Iterable[Route]) -> Route | None:
        eligible = [r for r in routes if r.available and r.safe]
        if not eligible:
            return None
        return sorted(eligible, key=lambda r: (-r.preference, r.name))[0]

    def validate(self, task: Task, *, routes: Iterable[Route], passed: bool, evidence_version: int | None = None) -> Task:
        if task.phase != Phase.PATCHED:
            task.add_failure(Failure.MISSING_EVIDENCE)
            return task
        route = self.choose_route(routes)
        if route is None:
            task.add_failure(Failure.NO_SAFE_ROUTE, terminal=Phase.BLOCKED)
            return task
        task.selected_route = route.name
        version = task.artifact_version if evidence_version is None else evidence_version
        task.evidence.append(Evidence("validation", version, passed, "test suite", route.name))
        if version != task.artifact_version:
            task.add_failure(Failure.STALE_EVIDENCE)
            return task
        if not passed:
            task.add_failure(Failure.VALIDATION_FAILED)
            return task
        missing = set(task.requirements) - task.satisfied
        if missing:
            task.add_failure(Failure.PARTIAL_FIX)
            return task
        task.phase = Phase.VALIDATED
        return task

    def audit(self, task: Task, *, regression_found: bool) -> Task:
        if task.phase != Phase.VALIDATED:
            task.add_failure(Failure.MISSING_EVIDENCE)
            return task
        task.evidence.append(Evidence("audit", task.artifact_version, not regression_found, "regression audit"))
        if regression_found:
            task.add_failure(Failure.AUDIT_REGRESSION)
            task.phase = Phase.PATCHED
            return task
        task.phase = Phase.AUDITED
        return task

    def decide(self, task: Task) -> bool:
        current_validation = any(
            e.kind == "validation" and e.success and e.artifact_version == task.artifact_version
            for e in task.evidence
        )
        current_audit = any(
            e.kind == "audit" and e.success and e.artifact_version == task.artifact_version
            for e in task.evidence
        )
        all_requirements = set(task.requirements).issubset(task.satisfied)
        accepted = (
            task.phase == Phase.AUDITED
            and task.reproduction_observed
            and current_validation
            and current_audit
            and all_requirements
            and not task.failures
        )
        if accepted:
            task.phase = Phase.COMPLETE
        return accepted


def failure_taxonomy(tasks: Iterable[Task]) -> dict[str, int]:
    counts = {f.value: 0 for f in Failure}
    for task in tasks:
        source = task.failure_history or task.failures
        for failure in set(source):
            counts[failure.value] += 1
    return {k: v for k, v in counts.items() if v}
