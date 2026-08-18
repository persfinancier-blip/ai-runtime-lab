from __future__ import annotations

from dataclasses import dataclass

SCHEMA_VERSION = 1


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    kind: str
    artifact_digest: str
    observed: bool
    outcome: str
    requirements: tuple[str, ...] = ()


@dataclass(frozen=True)
class Claim:
    claim_id: str
    requirement_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    complete: bool = True


@dataclass(frozen=True)
class Task:
    artifact_digest: str
    requirements: tuple[str, ...]
    schema_version: int = SCHEMA_VERSION


@dataclass(frozen=True)
class Verdict:
    accepted: bool
    errors: tuple[str, ...]


class Verifier:
    """Deterministic completion verifier. Agent prose is never authoritative evidence."""

    def verify(self, task: Task, claim: Claim, evidence: list[Evidence]) -> Verdict:
        errors: list[str] = []
        if task.schema_version != SCHEMA_VERSION:
            errors.append("unsupported_schema")
        if not claim.complete:
            errors.append("claim_not_complete")
        if set(claim.requirement_ids) != set(task.requirements):
            errors.append("requirements_not_fully_claimed")

        by_id = {item.evidence_id: item for item in evidence}
        linked: list[Evidence] = []
        for evidence_id in claim.evidence_ids:
            item = by_id.get(evidence_id)
            if item is None:
                errors.append(f"missing_evidence:{evidence_id}")
                continue
            linked.append(item)
            if not item.observed:
                errors.append(f"unobserved:{evidence_id}")
            if item.artifact_digest != task.artifact_digest:
                errors.append(f"stale_evidence:{evidence_id}")
            if item.kind == "test" and item.outcome != "pass":
                errors.append(f"test_not_passing:{evidence_id}")

        for requirement in task.requirements:
            proven = any(
                item.observed
                and item.artifact_digest == task.artifact_digest
                and item.outcome == "pass"
                and requirement in item.requirements
                for item in linked
            )
            if not proven:
                errors.append(f"requirement_unproven:{requirement}")

        passing_test = any(
            item.kind == "test"
            and item.observed
            and item.artifact_digest == task.artifact_digest
            and item.outcome == "pass"
            for item in linked
        )
        if not passing_test:
            errors.append("no_observed_passing_test")

        return Verdict(accepted=not errors, errors=tuple(errors))
