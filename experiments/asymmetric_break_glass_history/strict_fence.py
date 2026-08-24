from __future__ import annotations

PUBLIC_MUTATION_TRIGGER_NAMES = (
    "lab086_public_authority_requires_current_authorization",
    "lab086_public_authority_is_immutable",
    "lab086_public_authority_is_not_deletable",
    "lab086_public_transition_requires_current_authorization",
    "lab086_public_transition_is_immutable",
    "lab086_public_transition_is_not_deletable",
    "lab086_public_head_insert_requires_current_authorization",
    "lab086_public_head_requires_current_authorization",
    "lab086_public_head_is_not_deletable",
)

# Lower LAB-083/LAB-082 writers are valid before the LAB-086 cutoff, but after
# migration they must not create a new consequential successor without the final
# LAB-086 pre/post full-history verification. Fence their canonical write points
# at SQL level so direct use of the lower controller/supported surface rolls back.
INHERITED_MUTATION_TRIGGERS = {
    "provider_rotation_authority_transitions": "lab086_normal_root_transition_requires_final_writer",
    "provider_rotation_threshold_proofs": "lab086_provider_threshold_proof_requires_final_writer",
    "asymmetric_provider_transitions": "lab086_provider_transition_requires_final_writer",
}

# Those same rows are authenticated historical evidence after cutoff.  Prevent
# ordinary DML from rewriting or deleting an already committed proof/transition;
# otherwise a stale/raw-DML path can create persistent fail-closed state that is
# noticed only by the next verifier.  Arbitrary schema/DDL control is a separate
# trust-boundary question (LAB-087), but the LAB-086 DML fence is complete.
INHERITED_HISTORY_IMMUTABILITY_TRIGGERS = {
    "provider_rotation_authority_transitions": (
        "lab086_normal_root_transition_is_immutable",
        "lab086_normal_root_transition_is_not_deletable",
    ),
    "provider_rotation_threshold_proofs": (
        "lab086_provider_threshold_proof_is_immutable",
        "lab086_provider_threshold_proof_is_not_deletable",
    ),
    "asymmetric_provider_transitions": (
        "lab086_provider_transition_is_immutable",
        "lab086_provider_transition_is_not_deletable",
    ),
}

# The authoritative root-head row needs all three DML operations fenced. SQLite
# INSERT OR REPLACE is not an UPDATE and can otherwise replace the singleton row;
# DELETE can remove it outright. Final writers temporarily remove all three only
# after full pre-verification in the same BEGIN IMMEDIATE transaction.
ROOT_HEAD_MUTATION_TRIGGER_NAMES = (
    "lab086_root_head_insert_requires_final_writer",
    "lab086_root_head_requires_final_writer",
    "lab086_root_head_delete_requires_final_writer",
)

# Historical names from earlier LAB-086 candidates. They must be removed because
# their proof-row predicates treated unauthenticated durable data as capability.
OBSOLETE_PUBLIC_MUTATION_TRIGGER_NAMES = (
    "lab086_public_authority_requires_root_proof",
    "lab086_public_transition_requires_root_proof",
    "lab086_public_head_requires_root_proof",
)


def _table_names(q):
    return {
        row[0]
        for row in q.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }


def _all_inherited_trigger_names():
    names = list(INHERITED_MUTATION_TRIGGERS.values())
    for pair in INHERITED_HISTORY_IMMUTABILITY_TRIGGERS.values():
        names.extend(pair)
    return tuple(names)


def remove_public_mutation_fence_locked(q):
    for name in (
        *PUBLIC_MUTATION_TRIGGER_NAMES,
        *_all_inherited_trigger_names(),
        *ROOT_HEAD_MUTATION_TRIGGER_NAMES,
        *OBSOLETE_PUBLIC_MUTATION_TRIGGER_NAMES,
    ):
        q.execute(f"DROP TRIGGER IF EXISTS {name}")


def _install_history_immutability(q, table, update_name, delete_name, label):
    q.execute(
        f"""CREATE TRIGGER {update_name}
        BEFORE UPDATE ON {table}
        WHEN EXISTS(
          SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
        )
        BEGIN
          SELECT RAISE(ABORT,'LAB-086 {label} is immutable after cutoff');
        END"""
    )
    q.execute(
        f"""CREATE TRIGGER {delete_name}
        BEFORE DELETE ON {table}
        WHEN EXISTS(
          SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
        )
        BEGIN
          SELECT RAISE(ABORT,'LAB-086 {label} cannot be deleted after cutoff');
        END"""
    )


def install_public_mutation_fence_locked(q):
    """Install unconditional post-cutoff deny policy for underlying writers.

    A durable proof row is evidence, never mutation authority. The final supported
    writer may temporarily remove these triggers only while it owns the same
    ``BEGIN IMMEDIATE`` transaction *after* all relevant cryptographic/history
    checks have passed. SQLite DDL is transactional, so rollback/crash restores the
    pre-transaction fence.

    The inherited-writer triggers fence both new canonical writes and mutation of
    already authenticated historical proof/transition rows. The root-head singleton
    is fenced on INSERT/UPDATE/DELETE so conflict algorithms such as INSERT OR
    REPLACE cannot bypass the update guard. If a stale/direct writer attempts any of
    those operations, the transaction aborts and preceding writes roll back.
    Tables are discovered dynamically so the isolated strict-fence fixture remains
    usable; on the real LAB-086 schema they are required by
    ``assert_public_mutation_fence_locked``.
    """
    remove_public_mutation_fence_locked(q)
    q.execute(
        """CREATE TRIGGER lab086_public_authority_requires_current_authorization
        BEFORE INSERT ON provider_recovery_public_authorities
        WHEN EXISTS(
          SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
        )
        BEGIN
          SELECT RAISE(ABORT,'LAB-086 public recovery authority mutation requires final supported writer');
        END"""
    )
    q.execute(
        """CREATE TRIGGER lab086_public_authority_is_immutable
        BEFORE UPDATE ON provider_recovery_public_authorities
        WHEN EXISTS(
          SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
        )
        BEGIN
          SELECT RAISE(ABORT,'LAB-086 public recovery authorities are immutable after cutoff');
        END"""
    )
    q.execute(
        """CREATE TRIGGER lab086_public_authority_is_not_deletable
        BEFORE DELETE ON provider_recovery_public_authorities
        WHEN EXISTS(
          SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
        )
        BEGIN
          SELECT RAISE(ABORT,'LAB-086 public recovery authorities cannot be deleted after cutoff');
        END"""
    )
    q.execute(
        """CREATE TRIGGER lab086_public_transition_requires_current_authorization
        BEFORE INSERT ON provider_recovery_public_transitions
        WHEN EXISTS(
          SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
        )
        BEGIN
          SELECT RAISE(ABORT,'LAB-086 public recovery transition mutation requires final supported writer');
        END"""
    )
    q.execute(
        """CREATE TRIGGER lab086_public_transition_is_immutable
        BEFORE UPDATE ON provider_recovery_public_transitions
        WHEN EXISTS(
          SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
        )
        BEGIN
          SELECT RAISE(ABORT,'LAB-086 public recovery transitions are immutable after cutoff');
        END"""
    )
    q.execute(
        """CREATE TRIGGER lab086_public_transition_is_not_deletable
        BEFORE DELETE ON provider_recovery_public_transitions
        WHEN EXISTS(
          SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
        )
        BEGIN
          SELECT RAISE(ABORT,'LAB-086 public recovery transitions cannot be deleted after cutoff');
        END"""
    )
    q.execute(
        """CREATE TRIGGER lab086_public_head_insert_requires_current_authorization
        BEFORE INSERT ON provider_recovery_public_head
        WHEN EXISTS(
          SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
        )
        BEGIN
          SELECT RAISE(ABORT,'LAB-086 public recovery head insertion requires final supported writer');
        END"""
    )
    q.execute(
        """CREATE TRIGGER lab086_public_head_requires_current_authorization
        BEFORE UPDATE ON provider_recovery_public_head
        WHEN EXISTS(
          SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
        )
        BEGIN
          SELECT RAISE(ABORT,'LAB-086 public recovery head mutation requires final supported writer');
        END"""
    )
    q.execute(
        """CREATE TRIGGER lab086_public_head_is_not_deletable
        BEFORE DELETE ON provider_recovery_public_head
        WHEN EXISTS(
          SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
        )
        BEGIN
          SELECT RAISE(ABORT,'LAB-086 public recovery head cannot be deleted after cutoff');
        END"""
    )

    tables = _table_names(q)
    if "provider_rotation_authority_transitions" in tables:
        q.execute(
            """CREATE TRIGGER lab086_normal_root_transition_requires_final_writer
            BEFORE INSERT ON provider_rotation_authority_transitions
            WHEN EXISTS(
              SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
            )
            BEGIN
              SELECT RAISE(ABORT,'LAB-086 normal root rotation requires final supported writer');
            END"""
        )
        _install_history_immutability(
            q,
            "provider_rotation_authority_transitions",
            *INHERITED_HISTORY_IMMUTABILITY_TRIGGERS["provider_rotation_authority_transitions"],
            "normal root transition history",
        )
    if "provider_rotation_threshold_proofs" in tables:
        q.execute(
            """CREATE TRIGGER lab086_provider_threshold_proof_requires_final_writer
            BEFORE INSERT ON provider_rotation_threshold_proofs
            WHEN EXISTS(
              SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
            )
            BEGIN
              SELECT RAISE(ABORT,'LAB-086 provider rotation requires final supported writer');
            END"""
        )
        _install_history_immutability(
            q,
            "provider_rotation_threshold_proofs",
            *INHERITED_HISTORY_IMMUTABILITY_TRIGGERS["provider_rotation_threshold_proofs"],
            "provider threshold proof history",
        )
    if "asymmetric_provider_transitions" in tables:
        q.execute(
            """CREATE TRIGGER lab086_provider_transition_requires_final_writer
            BEFORE INSERT ON asymmetric_provider_transitions
            WHEN EXISTS(
              SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
            )
            BEGIN
              SELECT RAISE(ABORT,'LAB-086 provider transition requires final supported writer');
            END"""
        )
        _install_history_immutability(
            q,
            "asymmetric_provider_transitions",
            *INHERITED_HISTORY_IMMUTABILITY_TRIGGERS["asymmetric_provider_transitions"],
            "provider transition history",
        )
    if "provider_rotation_authority_head" in tables:
        q.execute(
            """CREATE TRIGGER lab086_root_head_insert_requires_final_writer
            BEFORE INSERT ON provider_rotation_authority_head
            WHEN EXISTS(
              SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
            )
            BEGIN
              SELECT RAISE(ABORT,'LAB-086 root head insertion requires final supported writer');
            END"""
        )
        q.execute(
            """CREATE TRIGGER lab086_root_head_requires_final_writer
            BEFORE UPDATE ON provider_rotation_authority_head
            WHEN EXISTS(
              SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
            )
            BEGIN
              SELECT RAISE(ABORT,'LAB-086 root head mutation requires final supported writer');
            END"""
        )
        q.execute(
            """CREATE TRIGGER lab086_root_head_delete_requires_final_writer
            BEFORE DELETE ON provider_rotation_authority_head
            WHEN EXISTS(
              SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
            )
            BEGIN
              SELECT RAISE(ABORT,'LAB-086 root head deletion requires final supported writer');
            END"""
        )


def assert_public_mutation_fence_locked(q):
    names = {
        row[0]
        for row in q.execute(
            "SELECT name FROM sqlite_master WHERE type='trigger'"
        ).fetchall()
    }
    missing = set(PUBLIC_MUTATION_TRIGGER_NAMES) - names
    tables = _table_names(q)
    inherited_required = {
        trigger
        for table, trigger in INHERITED_MUTATION_TRIGGERS.items()
        if table in tables
    }
    for table, pair in INHERITED_HISTORY_IMMUTABILITY_TRIGGERS.items():
        if table in tables:
            inherited_required.update(pair)
    missing |= inherited_required - names
    if "provider_rotation_authority_head" in tables:
        missing |= set(ROOT_HEAD_MUTATION_TRIGGER_NAMES) - names
    obsolete = set(OBSOLETE_PUBLIC_MUTATION_TRIGGER_NAMES) & names
    if missing or obsolete:
        raise RuntimeError(
            f"LAB-086 public mutation fence mismatch missing={sorted(missing)} obsolete={sorted(obsolete)}"
        )
    return True
