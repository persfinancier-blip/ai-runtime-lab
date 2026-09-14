from __future__ import annotations

import sqlite3

import pytest

from experiments.mutable_shared_anchor_writer.adoption_schema_domains import (
    AdoptionSchemaDomainError,
    validate_required_not_null_contract,
)


def _schema(*, receipt_generation_type="INTEGER", nullable_stable_binding=False):
    q = sqlite3.connect(":memory:", isolation_level=None)
    stable_binding = "TEXT" if nullable_stable_binding else "TEXT NOT NULL"
    q.executescript(
        f"""
        CREATE TABLE shared_anchor_meta(
          singleton INTEGER PRIMARY KEY CHECK(singleton=1),
          reserved_position INTEGER NOT NULL CHECK(reserved_position>=0)
        );
        CREATE TABLE shared_anchor_intents(
          intent_id TEXT PRIMARY KEY,
          component_id TEXT NOT NULL,
          intent_type TEXT NOT NULL,
          payload_digest TEXT NOT NULL,
          provider_id TEXT NOT NULL,
          provider_generation INTEGER NOT NULL,
          predecessor_position INTEGER NOT NULL,
          position INTEGER NOT NULL UNIQUE,
          request_id TEXT NOT NULL UNIQUE,
          status TEXT NOT NULL CHECK(status IN ('PREPARED','CONFIRMED')),
          receipt_binding TEXT
        );
        CREATE TABLE component_anchor_watermarks(
          component_id TEXT PRIMARY KEY,
          position INTEGER NOT NULL CHECK(position>=0)
        );
        CREATE TABLE asymmetric_provider_receipts(
          request_id TEXT PRIMARY KEY,
          provider_id TEXT NOT NULL,
          generation {receipt_generation_type} NOT NULL,
          position INTEGER NOT NULL,
          kind TEXT NOT NULL,
          challenge TEXT NOT NULL,
          signature TEXT NOT NULL,
          stable_binding {stable_binding}
        );
        """
    )
    q.execute("BEGIN IMMEDIATE")
    return q


def test_canonical_receipt_schema_is_accepted():
    q = _schema()
    try:
        assert validate_required_not_null_contract(q) is True
    finally:
        q.rollback()
        q.close()


def test_legacy_receipt_generation_text_affinity_is_rejected():
    q = _schema(receipt_generation_type="TEXT")
    try:
        with pytest.raises(AdoptionSchemaDomainError, match="asymmetric_provider_receipts"):
            validate_required_not_null_contract(q)
    finally:
        q.rollback()
        q.close()


def test_legacy_receipt_nullable_binding_is_rejected():
    q = _schema(nullable_stable_binding=True)
    try:
        with pytest.raises(AdoptionSchemaDomainError, match="stable_binding"):
            validate_required_not_null_contract(q)
    finally:
        q.rollback()
        q.close()


def test_sqlite_applies_receipt_affinity_before_before_insert_trigger():
    q = sqlite3.connect(":memory:", isolation_level=None)
    observed = []
    q.create_function("capture_generation", 1, lambda value: observed.append(value) or 1)
    q.executescript(
        """
        CREATE TABLE asymmetric_provider_receipts(
          request_id TEXT PRIMARY KEY,
          provider_id TEXT NOT NULL,
          generation TEXT NOT NULL,
          position INTEGER NOT NULL,
          kind TEXT NOT NULL,
          challenge TEXT NOT NULL,
          signature TEXT NOT NULL,
          stable_binding TEXT NOT NULL
        );
        CREATE TRIGGER capture_receipt_generation
        BEFORE INSERT ON asymmetric_provider_receipts
        BEGIN
          SELECT capture_generation(NEW.generation);
        END;
        """
    )
    try:
        q.execute(
            "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
            ("req", "provider", 1, 1, "RECONCILE", "challenge", "signature", "binding"),
        )
        assert observed == ["1"]
    finally:
        q.close()
