from __future__ import annotations

import sqlite3

from experiments.provider_generation_history.activation_schema_provenance import (
    ActivationSchemaMigrationRequired,
    classify_activation_schema_provenance_locked,
)
from experiments.provider_generation_history.protocol import HistoricalVerificationError


_RECOVERABLE_EXPLICIT_MIGRATION_STATES = frozenset(
    {
        "LEGACY_ABSENT",
        "DDL_INSTALLED_UNMARKED",
        "DDL_INSTALLED_PREPARED",
    }
)


def classify_activation_schema_provenance(path) -> str:
    """Read-only path-level wrapper around the locked LAB-092 classifier.

    Startup owns this short-lived connection. It deliberately begins a read
    transaction and never installs/repairs DDL, writes a migration marker, or obtains
    provider-history mutation authority.
    """
    q = sqlite3.connect(str(path), timeout=5, isolation_level=None)
    q.execute("PRAGMA busy_timeout=5000")
    try:
        q.execute("BEGIN")
        state = classify_activation_schema_provenance_locked(q)
        q.commit()
        return state
    except:
        if q.in_transaction:
            q.rollback()
        raise
    finally:
        q.close()


def require_complete_activation_schema_provenance_for_startup(path) -> None:
    """Reject every non-COMPLETE startup without mutating migration state."""
    state = classify_activation_schema_provenance(path)
    if state == "COMPLETE":
        return
    if state in _RECOVERABLE_EXPLICIT_MIGRATION_STATES:
        raise ActivationSchemaMigrationRequired(
            "activation schema requires explicit migrate_activation_schema_v1()"
        )
    raise HistoricalVerificationError("invalid activation schema provenance state")


class ActivationSchemaProvenanceStartupMixin:
    """LAB-092 startup gate that runs before inherited initialization side effects.

    Keep this mixin opt-in until LAB-090 activation installation/fencing and the
    explicit migration writer are composed. It intentionally has no migration method
    and no provider-history reference.
    """

    def __init__(self, path, *args, **kwargs):
        require_complete_activation_schema_provenance_for_startup(path)
        super().__init__(path, *args, **kwargs)
