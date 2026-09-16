from __future__ import annotations

import sqlite3
from types import SimpleNamespace

import pytest

from experiments.provider_generation_history.activation_schema import ACTIVATION_TABLE_SQL, ACTIVATION_TRIGGER_SQL
from experiments.provider_generation_history.activation_schema_migration import install_and_reserve_activation_schema_v1
from experiments.provider_generation_history.activation_schema_provenance import MIGRATION_INTENT_ID, completion_intent
from experiments.provider_generation_history.protocol import CurrentGenerationRequired, HistoricalVerificationError
from experiments.shared_anchor_intent_ledger.protocol import PendingIntent


class _History:
    def __init__(self, generation_id="g1"):
        self.descriptor = SimpleNamespace(provider_id="provider", generation=1, generation_id=generation_id)

    def _verify_durable_locked(self, q):
        return self.descriptor


class _Ledger:
    def __init__(self, path, runtime="g1", durable="g1"):
        self.path = str(path); self.runtime = SimpleNamespace(generation_id=runtime); self.history = _History(durable)

    def _con(self): return sqlite3.connect(self.path, timeout=5, isolation_level=None)
    def _history(self): return self.history
    def _descriptor_from_attested(self, attested): return self.runtime
    def _request_id(self, position, intent_id, component_id, intent_type, payload_digest): return f"request:{position}:{intent_id}"
    def entry(self, intent_id):
        q = self._con()
        try: return q.execute("SELECT intent_id,status FROM shared_anchor_intents WHERE intent_id=?", (intent_id,)).fetchone()
        finally: q.close()


def _legacy_db(path):
    q = sqlite3.connect(path)
    q.executescript("""
        CREATE TABLE shared_anchor_meta(singleton INTEGER PRIMARY KEY,reserved_position INTEGER NOT NULL);
        INSERT INTO shared_anchor_meta VALUES(1,0);
        CREATE TABLE shared_anchor_intents(
          intent_id TEXT PRIMARY KEY, component_id TEXT NOT NULL, intent_type TEXT NOT NULL,
          payload_digest TEXT NOT NULL, provider_id TEXT NOT NULL, provider_generation INTEGER NOT NULL,
          predecessor INTEGER NOT NULL, position INTEGER NOT NULL, request_id TEXT NOT NULL,
          status TEXT NOT NULL, stable_binding TEXT);
    """)
    q.commit(); q.close()


def _surface(monkeypatch, path, runtime="g1", durable="g1"):
    ledger = _Ledger(path, runtime, durable)
    monkeypatch.setattr("experiments.provider_generation_history.activation_schema_migration._migration_reservation_surface", lambda *args: ledger)
    return ledger


def _insert_marker(path, status="PREPARED", intent_id=MIGRATION_INTENT_ID):
    intent = completion_intent(); q = sqlite3.connect(path)
    q.execute("INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)", (
        intent_id, intent.component_id, intent.intent_type, intent.payload_digest,
        "provider", 1, 0, 1, "request:1:marker", status, None))
    q.execute("UPDATE shared_anchor_meta SET reserved_position=1"); q.commit(); q.close()


def test_partial_ddl_fails_closed_without_repair(tmp_path, monkeypatch):
    path = tmp_path / "partial.sqlite"; _legacy_db(path)
    q = sqlite3.connect(path); q.execute(ACTIVATION_TABLE_SQL); q.commit(); q.close(); _surface(monkeypatch, path)
    with pytest.raises(HistoricalVerificationError, match="partially installed"):
        install_and_reserve_activation_schema_v1(path, object(), object())
    q = sqlite3.connect(path)
    assert q.execute("SELECT 1 FROM sqlite_master WHERE type='trigger' AND name='block_intent_during_provider_activation'").fetchone() is None
    q.close()


def test_unrelated_prepared_blocks_fresh_install(tmp_path, monkeypatch):
    path = tmp_path / "pending-fresh.sqlite"; _legacy_db(path); _insert_marker(path, intent_id="other:prepared"); _surface(monkeypatch, path)
    with pytest.raises(PendingIntent):
        install_and_reserve_activation_schema_v1(path, object(), object())
    q = sqlite3.connect(path)
    assert q.execute("SELECT 1 FROM sqlite_master WHERE name='provider_generation_activations'").fetchone() is None
    q.close()


def test_unrelated_prepared_blocks_prepared_resume(tmp_path, monkeypatch):
    path = tmp_path / "pending-resume.sqlite"; _legacy_db(path); _insert_marker(path, intent_id="other:prepared")
    q = sqlite3.connect(path); q.execute(ACTIVATION_TABLE_SQL); q.execute(ACTIVATION_TRIGGER_SQL); q.commit(); q.close()
    _insert_marker(path); _surface(monkeypatch, path)
    with pytest.raises(PendingIntent):
        install_and_reserve_activation_schema_v1(path, object(), object())


def test_stale_runtime_generation_fails_before_install(tmp_path, monkeypatch):
    path = tmp_path / "stale.sqlite"; _legacy_db(path); _surface(monkeypatch, path, "old", "new")
    with pytest.raises(CurrentGenerationRequired):
        install_and_reserve_activation_schema_v1(path, object(), object())
    q = sqlite3.connect(path)
    assert q.execute("SELECT 1 FROM sqlite_master WHERE name='provider_generation_activations'").fetchone() is None
    q.close()


def test_exact_prepared_resume_is_idempotent(tmp_path, monkeypatch):
    path = tmp_path / "resume.sqlite"; _legacy_db(path)
    q = sqlite3.connect(path); q.execute(ACTIVATION_TABLE_SQL); q.execute(ACTIVATION_TRIGGER_SQL); q.commit(); q.close()
    _insert_marker(path); _surface(monkeypatch, path)
    assert install_and_reserve_activation_schema_v1(path, object(), object()) == (MIGRATION_INTENT_ID, "PREPARED")
    q = sqlite3.connect(path)
    assert q.execute("SELECT reserved_position FROM shared_anchor_meta").fetchone()[0] == 1
    assert q.execute("SELECT COUNT(*) FROM shared_anchor_intents").fetchone()[0] == 1
    q.close()


def test_confirmed_corrupt_ddl_fails_closed(tmp_path, monkeypatch):
    path = tmp_path / "confirmed.sqlite"; _legacy_db(path)
    q = sqlite3.connect(path); q.execute(ACTIVATION_TABLE_SQL); q.execute(ACTIVATION_TRIGGER_SQL); q.commit(); q.close()
    _insert_marker(path, "CONFIRMED")
    q = sqlite3.connect(path); q.execute("DROP TRIGGER block_intent_during_provider_activation"); q.commit(); q.close(); _surface(monkeypatch, path)
    with pytest.raises(HistoricalVerificationError, match="confirmed.*missing or mismatched DDL"):
        install_and_reserve_activation_schema_v1(path, object(), object())
    q = sqlite3.connect(path)
    assert q.execute("SELECT 1 FROM sqlite_master WHERE type='trigger' AND name='block_intent_during_provider_activation'").fetchone() is None
    q.close()
