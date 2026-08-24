from __future__ import annotations

PUBLIC_MUTATION_TRIGGER_NAMES = (
    "lab086_public_authority_requires_current_authorization",
    "lab086_public_authority_is_immutable",
    "lab086_public_authority_is_not_deletable",
    "lab086_public_transition_requires_current_authorization",
    "lab086_public_transition_is_immutable",
    "lab086_public_transition_is_not_deletable",
    "lab086_public_head_requires_current_authorization",
    "lab086_public_head_is_not_deletable",
)

# Historical names from earlier LAB-086 candidates. They must be removed because
# their proof-row predicates treated unauthenticated durable data as capability.
OBSOLETE_PUBLIC_MUTATION_TRIGGER_NAMES = (
    "lab086_public_authority_requires_root_proof",
    "lab086_public_transition_requires_root_proof",
    "lab086_public_head_requires_root_proof",
)


def remove_public_mutation_fence_locked(q):
    for name in (*PUBLIC_MUTATION_TRIGGER_NAMES, *OBSOLETE_PUBLIC_MUTATION_TRIGGER_NAMES):
        q.execute(f"DROP TRIGGER IF EXISTS {name}")


def install_public_mutation_fence_locked(q):
    """Install unconditional post-cutoff deny policy for underlying writers.

    This fence deliberately does not inspect proof rows. A durable row is evidence,
    not mutation authority. The final supported writer may temporarily remove these
    triggers only while it owns the same BEGIN IMMEDIATE transaction *after* all
    cryptographic quorums have been verified. SQLite DDL is transactional, so a
    rollback/crash restores the pre-transaction fence.
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


def assert_public_mutation_fence_locked(q):
    names = {
        row[0]
        for row in q.execute(
            "SELECT name FROM sqlite_master WHERE type='trigger'"
        ).fetchall()
    }
    missing = set(PUBLIC_MUTATION_TRIGGER_NAMES) - names
    obsolete = set(OBSOLETE_PUBLIC_MUTATION_TRIGGER_NAMES) & names
    if missing or obsolete:
        raise RuntimeError(
            f"LAB-086 public mutation fence mismatch missing={sorted(missing)} obsolete={sorted(obsolete)}"
        )
    return True
