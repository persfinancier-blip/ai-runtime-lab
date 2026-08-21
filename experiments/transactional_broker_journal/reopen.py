from __future__ import annotations

import sqlite3
from pathlib import Path

from .protocol import CorruptJournal, TransactionalJournal


def reopen_journal(path: str | Path) -> TransactionalJournal:
    """Reopen an existing journal without importing credential generation from caller state.

    The durable SQL row is authoritative. This helper is restart-only: it refuses a
    missing/malformed journal rather than silently bootstrapping generation 1.
    """
    path = str(path)
    q = sqlite3.connect(path, timeout=5)
    try:
        row = q.execute(
            "SELECT credential_generation FROM broker_meta WHERE singleton=1"
        ).fetchone()
    except sqlite3.Error as exc:
        raise CorruptJournal("existing journal metadata unavailable") from exc
    finally:
        q.close()
    if row is None or len(row) != 1 or type(row[0]) is not int or row[0] < 1:
        raise CorruptJournal("invalid durable journal generation")
    journal = TransactionalJournal(path, row[0])
    journal.verify_durable()
    return journal
