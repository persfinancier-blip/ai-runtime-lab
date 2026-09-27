import sqlite3

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    SignedAnchorProvider,
)
from experiments.provider_generation_history.activation_schema_migration import (
    migrate_activation_schema_v1,
)
from experiments.provider_generation_history.activation_schema_provenance import (
    MIGRATION_INTENT_ID,
    classify_activation_schema_provenance_locked,
)
from experiments.provider_generation_history.protocol import GenerationDescriptor
from experiments.provider_generation_history.supported import (
    SupportedHistoricalSharedAnchorLedger,
)


def _runtime(key=b"provider-key-1"):
    provider = SignedAnchorProvider("anchor-A", 1, key, value=0)
    verifier = AttestationVerifier(
        {("anchor-A", 1): key}, ProviderIdentity("anchor-A", 1)
    )
    attested = AttestedCatchup(provider, verifier)
    bootstrap = GenerationDescriptor("anchor-A", 1, key.hex())
    return provider, attested, bootstrap


def test_explicit_bootstrap_reaches_complete_before_normal_startup(tmp_path):
    path = tmp_path / "shared.db"
    provider, attested, bootstrap = _runtime()

    ledger = migrate_activation_schema_v1(path, attested, bootstrap)

    assert type(ledger) is SupportedHistoricalSharedAnchorLedger
    assert provider.value == 1
    with sqlite3.connect(path) as q:
        assert classify_activation_schema_provenance_locked(q) == "COMPLETE"
        row = q.execute(
            "SELECT status,position FROM shared_anchor_intents WHERE intent_id=?",
            (MIGRATION_INTENT_ID,),
        ).fetchone()
        assert row == ("CONFIRMED", 1)

    restarted = SupportedHistoricalSharedAnchorLedger(path, attested, bootstrap)
    assert restarted.verify_durable() is True


def test_explicit_bootstrap_is_idempotent_after_complete(tmp_path):
    path = tmp_path / "shared.db"
    provider, attested, bootstrap = _runtime()

    first = migrate_activation_schema_v1(path, attested, bootstrap)
    second = migrate_activation_schema_v1(path, attested, bootstrap)

    assert first.verify_durable() is True
    assert second.verify_durable() is True
    assert provider.value == 1
    with sqlite3.connect(path) as q:
        assert classify_activation_schema_provenance_locked(q) == "COMPLETE"
        assert q.execute(
            "SELECT COUNT(*) FROM shared_anchor_intents WHERE intent_id=?",
            (MIGRATION_INTENT_ID,),
        ).fetchone()[0] == 1
