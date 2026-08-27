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

# Transaction-scoped final writers need creation + head-UPDATE capability, not
# authority to rewrite/delete already authenticated history or replace/delete
# initialized singleton heads. Keep the full trigger set above for reinstall/audit.
PUBLIC_MUTATION_THAW_TRIGGER_NAMES = (
    "lab086_public_authority_requires_current_authorization",
    "lab086_public_transition_requires_current_authorization",
    "lab086_public_head_requires_current_authorization",
)

INHERITED_MUTATION_TRIGGERS = {
    "provider_rotation_authority_transitions": "lab086_normal_root_transition_requires_final_writer",
    "provider_rotation_threshold_proofs": "lab086_provider_threshold_proof_requires_final_writer",
    "asymmetric_provider_transitions": "lab086_provider_transition_requires_final_writer",
}

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

ROOT_HEAD_MUTATION_TRIGGER_NAMES = (
    "lab086_root_head_insert_requires_final_writer",
    "lab086_root_head_requires_final_writer",
    "lab086_root_head_delete_requires_final_writer",
)

CURRENT_AUTHORITY_WRITER_TRIGGER_NAMES = (
    "lab086_root_authority_insert_requires_final_writer",
    "lab086_provider_generation_insert_requires_final_writer",
    "lab086_provider_head_insert_requires_final_writer",
    "lab086_provider_head_update_requires_final_writer",
    "lab086_provider_head_delete_requires_final_writer",
)

ROOT_HEAD_THAW_TRIGGER_NAMES = (
    "lab086_root_head_requires_final_writer",
)

CURRENT_AUTHORITY_THAW_TRIGGER_NAMES = (
    "lab086_root_authority_insert_requires_final_writer",
    "lab086_provider_generation_insert_requires_final_writer",
    "lab086_provider_head_update_requires_final_writer",
)

THAW_INSERT_HISTORY_COLLISION_FENCES = {
    "provider_recovery_public_authorities": (
        "authority_id", "lab086_public_authority_existing_key_no_replace"
    ),
    "provider_recovery_public_transitions": (
        "new_authority_id", "lab086_public_transition_existing_key_no_replace"
    ),
    "provider_rotation_authorities": (
        "authority_id", "lab086_root_authority_existing_key_no_replace"
    ),
    "provider_rotation_authority_transitions": (
        "new_authority_id", "lab086_root_transition_existing_key_no_replace"
    ),
    "provider_rotation_threshold_proofs": (
        "new_provider_generation_id", "lab086_threshold_proof_existing_key_no_replace"
    ),
    "asymmetric_provider_generations": (
        "generation_id", "lab086_provider_generation_existing_key_no_replace"
    ),
    "asymmetric_provider_transitions": (
        "new_generation_id", "lab086_provider_transition_existing_key_no_replace"
    ),
}

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

OBSOLETE_PUBLIC_MUTATION_TRIGGER_NAMES = (
    "lab086_public_authority_requires_root_proof",
    "lab086_public_transition_requires_root_proof",
    "lab086_public_head_requires_root_proof",
)

POST_CUTOFF_ONLY_EVIDENCE_TABLES = (
    "provider_asymmetric_break_glass_proofs",
    "provider_asymmetric_recovery_public_root_proofs",
)

POST_CUTOFF_EVIDENCE_FREEZE_TRIGGERS = {
    "provider_asymmetric_break_glass_proofs": (
        "new_rotation_authority_id",
        "lab086_break_glass_proof_no_replace",
        "lab086_break_glass_proof_is_immutable",
        "lab086_break_glass_proof_is_not_deletable",
    ),
    "provider_asymmetric_recovery_public_root_proofs": (
        "new_public_authority_id",
        "lab086_public_root_proof_no_replace",
        "lab086_public_root_proof_is_immutable",
        "lab086_public_root_proof_is_not_deletable",
    ),
}

# LAB-082 historical receipts are append-only authenticated evidence. New
# request IDs must remain insertable after cutoff, but an already committed
# receipt may never be rewritten, deleted, REPLACE'd, or UPSERT-mutated.
PROVIDER_RECEIPT_HISTORY_FREEZE_TRIGGERS = (
    "lab086_provider_receipt_no_replace",
    "lab086_provider_receipt_is_immutable",
    "lab086_provider_receipt_is_not_deletable",
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


def _all_post_cutoff_evidence_trigger_names():
    return tuple(
        name
        for _, insert_name, update_name, delete_name in POST_CUTOFF_EVIDENCE_FREEZE_TRIGGERS.values()
        for name in (insert_name, update_name, delete_name)
    )


def _all_post_cutoff_evidence_creation_trigger_names():
    return tuple(
        insert_name
        for _, insert_name, _, _ in POST_CUTOFF_EVIDENCE_FREEZE_TRIGGERS.values()
    )


def _all_provider_receipt_trigger_names():
    return PROVIDER_RECEIPT_HISTORY_FREEZE_TRIGGERS


def _all_thaw_insert_history_collision_trigger_names():
    return tuple(
        trigger_name
        for _, trigger_name in THAW_INSERT_HISTORY_COLLISION_FENCES.values()
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


def _remove_all_public_mutation_fence_triggers_locked(q):
    """Full trigger cleanup used only before reinstalling the complete fence."""
    for name in (
        *PUBLIC_MUTATION_TRIGGER_NAMES,
        *_all_inherited_trigger_names(),
        *ROOT_HEAD_MUTATION_TRIGGER_NAMES,
        *CURRENT_AUTHORITY_WRITER_TRIGGER_NAMES,
        *_all_thaw_insert_history_collision_trigger_names(),
        *_all_post_cutoff_evidence_creation_trigger_names(),
        *OBSOLETE_PUBLIC_MUTATION_TRIGGER_NAMES,
    ):
        q.execute(f"DROP TRIGGER IF EXISTS {name}")


def remove_public_mutation_fence_locked(q):
    """Grant only the DML capability required by verified final writers."""
    for name in (
        *PUBLIC_MUTATION_THAW_TRIGGER_NAMES,
        *INHERITED_MUTATION_TRIGGERS.values(),
        *ROOT_HEAD_THAW_TRIGGER_NAMES,
        *CURRENT_AUTHORITY_THAW_TRIGGER_NAMES,
        *_all_post_cutoff_evidence_creation_trigger_names(),
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


def _install_thaw_insert_history_collision_fences_locked(q):
    tables = _table_names(q)
    for name in _all_thaw_insert_history_collision_trigger_names():
        q.execute(f"DROP TRIGGER IF EXISTS {name}")
    for table, (key_column, trigger_name) in THAW_INSERT_HISTORY_COLLISION_FENCES.items():
        if table not in tables:
            continue
        semantic_collision = ""
        if table == "asymmetric_provider_generations":
            semantic_collision = """
               OR EXISTS(
                 SELECT 1 FROM asymmetric_provider_generations
                 WHERE provider_id IS NEW.provider_id
                   AND generation IS NEW.generation
               )
            """
        q.execute(
            f"""CREATE TRIGGER {trigger_name}
            BEFORE INSERT ON {table}
            WHEN EXISTS(SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1)
             AND (
               NEW.{key_column} IS NULL
               OR EXISTS(SELECT 1 FROM {table} WHERE {key_column} IS NEW.{key_column})
               {semantic_collision}
             )
            BEGIN
              SELECT RAISE(ABORT,'LAB-086 existing authenticated history key cannot be replaced');
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


def _install_post_cutoff_evidence_freeze_locked(q):
    tables = _table_names(q)
    for name in _all_post_cutoff_evidence_trigger_names():
        q.execute(f"DROP TRIGGER IF EXISTS {name}")
    for table, (key_column, insert_name, update_name, delete_name) in POST_CUTOFF_EVIDENCE_FREEZE_TRIGGERS.items():
        if table not in tables:
            continue
        no_replace_name = f"{insert_name}_existing_key_no_replace"
        q.execute(f"DROP TRIGGER IF EXISTS {no_replace_name}")
        q.execute(
            f"""CREATE TRIGGER {no_replace_name}
            BEFORE INSERT ON {table}
            WHEN EXISTS(SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1)
             AND (
               NEW.{key_column} IS NULL
               OR EXISTS(SELECT 1 FROM {table} WHERE {key_column} IS NEW.{key_column})
             )
            BEGIN
              SELECT RAISE(ABORT,'LAB-086 existing post-cutoff evidence key cannot be replaced');
            END"""
        )
        q.execute(
            f"""CREATE TRIGGER {insert_name}
            BEFORE INSERT ON {table}
            WHEN EXISTS(SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1)
            BEGIN
              SELECT RAISE(ABORT,'LAB-086 post-cutoff evidence creation requires final supported writer');
            END"""
        )
        _install_history_immutability(
            q, table, update_name, delete_name, "post-cutoff evidence history"
        )


def _install_provider_receipt_freeze_locked(q):
    tables = _table_names(q)
    for name in _all_provider_receipt_trigger_names():
        q.execute(f"DROP TRIGGER IF EXISTS {name}")
    if "asymmetric_provider_receipts" not in tables:
        return
    insert_name, update_name, delete_name = PROVIDER_RECEIPT_HISTORY_FREEZE_TRIGGERS
    q.execute(
        f"""CREATE TRIGGER {insert_name}
        BEFORE INSERT ON asymmetric_provider_receipts
        WHEN EXISTS(
          SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
        )
         AND EXISTS(
          SELECT 1 FROM asymmetric_provider_receipts WHERE request_id=NEW.request_id
        )
        BEGIN
          SELECT RAISE(ABORT,'LAB-086 committed provider receipt cannot be replaced');
        END"""
    )
    _install_history_immutability(
        q,
        "asymmetric_provider_receipts",
        update_name,
        delete_name,
        "provider receipt history",
    )


def install_public_mutation_fence_locked(q):
    _assert_no_pre_cutoff_post_cutoff_evidence_locked(q)
    _remove_all_public_mutation_fence_triggers_locked(q)
    _install_thaw_insert_history_collision_fences_locked(q)
    _install_legacy_projection_freeze_locked(q)
    _install_current_authority_fence_locked(q)
    _install_migration_metadata_fence_locked(q)
    _install_post_cutoff_evidence_freeze_locked(q)
    _install_provider_receipt_freeze_locked(q)
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
    thaw_collision_required = {
        trigger_name
        for table, (_, trigger_name) in THAW_INSERT_HISTORY_COLLISION_FENCES.items()
        if table in tables
    }
    missing |= thaw_collision_required - names
    if set(MIGRATION_METADATA_FENCE_TRIGGERS).issubset(tables):
        missing |= set(_all_migration_metadata_trigger_names()) - names
    evidence_required = {
        trigger
        for table, (_, *triggers) in POST_CUTOFF_EVIDENCE_FREEZE_TRIGGERS.items()
        if table in tables
        for trigger in triggers
    }
    evidence_required |= {
        f"{insert_name}_existing_key_no_replace"
        for table, (_, insert_name, _, _) in POST_CUTOFF_EVIDENCE_FREEZE_TRIGGERS.items()
        if table in tables
    }
    missing |= evidence_required - names
    if "asymmetric_provider_receipts" in tables:
        missing |= set(_all_provider_receipt_trigger_names()) - names
    obsolete = set(OBSOLETE_PUBLIC_MUTATION_TRIGGER_NAMES) & names
    if missing or obsolete:
        raise RuntimeError(
            f"LAB-086 public mutation fence mismatch missing={sorted(missing)} obsolete={sorted(obsolete)}"
        )
    return True
