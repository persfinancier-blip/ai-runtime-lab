from __future__ import annotations

from experiments.provider_rotation_recovery.protocol import RecoveryAuthorityMismatch
from .asymmetric_custody import (
    AsymmetricRecoveryCustody,
    CustodySubstitution,
    PublicRecoveryAuthority,
    custody_rotation_payload,
)
from .protocol import LifecycleRollback, LifecycleSubstitution, VersionedRecoveryAuthority
from .supported import SupportedRecoveryAuthorityLifecycleLedger


class CustodyBindingError(RuntimeError):
    pass


class SupportedPublicRecoveryAuthorityLifecycleLedger(SupportedRecoveryAuthorityLifecycleLedger):
    """LAB-085 supported boundary binding symmetric lifecycle and public-only custody.

    The symmetric LAB-085/LAB-084 authority remains the compatibility path for
    existing HMAC break-glass history. The public custody authority is the
    verification-only lifecycle representation. Both heads advance atomically
    under the same current root authorization; callers cannot advance only one
    side through this supported surface.
    """

    def __init__(
        self,
        path,
        attested,
        bootstrap,
        signer,
        rotation_authority,
        enablement,
        recovery_authority,
        public_recovery_authority,
    ):
        if type(public_recovery_authority) is not PublicRecoveryAuthority:
            raise TypeError("exact LAB-085 PublicRecoveryAuthority required")
        self._lab085_custody_initializing = True
        super().__init__(
            path,
            attested,
            bootstrap,
            signer,
            rotation_authority,
            enablement,
            recovery_authority,
        )
        self.public_recovery_custody = AsymmetricRecoveryCustody(path, public_recovery_authority)
        self._init_custody_binding()
        self._lab085_custody_initializing = False
        self.verify_durable()

    @staticmethod
    def _compatible(symmetric: VersionedRecoveryAuthority, public: PublicRecoveryAuthority):
        symmetric.validate(); public.validate()
        if (
            symmetric.recovery.name != public.name
            or symmetric.version != public.version
            or symmetric.generation != public.generation
            or symmetric.recovery.threshold != public.threshold
        ):
            raise CustodyBindingError("symmetric/public recovery authority metadata mismatch")
        return True

    def _init_custody_binding(self):
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            q.execute(
                """
                CREATE TABLE IF NOT EXISTS provider_recovery_custody_bindings(
                  symmetric_authority_id TEXT PRIMARY KEY,
                  public_authority_id TEXT NOT NULL UNIQUE,
                  version INTEGER NOT NULL,
                  generation INTEGER NOT NULL
                )
                """
            )
            count = q.execute("SELECT COUNT(*) FROM provider_recovery_custody_bindings").fetchone()[0]
            symmetric = self.recovery_lifecycle.current_locked(q)
            recovery = self.recovery.current_recovery_locked(q)
            public = self.public_recovery_custody.current_locked(q)
            if recovery.authority_id != symmetric.recovery.authority_id:
                raise RecoveryAuthorityMismatch("LAB-084/LAB-085 recovery heads diverged")
            self._compatible(symmetric, public)
            if count == 0:
                symmetric_count = q.execute(
                    "SELECT COUNT(*) FROM provider_recovery_lifecycle_authorities"
                ).fetchone()[0]
                public_count = q.execute(
                    "SELECT COUNT(*) FROM provider_recovery_public_authorities"
                ).fetchone()[0]
                if symmetric_count != 1 or public_count != 1:
                    raise CustodyBindingError("refuse to auto-bind pre-existing unbound custody history")
                q.execute(
                    "INSERT INTO provider_recovery_custody_bindings VALUES(?,?,?,?)",
                    (symmetric.authority_id, public.authority_id, symmetric.version, symmetric.generation),
                )
            self._verify_custody_bindings_locked(q)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def _verify_custody_bindings_locked(self, q):
        symmetric_rows = q.execute(
            "SELECT authority_id FROM provider_recovery_lifecycle_authorities ORDER BY version"
        ).fetchall()
        public_rows = q.execute(
            "SELECT authority_id FROM provider_recovery_public_authorities ORDER BY version"
        ).fetchall()
        binding_rows = q.execute(
            "SELECT symmetric_authority_id,public_authority_id,version,generation "
            "FROM provider_recovery_custody_bindings ORDER BY version"
        ).fetchall()
        if not symmetric_rows or len(symmetric_rows) != len(public_rows) or len(binding_rows) != len(symmetric_rows):
            raise CustodyBindingError("recovery custody history cardinality mismatch")

        symmetric = [self.recovery_lifecycle._load_recovery_locked(q, row[0]) for row in symmetric_rows]
        public = [self.public_recovery_custody._load_authority_locked(q, row[0]) for row in public_rows]
        for s, p, binding in zip(symmetric, public, binding_rows):
            self._compatible(s, p)
            expected = (s.authority_id, p.authority_id, s.version, s.generation)
            if tuple(binding) != expected:
                raise CustodyBindingError("recovery custody binding substitution")

        for index in range(1, len(symmetric)):
            srow = q.execute(
                "SELECT old_authority_id,root_authority_id FROM provider_recovery_lifecycle_transitions "
                "WHERE new_authority_id=?",
                (symmetric[index].authority_id,),
            ).fetchone()
            prow = q.execute(
                "SELECT old_authority_id,root_authority_id FROM provider_recovery_public_transitions "
                "WHERE new_authority_id=?",
                (public[index].authority_id,),
            ).fetchone()
            if srow is None or prow is None:
                raise CustodyBindingError("missing symmetric/public custody transition pair")
            if srow[0] != symmetric[index - 1].authority_id or prow[0] != public[index - 1].authority_id:
                raise CustodyBindingError("recovery custody predecessor mismatch")
            if srow[1] != prow[1]:
                raise CustodyBindingError("symmetric/public rotation used different root authority")

        symmetric_head = self.recovery_lifecycle.current_locked(q)
        recovery_head = self.recovery.current_recovery_locked(q)
        public_head = self.public_recovery_custody.current_locked(q)
        if recovery_head.authority_id != symmetric_head.recovery.authority_id:
            raise RecoveryAuthorityMismatch("LAB-084/LAB-085 recovery heads diverged")
        self._compatible(symmetric_head, public_head)
        head_binding = q.execute(
            "SELECT public_authority_id,version,generation FROM provider_recovery_custody_bindings "
            "WHERE symmetric_authority_id=?",
            (symmetric_head.authority_id,),
        ).fetchone()
        if head_binding != (public_head.authority_id, symmetric_head.version, symmetric_head.generation):
            raise CustodyBindingError("current recovery custody heads are not bound")
        return True

    def recovery_custody_rotation_payloads(self, new_symmetric, new_public):
        if type(new_symmetric) is not VersionedRecoveryAuthority:
            raise TypeError("exact LAB-085 VersionedRecoveryAuthority required")
        if type(new_public) is not PublicRecoveryAuthority:
            raise TypeError("exact LAB-085 PublicRecoveryAuthority required")
        self._compatible(new_symmetric, new_public)
        q = self._con()
        try:
            q.execute("BEGIN")
            root = self.rotation_authority.current_locked(q)
            old_symmetric = self.recovery_lifecycle.current_locked(q)
            old_public = self.public_recovery_custody.current_locked(q)
            self._compatible(old_symmetric, old_public)
            symmetric_payload = self.recovery_lifecycle.make_intent(root, old_symmetric, new_symmetric).payload
            public_payload = custody_rotation_payload(old_public, new_public, root.authority_id)
            q.commit()
            return symmetric_payload, public_payload
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def rotate_recovery_authority(self, *args, **kwargs):
        raise CustodyBindingError(
            "public custody is enabled; use rotate_recovery_authority_with_custody so both heads advance atomically"
        )

    def rotate_recovery_authority_with_custody(
        self,
        new_symmetric,
        new_public,
        old_symmetric_signatures,
        new_symmetric_signatures,
        root_signatures,
        old_public_signatures,
        new_public_signatures,
    ):
        if type(new_symmetric) is not VersionedRecoveryAuthority:
            raise TypeError("exact LAB-085 VersionedRecoveryAuthority required")
        if type(new_public) is not PublicRecoveryAuthority:
            raise TypeError("exact LAB-085 PublicRecoveryAuthority required")
        self._compatible(new_symmetric, new_public)
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._reject_prepared_locked(q)
            self._verify_custody_bindings_locked(q)
            root = self.rotation_authority.current_locked(q)
            old_symmetric = self.recovery_lifecycle.current_locked(q)
            recovery_head = self.recovery.current_recovery_locked(q)
            old_public = self.public_recovery_custody.current_locked(q)
            if recovery_head.authority_id != old_symmetric.recovery.authority_id:
                raise RecoveryAuthorityMismatch("LAB-084/LAB-085 recovery heads diverged")
            self._compatible(old_symmetric, old_public)

            out = self.recovery_lifecycle.rotate_locked(
                q,
                root,
                new_symmetric,
                tuple(old_symmetric_signatures),
                tuple(new_symmetric_signatures),
                tuple(root_signatures),
            )
            self.recovery._insert_recovery_locked(q, new_symmetric.recovery)
            changed = q.execute(
                "UPDATE provider_rotation_recovery_head SET authority_id=?,generation=? "
                "WHERE singleton=1 AND authority_id=? AND generation=?",
                (
                    new_symmetric.recovery.authority_id,
                    new_symmetric.recovery.generation,
                    old_symmetric.recovery.authority_id,
                    old_symmetric.recovery.generation,
                ),
            ).rowcount
            if changed != 1:
                raise LifecycleRollback("LAB-084 recovery head changed during custody rotation")

            self.public_recovery_custody.rotate_locked(
                q,
                new_public,
                root.authority_id,
                tuple(old_public_signatures),
                tuple(new_public_signatures),
            )
            q.execute(
                "INSERT INTO provider_recovery_custody_bindings VALUES(?,?,?,?)",
                (new_symmetric.authority_id, new_public.authority_id, new_symmetric.version, new_symmetric.generation),
            )
            self._verify_custody_bindings_locked(q)
            q.commit()
            return {
                **out,
                "public_authority_id": new_public.authority_id,
                "symmetric_authority_id": new_symmetric.authority_id,
            }
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def verify_durable(self):
        if getattr(self, "_lab085_custody_initializing", False):
            return SupportedRecoveryAuthorityLifecycleLedger.verify_durable(self)
        SupportedRecoveryAuthorityLifecycleLedger.verify_durable(self)
        if not hasattr(self, "public_recovery_custody"):
            return True
        self.public_recovery_custody.verify_durable()
        q = self._con()
        try:
            q.execute("BEGIN")
            self._verify_custody_bindings_locked(q)
            q.commit()
            return True
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
