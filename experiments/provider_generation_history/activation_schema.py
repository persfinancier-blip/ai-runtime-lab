from __future__ import annotations

"""Immutable LAB-090 activation schema definitions.

This module owns only names, exact SQLite DDL, and SQL normalization used to
classify the provider-activation schema. It deliberately owns no ledger,
provider, connection, rotation, receipt, or mutation authority.
"""

ACTIVATION_TABLE_NAME = "provider_generation_activations"
ACTIVATION_TABLE_SQL = """CREATE TABLE provider_generation_activations(
  activation_id TEXT PRIMARY KEY,
  new_generation_id TEXT NOT NULL UNIQUE,
  provider_id TEXT NOT NULL,
  generation INTEGER NOT NULL,
  expected_position INTEGER NOT NULL,
  fence INTEGER NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('SQL_COMMITTED','COMMITTED'))
)"""
ACTIVATION_TRIGGER_NAME = "block_intent_during_provider_activation"
ACTIVATION_TRIGGER_SQL = """CREATE TRIGGER block_intent_during_provider_activation
BEFORE INSERT ON shared_anchor_intents
WHEN EXISTS(
  SELECT 1 FROM provider_generation_activations WHERE status='SQL_COMMITTED'
)
BEGIN
  SELECT RAISE(ABORT, 'provider activation unresolved');
END"""


def normalized_sql(sql: str) -> str:
    return " ".join(sql.split())
