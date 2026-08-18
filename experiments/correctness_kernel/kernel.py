from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from experiments.capability_planner.planner import Planner, Requirement
from experiments.durable_run_state.protocol import DurableEngine, EffectLedger, JsonStateStore
from experiments.escalation_policy.policy import Decision, decide
from experiments.evidence_ledger.protocol import Ledger, Observation, Verifier as LedgerVerifier
from experiments.memory_safety.memory_safety import MemoryStore
from experiments.verification_harness.protocol import Claim, Evidence, Task, Verifier as ClaimVerifier


@dataclass(frozen=True)
class Binding:
    work_id: str
    artifact_digest: str
    effect_key: str
    evidence_namespace: str


@dataclass(frozen=True)
class Completion:
    done: bool
    reason: str


class Kernel:
    """Thin composition layer over LAB-005/006/007/008/011/012 primitives."""

    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.store = JsonStateStore(self.root / "run.json")
        self.effects = EffectLedger(self.root / "effects.json")
        self.engine = DurableEngine(self.store, self.effects)
        self.ledger = Ledger(self.root / "evidence.jsonl")
        self.memory = MemoryStore(self.root / "memory.json")

    def start(self, work_id: str, artifact_digest: str):
        state = self.engine.start_or_resume(work_id, {"artifact_digest": artifact_digest})
        if state.effect_key is None:
            state = self.engine.prepare_effect(state, value=artifact_digest)
        return state

    def binding(self, state) -> Binding:
        return Binding(
            state.work_id,
            state.payload["artifact_digest"],
            state.effect_key,
            f"{state.work_id}:evidence:v1",
        )

    def perform(self, state, timeout: bool = False):
        return self.engine.execute_effect(state, timeout_after_commit=timeout)

    def reconcile_receipt(self, state):
        state = self.engine.start_or_resume(state.work_id)
        if state.phase != "EFFECT_CONFIRMED" or not state.effect_receipt:
            return state, None
        evidence_id = self.ledger.observe(
            Observation(
                "side_effect",
                state.payload["artifact_digest"],
                "external-system",
                True,
                "PASS",
                output_digest=state.effect_receipt,
            )
        )
        return state, evidence_id

    def add_test_evidence(self, artifact_digest: str, requirements=("done",)):
        evidence_id = self.ledger.observe(
            Observation("test", artifact_digest, "deterministic-test", True, "PASS")
        )
        return evidence_id, Evidence(
            evidence_id,
            "test",
            artifact_digest,
            True,
            "pass",
            tuple(requirements),
        )

    def completion(self, artifact_digest, requirements, evidence_ids, claim_evidence):
        if not LedgerVerifier(self.ledger).verify(artifact_digest, evidence_ids):
            return Completion(False, "ledger_evidence_invalid")
        claim = Claim(
            "completion",
            tuple(requirements),
            tuple(item.evidence_id for item in claim_evidence),
            True,
        )
        verdict = ClaimVerifier().verify(
            Task(artifact_digest, tuple(requirements)), claim, list(claim_evidence)
        )
        return Completion(
            verdict.accepted,
            "verified" if verdict.accepted else "|".join(verdict.errors),
        )

    def authoritative_memory(self, topic):
        return self.memory.authoritative(topic)

    def plan_route(self, routes, observations, operation="write", now=10):
        return Planner(routes, observations).plan(
            Requirement(1, operation, {"safe": True}, {"preferred": 5}), now
        )

    def safe_next_action(self, ctx, topology, plan_selected):
        policy = decide(ctx)
        if policy.decision in {Decision.BLOCK, Decision.ESCALATE, Decision.PROBE}:
            return policy.decision.value
        if plan_selected is None:
            return "BLOCK"
        return f"{policy.decision.value}:{topology}:{plan_selected}"

    def naive_done_from_narrative(self, topic):
        """Deliberately unsafe composition retained only for the seeded-failure test."""
        return any("done" in memory.value.lower() for memory in self.memory.naive(topic))
