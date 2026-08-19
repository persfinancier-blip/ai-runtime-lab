from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
import json
import time


class Requirement(str, Enum):
    REQUIRED = "required"
    AUDIT = "audit"


class Enforcement(str, Enum):
    KERNEL = "kernel"
    PROCESS = "process"
    POLICY_ONLY = "policy_only"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class Mechanism:
    name: str
    dimension: str
    enforcement: Enforcement
    available: bool
    observed: bool
    detail: str = ""


@dataclass(frozen=True)
class CapabilityReport:
    platform: str
    kernel: str
    generation: int
    observed_at: float
    ttl_seconds: float
    mechanisms: tuple[Mechanism, ...]

    def is_fresh(self, now: float) -> bool:
        return now <= self.observed_at + self.ttl_seconds

    def digest(self) -> str:
        raw = {
            "platform": self.platform,
            "kernel": self.kernel,
            "generation": self.generation,
            "observed_at": self.observed_at,
            "ttl_seconds": self.ttl_seconds,
            "mechanisms": [m.__dict__ for m in self.mechanisms],
        }
        return sha256(json.dumps(raw, sort_keys=True, default=str).encode()).hexdigest()


@dataclass(frozen=True)
class SandboxRequest:
    task_id: str
    sandbox_generation: int
    credential_generation: int
    requirements: dict[str, Requirement]
    non_security_critical: bool = False


@dataclass(frozen=True)
class BoundDimension:
    dimension: str
    requirement: Requirement
    mechanism: str
    enforcement: Enforcement


@dataclass(frozen=True)
class SandboxPlan:
    task_id: str
    sandbox_generation: int
    credential_generation: int
    report_generation: int
    report_digest: str
    non_security_critical: bool
    bindings: tuple[BoundDimension, ...]


class SandboxUnavailable(RuntimeError):
    pass


class StaleCapabilityReport(SandboxUnavailable):
    pass


class GenerationDrift(SandboxUnavailable):
    pass


class SandboxAdapter:
    """Binds requested security dimensions only to observed enforcing mechanisms."""

    def plan(self, request: SandboxRequest, report: CapabilityReport, *, now: float | None = None) -> SandboxPlan:
        now = time.time() if now is None else now
        if not report.is_fresh(now):
            raise StaleCapabilityReport("capability report expired; re-probe before launch")

        by_dimension: dict[str, list[Mechanism]] = {}
        for mechanism in report.mechanisms:
            by_dimension.setdefault(mechanism.dimension, []).append(mechanism)

        bindings: list[BoundDimension] = []
        for dimension, requirement in sorted(request.requirements.items()):
            candidates = [
                m for m in by_dimension.get(dimension, ())
                if m.available and m.observed and m.enforcement in {Enforcement.KERNEL, Enforcement.PROCESS}
            ]
            if candidates:
                candidates.sort(key=lambda m: (0 if m.enforcement is Enforcement.KERNEL else 1, m.name))
                chosen = candidates[0]
                bindings.append(BoundDimension(dimension, requirement, chosen.name, chosen.enforcement))
                continue

            if requirement is Requirement.AUDIT and request.non_security_critical:
                bindings.append(BoundDimension(dimension, requirement, "policy-audit-only", Enforcement.POLICY_ONLY))
                continue

            raise SandboxUnavailable(f"required dimension {dimension!r} has no observed enforcement backend")

        return SandboxPlan(
            task_id=request.task_id,
            sandbox_generation=request.sandbox_generation,
            credential_generation=request.credential_generation,
            report_generation=report.generation,
            report_digest=report.digest(),
            non_security_critical=request.non_security_critical,
            bindings=tuple(bindings),
        )

    def validate_launch(
        self,
        plan: SandboxPlan,
        report: CapabilityReport,
        *,
        sandbox_generation: int,
        credential_generation: int,
        now: float | None = None,
    ) -> None:
        now = time.time() if now is None else now
        if not report.is_fresh(now):
            raise StaleCapabilityReport("capability report expired before launch")
        if plan.report_generation != report.generation or plan.report_digest != report.digest():
            raise GenerationDrift("capability report changed after plan")
        if plan.sandbox_generation != sandbox_generation:
            raise GenerationDrift("sandbox generation changed after plan")
        if plan.credential_generation != credential_generation:
            raise GenerationDrift("credential generation changed after plan")
        for binding in plan.bindings:
            if binding.enforcement is Enforcement.POLICY_ONLY:
                if binding.requirement is not Requirement.AUDIT or not plan.non_security_critical:
                    raise SandboxUnavailable("policy-only binding is not authorized for this task")
                continue
            matches = [
                m for m in report.mechanisms
                if m.dimension == binding.dimension
                and m.name == binding.mechanism
                and m.available and m.observed
                and m.enforcement == binding.enforcement
                and m.enforcement in {Enforcement.KERNEL, Enforcement.PROCESS}
            ]
            if not matches:
                raise SandboxUnavailable(f"binding {binding.dimension!r} is not backed by current observed enforcement")


class UnsafeAdapter:
    """Seeded bad design: treats declared mechanisms as enforced without observation."""

    def plan(self, request: SandboxRequest, report: CapabilityReport) -> SandboxPlan:
        bindings = []
        for dimension in sorted(request.requirements):
            mechanisms = [m for m in report.mechanisms if m.dimension == dimension]
            name = mechanisms[0].name if mechanisms else "assumed"
            bindings.append(BoundDimension(dimension, request.requirements[dimension], name, Enforcement.KERNEL))
        return SandboxPlan(
            request.task_id,
            request.sandbox_generation,
            request.credential_generation,
            report.generation,
            report.digest(),
            request.non_security_critical,
            tuple(bindings),
        )
