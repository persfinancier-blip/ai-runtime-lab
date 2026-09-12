"""Non-SQL compatibility check between LAB-099 frozen reference layers.

This test-only module composes the independent byte-exact authority vectors with the
side-effect-free schema-identity oracle. It deliberately does not define precursor SQL,
mutation plans, production APIs, or discoverable ``test_*`` cases.

Its only claim is that fields already frozen in the PREPARED/CONFIRMED reference vectors
map exactly onto the schema-identity verifier boundary.
"""

from __future__ import annotations

from lab099_precursor_reference_vectors import (
    CONFIRMED_DIGEST,
    CONFIRMED_REFERENCE_VALUES,
    PREPARED_DIGEST,
    PREPARED_REFERENCE_VALUES,
    REFERENCE_ONLY_RELATION_DEFINITION_DIGEST,
    RESULTING_PROVENANCE_HEAD_DIGEST,
    validate_reference_vectors,
)
from lab099_schema_identity_reference import (
    ConfirmedSchemaIdentity,
    CurrentSchemaIdentity,
    PreparedSchemaIdentity,
    verify_schema_identity_boundary,
)


def validate_schema_vector_compatibility() -> bool:
    """Prove exact field compatibility without selecting physical SQLite DDL."""

    if validate_reference_vectors() is not True:
        raise AssertionError("authority reference vectors did not validate")

    prepared = PreparedSchemaIdentity(
        logical_database_identity_digest=PREPARED_REFERENCE_VALUES[1],
        predecessor_lab092_completion_digest=PREPARED_REFERENCE_VALUES[2],
        predecessor_provenance_head_digest=PREPARED_REFERENCE_VALUES[3],
        predecessor_epoch=PREPARED_REFERENCE_VALUES[4],
        relation_definition_digest=PREPARED_REFERENCE_VALUES[7],
        prepared_event_digest=PREPARED_DIGEST,
    )

    if prepared.relation_definition_digest != REFERENCE_ONLY_RELATION_DEFINITION_DIGEST:
        raise AssertionError("PREPARED relation-definition digest mapping drift")

    current_prepared = CurrentSchemaIdentity(
        logical_database_identity_digest=PREPARED_REFERENCE_VALUES[1],
        lab092_completion_digest=PREPARED_REFERENCE_VALUES[2],
        provenance_head_digest=PREPARED_REFERENCE_VALUES[3],
        provenance_epoch=PREPARED_REFERENCE_VALUES[4],
        observed_relation_definition_digest=PREPARED_REFERENCE_VALUES[7],
    )
    if (
        verify_schema_identity_boundary(
            current_prepared,
            prepared=prepared,
            confirmed=None,
        )
        != "PREPARED_INCOMPLETE"
    ):
        raise AssertionError("PREPARED vector fields do not map to schema oracle")

    if CONFIRMED_REFERENCE_VALUES[1] != PREPARED_REFERENCE_VALUES[1]:
        raise AssertionError("CONFIRMED logical database identity drift")
    if CONFIRMED_REFERENCE_VALUES[2] != PREPARED_DIGEST:
        raise AssertionError("CONFIRMED no longer binds exact PREPARED digest")
    if CONFIRMED_REFERENCE_VALUES[3] != PREPARED_REFERENCE_VALUES[2]:
        raise AssertionError("CONFIRMED LAB-092 completion lineage drift")
    if CONFIRMED_REFERENCE_VALUES[6] != PREPARED_REFERENCE_VALUES[7]:
        raise AssertionError("CONFIRMED relation-definition digest drift")
    if CONFIRMED_REFERENCE_VALUES[7] != RESULTING_PROVENANCE_HEAD_DIGEST:
        raise AssertionError("CONFIRMED resulting provenance head mapping drift")

    confirmed = ConfirmedSchemaIdentity(
        logical_database_identity_digest=CONFIRMED_REFERENCE_VALUES[1],
        prepared_event_digest=CONFIRMED_REFERENCE_VALUES[2],
        relation_definition_digest=CONFIRMED_REFERENCE_VALUES[6],
        resulting_provenance_head_digest=CONFIRMED_REFERENCE_VALUES[7],
        resulting_epoch=CONFIRMED_REFERENCE_VALUES[8],
        confirmed_event_digest=CONFIRMED_DIGEST,
    )
    current_confirmed = CurrentSchemaIdentity(
        logical_database_identity_digest=CONFIRMED_REFERENCE_VALUES[1],
        lab092_completion_digest=CONFIRMED_REFERENCE_VALUES[3],
        provenance_head_digest=CONFIRMED_REFERENCE_VALUES[7],
        provenance_epoch=CONFIRMED_REFERENCE_VALUES[8],
        observed_relation_definition_digest=CONFIRMED_REFERENCE_VALUES[6],
    )
    if (
        verify_schema_identity_boundary(
            current_confirmed,
            prepared=prepared,
            confirmed=confirmed,
        )
        != "CONFIRMED"
    ):
        raise AssertionError("CONFIRMED vector fields do not map to schema oracle")

    return True


if __name__ == "__main__":
    assert validate_schema_vector_compatibility()
