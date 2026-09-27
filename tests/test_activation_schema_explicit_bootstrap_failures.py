import sqlite3

import pytest

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    SignedAnchorProvider,
)
from experiments.provider_generation_history.activation_schema import ACTIVATION_TABLE_SQL
from experiments.provider_generation_history.activation_schema_migration import (
    _explicit_bootstrap_surface,
    install_and_reserve_activation_schema_v1,
    migrate_activation_schema_v1,
)
from experiments.provider_generation_history.activation_schema_provenance import (
    MIGRATION_INTENT_ID,
    classify_activation_schema_provenance_locked,
)
from experiments.provider_generation_history.protocol import (
    CurrentGenerationRequired,
    GenerationDescriptor,
    HistoricalVerificationError,
)
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger
from experiments.shared_anchor_intent_ledger.protocol import Intent, PendingIntent


def _runtime(generation=1, key=b"provider-key-1"):
    provider = SignedAnchorProvider("anchor-A", generation, key, value=0)
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    attested = AttestedCatchup(provider, verifier)
    bootstrap = GenerationDescriptor("anchor-A", 1, b"provider-key-1".hex())
    return provider, attested, bootstrap


def test_partial_activation_ddl_fails_closed_without_marker(tmp_path):
    path = tmp_path / "shared.db"
    _, attested, bootstrap = _runtime()
    _explicit_bootstrap_surface(path, attested, bootstrap)
    with sqlite3.connect(path) as q:
        q.execute(ACTIVATION_TABLE_SQL)
        q.commit()

    with pytest.raises(HistoricalVerificationError, match="partially installed"):
        install_and_reserve_activation_schema_v1(path, attested, bootstrap)

    with sqlite3.connect(path) as q:
        assert classify_activation_schema_provenance_locked(q) != "COMPLETE"
        assert q.execute(
            "SELECT COUNT(*) FROM shared_anchor_intents WHERE intent_id=?",
            (MIGRATION_INTENT_ID,),
        ).fetchone()[0] == 0


def test_unrelated_prepared_intent_blocks_migration_without_consuming_tail(tmp_path):
    path = tmp_path / "shared.db"
    _, attested, bootstrap = _runtime()
    legacy = _explicit_bootstrap_surface(path, attested, bootstrap)
    unrelated = Intent("other", "component", "migration", {"purpose": "unrelated"})
    reserved = legacy.reserve(unrelated)

    with pytest.raises(PendingIntent, match="another anchor intent"):
        install_and_reserve_activation_schema_v1(path, attested, bootstrap)

    with sqlite3.connect(path) as q:
        assert q.execute(
            "SELECT status FROM shared_anchor_intents WHERE intent_id=?",
            (reserved.intent_id,),
        ).fetchone() == ("PREPARED",)
        assert q.execute(
            "SELECT COUNT(*) FROM shared_anchor_intents WHERE intent_id=?",
            (MIGRATION_INTENT_ID,),
        ).fetchone()[0] == 0


def test_stale_runtime_fails_before_activation_reservation(tmp_path):
    path = tmp_path / "shared.db"
    _, attested, bootstrap = _runtime()
    legacy = _explicit_bootstrap_surface(path, attested, bootstrap)
    key2 = b"provider-key-2"
    successor = GenerationDescriptor("anchor-A", 2, key2.hex())
    history = legacy._history()
    proof = history.make_transition(bootstrap, successor)
    q = history._con()
    try:
        q.execute("BEGIN IMMEDIATE")
        history._rotate_locked(q, successor, proof)
        q.commit()
    finally:
        q.close()

    with pytest.raises(CurrentGenerationRequired):
        install_and_reserve_activation_schema_v1(path, attested, bootstrap)

    with sqlite3.connect(path) as q:
        assert q.execute(
            "SELECT COUNT(*) FROM shared_anchor_intents WHERE intent_id=?",
            (MIGRATION_INTENT_ID,),
        ).fetchone()[0] == 0


def test_failed_confirmation_leaves_prepared_and_retry_completes(tmp_path, monkeypatch):
    path = tmp_path / "shared.db"
    provider, attested, bootstrap = _runtime()
    original_execute = SupportedHistoricalSharedAnchorLedger.execute

    def fail_confirmation(self, intent):
        if intent.intent_id == MIGRATION_INTENT_ID:
            raise RuntimeError("injected confirmation failure")
        return original_execute(self, intent)

    monkeypatch.setattr(SupportedHistoricalSharedAnchorLedger, "execute", fail_confirmation)
    with pytest.raises(RuntimeError, match="injected confirmation failure"):
        migrate_activation_schema_v1(path, attested, bootstrap)

    with sqlite3.connect(path) as q:
        assert classify_activation_schema_provenance_locked(q) != "COMPLETE"
        assert q.execute(
            "SELECT status FROM shared_anchor_intents WHERE intent_id=?",
            (MIGRATION_INTENT_ID,),
        ).fetchone() == ("PREPARED",)
    assert provider.value == 0

    monkeypatch.setattr(SupportedHistoricalSharedAnchorLedger, "execute", original_execute)
    recovered = migrate_activation_schema_v1(path, attested, bootstrap)
    assert recovered.verify_durable() is True
    assert provider.value == 1
    with sqlite3.connect(path) as q:
        assert classify_activation_schema_provenance_locked(q) == "COMPLETE"
        assert q.execute(
            "SELECT status FROM shared_anchor_intents WHERE intent_id=?",
            (MIGRATION_INTENT_ID,),
        ).fetchone() == ("CONFIRMED",)


def test_unknown_outcome_confirmation_retry_reconciles_without_double_increment(
    tmp_path, monkeypatch
):
    path = tmp_path / "shared.db"
    provider, attested, bootstrap = _runtime()
    original_execute = SupportedHistoricalSharedAnchorLedger.execute
    injected = False

    def timeout_after_provider_commit(self, intent):
        nonlocal injected
        if intent.intent_id == MIGRATION_INTENT_ID and not injected:
            injected = True
            return original_execute(self, intent, timeout_after_commit=True)
        return original_execute(self, intent)

    monkeypatch.setattr(
        SupportedHistoricalSharedAnchorLedger,
        "execute",
        timeout_after_provider_commit,
    )
    with pytest.raises(PendingIntent):
        migrate_activation_schema_v1(path, attested, bootstrap)

    # The external effect committed, but durable migration provenance is still PREPARED.
    assert provider.value == 1
    with sqlite3.connect(path) as q:
        assert classify_activation_schema_provenance_locked(q) == "DDL_INSTALLED_PREPARED"
        assert q.execute(
            "SELECT status FROM shared_anchor_intents WHERE intent_id=?",
            (MIGRATION_INTENT_ID,),
        ).fetchone() == ("PREPARED",)

    recovered = migrate_activation_schema_v1(path, attested, bootstrap)
    assert recovered.verify_durable() is True
    assert provider.value == 1
    with sqlite3.connect(path) as q:
        assert classify_activation_schema_provenance_locked(q) == "COMPLETE"
        assert q.execute(
            "SELECT status FROM shared_anchor_intents WHERE intent_id=?",
            (MIGRATION_INTENT_ID,),
        ).fetchone() == ("CONFIRMED",)
