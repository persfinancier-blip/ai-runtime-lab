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

# Those same rows are authenticated historical evidence after cutoff. Prevent
# ordinary DML from rewriting or deleting an already committed proof/transition;
# otherwise a stale/raw-DML path can create persistent fail-closed state that is
# noticed only by the next verifier. Arbitrary schema/DDL control is a separate
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

# The migration projection is the authenticated replacement for historical HMAC
# authority after cutoff. Every SQL row whose semantics are committed by that
# projection must therefore be frozen against ordinary DML. Four legacy tables
# are updated once *inside the cutoff transaction* to scrub HMAC material; their
# UPDATE guards permit only that canonical scrub while requiring every semantic
# field to stay identical. All other projected rows are fully immutable.
LEGACY_PROJECTION_FREEZE_TRIGGERS = {
    "provider_rotation_recovery_transitions": (
        "lab086_legacy_recovery_transition_no_insert",
        "lab086_legacy_recovery_transition_semantics_immutable",
        "lab086_legacy_recovery_transition_no_delete",
    ),
    "provider_rotation_recovery_authorities": (
        "lab086_compat_recovery_authority_no_insert",
        "lab086_compat_recovery_authority_semantics_immutable",
        "lab086_compat_recovery_authority_no_delete",
    ),
    "provider_rotation_recovery_head": (
        "lab086_compat_recovery_head_no_insert",
        "lab086_compat_recovery_head_immutable",
        "lab086_compat_recovery_head_no_delete",
    ),
    "provider_recovery_lifecycle_authorities": (
        "lab086_lifecycle_authority_no_insert",
        "lab086_lifecycle_authority_semantics_immutable",
        "lab086_lifecycle_authority_no_delete",
    ),
    "provider_recovery_lifecycle_head": (
        "lab086_lifecycle_head_no_insert",
        "lab086_lifecycle_head_immutable",
        "lab086_lifecycle_head_no_delete",
    ),
    "provider_recovery_lifecycle_transitions": (
        "lab086_lifecycle_transition_no_insert",
        "lab086_lifecycle_transition_semantics_immutable",
        "lab086_lifecycle_transition_no_delete",
    ),
    "provider_recovery_custody_bindings": (
        "lab086_custody_binding_no_insert",
        "lab086_custody_binding_immutable",
        "lab086_custody_binding_no_delete",
    ),
    "provider_rotation_recovery_custody_proofs": (
        "lab086_custody_proof_no_insert",
        "lab086_custody_proof_immutable",
        "lab086_custody_proof_no_delete",
    ),
    "provider_recovery_custody_enablement": (
        "lab086_custody_enablement_no_insert",
        "lab086_custody_enablement_immutable",
        "lab086_custody_enablement_no_delete",
    ),
    "provider_recovery_custody_enablement_proof": (
        "lab086_custody_enablement_proof_no_insert",
        "lab086_custody_enablement_proof_immutable",
        "lab086_custody_enablement_proof_no_delete",
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

# Current authority tables need a split policy. Creating the next root/provider
# generation and moving the provider head are final-writer operations, so those
# guards are transactionally thawed. Existing authority rows and the threshold
# enablement singleton are historical trust state and stay immutable even while
# the final writer owns its BEGIN IMMEDIATE transaction.
CURRENT_AUTHORITY_WRITER_TRIGGER_NAMES = (
    "lab086_root_authority_insert_requires_final_writer",
    "lab086_provider_generation_insert_requires_final_writer",
    "lab086_provider_head_insert_requires_final_writer",
    "lab086_provider_head_update_requires_final_writer",
    "lab086_provider_head_delete_requires_final_writer",
)

CURRENT_AUTHORITY_HISTORY_TRIGGERS = {
    "provider_rotation_authorities": (
        "lab086_root_authority_is_immutable",
        "lab086_root_authority_is_not_deletable",
    ),
    "asymmetric_provider_generations": (
        "lab086_provider_generation_is_immutable",
        "lab086_provider_generation_is_not_deletable",
    ),
}

THRESHOLD_ENABLEMENT_FREEZE_TRIGGER_NAMES = (
    "lab086_threshold_enablement_no_insert",
    "lab086_threshold_enablement_is_immutable",
    "lab086_threshold_enablement_is_not_deletable",
)

# The three authenticated cutoff singletons are themselves durable trust metadata.
# Once a complete cutoff exists, ordinary DML must not rewrite/delete/replace any
# of them and thereby turn a previously valid history into a persistent fail-closed
# restart.  The triggers become active only after all three singleton rows exist,
# so the first atomic migration ceremony can keep its existing
# projection -> boundary -> root-proof insertion order.
MIGRATION_METADATA_FENCE_TRIGGERS = {
    "provider_asymmetric_break_glass_boundary": (
        "lab086_migration_boundary_no_insert",
        "lab086_migration_boundary_is_immutable",
        "lab086_migration_boundary_no_delete",
    ),
    "provider_asymmetric_break_glass_legacy_projection": (
        "lab086_migration_projection_no_insert",
        "lab086_migration_projection_is_immutable",
        "lab086_migration_projection_no_delete",
    ),
    "provider_asymmetric_break_glass_root_proof": (
        "lab086_migration_root_proof_no_insert",
        "lab086_migration_root_proof_is_immutable",
        "lab086_migration_root_proof_no_delete",
    ),
}

# Historical names from earlier LAB-086 candidates. They must be removed because
# their proof-row predicates treated unauthenticated durable data as capability.
OBSOLETE_PUBLIC_MUTATION_TRIGGER_NAMES = (
    "lab086_public_authority_requires_root_proof",
    "lab086_public_transition_requires_root_proof",
    "lab086_public_head_requires_root_proof",
)

# These tables contain evidence that is meaningful only after the authenticated
# LAB-086 cutoff exists. A row in either table before the cutoff is an impossible
# partial state for every supported transaction. Allowing migration to proceed over
# it converts pre-existing debris into a guaranteed post-cutoff restart failure.
POST_CUTOFF_ONLY_EVIDENCE_TABLES = (
    "provider_asymmetric_break_glass_proofs",
    "provider_asymmetric_recovery_public_root_proofs",
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


def _all_legacy_projection_trigger_names():
    return tuple(
        name
        for names in LEGACY_PROJECTION_FREEZE_TRIGGERS.values()
        for name in names
    )


def _all_current_authority_history_trigger_names():
    names = []
    for pair in CURRENT_AUTHORITY_HISTORY_TRIGGERS.values():
        names.extend(pair)
    names.extend(THRESHOLD_ENABLEMENT_FREEZE_TRIGGER_NAMES)
    return tuple(names)


def _all_migration_metadata_trigger_names():
    return tuple(
        name
        for names in MIGRATION_METADATA_FENCE_TRIGGERS.values()
        for name in names
    )


def _assert_no_pre_cutoff_post_cutoff_evidence_locked(q):
    tables = _table_names(q)
    if "provider_asymmetric_break_glass_boundary" not in tables:
        return True
    boundary = q.execute(
        "SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1"
    ).fetchone()
    if boundary is not None:
        return True
    for table in POST_CUTOFF_ONLY_EVIDENCE_TABLES:
        if table not in tables:
            continue
        if q.execute(f"SELECT 1 FROM {table} LIMIT 1").fetchone() is not None:
            raise RuntimeError(
                f"LAB-086 orphan post-cutoff evidence exists before migration in {table}"
            )
    return True


def remove_public_mutation_fence_locked(q):
    # Legacy-projection and current-authority history freeze triggers are
    # intentionally *not* removed here. Final post-cutoff writers never need to
    # rewrite an already authenticated authority row or threshold enablement.
    for name in (
        *PUBLIC_MUTATION_TRIGGER_NAMES,
        *_all_inherited_trigger_names(),
        *ROOT_HEAD_MUTATION_TRIGGER_NAMES,
        *CURRENT_AUTHORITY_WRITER_TRIGGER_NAMES,
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


def _create_legacy_deny_insert_delete(q, table, names, label):
    insert_name, _, delete_name = names
    q.execute(
        f"""CREATE TRIGGER {insert_name}
        BEFORE INSERT ON {table}
        WHEN EXISTS(
          SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
        )
        BEGIN
          SELECT RAISE(ABORT,'LAB-086 {label} cannot be inserted after cutoff');
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


def _create_legacy_deny_update(q, table, name, label):
    q.execute(
        f"""CREATE TRIGGER {name}
        BEFORE UPDATE ON {table}
        WHEN EXISTS(
          SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
        )
        BEGIN
          SELECT RAISE(ABORT,'LAB-086 {label} is immutable after cutoff');
        END"""
    )


def _install_legacy_projection_freeze_locked(q):
    tables = _table_names(q)
    for name in _all_legacy_projection_trigger_names():
        q.execute(f"DROP TRIGGER IF EXISTS {name}")

    # Legacy recovery transition: the migration may only erase HMAC signatures.
    table = "provider_rotation_recovery_transitions"
    if table in tables:
        names = LEGACY_PROJECTION_FREEZE_TRIGGERS[table]
        _create_legacy_deny_insert_delete(q, table, names, "legacy recovery transition")
        q.execute(
            f"""CREATE TRIGGER {names[1]}
            BEFORE UPDATE ON {table}
            WHEN EXISTS(SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1)
             AND NOT (
               NEW.new_rotation_authority_id IS OLD.new_rotation_authority_id AND
               NEW.old_rotation_authority_id IS OLD.old_rotation_authority_id AND
               NEW.old_rotation_version IS OLD.old_rotation_version AND
               NEW.old_rotation_generation IS OLD.old_rotation_generation AND
               NEW.recovery_authority_id IS OLD.recovery_authority_id AND
               NEW.recovery_generation IS OLD.recovery_generation AND
               NEW.intent_digest IS OLD.intent_digest AND
               NEW.signatures_json='[]'
             )
            BEGIN SELECT RAISE(ABORT,'LAB-086 legacy recovery transition semantics are immutable after cutoff'); END"""
        )

    # Compatibility recovery authority: only key-map scrubbing is allowed.
    table = "provider_rotation_recovery_authorities"
    if table in tables:
        names = LEGACY_PROJECTION_FREEZE_TRIGGERS[table]
        _create_legacy_deny_insert_delete(q, table, names, "compatibility recovery authority")
        q.execute(
            f"""CREATE TRIGGER {names[1]}
            BEFORE UPDATE ON {table}
            WHEN EXISTS(SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1)
             AND NOT (
               NEW.authority_id IS OLD.authority_id AND NEW.name IS OLD.name AND
               NEW.generation IS OLD.generation AND NEW.threshold IS OLD.threshold AND
               NEW.revoked_json IS OLD.revoked_json AND NEW.keys_json='{{}}'
             )
            BEGIN SELECT RAISE(ABORT,'LAB-086 compatibility recovery authority semantics are immutable after cutoff'); END"""
        )

    # Versioned recovery authority: only key-map scrubbing is allowed.
    table = "provider_recovery_lifecycle_authorities"
    if table in tables:
        names = LEGACY_PROJECTION_FREEZE_TRIGGERS[table]
        _create_legacy_deny_insert_delete(q, table, names, "recovery lifecycle authority")
        q.execute(
            f"""CREATE TRIGGER {names[1]}
            BEFORE UPDATE ON {table}
            WHEN EXISTS(SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1)
             AND NOT (
               NEW.authority_id IS OLD.authority_id AND NEW.version IS OLD.version AND
               NEW.name IS OLD.name AND NEW.generation IS OLD.generation AND
               NEW.threshold IS OLD.threshold AND NEW.revoked_json IS OLD.revoked_json AND
               NEW.keys_json='{{}}'
             )
            BEGIN SELECT RAISE(ABORT,'LAB-086 recovery lifecycle authority semantics are immutable after cutoff'); END"""
        )

    # Versioned recovery transition: migration may only erase its three HMAC sets.
    table = "provider_recovery_lifecycle_transitions"
    if table in tables:
        names = LEGACY_PROJECTION_FREEZE_TRIGGERS[table]
        _create_legacy_deny_insert_delete(q, table, names, "recovery lifecycle transition")
        q.execute(
            f"""CREATE TRIGGER {names[1]}
            BEFORE UPDATE ON {table}
            WHEN EXISTS(SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1)
             AND NOT (
               NEW.new_authority_id IS OLD.new_authority_id AND
               NEW.old_authority_id IS OLD.old_authority_id AND
               NEW.root_authority_id IS OLD.root_authority_id AND
               NEW.root_version IS OLD.root_version AND
               NEW.root_generation IS OLD.root_generation AND
               NEW.intent_digest IS OLD.intent_digest AND
               NEW.old_signatures_json='[]' AND NEW.new_signatures_json='[]' AND
               NEW.root_signatures_json='[]'
             )
            BEGIN SELECT RAISE(ABORT,'LAB-086 recovery lifecycle transition semantics are immutable after cutoff'); END"""
        )

    # Every other row in the signed legacy projection is fully frozen.
    for table, label in (
        ("provider_rotation_recovery_head", "compatibility recovery head"),
        ("provider_recovery_lifecycle_head", "recovery lifecycle head"),
        ("provider_recovery_custody_bindings", "recovery custody binding"),
        ("provider_rotation_recovery_custody_proofs", "recovery custody proof"),
        ("provider_recovery_custody_enablement", "recovery custody enablement"),
        ("provider_recovery_custody_enablement_proof", "recovery custody enablement proof"),
    ):
        if table not in tables:
            continue
        names = LEGACY_PROJECTION_FREEZE_TRIGGERS[table]
        _create_legacy_deny_insert_delete(q, table, names, label)
        _create_legacy_deny_update(q, table, names[1], label)


def _install_current_authority_fence_locked(q):
    tables = _table_names(q)
    for name in (
        *CURRENT_AUTHORITY_WRITER_TRIGGER_NAMES,
        *_all_current_authority_history_trigger_names(),
    ):
        q.execute(f"DROP TRIGGER IF EXISTS {name}")

    if "provider_rotation_authorities" in tables:
        q.execute(
            """CREATE TRIGGER lab086_root_authority_insert_requires_final_writer
            BEFORE INSERT ON provider_rotation_authorities
            WHEN EXISTS(
              SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
            )
            BEGIN
              SELECT RAISE(ABORT,'LAB-086 root authority creation requires final supported writer');
            END"""
        )
        _install_history_immutability(
            q,
            "provider_rotation_authorities",
            *CURRENT_AUTHORITY_HISTORY_TRIGGERS["provider_rotation_authorities"],
            "root authority history",
        )

    if "asymmetric_provider_generations" in tables:
        q.execute(
            """CREATE TRIGGER lab086_provider_generation_insert_requires_final_writer
            BEFORE INSERT ON asymmetric_provider_generations
            WHEN EXISTS(
              SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
            )
            BEGIN
              SELECT RAISE(ABORT,'LAB-086 provider generation creation requires final supported writer');
            END"""
        )
        _install_history_immutability(
            q,
            "asymmetric_provider_generations",
            *CURRENT_AUTHORITY_HISTORY_TRIGGERS["asymmetric_provider_generations"],
            "provider generation history",
        )

    if "asymmetric_provider_head" in tables:
        for name, operation, label in (
            ("lab086_provider_head_insert_requires_final_writer", "INSERT", "insertion"),
            ("lab086_provider_head_update_requires_final_writer", "UPDATE", "mutation"),
            ("lab086_provider_head_delete_requires_final_writer", "DELETE", "deletion"),
        ):
            q.execute(
                f"""CREATE TRIGGER {name}
                BEFORE {operation} ON asymmetric_provider_head
                WHEN EXISTS(
                  SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
                )
                BEGIN
                  SELECT RAISE(ABORT,'LAB-086 provider head {label} requires final supported writer');
                END"""
            )

    if "provider_rotation_threshold_enablement" in tables:
        for name, operation, label in (
            ("lab086_threshold_enablement_no_insert", "INSERT", "cannot be inserted"),
            ("lab086_threshold_enablement_is_immutable", "UPDATE", "is immutable"),
            ("lab086_threshold_enablement_is_not_deletable", "DELETE", "cannot be deleted"),
        ):
            q.execute(
                f"""CREATE TRIGGER {name}
                BEFORE {operation} ON provider_rotation_threshold_enablement
                WHEN EXISTS(
                  SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
                )
                BEGIN
                  SELECT RAISE(ABORT,'LAB-086 threshold enablement {label} after cutoff');
                END"""
            )


def _install_migration_metadata_fence_locked(q):
    tables = _table_names(q)
    required = set(MIGRATION_METADATA_FENCE_TRIGGERS)
    for name in _all_migration_metadata_trigger_names():
        q.execute(f"DROP TRIGGER IF EXISTS {name}")
    if not required.issubset(tables):
        return

    complete = (
        "EXISTS(SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1) "
        "AND EXISTS(SELECT 1 FROM provider_asymmetric_break_glass_legacy_projection WHERE singleton=1) "
        "AND EXISTS(SELECT 1 FROM provider_asymmetric_break_glass_root_proof WHERE singleton=1)"
    )
    labels = {
        "provider_asymmetric_break_glass_boundary": "migration boundary",
        "provider_asymmetric_break_glass_legacy_projection": "migration legacy projection",
        "provider_asymmetric_break_glass_root_proof": "migration root proof",
    }
    for table, names in MIGRATION_METADATA_FENCE_TRIGGERS.items():
        label = labels[table]
        for name, operation, action in (
            (names[0], "INSERT", "cannot be inserted/replaced"),
            (names[1], "UPDATE", "is immutable"),
            (names[2], "DELETE", "cannot be deleted"),
        ):
            q.execute(
                f"""CREATE TRIGGER {name}
                BEFORE {operation} ON {table}
                WHEN {complete}
                BEGIN
                  SELECT RAISE(ABORT,'LAB-086 {label} {action} after cutoff');
                END"""
            )



def install_public_mutation_fence_locked(q):
    """Install unconditional post-cutoff deny policy for underlying writers.

    A durable proof row is evidence, never mutation authority. The final supported
    writer may temporarily remove current-authority triggers only while it owns the
    same ``BEGIN IMMEDIATE`` transaction *after* all relevant cryptographic/history
    checks have passed. SQLite DDL is transactional, so rollback/crash restores the
    pre-transaction fence.

    The signed migration projection is frozen separately and is never thawed by a
    final writer. Its scrub-aware UPDATE guards allow exactly the key/signature
    erasure performed inside the cutoff transaction, while every semantic field,
    insert and delete is denied once the boundary row exists.

    The inherited-writer triggers fence both new canonical writes and mutation of
    already authenticated historical proof/transition rows. The root-head singleton
    is fenced on INSERT/UPDATE/DELETE so conflict algorithms such as INSERT OR
    REPLACE cannot bypass the update guard. If a stale/direct writer attempts any of
    those operations, the transaction aborts and preceding writes roll back.
    Current root/provider authority rows are similarly split between thawable
    successor/head writes and non-thawable historical immutability.
    Post-cutoff-only evidence is also rejected before any authenticated migration
    boundary exists; supported execution can never create that partial state, and
    accepting it would turn debris into a durable restart failure after cutoff.
    Tables are discovered dynamically so the isolated strict-fence fixture remains
    usable; on the real LAB-086 schema they are required by
    ``assert_public_mutation_fence_locked``.
    """
    _assert_no_pre_cutoff_post_cutoff_evidence_locked(q)
    remove_public_mutation_fence_locked(q)
    _install_legacy_projection_freeze_locked(q)
    _install_current_authority_fence_locked(q)
    _install_migration_metadata_fence_locked(q)
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
    legacy_required = {
        trigger
        for table, triggers in LEGACY_PROJECTION_FREEZE_TRIGGERS.items()
        if table in tables
        for trigger in triggers
    }
    missing |= legacy_required - names
    if "provider_rotation_authority_head" in tables:
        missing |= set(ROOT_HEAD_MUTATION_TRIGGER_NAMES) - names
    if "provider_rotation_authorities" in tables:
        missing |= {"lab086_root_authority_insert_requires_final_writer"} - names
        missing |= set(CURRENT_AUTHORITY_HISTORY_TRIGGERS["provider_rotation_authorities"]) - names
    if "asymmetric_provider_generations" in tables:
        missing |= {"lab086_provider_generation_insert_requires_final_writer"} - names
        missing |= set(CURRENT_AUTHORITY_HISTORY_TRIGGERS["asymmetric_provider_generations"]) - names
    if "asymmetric_provider_head" in tables:
        missing |= {
            "lab086_provider_head_insert_requires_final_writer",
            "lab086_provider_head_update_requires_final_writer",
            "lab086_provider_head_delete_requires_final_writer",
        } - names
    if "provider_rotation_threshold_enablement" in tables:
        missing |= set(THRESHOLD_ENABLEMENT_FREEZE_TRIGGER_NAMES) - names
    if set(MIGRATION_METADATA_FENCE_TRIGGERS).issubset(tables):
        missing |= set(_all_migration_metadata_trigger_names()) - names
    obsolete = set(OBSOLETE_PUBLIC_MUTATION_TRIGGER_NAMES) & names
    if missing or obsolete:
        raise RuntimeError(
            f"LAB-086 public mutation fence mismatch missing={sorted(missing)} obsolete={sorted(obsolete)}"
        )
    return True
