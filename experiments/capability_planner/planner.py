from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import hashlib
import json

SCHEMA_VERSION = 1


@dataclass(frozen=True)
class CapabilityObservation:
    schema_version: int
    capability_id: str
    route: str
    operation: str
    observed_at: int
    ttl: int
    available: bool
    properties: dict[str, Any]
    evidence_ref: str

    def fresh(self, now: int) -> bool:
        return self.observed_at <= now <= self.observed_at + self.ttl


@dataclass(frozen=True)
class Requirement:
    schema_version: int
    operation: str
    hard: dict[str, Any]
    preferences: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class Route:
    name: str
    operation: str
    capability_id: str
    declared_properties: dict[str, Any]
    base_priority: int = 0


@dataclass(frozen=True)
class Plan:
    selected: str | None
    score: int | None
    evidence_refs: tuple[str, ...]
    rejected: dict[str, tuple[str, ...]]
    explanation_id: str


class Planner:
    def __init__(self, routes: list[Route], observations: list[CapabilityObservation]):
        self.routes = routes
        self.obs = {o.capability_id: o for o in observations}

    @staticmethod
    def _satisfies(actual: Any, expected: Any) -> bool:
        if isinstance(expected, (list, tuple, set)):
            return actual in expected
        return actual == expected

    def plan(self, req: Requirement, now: int) -> Plan:
        if req.schema_version != SCHEMA_VERSION:
            raise ValueError("unsupported requirement schema")

        viable: list[tuple[int, str, str]] = []
        rejected: dict[str, tuple[str, ...]] = {}

        for route in self.routes:
            reasons: list[str] = []
            if route.operation != req.operation:
                reasons.append("operation_mismatch")

            observation = self.obs.get(route.capability_id)
            if observation is None:
                reasons.append("missing_observation")
            else:
                if observation.schema_version != SCHEMA_VERSION:
                    reasons.append("observation_schema_mismatch")
                if not observation.fresh(now):
                    reasons.append("stale_observation")
                if not observation.available:
                    reasons.append("unavailable")
                if observation.operation != req.operation:
                    reasons.append("observation_operation_mismatch")

                properties = dict(route.declared_properties)
                properties.update(observation.properties)
                for key, expected in req.hard.items():
                    if not self._satisfies(properties.get(key), expected):
                        reasons.append(f"hard:{key}")

            if reasons:
                rejected[route.name] = tuple(sorted(set(reasons)))
                continue

            properties = dict(route.declared_properties)
            properties.update(observation.properties)
            score = route.base_priority
            for key, weight in req.preferences.items():
                if properties.get(key) is True:
                    score += weight
            viable.append((score, route.name, observation.evidence_ref))

        viable.sort(key=lambda item: (-item[0], item[1]))
        selected = viable[0] if viable else None
        payload = {
            "selected": selected[1] if selected else None,
            "score": selected[0] if selected else None,
            "rejected": rejected,
            "evidence_refs": [selected[2]] if selected else [],
        }
        explanation_id = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode("utf-8")
        ).hexdigest()

        return Plan(
            selected=selected[1] if selected else None,
            score=selected[0] if selected else None,
            evidence_refs=(selected[2],) if selected else (),
            rejected=rejected,
            explanation_id=explanation_id,
        )
