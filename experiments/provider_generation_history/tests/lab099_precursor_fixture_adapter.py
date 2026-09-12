"""Test-only LAB-099 precursor-cutover corruption/crash adapter.

This module deliberately does not define LAB-099 protocol bytes, SQL DDL, authenticators,
or provenance events. Those are security authority, not test conveniences.

The adapter accepts only an independently frozen fixture-vector module whose values are
byte-exact protocol/DDL evidence. Until that vector module exists, every mutation helper
fails closed. This prevents RED-intent tests from accidentally inventing a second,
unauthenticated LAB-099 protocol while production behavior is still absent.

Nothing in this module is imported by production code.
"""

from __future__ import annotations

import importlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable


_VECTOR_MODULE = (
    "experiments.provider_generation_history.tests."
    "lab099_precursor_fixture_vectors"
)


class FixtureVectorUnavailable(RuntimeError):
    """Exact LAB-099 test vectors are not frozen/materialized yet."""


class FixtureVectorContractError(RuntimeError):
    """The independent fixture-vector module violates the test harness contract."""


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
    """One exact SQL statement supplied by the independent fixture-vector oracle."""

    sql: str
    params: tuple[Any, ...] = ()

    def __post_init__(self) -> None:
        if type(self.sql) is not str or not self.sql.strip():
            raise FixtureVectorContractError("fixture SQL must be non-empty exact text")
        if type(self.params) is not tuple:
            raise FixtureVectorContractError(
                "fixture SQL params must be an exact tuple"
            )


def _vectors() -> ModuleType:
    try:
        module = importlib.import_module(_VECTOR_MODULE)
    except ModuleNotFoundError as exc:
        if exc.name == _VECTOR_MODULE:
            raise FixtureVectorUnavailable(
                "exact LAB-099 precursor fixture vectors are not present; "
                "do not synthesize DDL/provenance/authenticator bytes in the adapter"
            ) from exc
        raise

    required = (
        "PRECURSOR_RELATION_NAME",
        "PRECURSOR_RELATION_SQL",
        "orphan_relation_plan",
        "atomic_prepared_plan",
        "uncommitted_prepared_plan",
        "advance_provenance_parent_plan",
        "commit_prepared_plan",
        "sibling_prepared_plan",
        "confirmed_event_plan",
    )
    missing = [name for name in required if not hasattr(module, name)]
    if missing:
        raise FixtureVectorContractError(
            "fixture-vector module is incomplete: " + ", ".join(missing)
        )

    relation_name = module.PRECURSOR_RELATION_NAME
    relation_sql = module.PRECURSOR_RELATION_SQL
    if type(relation_name) is not str or not relation_name:
        raise FixtureVectorContractError(
            "PRECURSOR_RELATION_NAME must be exact non-empty text"
        )
    if not relation_name.replace("_", "a").isalnum() or relation_name[0].isdigit():
        raise FixtureVectorContractError(
            "PRECURSOR_RELATION_NAME must be a simple SQLite identifier"
        )
    if type(relation_sql) is not str or not relation_sql.strip():
        raise FixtureVectorContractError(
            "PRECURSOR_RELATION_SQL must be exact non-empty text"
        )
    return module


def _coerce_plan(plan: Iterable[Any]) -> tuple[SqlMutation, ...]:
    mutations: list[SqlMutation] = []
    for item in plan:
        if isinstance(item, SqlMutation):
            mutation = item
        elif (
            type(item) is tuple
            and len(item) == 2
            and type(item[0]) is str
            and type(item[1]) is tuple
        ):
            mutation = SqlMutation(item[0], item[1])
        else:
            raise FixtureVectorContractError(
                "fixture plan entries must be SqlMutation or exact (sql, params) tuples"
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
            q.execute(mutation.sql, mutation.params)
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

    vectors = _vectors()
    _apply_plan(path, vectors.orphan_relation_plan())


def install_atomic_prepared_cutover(
    path: Path | str,
    attested: Any,
    bootstrap: Any,
) -> PreparedCutoverFixture:
    """Atomically install exact DDL + independently authenticated PREPARED evidence."""

    vectors = _vectors()
    result = vectors.atomic_prepared_plan(path, attested, bootstrap)
    if type(result) is not tuple or len(result) != 2:
        raise FixtureVectorContractError(
            "atomic_prepared_plan must return (mutation_plan, prepared_event_digest)"
        )
    plan, prepared_digest = result
    _apply_plan(path, plan)
    return PreparedCutoverFixture(
        _digest(prepared_digest, field="prepared_event_digest")
    )


def build_uncommitted_prepared_cutover(
    path: Path | str,
    attested: Any,
    bootstrap: Any,
) -> Any:
    """Build exact PREPARED fixture bytes without mutating the target database."""

    vectors = _vectors()
    prepared = vectors.uncommitted_prepared_plan(path, attested, bootstrap)
    digest = getattr(prepared, "prepared_event_digest", None)
    _digest(digest, field="prepared.prepared_event_digest")
    return prepared


def advance_authenticated_provenance_parent(path: Path | str) -> None:
    """Apply an exact independently-authenticated successor-head fixture transition."""

    vectors = _vectors()
    _apply_plan(path, vectors.advance_provenance_parent_plan(path))


def commit_prepared_cutover(path: Path | str, prepared: Any) -> None:
    """Attempt to commit exact PREPARED bytes against the target's current parent."""

    vectors = _vectors()
    _digest(
        getattr(prepared, "prepared_event_digest", None),
        field="prepared.prepared_event_digest",
    )
    _apply_plan(path, vectors.commit_prepared_plan(path, prepared))


def build_sibling_prepared(path: Path | str, prepared: Any) -> Any:
    """Build a semantically distinct exact sibling fixture under the same parent."""

    vectors = _vectors()
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

    vectors = _vectors()
    digest = _digest(prepared_event_digest, field="prepared_event_digest")
    _apply_plan(path, vectors.confirmed_event_plan(path, digest))


def delete_precursor_relation(path: Path | str) -> None:
    """Delete the exact frozen precursor relation to model post-cutover corruption."""

    vectors = _vectors()
    name = vectors.PRECURSOR_RELATION_NAME
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
        q.execute(f'DROP TABLE "{name}"')
        q.commit()
    except:
        if q.in_transaction:
            q.rollback()
        raise
    finally:
        q.close()
