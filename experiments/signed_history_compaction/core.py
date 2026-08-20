from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from experiments.transition_history_integrity.protocol import (
    HistoryStore,
    IntegrityError as HistoryIntegrityError,
    ThresholdError,
    digest,
    recovery_payload,
    rotation_payload,
    verify_threshold,
)

SCHEMA = 1
PROTOCOL = "lab062-signed-compaction-v1"


class CompactionError(RuntimeError):
    pass


class AuthenticationError(CompactionError):
    pass


class ArchiveError(CompactionError):
    pass


class HeadMismatch(CompactionError):
    pass


class StaleCheckpoint(CompactionError):
    pass


class UnknownOutcome(CompactionError):
    pass


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def mac(key: bytes, obj) -> str:
    return hmac.new(key, canon(obj), hashlib.sha256).hexdigest()


def row_obj(row):
    names = (
        "sequence",
        "proposal_id",
        "transition_digest",
        "kind",
        "predecessor_root_id",
        "predecessor_recovery_id",
        "successor_root_id",
        "successor_recovery_id",
        "proof_json",
    )
    return dict(zip(names, row))


def strict_int(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise AuthenticationError(f"invalid {name}")


def strict_hex(value, name, length=64):
    if type(value) is not str or len(value) != length:
        raise AuthenticationError(f"invalid {name}")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise AuthenticationError(f"invalid {name}") from exc


def seed_commitment(bootstrap_root_id: str, bootstrap_recovery_id: str) -> str:
    return sha(
        canon(
            {
                "kind": "lab062-prefix-seed",
                "bootstrap_root_id": bootstrap_root_id,
                "bootstrap_recovery_id": bootstrap_recovery_id,
                "protocol": PROTOCOL,
            }
        )
    )


def advance_commitment(previous: str, row) -> str:
    return sha(bytes.fromhex(previous) + canon(row_obj(row)))


@dataclass(frozen=True)
class SignedCheckpoint:
    schema_version: int
    protocol_version: str
    history_id: str
    sequence: int
    root_id: str
    recovery_id: str
    prefix_commitment: str
    base_sequence: int
    base_archive_id: str | None
    external_anchor_id: str
    signer_id: str
    signature: str

    @property
    def unsigned(self):
        body = asdict(self)
        body.pop("signature")
        return body

    @property
    def checkpoint_id(self):
        return sha(canon(asdict(self)))

    @classmethod
    def parse(cls, raw):
        body = json.loads(raw) if isinstance(raw, str) else dict(raw)
        if set(body) != set(cls.__dataclass_fields__):
            raise AuthenticationError("checkpoint fields")
        strict_int(body["schema_version"], "schema_version", 1)
        strict_int(body["sequence"], "sequence")
        strict_int(body["base_sequence"], "base_sequence")
        if body["base_sequence"] > body["sequence"]:
            raise AuthenticationError("base beyond checkpoint")
        for name in ("protocol_version", "external_anchor_id"):
            if type(body[name]) is not str or not body[name]:
                raise AuthenticationError(f"invalid {name}")
        for name in ("history_id", "root_id", "recovery_id", "prefix_commitment", "signature"):
            strict_hex(body[name], name)
        strict_hex(body["signer_id"], "signer_id", 16)
        if body["base_archive_id"] is not None:
            strict_hex(body["base_archive_id"], "base_archive_id")
        return cls(**body)


@dataclass(frozen=True)
class ArchiveManifest:
    schema_version: int
    protocol_version: str
    history_id: str
    archive_id: str
    previous_archive_id: str | None
    start_sequence: int
    end_sequence: int
    start_root_id: str
    start_recovery_id: str
    start_commitment: str
    end_root_id: str
    end_recovery_id: str
    end_commitment: str
    checkpoint_id: str
    artifact_sha256: str
    row_count: int

    @classmethod
    def parse(cls, raw):
        body = json.loads(raw) if isinstance(raw, str) else dict(raw)
        if set(body) != set(cls.__dataclass_fields__):
            raise ArchiveError("manifest fields")
        for name in ("schema_version", "start_sequence", "end_sequence", "row_count"):
            if type(body[name]) is not int:
                raise ArchiveError(f"invalid {name}")
        if body["start_sequence"] < 1 or body["end_sequence"] < body["start_sequence"] - 1:
            raise ArchiveError("manifest range")
        for name in (
            "history_id", "archive_id", "start_root_id", "start_recovery_id",
            "start_commitment", "end_root_id", "end_recovery_id", "end_commitment",
            "checkpoint_id", "artifact_sha256",
        ):
            try:
                strict_hex(body[name], name)
            except AuthenticationError as exc:
                raise ArchiveError(str(exc)) from exc
        if body["previous_archive_id"] is not None:
            try:
                strict_hex(body["previous_archive_id"], "previous_archive_id")
            except AuthenticationError as exc:
                raise ArchiveError(str(exc)) from exc
        return cls(**body)
