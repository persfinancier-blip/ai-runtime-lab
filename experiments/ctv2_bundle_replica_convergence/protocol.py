from __future__ import annotations

import hashlib
import hmac
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


class ReplicaError(RuntimeError):
    pass


class AuthenticationError(ReplicaError):
    pass


class ContinuityError(ReplicaError):
    pass


class RollbackError(ReplicaError):
    pass


class SplitViewDetected(ReplicaError):
    pass


class DuplicateReplicaIdentity(ReplicaError):
    pass


class UnknownReplica(ReplicaError):
    pass


def canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def digest(obj: object) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def key_id(key: bytes) -> str:
    return hashlib.sha256(key).hexdigest()[:16]


def sign(key: bytes, obj: object) -> str:
    return hmac.new(key, canonical(obj), hashlib.sha256).hexdigest()


@dataclass(frozen=True)
class RootEvent:
    provider_id: str
    version: int
    epoch: int
    predecessor_root: str | None
    root_material_digest: str
    signer_id: str
    bundle_signer_id: str
    signature: str

    @property
    def unsigned(self) -> dict:
        return {
            "kind": "root",
            "provider_id": self.provider_id,
            "version": self.version,
            "epoch": self.epoch,
            "predecessor_root": self.predecessor_root,
            "root_material_digest": self.root_material_digest,
            "signer_id": self.signer_id,
            "bundle_signer_id": self.bundle_signer_id,
        }

    @property
    def event_id(self) -> str:
        return digest({**self.unsigned, "signature": self.signature})

    @classmethod
    def issue(
        cls,
        *,
        provider_id: str,
        version: int,
        epoch: int,
        predecessor_root: str | None,
        root_material_digest: str,
        root_key: bytes,
        bundle_key: bytes,
    ) -> "RootEvent":
        unsigned = {
            "kind": "root",
            "provider_id": provider_id,
            "version": version,
            "epoch": epoch,
            "predecessor_root": predecessor_root,
            "root_material_digest": root_material_digest,
            "signer_id": key_id(root_key),
            "bundle_signer_id": key_id(bundle_key),
        }
        return cls(**{k: v for k, v in unsigned.items() if k != "kind"}, signature=sign(root_key, unsigned))


@dataclass(frozen=True)
class BundleEvent:
    bundle_id: str
    version: int
    generation: int
    root_event_id: str
    predecessor_bundle: str | None
    payload_digest: str
    signer_id: str
    signature: str

    @property
    def unsigned(self) -> dict:
        return {
            "kind": "bundle",
            "bundle_id": self.bundle_id,
            "version": self.version,
            "generation": self.generation,
            "root_event_id": self.root_event_id,
            "predecessor_bundle": self.predecessor_bundle,
            "payload_digest": self.payload_digest,
            "signer_id": self.signer_id,
        }

    @property
    def event_id(self) -> str:
        return digest({**self.unsigned, "signature": self.signature})

    @classmethod
    def issue(
        cls,
        *,
        bundle_id: str,
        version: int,
        generation: int,
        root_event_id: str,
        predecessor_bundle: str | None,
        payload_digest: str,
        bundle_key: bytes,
    ) -> "BundleEvent":
        unsigned = {
            "kind": "bundle",
            "bundle_id": bundle_id,
            "version": version,
            "generation": generation,
            "root_event_id": root_event_id,
            "predecessor_bundle": predecessor_bundle,
            "payload_digest": payload_digest,
            "signer_id": key_id(bundle_key),
        }
        return cls(**{k: v for k, v in unsigned.items() if k != "kind"}, signature=sign(bundle_key, unsigned))


Event = RootEvent | BundleEvent


@dataclass(frozen=True)
class ReplicaHead:
    provider_id: str
    root_event_id: str
    root_version: int
    root_epoch: int
    bundle_event_id: str | None
    bundle_version: int
    bundle_generation: int
    history_length: int
    history_digest: str

    @property
    def head_id(self) -> str:
        return digest(asdict(self))


class AuthenticatedHistory:
    """Linear authenticated root+bundle history; not a consensus protocol."""

    def __init__(
        self,
        *,
        root_keys: Mapping[str, bytes],
        bundle_keys: Mapping[str, bytes],
        events: Sequence[Event] = (),
    ):
        self.root_keys = dict(root_keys)
        self.bundle_keys = dict(bundle_keys)
        self.events = list(events)

    def copy(self) -> "AuthenticatedHistory":
        return AuthenticatedHistory(root_keys=self.root_keys, bundle_keys=self.bundle_keys, events=self.events)

    def event_ids(self) -> tuple[str, ...]:
        return tuple(event.event_id for event in self.events)

    def history_digest(self) -> str:
        return digest({"event_ids": self.event_ids()})

    def _verify_root_signature(self, event: RootEvent) -> None:
        key = self.root_keys.get(event.signer_id)
        if key is None or not hmac.compare_digest(sign(key, event.unsigned), event.signature):
            raise AuthenticationError("root signature")

    def _verify_bundle_signature(self, event: BundleEvent, current_root: RootEvent) -> None:
        if event.root_event_id != current_root.event_id:
            raise ContinuityError("bundle bound to non-current root")
        if event.signer_id != current_root.bundle_signer_id:
            raise AuthenticationError("bundle signer not authorized by current root")
        key = self.bundle_keys.get(event.signer_id)
        if key is None or not hmac.compare_digest(sign(key, event.unsigned), event.signature):
            raise AuthenticationError("bundle signature")

    def validate(self) -> ReplicaHead:
        if not self.events:
            raise ContinuityError("empty history")

        current_root: RootEvent | None = None
        current_bundle: BundleEvent | None = None
        provider_id: str | None = None

        for idx, event in enumerate(self.events):
            if isinstance(event, RootEvent):
                self._verify_root_signature(event)
                if current_root is None:
                    if idx != 0 or event.version != 1 or event.predecessor_root is not None:
                        raise ContinuityError("invalid bootstrap root")
                    provider_id = event.provider_id
                else:
                    if event.provider_id != provider_id:
                        raise ContinuityError("provider substitution")
                    if event.signer_id != current_root.signer_id:
                        raise AuthenticationError("root successor not authorized by predecessor authority")
                    if event.predecessor_root != current_root.event_id:
                        raise ContinuityError("root predecessor")
                    if event.version != current_root.version + 1:
                        raise ContinuityError("root version gap")
                    if event.epoch not in {current_root.epoch, current_root.epoch + 1}:
                        raise ContinuityError("root epoch jump")
                current_root = event
            else:
                if current_root is None:
                    raise ContinuityError("bundle before root")
                self._verify_bundle_signature(event, current_root)
                if current_bundle is None:
                    if event.version != 1 or event.generation != 1 or event.predecessor_bundle is not None:
                        raise ContinuityError("invalid bootstrap bundle")
                else:
                    if event.bundle_id != current_bundle.bundle_id:
                        raise ContinuityError("bundle lineage substitution")
                    if event.predecessor_bundle != current_bundle.event_id:
                        raise ContinuityError("bundle predecessor")
                    if event.version != current_bundle.version + 1 or event.generation != current_bundle.generation + 1:
                        raise ContinuityError("bundle version/generation gap")
                current_bundle = event

        if current_root is None or provider_id is None:
            raise ContinuityError("missing root")
        return ReplicaHead(
            provider_id=provider_id,
            root_event_id=current_root.event_id,
            root_version=current_root.version,
            root_epoch=current_root.epoch,
            bundle_event_id=None if current_bundle is None else current_bundle.event_id,
            bundle_version=0 if current_bundle is None else current_bundle.version,
            bundle_generation=0 if current_bundle is None else current_bundle.generation,
            history_length=len(self.events),
            history_digest=self.history_digest(),
        )

    def append(self, event: Event) -> ReplicaHead:
        candidate = self.copy()
        candidate.events.append(event)
        head = candidate.validate()
        self.events.append(event)
        return head

    def prefix_relation(self, other: "AuthenticatedHistory") -> str:
        self.validate()
        other.validate()
        a = self.event_ids()
        b = other.event_ids()
        common = min(len(a), len(b))
        if a[:common] != b[:common]:
            return "DIVERGENT"
        if len(a) == len(b):
            return "SAME"
        return "SELF_PREFIX" if len(a) < len(b) else "OTHER_PREFIX"

    def divergence(self, other: "AuthenticatedHistory") -> dict | None:
        self.validate()
        other.validate()
        a = self.event_ids()
        b = other.event_ids()
        common = 0
        for left, right in zip(a, b):
            if left != right:
                break
            common += 1
        if common == min(len(a), len(b)):
            return None
        left = self.events[common]
        right = other.events[common]
        return {
            "common_prefix": common,
            "left_event": left.event_id,
            "right_event": right.event_id,
            "left_kind": "root" if isinstance(left, RootEvent) else "bundle",
            "right_kind": "root" if isinstance(right, RootEvent) else "bundle",
            "same_predecessor": (
                left.predecessor_root == right.predecessor_root
                if isinstance(left, RootEvent) and isinstance(right, RootEvent)
                else left.predecessor_bundle == right.predecessor_bundle
                if isinstance(left, BundleEvent) and isinstance(right, BundleEvent)
                else False
            ),
        }


class ReplicaStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, replica_id: str, history: AuthenticatedHistory) -> None:
        head = history.validate()
        raw = {
            "replica_id": replica_id,
            "watermark": {
                "history_length": head.history_length,
                "history_digest": head.history_digest,
                "head_id": head.head_id,
            },
            "events": [serialize_event(event) for event in history.events],
        }
        fd, temp_path = tempfile.mkstemp(prefix=self.path.name + ".", dir=str(self.path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(raw, handle, sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, self.path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def load(self, root_keys: Mapping[str, bytes], bundle_keys: Mapping[str, bytes]) -> tuple[str, AuthenticatedHistory, dict]:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        history = AuthenticatedHistory(
            root_keys=root_keys,
            bundle_keys=bundle_keys,
            events=[deserialize_event(item) for item in raw["events"]],
        )
        head = history.validate()
        watermark = raw["watermark"]
        if (
            watermark["history_length"] != head.history_length
            or watermark["history_digest"] != head.history_digest
            or watermark["head_id"] != head.head_id
        ):
            raise RollbackError("persisted watermark/head mismatch")
        return raw["replica_id"], history, watermark


def serialize_event(event: Event) -> dict:
    return {"kind": "root" if isinstance(event, RootEvent) else "bundle", **asdict(event)}


def deserialize_event(raw: dict) -> Event:
    item = dict(raw)
    kind = item.pop("kind")
    if kind == "root":
        return RootEvent(**item)
    if kind == "bundle":
        return BundleEvent(**item)
    raise ContinuityError("unknown event kind")


class Replica:
    def __init__(self, *, replica_id: str, history: AuthenticatedHistory, store: ReplicaStore | None = None):
        self.replica_id = replica_id
        self.history = history
        self.store = store
        self.history.validate()
        if store is not None:
            store.save(replica_id, history)

    @classmethod
    def restart(
        cls,
        *,
        store: ReplicaStore,
        root_keys: Mapping[str, bytes],
        bundle_keys: Mapping[str, bytes],
    ) -> "Replica":
        replica_id, history, _ = store.load(root_keys, bundle_keys)
        obj = cls.__new__(cls)
        obj.replica_id = replica_id
        obj.history = history
        obj.store = store
        return obj

    @property
    def head(self) -> ReplicaHead:
        return self.history.validate()

    def _persist(self) -> None:
        if self.store is not None:
            self.store.save(self.replica_id, self.history)

    def receive(self, incoming: AuthenticatedHistory) -> str:
        relation = self.history.prefix_relation(incoming)
        if relation == "SAME":
            return "SAME"
        if relation == "SELF_PREFIX":
            self.history = incoming.copy()
            self._persist()
            return "CAUGHT_UP"
        if relation == "OTHER_PREFIX":
            raise RollbackError("incoming authenticated history is stale")
        details = self.history.divergence(incoming)
        raise SplitViewDetected(json.dumps(details, sort_keys=True))

    def exchange(self, other: "Replica") -> str:
        if other.replica_id == self.replica_id and other.head.head_id != self.head.head_id:
            raise DuplicateReplicaIdentity("same replica identity presents conflicting views")
        relation = self.history.prefix_relation(other.history)
        if relation == "DIVERGENT":
            details = self.history.divergence(other.history)
            raise SplitViewDetected(json.dumps({
                "left_replica": self.replica_id,
                "right_replica": other.replica_id,
                **(details or {}),
            }, sort_keys=True))
        if relation == "SELF_PREFIX":
            self.history = other.history.copy()
            self._persist()
            return "CAUGHT_UP_SELF"
        if relation == "OTHER_PREFIX":
            other.history = self.history.copy()
            other._persist()
            return "CAUGHT_UP_OTHER"
        return "SAME"


@dataclass(frozen=True)
class ReplicaView:
    replica_id: str
    head_id: str
    history_digest: str
    history_length: int
    signature: str

    @property
    def unsigned(self) -> dict:
        return {
            "replica_id": self.replica_id,
            "head_id": self.head_id,
            "history_digest": self.history_digest,
            "history_length": self.history_length,
        }


def make_view(replica: Replica, key: bytes) -> ReplicaView:
    head = replica.head
    unsigned = {
        "replica_id": replica.replica_id,
        "head_id": head.head_id,
        "history_digest": head.history_digest,
        "history_length": head.history_length,
    }
    return ReplicaView(**unsigned, signature=sign(key, unsigned))


class ViewPolicy:
    """Authenticates independent replica identities; evidence quorum is not consensus."""

    def __init__(self, keys: Mapping[str, bytes], threshold: int):
        self.keys = dict(keys)
        self.threshold = threshold

    def verify(self, views: Iterable[ReplicaView]) -> tuple[str, ...]:
        by_id: dict[str, ReplicaView] = {}
        valid: set[str] = set()
        for view in views:
            previous = by_id.get(view.replica_id)
            if previous is not None and previous != view:
                raise DuplicateReplicaIdentity(view.replica_id)
            by_id[view.replica_id] = view
            key = self.keys.get(view.replica_id)
            if key is None:
                continue
            if hmac.compare_digest(sign(key, view.unsigned), view.signature):
                valid.add(view.replica_id)
        if len(valid) < self.threshold:
            raise UnknownReplica(f"valid replica views={len(valid)} threshold={self.threshold}")
        return tuple(sorted(valid))


class UnsafeIsolatedReplica:
    """Deliberately unsafe: locally authenticates but never compares histories."""

    def __init__(self):
        self.accepted: list[str] = []

    def accept(self, history: AuthenticatedHistory) -> str:
        head = history.validate()
        self.accepted.append(head.head_id)
        return head.head_id
