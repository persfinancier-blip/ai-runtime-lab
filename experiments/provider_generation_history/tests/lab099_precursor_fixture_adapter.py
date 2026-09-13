"""Test-only LAB-099 precursor-cutover corruption/crash adapter.

This module deliberately does not define LAB-099 protocol bytes, authenticators, or
provenance events. Those are security authority, not test conveniences.

The physical precursor relation identity is already frozen independently, so the adapter
may install/delete that exact literal DDL directly from the side-effect-free relation
reference oracle. Authority-bearing PREPARED/CONFIRMED/provenance mutations remain
separately gated on an independently frozen fixture-vector module and fail closed until
that module exists.

Nothing in this module is imported by production code.
"""

from __future__ import annotations

import importlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable


_RELATION_REFERENCE_MODULE = (
    "experiments.provider_generation_history.tests."
    "lab099_precursor_relation_reference"
)
_VECTOR_MODULE = (
    "experiments.provider_generation_history.tests."
    "lab099_precursor_fixture_vectors"
)


class FixtureVectorUnavailable(RuntimeError):
    """Exact LAB-099 authority-bearing fixture vectors are not materialized yet."""


class FixtureVectorContractError(RuntimeError):
    """An independent LAB-099 test fixture oracle violates the harness contract."""


@dataclass(frozen=True)
class PreparedCutoverFixture:
    """Identity returned after exact DDL+PREPARED fixture installation."""

    prepared_event_digest: bytes

    def __post_init__(self) -> None:
        if (
            type(self.prepared_event_digest) is not bytes
            or len(self.prepared_event_digest) != 32
        ):
            raise FixtureVectorContractError(
                "prepared_event_digest must be exact 32-byte digest"
            )


@dataclass(frozen=True)
class SqlMutation:
    """One exact SQL statement supplied by an independent fixture oracle."""

    sql: str
    params: tuple[Any, ...] = ()
    expected_rowcount: int | None = None

    def __post_init__(self) -> None:
        if type(self.sql) is not str or not self.sql.strip():
            raise FixtureVectorContractError("fixture SQL must be non-empty exact text")
        if type(self.params) is not tuple:
            raise FixtureVectorContractError(
                "fixture SQL params must be an exact tuple"
            )
        if self.expected_rowcount is not None and (
            type(self.expected_rowcount) is not int or self.expected_rowcount < 0
        ):
            raise FixtureVectorContractError(
                "expected_rowcount must be an exact non-negative int or None"
            )


def _simple_identifier(value: Any, *, field: str) -> str:
    if type(value) is not str or not value:
        raise FixtureVectorContractError(f"{field} must be exact non-empty text")
    if not value.replace("_", "a").isalnum() or value[0].isdigit():
        raise FixtureVectorContractError(f"{field} must be a simple SQLite identifier")
    return value


def _relation_reference() -> ModuleType:
    try:
        module = importlib.import_module(_RELATION_REFERENCE_MODULE)
    except ModuleNotFoundError as exc:
        if exc.name == _RELATION_REFERENCE_MODULE:
            raise FixtureVectorUnavailable(
                "frozen LAB-099 precursor relation reference is not present"
            ) from exc
        raise

    required = (
        "PRECURSOR_RELATION_NAME",
        "PRECURSOR_RELATION_DDL_V1",
        "FROZEN_RELATION_DEFINITION_DIGEST",
        "validate_precursor_relation_reference",
    )
    missing = [name for name in required if not hasattr(module, name)]
    if missing:
        raise FixtureVectorContractError(
            "relation-reference module is incomplete: " + ", ".join(missing)
        )

    _simple_identifier(module.PRECURSOR_RELATION_NAME, field="PRECURSOR_RELATION_NAME")
    if (
        type(module.PRECURSOR_RELATION_DDL_V1) is not str
        or not module.PRECURSOR_RELATION_DDL_V1.strip()
    ):
        raise FixtureVectorContractError(
            "PRECURSOR_RELATION_DDL_V1 must be exact non-empty text"
        )
    digest = module.FROZEN_RELATION_DEFINITION_DIGEST
    if type(digest) is not bytes or len(digest) != 32:
        raise FixtureVectorContractError(
            "FROZEN_RELATION_DEFINITION_DIGEST must be exact 32-byte digest"
        )
    if module.validate_precursor_relation_reference() is not True:
        raise FixtureVectorContractError("precursor relation reference self-check failed")
    return module


def _vectors(*required: str) -> ModuleType:
    try:
        module = importlib.import_module(_VECTOR_MODULE)
    except ModuleNotFoundError as exc:
        if exc.name == _VECTOR_MODULE:
            raise FixtureVectorUnavailable(
                "authority-bearing LAB-099 fixture vectors are not present; "
                "do not synthesize provenance/authenticator bytes in the adapter"
            ) from exc
        raise

    missing = [name for name in required if not hasattr(module, name)]
    if missing:
        raise FixtureVectorContractError(
            "fixture-vector module is incomplete for requested operation: "
            + ", ".join(missing)
        )
    return module


def _coerce_plan(plan: Iterable[Any]) -> tuple[SqlMutation, ...]:
    mutations: list[SqlMutation] = []
    for item in plan:
        if isinstance(item, SqlMutation):
            mutation = item
        elif (
            type(item) is tuple
            and len(item) in {2, 3}
            and type(item[0]) is str
            and type(item[1]) is tuple
        ):
            expected_rowcount = None if len(item) == 2 else item[2]
            mutation = SqlMutation(item[0], item[1], expected_rowcount)
        else:
            raise FixtureVectorContractError(
                "fixture plan entries must be SqlMutation or exact "
                "(sql, params[, expected_rowcount]) tuples"
            )
        mutations.append(mutation)
    if not mutations:
        raise FixtureVectorContractError("fixture mutation plan must not be empty")
    return tuple(mutations)


def _con(path: Path | str) -> sqlite3.Connection:
    q = sqlite3.connect(str(path), timeout=5, isolation_level=None)
    q.execute("PRAGMA busy_timeout=5000")
    return q


def _apply_plan(path: Path | str, plan: Iterable[Any]) -> None:
    mutations = _coerce_plan(plan)
    q = _con(path)
    try:
        q.execute("BEGIN IMMEDIATE")
        for mutation in mutations:
            cursor = q.execute(mutation.sql, mutation.params)
            if (
                mutation.expected_rowcount is not None
                and cursor.rowcount != mutation.expected_rowcount
            ):
                raise FixtureVectorContractError(
                    "fixture mutation rowcount mismatch: "
                    f"expected {mutation.expected_rowcount}, got {cursor.rowcount}"
                )
        q.commit()
    except:
        if q.in_transaction:
            q.rollback()
        raise
    finally:
        q.close()


def _digest(value: Any, *, field: str) -> bytes:
    if type(value) is not bytes or len(value) != 32:
        raise FixtureVectorContractError(f"{field} must be exact 32-byte digest")
    return value


def install_precursor_relation_without_prepared(path: Path | str) -> None:
    """Install only the exact frozen precursor relation, intentionally no PREPARED."""

    reference = _relation_reference()
    _apply_plan(path, ((reference.PRECURSOR_RELATION_DDL_V1, ()),))


def install_atomic_prepared_cutover(
    path: Path | str,
    attested: Any,
    bootstrap: Any,
) -> PreparedCutoverFixture:
    """Atomically install exact DDL + independently authenticated PREPARED evidence."""

    vectors = _vectors("atomic_prepared_plan")
    result = vectors.atomic_prepared_plan(path, attested, bootstrap)
    if type(result) is not tuple or len(result) != 2:
        raise FixtureVectorContractError(
            "atomic_prepared_plan must return (mutation_plan, prepared_event_digest)"
        )
    plan, prepared_digest = result
    mutations = list(_coerce_plan(plan))
    reference = _relation_reference()
    if not mutations or mutations[0].sql != reference.PRECURSOR_RELATION_DDL_V1:
        raise FixtureVectorContractError(
            "atomic PREPARED plan must begin with the exact frozen precursor DDL"
        )
    _apply_plan(path, mutations)
    return PreparedCutoverFixture(
        _digest(prepared_digest, field="prepared_event_digest")
    )


def build_uncommitted_prepared_cutover(
    path: Path | str,
    attested: Any,
    bootstrap: Any,
) -> Any:
    """Build exact PREPARED fixture bytes without mutating the target database."""

    vectors = _vectors("uncommitted_prepared_plan")
    prepared = vectors.uncommitted_prepared_plan(path, attested, bootstrap)
    digest = getattr(prepared, "prepared_event_digest", None)
    _digest(digest, field="prepared.prepared_event_digest")
    return prepared


def advance_authenticated_provenance_parent(path: Path | str) -> None:
    """Apply an exact independently-authenticated successor-head fixture transition."""

    vectors = _vectors("advance_provenance_parent_plan")
    _apply_plan(path, vectors.advance_provenance_parent_plan(path))


def commit_prepared_cutover(path: Path | str, prepared: Any) -> None:
    """Attempt to commit exact PREPARED bytes against the target's current parent."""

    vectors = _vectors("commit_prepared_plan")
    _digest(
        getattr(prepared, "prepared_event_digest", None),
        field="prepared.prepared_event_digest",
    )
    _apply_plan(path, vectors.commit_prepared_plan(path, prepared))


def build_sibling_prepared(path: Path | str, prepared: Any) -> Any:
    """Build a semantically distinct exact sibling fixture under the same parent."""

    vectors = _vectors("sibling_prepared_plan")
    _digest(
        getattr(prepared, "prepared_event_digest", None),
        field="prepared.prepared_event_digest",
    )
    sibling = vectors.sibling_prepared_plan(path, prepared)
    _digest(
        getattr(sibling, "prepared_event_digest", None),
        field="sibling.prepared_event_digest",
    )
    return sibling


def install_confirmed_event(
    path: Path | str,
    *,
    prepared_event_digest: bytes,
) -> None:
    """Install exact CONFIRMED fixture evidence referring to supplied PREPARED digest."""

    vectors = _vectors("confirmed_event_plan")
    digest = _digest(prepared_event_digest, field="prepared_event_digest")
    _apply_plan(path, vectors.confirmed_event_plan(path, digest))


def delete_precursor_relation(path: Path | str) -> None:
    """Delete the exact frozen precursor relation to model post-cutover corruption."""

    reference = _relation_reference()
    name = _simple_identifier(
        reference.PRECURSOR_RELATION_NAME,
        field="PRECURSOR_RELATION_NAME",
    )
    q = _con(path)
    try:
        q.execute("BEGIN IMMEDIATE")
        row = q.execute(
            "SELECT type,sql FROM sqlite_master WHERE name=?",
            (name,),
        ).fetchone()
        if row is None or row[0] != "table":
            raise FixtureVectorContractError(
                "precursor relation is absent before deletion fixture"
            )
        if row[1] is None:
            raise FixtureVectorContractError(
                "precursor relation has no SQLite definition before deletion fixture"
            )
        q.execute(f'DROP TABLE "{name}"')
        q.commit()
    except:
        if q.in_transaction:
            q.rollback()
        raise
    finally:
        q.close()
