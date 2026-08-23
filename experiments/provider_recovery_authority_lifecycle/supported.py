from __future__ import annotations

from experiments.provider_threshold_rotation.protocol import (
    InvalidAuthority,
    ProviderRotationIntent,
    RotationAuthority,
    Signature,
    StaleAuthority,
    ThresholdNotMet,
    ThresholdProof,
    verify_threshold,
)
from experiments.provider_threshold_rotation.strict import require_canonical_authority
from experiments.provider_threshold_rotation.supported import (
    SupportedThresholdAuthorizedAsymmetricProviderLedger,
)
from experiments.provider_rotation_recovery.protocol import (
    DurableRecoveryController,
    RecoveryAuthority,
    RecoveryAuthorityMismatch,
    RecoveryError,
    RecoveryIntent,
    RecoveryProof,
    verify_recovery_threshold,
)
from experiments.provider_rotation_recovery.supported import (
    SupportedRecoveryThresholdProviderLedger,
)

from .protocol import (
    DurableRecoveryAuthorityLifecycle,
    LifecycleRollback,
    LifecycleSubstitution,
    VersionedRecoveryAuthority,
)


class ManagedRecoveryController(DurableRecoveryController):
    """LAB-084 tables with a LAB-085-managed recovery head.

    LAB-084 intentionally pins its head to bootstrap. LAB-085 is the explicit
    authority that may advance that head, so construction only verifies schema,
    content identities and exact persisted proof bytes. The supported LAB-085
    surface performs the stronger mixed-history/window verification before any
    object is returned to callers.
    """

    def verify_durable(self):
        q = self._con()
        try:
            q.execute("BEGIN")
            heads = q.execute(
                "SELECT authority_id,generation FROM provider_rotation_recovery_head "
                "WHERE singleton=1"
            ).fetchall()
            if len(heads) != 1:
                raise RecoveryError("missing/duplicate managed recovery head")
            current = self._load_recovery_locked(q, heads[0][0])
            if current.generation != heads[0][1]:
                raise RecoveryError("managed recovery head generation mismatch")
            for row in q.execute(
                "SELECT new_rotation_authority_id,old_rotation_authority_id,"
                "recovery_authority_id,recovery_generation FROM "
                "provider_rotation_recovery_transitions"
            ).fetchall():
                old = self.rotation_store._load_locked(q, row[1])
                new = self.rotation_store._load_locked(q, row[0])
                if (
                    new.authority_name != old.authority_name
                    or new.version != old.version + 1
                    or new.generation != old.generation + 1
                ):
                    raise RecoveryError("managed recovery transition continuity mismatch")
                recovery = self._load_recovery_locked(q, row[2])
                if recovery.generation != row[3]:
                    raise RecoveryError("managed recovery transition generation mismatch")
            q.commit()
            return True
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def verify_recovery_transition_with_authority_locked(
        self, q, old: RotationAuthority, new: RotationAuthority, recovery: RecoveryAuthority
    ):
        row = q.execute(
            "SELECT old_rotation_authority_id,old_rotation_version,"
            "old_rotation_generation,recovery_authority_id,recovery_generation,"
            "intent_digest,signatures_json FROM provider_rotation_recovery_transitions "
            "WHERE new_rotation_authority_id=?",
            (new.authority_id,),
        ).fetchone()
        if row is None:
            raise RecoveryError("missing managed recovery transition")
        if (row[0], row[1], row[2]) != (
            old.authority_id,
            old.version,
            old.generation,
        ):
            raise RecoveryError("managed recovery predecessor mismatch")
        if (row[3], row[4]) != (recovery.authority_id, recovery.generation):
            raise RecoveryAuthorityMismatch("managed recovery proof authority mismatch")
        intent = RecoveryIntent(
            old.authority_id,
            old.version,
            old.generation,
            new.descriptor,
            recovery.authority_id,
            recovery.generation,
        )
        proof = RecoveryProof(
            row[5], row[3], row[4], self._decode_signatures(row[6])
        )
        verify_recovery_threshold(recovery, intent, proof)
        return True


class SupportedRecoveryAuthorityLifecycleLedger(SupportedRecoveryThresholdProviderLedger):
    """LAB-085 supported surface.

    Recovery-authority rotation and LAB-084 break-glass recovery share the same
    SQLite write boundary. A recovery generation is valid only in the normal-root
    version interval implied by the root that co-authorized its activation.
    """

    def __init__(
        self,
        path,
        attested,
        bootstrap,
        signer,
        rotation_authority: RotationAuthority,
        enablement,
        recovery_authority: RecoveryAuthority,
    ):
        if type(recovery_authority) is not RecoveryAuthority:
            raise TypeError("exact LAB-084 RecoveryAuthority required")
        self._lab085_initializing = True
        # Skip LAB-084's constructor because its controller intentionally pins the
        # recovery head to bootstrap. Reuse the audited LAB-083 initialization,
        # then install a managed LAB-084 controller and LAB-085 lifecycle.
        SupportedThresholdAuthorizedAsymmetricProviderLedger.__init__(
            self,
            path,
            attested,
            bootstrap,
            signer,
            rotation_authority,
            enablement,
        )
        self.recovery = ManagedRecoveryController(
            path, self.rotation_authority, recovery_authority
        )
        self.recovery_lifecycle = DurableRecoveryAuthorityLifecycle(
            path, VersionedRecoveryAuthority(1, recovery_authority)
        )
        self._lab085_initializing = False
        self.verify_durable()

    @staticmethod
    def _reject_prepared_locked(q):
        return SupportedRecoveryThresholdProviderLedger._reject_prepared_locked(q)

    def recovery_rotation_payload(self, new: VersionedRecoveryAuthority):
        if type(new) is not VersionedRecoveryAuthority:
            raise TypeError("exact LAB-085 VersionedRecoveryAuthority required")
        q = self._con()
        try:
            q.execute("BEGIN")
            root = self.rotation_authority.current_locked(q)
            old = self.recovery_lifecycle.current_locked(q)
            current_recovery = self.recovery.current_recovery_locked(q)
            if current_recovery.authority_id != old.recovery.authority_id:
                raise RecoveryAuthorityMismatch("LAB-084/LAB-085 recovery heads diverged")
            payload = self.recovery_lifecycle.make_intent(root, old, new).payload
            q.commit()
            return payload
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def rotate_recovery_authority(
        self,
        new: VersionedRecoveryAuthority,
        old_signatures: tuple[Signature, ...],
        new_signatures: tuple[Signature, ...],
        root_signatures: tuple[Signature, ...],
    ):
        if type(new) is not VersionedRecoveryAuthority:
            raise TypeError("exact LAB-085 VersionedRecoveryAuthority required")
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._reject_prepared_locked(q)
            root = self.rotation_authority.current_locked(q)
            old = self.recovery_lifecycle.current_locked(q)
            current_recovery = self.recovery.current_recovery_locked(q)
            if current_recovery.authority_id != old.recovery.authority_id:
                raise RecoveryAuthorityMismatch("LAB-084/LAB-085 recovery heads diverged")
            out = self.recovery_lifecycle.rotate_locked(
                q, root, new, old_signatures, new_signatures, root_signatures
            )
            self.recovery._insert_recovery_locked(q, new.recovery)
            changed = q.execute(
                "UPDATE provider_rotation_recovery_head SET authority_id=?,generation=? "
                "WHERE singleton=1 AND authority_id=? AND generation=?",
                (
                    new.recovery.authority_id,
                    new.recovery.generation,
                    old.recovery.authority_id,
                    old.recovery.generation,
                ),
            ).rowcount
            if changed != 1:
                raise LifecycleRollback("LAB-084 recovery head changed during lifecycle rotation")
            q.commit()
            return out
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def _lifecycle_windows_locked(self, q, rotation_by_id):
        rows = q.execute(
            "SELECT authority_id FROM provider_recovery_lifecycle_authorities ORDER BY version"
        ).fetchall()
        versions = [self.recovery_lifecycle._load_recovery_locked(q, r[0]) for r in rows]
        if not versions:
            raise LifecycleSubstitution("missing recovery lifecycle history")
        windows = {}
        activation = None
        for index, current in enumerate(versions):
            deactivation = None
            if index + 1 < len(versions):
                nxt = versions[index + 1]
                root = self.recovery_lifecycle.verify_transition_locked(q, current, nxt)
                actual_root = rotation_by_id.get(root.authority_id)
                if actual_root is None or actual_root.descriptor != root.descriptor:
                    raise LifecycleSubstitution(
                        "recovery lifecycle co-authorizing root is not in normal authority history"
                    )
                deactivation = actual_root.version
            windows[current.recovery.authority_id] = (
                current,
                activation,
                deactivation,
            )
            if deactivation is not None:
                activation = deactivation
        return windows

    def _verify_mixed_authority_history_locked(self, q, provider_transitions):
        rows = q.execute(
            "SELECT authority_id FROM provider_rotation_authorities ORDER BY version"
        ).fetchall()
        if not rows:
            raise InvalidAuthority("missing authority history")
        authorities = [self.rotation_authority._load_locked(q, r[0]) for r in rows]
        if authorities[0].authority_id != self.rotation_authority.bootstrap.authority_id:
            raise StaleAuthority("authority bootstrap changed")
        by_id = {a.authority_id: a for a in authorities}

        # Verify the LAB-085 lifecycle from the same SQL snapshot used below.
        self.recovery_lifecycle.verify_durable_locked(q)
        windows = self._lifecycle_windows_locked(q, by_id)
        current_lifecycle = self.recovery_lifecycle.current_locked(q)
        current_recovery = self.recovery.current_recovery_locked(q)
        if current_recovery.authority_id != current_lifecycle.recovery.authority_id:
            raise RecoveryAuthorityMismatch("LAB-084/LAB-085 recovery heads diverged")

        normal_count = q.execute(
            "SELECT COUNT(*) FROM provider_rotation_authority_transitions"
        ).fetchone()[0]
        recovery_count = q.execute(
            "SELECT COUNT(*) FROM provider_rotation_recovery_transitions"
        ).fetchone()[0]
        if normal_count + recovery_count != len(authorities) - 1:
            raise RecoveryError("authority proof count does not match history edges")

        for old, new in zip(authorities, authorities[1:]):
            if (
                new.authority_name != old.authority_name
                or new.version != old.version + 1
                or new.generation != old.generation + 1
            ):
                raise RecoveryError("authority history continuity mismatch")
            normal = q.execute(
                "SELECT COUNT(*) FROM provider_rotation_authority_transitions "
                "WHERE new_authority_id=?",
                (new.authority_id,),
            ).fetchone()[0]
            recovery_row = q.execute(
                "SELECT recovery_authority_id,recovery_generation FROM "
                "provider_rotation_recovery_transitions WHERE new_rotation_authority_id=?",
                (new.authority_id,),
            ).fetchone()
            recovery = 0 if recovery_row is None else 1
            if normal + recovery != 1:
                raise RecoveryError("authority edge must have exactly one normal or recovery proof")
            if normal:
                self._verify_normal_edge_locked(q, old, new)
                continue

            window = windows.get(recovery_row[0])
            if window is None:
                raise RecoveryAuthorityMismatch(
                    "break-glass proof references unknown recovery lifecycle generation"
                )
            versioned, lower, upper = window
            if versioned.recovery.generation != recovery_row[1]:
                raise RecoveryAuthorityMismatch("break-glass recovery generation mismatch")
            if lower is not None and old.version < lower:
                raise RecoveryAuthorityMismatch("recovery generation used before activation cutoff")
            if upper is not None and old.version >= upper:
                raise RecoveryAuthorityMismatch("stale recovery generation used after rotation cutoff")
            self.recovery.verify_recovery_transition_with_authority_locked(
                q, old, new, versioned.recovery
            )

        head = self.rotation_authority.current_locked(q)
        if head.authority_id != authorities[-1].authority_id:
            raise StaleAuthority("authority head rollback")

        for provider_id, old_gid, new_gid in provider_transitions:
            row = q.execute(
                "SELECT authority_id,authority_version,authority_generation,intent_digest,"
                "signatures_json FROM provider_rotation_threshold_proofs "
                "WHERE new_provider_generation_id=?",
                (new_gid,),
            ).fetchone()
            if row is None:
                raise ThresholdNotMet("provider transition missing threshold proof")
            authority = by_id.get(row[0])
            if authority is None:
                raise InvalidAuthority("threshold proof references unknown historical authority")
            intent = ProviderRotationIntent(
                provider_id,
                old_gid,
                new_gid,
                authority.authority_id,
                authority.version,
                authority.generation,
            )
            proof = ThresholdProof(
                row[3],
                row[0],
                row[1],
                row[2],
                self.rotation_authority._decode_signatures(row[4]),
            )
            verify_threshold(authority, intent, proof)
        return head

    def verify_durable(self):
        if getattr(self, "_lab085_initializing", False):
            return True
        # LAB-084's verify_durable dynamically dispatches the mixed-history method
        # above but also asserts bootstrap recovery=head. Re-run the durable stack
        # explicitly without that LAB-084-only invariant.
        from experiments.asymmetric_provider_history.supported import (
            SupportedAsymmetricHistoricalSharedAnchorLedger,
        )

        SupportedAsymmetricHistoricalSharedAnchorLedger.verify_durable(self)
        if not hasattr(self, "rotation_authority"):
            return True
        q = self._con()
        try:
            q.execute("BEGIN")
            enablement = self._load_enablement_locked(q)
            rows = q.execute(
                "SELECT t.provider_id,t.old_generation_id,t.new_generation_id,g.generation "
                "FROM asymmetric_provider_transitions t JOIN asymmetric_provider_generations g "
                "ON g.generation_id=t.new_generation_id WHERE g.generation>? ORDER BY g.generation",
                (enablement.start_provider_generation,),
            ).fetchall()
            transitions = [(r[0], r[1], r[2]) for r in rows]
            self._verify_mixed_authority_history_locked(q, transitions)
            q.commit()
            return True
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
