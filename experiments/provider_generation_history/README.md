# LAB-081 — provider generation history

This experiment separates two authorities that LAB-080 deliberately conflated:

- **current effect authority** — only the active provider generation may create new anchor effects;
- **historical verification authority** — prior authenticated generations may verify receipts they originally produced, but cannot create new effects through the supported shared-ledger surface.

The integrated supported surface is `SupportedHistoricalSharedAnchorLedger`. It uses the exact LAB-080 SQLite database as the serialization boundary: reservation and provider rotation read/update the same durable provider head under `BEGIN IMMEDIATE`, and provider rotation is blocked while any shared-anchor intent is `PREPARED`.

Each CONFIRMED ledger row has immutable signed historical receipt evidence bound to provider ID, generation, position and request ID. The stable receipt identity intentionally excludes the fresh reconciliation challenge. Repeated current-head checks therefore do not rewrite historical receipt evidence.

Restart verification checks provider-generation continuity, historical receipt signatures, ledger rows and component watermarks inside one consistent SQL read transaction. The integrated provider-history object blocks its standalone `rotate()` method so callers cannot bypass the shared-ledger coordinator.

Run the isolated and integration suites:

```bash
python -m unittest experiments.provider_generation_history.tests.test_protocol -v
python -m unittest experiments.provider_generation_history.tests.test_integration -v
```

This remains a reference model. Its HMAC keys model authenticated provider generations and are not a claim of production HSM/PKI key custody or cryptographic read-only key separation. Production historical verification should use verification-only public material. The experiment also does not provide provider consensus, cross-provider failover, or atomicity between an external provider's own rotation and the local SQL commit.
