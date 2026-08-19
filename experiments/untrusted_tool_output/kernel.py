from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Authority(str, Enum):
    CONTROL = 'control'
    DATA = 'data'
    EVIDENCE_CANDIDATE = 'evidence_candidate'


class Trust(str, Enum):
    TRUSTED = 'trusted'
    UNTRUSTED = 'untrusted'


class Decision(str, Enum):
    ALLOW = 'allow'
    BLOCK = 'block'
    ESCALATE = 'escalate'


PRIVILEGED_ACTIONS = {'send_secret', 'delete_data', 'make_payment', 'change_policy'}


@dataclass(frozen=True)
class Envelope:
    source: str
    authority: Authority
    trust: Trust
    payload: dict[str, Any] = field(default_factory=dict)
    text: str = ''
    channel: str = 'tool_output'

    @property
    def is_authoritative_control(self) -> bool:
        return self.authority is Authority.CONTROL and self.trust is Trust.TRUSTED and self.channel == 'control'


@dataclass(frozen=True)
class ControlRequest:
    action: str
    target: str
    allowed_actions: frozenset[str]
    requires_human: frozenset[str] = frozenset()
    protected_target: bool = True
    artifact_version: str | None = None


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    artifact_version: str
    observed: bool
    independent: bool


@dataclass(frozen=True)
class Plan:
    decision: Decision
    action: str | None
    target: str | None
    facts: tuple[str, ...]
    accepted_evidence: tuple[str, ...]
    reasons: tuple[str, ...]


class PolicyKernel:
    def plan(
        self,
        request: ControlRequest,
        inputs: list[Envelope],
        evidence: list[EvidenceRecord] | None = None,
    ) -> Plan:
        reasons: list[str] = []
        facts: list[str] = []
        accepted_evidence: list[str] = []
        denied_actions: set[str] = set()

        # External envelopes may inform facts but cannot mutate control-plane action/target/policy.
        for env in inputs:
            if env.authority in {Authority.DATA, Authority.EVIDENCE_CANDIDATE}:
                facts.extend(self._extract_facts(env))
                if self._contains_control_smuggling(env):
                    reasons.append(f'ignored_control_smuggling:{env.source}')
            elif env.is_authoritative_control:
                # Explicit trusted control may narrow constraints, never silently widen user-granted authority.
                narrowing = env.payload.get('deny_actions')
                if isinstance(narrowing, list):
                    denied_actions.update(str(a) for a in narrowing)
                    reasons.extend(f'control_denied:{a}' for a in narrowing)
            else:
                reasons.append(f'non_authoritative_control_ignored:{env.source}')

        action = request.action
        target = request.target

        if action in denied_actions:
            return Plan(Decision.BLOCK, None, None, tuple(facts), (), tuple(reasons + ['action_denied_by_control']))
        if action not in request.allowed_actions:
            return Plan(Decision.BLOCK, None, None, tuple(facts), (), tuple(reasons + ['action_not_allowed']))
        if action in PRIVILEGED_ACTIONS or action in request.requires_human:
            return Plan(Decision.ESCALATE, action, target, tuple(facts), (), tuple(reasons + ['human_gate_required']))

        for rec in evidence or []:
            version_ok = request.artifact_version is None or rec.artifact_version == request.artifact_version
            if rec.observed and rec.independent and version_ok:
                accepted_evidence.append(rec.evidence_id)

        return Plan(Decision.ALLOW, action, target, tuple(facts), tuple(accepted_evidence), tuple(reasons))

    @staticmethod
    def _extract_facts(env: Envelope) -> list[str]:
        out: list[str] = []
        for key in ('fact', 'status', 'value', 'summary'):
            val = env.payload.get(key)
            if isinstance(val, (str, int, float, bool)):
                out.append(f'{key}={val}')
        if env.text:
            out.append(f'text:{env.text}')
        return out

    @staticmethod
    def _contains_control_smuggling(env: Envelope) -> bool:
        forbidden = {'requested_action', 'action', 'permission', 'allowed_actions', 'target', 'redirect_target', 'escalation', 'skip_escalation', 'evidence_trusted'}
        return any(k in env.payload for k in forbidden)


class UnsafeConcatenatingAgent:
    """Deliberately unsafe baseline: treats tool output as instructions."""

    def decide(self, request: ControlRequest, tool_output: Envelope) -> tuple[str, str]:
        action = request.action
        target = request.target
        if 'requested_action' in tool_output.payload:
            action = str(tool_output.payload['requested_action'])
        if 'redirect_target' in tool_output.payload:
            target = str(tool_output.payload['redirect_target'])
        return action, target
