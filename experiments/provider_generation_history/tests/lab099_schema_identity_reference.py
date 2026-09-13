"""Test-owned LAB-099 schema-identity verifier reference.

This module freezes only the already-decided verification boundary. It does not define
precursor SQL, production APIs, authenticators, migration mutation plans, or provenance
persistence. Physical DDL remains independently implementation-gated.

The oracle is intentionally small and side-effect free so future RED tests can compare
production classification against one unambiguous authority boundary without smuggling
literal SQLite choices into the test harness.
"""

from __future__ import annotations

from dataclasses import dataclass


class SchemaIdentityReferenceError(RuntimeError):
    """Frozen schema-identity authority relation is absent, stale, forked, or corrupt."""


def _digest32(value: bytes | None, *, field: str, optional: bool = False) -> bytes | None:
    if optional and value is None:
        return None
    if type(value) is not bytes or len(value) != 32:
        raise SchemaIdentityReferenceError(f"{field} must be exact 32-byte digest")
    return value


def _epoch(value: int, *, field: str) -> int:
    if type(value) is not int or value < 0:
        raise SchemaIdentityReferenceError(f"{field} must be exact non-negative int")
    return value


@dataclass(frozen=True)
class CurrentSchemaIdentity:
    logical_database_identity_digest: bytes
    lab092_completion_digest: bytes
    provenance_head_digest: bytes
    provenance_epoch: int
    observed_relation_definition_digest: bytes | None

    def __post_init__(self) -> None:
        _digest32(self.logical_database_identity_digest, field="current.logical_database_identity_digest")
        _digest32(self.lab092_completion_digest, field="current.lab092_completion_digest")
        _digest32(self.provenance_head_digest, field="current.provenance_head_digest")
        _epoch(self.provenance_epoch, field="current.provenance_epoch")
        _digest32(
            self.observed_relation_definition_digest,
            field="current.observed_relation_definition_digest",
            optional=True,
        )


@dataclass(frozen=True)
class PreparedSchemaIdentity:
    logical_database_identity_digest: bytes
    predecessor_lab092_completion_digest: bytes
    predecessor_provenance_head_digest: bytes
    predecessor_epoch: int
    relation_definition_digest: bytes
    prepared_event_digest: bytes

    def __post_init__(self) -> None:
        _digest32(self.logical_database_identity_digest, field="prepared.logical_database_identity_digest")
        _digest32(
            self.predecessor_lab092_completion_digest,
            field="prepared.predecessor_lab092_completion_digest",
        )
        _digest32(
            self.predecessor_provenance_head_digest,
            field="prepared.predecessor_provenance_head_digest",
        )
        _epoch(self.predecessor_epoch, field="prepared.predecessor_epoch")
        _digest32(self.relation_definition_digest, field="prepared.relation_definition_digest")
        _digest32(self.prepared_event_digest, field="prepared.prepared_event_digest")


@dataclass(frozen=True)
class ConfirmedSchemaIdentity:
    logical_database_identity_digest: bytes
    prepared_event_digest: bytes
    relation_definition_digest: bytes
    resulting_provenance_head_digest: bytes
    resulting_epoch: int
    confirmed_event_digest: bytes

    def __post_init__(self) -> None:
        _digest32(self.logical_database_identity_digest, field="confirmed.logical_database_identity_digest")
        _digest32(self.prepared_event_digest, field="confirmed.prepared_event_digest")
        _digest32(self.relation_definition_digest, field="confirmed.relation_definition_digest")
        _digest32(
            self.resulting_provenance_head_digest,
            field="confirmed.resulting_provenance_head_digest",
        )
        _epoch(self.resulting_epoch, field="confirmed.resulting_epoch")
        _digest32(self.confirmed_event_digest, field="confirmed.confirmed_event_digest")


def verify_schema_identity_boundary(
    current: CurrentSchemaIdentity,
    *,
    prepared: PreparedSchemaIdentity | None,
    confirmed: ConfirmedSchemaIdentity | None,
) -> str:
    """Return the frozen cutover state or fail closed.

    Authority rules frozen here:
    - a valid LAB-092 completion digest alone is not precursor-schema authority;
    - physical schema without authenticated PREPARED authority is an orphan;
    - PREPARED binds logical DB, LAB-092 completion, predecessor head+epoch, and one
      exact relation-definition digest;
    - CONFIRMED binds the exact PREPARED digest and same relation-definition digest;
    - PREPARED is valid only while its predecessor head+epoch is current;
    - CONFIRMED is valid only at its authenticated resulting head+epoch;
    - missing/different schema after PREPARED or CONFIRMED is corruption, never a
      downgrade path to legacy LAB-090/LAB-092 semantics.
    """

    if type(current) is not CurrentSchemaIdentity:
        raise TypeError("exact CurrentSchemaIdentity required")
    if prepared is not None and type(prepared) is not PreparedSchemaIdentity:
        raise TypeError("exact PreparedSchemaIdentity required")
    if confirmed is not None and type(confirmed) is not ConfirmedSchemaIdentity:
        raise TypeError("exact ConfirmedSchemaIdentity required")

    observed = current.observed_relation_definition_digest

    if prepared is None:
        if confirmed is not None:
            raise SchemaIdentityReferenceError("CONFIRMED cannot exist without exact PREPARED evidence")
        if observed is not None:
            raise SchemaIdentityReferenceError("precursor relation exists without authenticated PREPARED authority")
        return "ABSENT"

    if prepared.logical_database_identity_digest != current.logical_database_identity_digest:
        raise SchemaIdentityReferenceError("PREPARED logical database identity mismatch")
    if prepared.predecessor_lab092_completion_digest != current.lab092_completion_digest:
        raise SchemaIdentityReferenceError("PREPARED LAB-092 predecessor completion mismatch")
    if observed is None:
        raise SchemaIdentityReferenceError("authenticated precursor schema is missing")
    if prepared.relation_definition_digest != observed:
        raise SchemaIdentityReferenceError("physical precursor schema digest differs from PREPARED authority")

    if confirmed is None:
        if prepared.predecessor_provenance_head_digest != current.provenance_head_digest:
            raise SchemaIdentityReferenceError("PREPARED predecessor provenance head is stale or forked")
        if prepared.predecessor_epoch != current.provenance_epoch:
            raise SchemaIdentityReferenceError("PREPARED predecessor provenance epoch is stale or forked")
        return "PREPARED_INCOMPLETE"

    if confirmed.logical_database_identity_digest != current.logical_database_identity_digest:
        raise SchemaIdentityReferenceError("CONFIRMED logical database identity mismatch")
    if confirmed.prepared_event_digest != prepared.prepared_event_digest:
        raise SchemaIdentityReferenceError("CONFIRMED does not bind the exact PREPARED event")
    if confirmed.relation_definition_digest != prepared.relation_definition_digest:
        raise SchemaIdentityReferenceError("CONFIRMED relation digest differs from PREPARED authority")
    if confirmed.relation_definition_digest != observed:
        raise SchemaIdentityReferenceError("physical precursor schema digest differs from CONFIRMED authority")
    if confirmed.resulting_provenance_head_digest != current.provenance_head_digest:
        raise SchemaIdentityReferenceError("CONFIRMED resulting provenance head is stale or forked")
    if confirmed.resulting_epoch != current.provenance_epoch:
        raise SchemaIdentityReferenceError("CONFIRMED resulting provenance epoch is stale or forked")
    return "CONFIRMED"


def validate_schema_identity_reference() -> bool:
    """Exercise the six frozen boundary cases without repository or SQLite mutation."""

    def d(start: int) -> bytes:
        return bytes((start + i) % 256 for i in range(32))

    logical = d(0)
    lab092 = d(32)
    parent = d(64)
    relation = d(96)
    prepared_digest = d(128)
    resulting = d(160)
    confirmed_digest = d(192)
    other = d(224)

    absent = CurrentSchemaIdentity(logical, lab092, parent, 7, None)
    if verify_schema_identity_boundary(absent, prepared=None, confirmed=None) != "ABSENT":
        raise AssertionError("LAB-092-only state must remain ABSENT")

    orphan = CurrentSchemaIdentity(logical, lab092, parent, 7, relation)
    try:
        verify_schema_identity_boundary(orphan, prepared=None, confirmed=None)
    except SchemaIdentityReferenceError:
        pass
    else:
        raise AssertionError("orphan schema must fail closed")

    prepared = PreparedSchemaIdentity(logical, lab092, parent, 7, relation, prepared_digest)
    if verify_schema_identity_boundary(orphan, prepared=prepared, confirmed=None) != "PREPARED_INCOMPLETE":
        raise AssertionError("exact PREPARED state must classify PREPARED_INCOMPLETE")

    wrong_schema = CurrentSchemaIdentity(logical, lab092, parent, 7, other)
    try:
        verify_schema_identity_boundary(wrong_schema, prepared=prepared, confirmed=None)
    except SchemaIdentityReferenceError:
        pass
    else:
        raise AssertionError("PREPARED schema digest mismatch must fail closed")

    stale = CurrentSchemaIdentity(logical, lab092, other, 8, relation)
    try:
        verify_schema_identity_boundary(stale, prepared=prepared, confirmed=None)
    except SchemaIdentityReferenceError:
        pass
    else:
        raise AssertionError("stale/forked PREPARED parent+epoch must fail closed")

    confirmed = ConfirmedSchemaIdentity(
        logical,
        prepared_digest,
        relation,
        resulting,
        8,
        confirmed_digest,
    )
    current_confirmed = CurrentSchemaIdentity(logical, lab092, resulting, 8, relation)
    if verify_schema_identity_boundary(
        current_confirmed,
        prepared=prepared,
        confirmed=confirmed,
    ) != "CONFIRMED":
        raise AssertionError("exact CONFIRMED state must classify CONFIRMED")

    wrong_prepared = ConfirmedSchemaIdentity(logical, other, relation, resulting, 8, confirmed_digest)
    try:
        verify_schema_identity_boundary(
            current_confirmed,
            prepared=prepared,
            confirmed=wrong_prepared,
        )
    except SchemaIdentityReferenceError:
        pass
    else:
        raise AssertionError("CONFIRMED must bind exact PREPARED digest")

    deleted_after_confirm = CurrentSchemaIdentity(logical, lab092, resulting, 8, None)
    try:
        verify_schema_identity_boundary(
            deleted_after_confirm,
            prepared=prepared,
            confirmed=confirmed,
        )
    except SchemaIdentityReferenceError:
        pass
    else:
        raise AssertionError("post-CONFIRMED schema absence must not downgrade")

    return True


if __name__ == "__main__":
    assert validate_schema_identity_reference()
