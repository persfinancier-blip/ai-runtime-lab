"""Independent literal-DDL identity oracle for LAB-099 precursor relation V1.

Test-only and side-effect free. This module does not create or mutate SQLite state.
It freezes the exact physical relation spelling already selected by the durable
LAB099_PRECURSOR_PHYSICAL_RELATION_V1_FROZEN contract.
"""

from __future__ import annotations

import hashlib

PRECURSOR_RELATION_NAME = "provider_activation_reservation_precursors"

PRECURSOR_RELATION_DDL_V1 = """CREATE TABLE provider_activation_reservation_precursors(
  activation_id TEXT PRIMARY KEY,
  logical_database_identity_digest TEXT NOT NULL,
  parent_chain_link_digest TEXT NOT NULL,
  parent_epoch INTEGER NOT NULL,
  old_generation_id TEXT NOT NULL,
  new_generation_id TEXT NOT NULL,
  successor_provider_id TEXT NOT NULL,
  successor_generation INTEGER NOT NULL,
  successor_key_id TEXT NOT NULL,
  expected_position INTEGER NOT NULL,
  protocol_version INTEGER NOT NULL CHECK(protocol_version=1),
  predecessor_mac TEXT NOT NULL,
  successor_mac TEXT NOT NULL,
  UNIQUE(logical_database_identity_digest,parent_chain_link_digest,parent_epoch)
)"""

FROZEN_RELATION_DEFINITION_DIGEST = bytes.fromhex(
    "696c54d1afdef52c05c120ce7d09a7a2eeb567daafb3a378b7dc4ca64f80e3bb"
)


def normalized_sql(sql: str) -> str:
    if type(sql) is not str:
        raise TypeError("exact str DDL required")
    return " ".join(sql.split())


def relation_definition_digest(sql: str = PRECURSOR_RELATION_DDL_V1) -> bytes:
    return hashlib.sha256(normalized_sql(sql).encode("utf-8", errors="strict")).digest()


def validate_precursor_relation_reference() -> bool:
    if relation_definition_digest() != FROZEN_RELATION_DEFINITION_DIGEST:
        raise AssertionError("LAB-099 precursor V1 literal DDL digest drift")
    if PRECURSOR_RELATION_NAME not in PRECURSOR_RELATION_DDL_V1:
        raise AssertionError("LAB-099 precursor relation name missing from literal DDL")
    return True


if __name__ == "__main__":
    assert validate_precursor_relation_reference()
