from __future__ import annotations

import json
import os
import tempfile
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


class ProtocolError(RuntimeError):
    pass


class UnsupportedSchemaError(ProtocolError):
    pass


class StaleStateError(ProtocolError):
    pass


class FenceError(ProtocolError):
    pass


class UnknownOutcome(ProtocolError):
    """The side effect may have committed, but the caller did not observe the result."""


@dataclass
class RunState:
    schema_version: int
    run_id: str
    work_id: str
    generation: int = 0
    fence: int = 0
    attempt: int = 0
    phase: str = "NEW"
    effect_key: str | None = None
    effect_receipt: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    evidence: list[str] = field(default_factory=list)

    @classmethod
    def new(cls, work_id: str, payload: dict[str, Any] | None = None) -> "RunState":
        return cls(
            schema_version=SCHEMA_VERSION,
            run_id=str(uuid.uuid4()),
            work_id=work_id,
            payload=dict(payload or {}),
        )

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "RunState":
        if raw.get("schema_version") != SCHEMA_VERSION:
            raise UnsupportedSchemaError(
                f"unsupported schema_version={raw.get('schema_version')}; expected={SCHEMA_VERSION}"
            )
        return cls(**raw)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class JsonStateStore:
    """Single-work-item durable store with atomic replace and CAS-style generation checks."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def exists(self) -> bool:
        return self.path.exists()

    def load(self) -> RunState:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return RunState.from_dict(raw)

    def _atomic_write(self, state: RunState) -> None:
        fd, tmp_name = tempfile.mkstemp(prefix=self.path.name + ".", dir=str(self.path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(state.to_dict(), fh, sort_keys=True, indent=2)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp_name, self.path)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)

    def create(self, state: RunState) -> RunState:
        if self.exists():
            raise StaleStateError("state already exists")
        state.generation = 1
        self._atomic_write(state)
        return state

    def save(self, state: RunState, *, expected_generation: int, expected_fence: int) -> RunState:
        current = self.load()
        if current.generation != expected_generation:
            raise StaleStateError(
                f"generation changed: expected={expected_generation} current={current.generation}"
            )
        if current.fence != expected_fence or state.fence != expected_fence:
            raise FenceError(
                f"fence changed: expected={expected_fence} current={current.fence} candidate={state.fence}"
            )
        state.generation = current.generation + 1
        self._atomic_write(state)
        return state

    def claim(self) -> RunState:
        state = self.load()
        expected_generation = state.generation
        expected_fence = state.fence
        state.fence += 1
        state.attempt += 1
        state.generation = expected_generation
        current = self.load()
        if current.generation != expected_generation or current.fence != expected_fence:
            raise StaleStateError("claim raced with another writer")
        state.generation = current.generation + 1
        self._atomic_write(state)
        return state


class EffectLedger:
    """Durable external-system simulator with idempotency and fencing."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"effects": {}, "max_fence": {}, "apply_count": 0})

    def _read(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, raw: dict[str, Any]) -> None:
        fd, tmp_name = tempfile.mkstemp(prefix=self.path.name + ".", dir=str(self.path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(raw, fh, sort_keys=True, indent=2)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp_name, self.path)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)

    def register_fence(self, work_id: str, fence: int) -> None:
        raw = self._read()
        current = int(raw["max_fence"].get(work_id, 0))
        if fence > current:
            raw["max_fence"][work_id] = fence
            self._write(raw)

    def lookup(self, effect_key: str | None) -> str | None:
        if not effect_key:
            return None
        return self._read()["effects"].get(effect_key, {}).get("receipt")

    def apply(
        self,
        *,
        work_id: str,
        effect_key: str,
        fence: int,
        value: str,
        timeout_after_commit: bool = False,
    ) -> str:
        raw = self._read()
        max_fence = int(raw["max_fence"].get(work_id, 0))
        if fence < max_fence:
            raise FenceError(f"stale worker fence={fence}; max_fence={max_fence}")
        raw["max_fence"][work_id] = max(max_fence, fence)

        existing = raw["effects"].get(effect_key)
        if existing:
            return str(existing["receipt"])

        receipt = f"receipt:{effect_key}"
        raw["effects"][effect_key] = {
            "work_id": work_id,
            "value": value,
            "fence": fence,
            "receipt": receipt,
        }
        raw["apply_count"] = int(raw["apply_count"]) + 1
        self._write(raw)
        if timeout_after_commit:
            raise UnknownOutcome("transport timed out after the side effect committed")
        return receipt

    @property
    def apply_count(self) -> int:
        return int(self._read()["apply_count"])


class DurableEngine:
    def __init__(self, store: JsonStateStore, ledger: EffectLedger):
        self.store = store
        self.ledger = ledger

    def start_or_resume(self, work_id: str, payload: dict[str, Any] | None = None) -> RunState:
        if not self.store.exists():
            state = RunState.new(work_id=work_id, payload=payload)
            self.store.create(state)
        state = self.store.claim()
        self.ledger.register_fence(state.work_id, state.fence)
        return self.reconcile(state)

    def _save(self, state: RunState, mutate) -> RunState:
        expected_generation = state.generation
        expected_fence = state.fence
        mutate(state)
        return self.store.save(
            state,
            expected_generation=expected_generation,
            expected_fence=expected_fence,
        )

    def prepare_effect(self, state: RunState, *, value: str) -> RunState:
        if state.phase == "DONE":
            return state
        if state.effect_key is None:
            state.effect_key = f"{state.work_id}:effect:v1"
        return self._save(
            state,
            lambda s: (
                s.payload.__setitem__("effect_value", value),
                setattr(s, "phase", "EFFECT_INTENT_RECORDED"),
            ),
        )

    def execute_effect(self, state: RunState, *, timeout_after_commit: bool = False) -> RunState:
        if state.phase == "DONE":
            return state
        if state.phase not in {"EFFECT_INTENT_RECORDED", "EFFECT_UNKNOWN"}:
            raise ProtocolError(f"cannot execute side effect from phase={state.phase}")
        if not state.effect_key:
            raise ProtocolError("effect intent has no idempotency key")
        value = str(state.payload.get("effect_value", ""))
        try:
            receipt = self.ledger.apply(
                work_id=state.work_id,
                effect_key=state.effect_key,
                fence=state.fence,
                value=value,
                timeout_after_commit=timeout_after_commit,
            )
        except UnknownOutcome:
            self._save(state, lambda s: setattr(s, "phase", "EFFECT_UNKNOWN"))
            raise
        return self._save(
            state,
            lambda s: (
                setattr(s, "effect_receipt", receipt),
                setattr(s, "phase", "EFFECT_CONFIRMED"),
                s.evidence.append(receipt),
            ),
        )

    def reconcile(self, state: RunState) -> RunState:
        if state.phase not in {"EFFECT_INTENT_RECORDED", "EFFECT_UNKNOWN"}:
            return state
        receipt = self.ledger.lookup(state.effect_key)
        if receipt is None:
            return state
        return self._save(
            state,
            lambda s: (
                setattr(s, "effect_receipt", receipt),
                setattr(s, "phase", "EFFECT_CONFIRMED"),
                s.evidence.append(receipt) if receipt not in s.evidence else None,
            ),
        )

    def complete(self, state: RunState) -> RunState:
        if state.phase == "DONE":
            return state
        if state.phase != "EFFECT_CONFIRMED":
            raise ProtocolError(f"cannot complete from phase={state.phase}")
        return self._save(state, lambda s: setattr(s, "phase", "DONE"))


class UnsafeCounter:
    """Deliberately unsafe baseline: no idempotency, no reconciliation."""

    def __init__(self):
        self.count = 0

    def apply_then_timeout(self) -> None:
        self.count += 1
        raise UnknownOutcome("caller cannot tell whether increment committed")

    def apply(self) -> None:
        self.count += 1
