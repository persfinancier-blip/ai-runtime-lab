"""Compatibility check across LAB-099 frozen DDL, vectors, and schema oracle.

Test-only, side-effect free, and non-SQL-mutating. It proves that the exact frozen
literal DDL hashes to the relation-definition digest carried by PREPARED/CONFIRMED
reference vectors and that those vectors map onto the schema-identity verifier boundary.
"""

from __future__ import annotations

from lab099_precursor_reference_vectors import (
    CONFIRMED_DIGEST,
    CONFIRMED_REFERENCE_VALUES,
    FROZEN_RELATION_DEFINITION_DIGEST,
    PREPARED_DIGEST,
    PREPARED_REFERENCE_VALUES,
    RESULTING_PROVENANCE_HEAD_DIGEST,
    validate_reference_vectors,
)
from lab099_precursor_relation_reference import (
    FROZEN_RELATION_DEFINITION_DIGEST as DDL_RELATION_DEFINITION_DIGEST,
    relation_definition_digest,
    validate_precursor_relation_reference,
)
from lab099_schema_identity_reference import (
    ConfirmedSchemaIdentity,
    CurrentSchemaIdentity,
    PreparedSchemaIdentity,
    verify_schema_identity_boundary,
)


def validate_schema_vector_compatibility() -> bool:
    if validate_precursor_relation_reference() is not True:
        raise AssertionError("literal DDL reference did not validate")
    if validate_reference_vectors() is not True:
        raise AssertionError("authority reference vectors did not validate")
    if relation_definition_digest() != FROZEN_RELATION_DEFINITION_DIGEST:
        raise AssertionError("literal DDL digest differs from vector authority")
    if DDL_RELATION_DEFINITION_DIGEST != FROZEN_RELATION_DEFINITION_DIGEST:
        raise AssertionError("DDL and vector frozen digest constants disagree")

    prepared = PreparedSchemaIdentity(
        logical_database_identity_digest=PREPARED_REFERENCE_VALUES[1],
        predecessor_lab092_completion_digest=PREPARED_REFERENCE_VALUES[2],
        predecessor_provenance_head_digest=PREPARED_REFERENCE_VALUES[3],
        predecessor_epoch=PREPARED_REFERENCE_VALUES[4],
        relation_definition_digest=PREPARED_REFERENCE_VALUES[7],
        prepared_event_digest=PREPARED_DIGEST,
    )
    if prepared.relation_definition_digest != FROZEN_RELATION_DEFINITION_DIGEST:
        raise AssertionError("PREPARED relation-definition digest mapping drift")

    current_prepared = CurrentSchemaIdentity(
        logical_database_identity_digest=PREPARED_REFERENCE_VALUES[1],
        lab092_completion_digest=PREPARED_REFERENCE_VALUES[2],
        provenance_head_digest=PREPARED_REFERENCE_VALUES[3],
        provenance_epoch=PREPARED_REFERENCE_VALUES[4],
        observed_relation_definition_digest=relation_definition_digest(),
    )
    if verify_schema_identity_boundary(
        current_prepared, prepared=prepared, confirmed=None
    ) != "PREPARED_INCOMPLETE":
        raise AssertionError("PREPARED vector fields do not map to schema oracle")

    if CONFIRMED_REFERENCE_VALUES[1] != PREPARED_REFERENCE_VALUES[1]:
        raise AssertionError("CONFIRMED logical database identity drift")
    if CONFIRMED_REFERENCE_VALUES[2] != PREPARED_DIGEST:
        raise AssertionError("CONFIRMED no longer binds exact PREPARED digest")
    if CONFIRMED_REFERENCE_VALUES[3] != PREPARED_REFERENCE_VALUES[2]:
        raise AssertionError("CONFIRMED LAB-092 completion lineage drift")
    if CONFIRMED_REFERENCE_VALUES[6] != FROZEN_RELATION_DEFINITION_DIGEST:
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
        observed_relation_definition_digest=relation_definition_digest(),
    )
    if verify_schema_identity_boundary(
        current_confirmed, prepared=prepared, confirmed=confirmed
    ) != "CONFIRMED":
        raise AssertionError("CONFIRMED vector fields do not map to schema oracle")

    return True


if __name__ == "__main__":
    assert validate_schema_vector_compatibility()
