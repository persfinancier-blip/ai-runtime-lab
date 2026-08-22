from __future__ import annotations

import hmac

from experiments.asymmetric_provider_history.integration import PendingRotationBlocked
from experiments.asymmetric_provider_history.supported import SupportedAsymmetricHistoricalSharedAnchorLedger
from experiments.provider_threshold_rotation.protocol import (
    InvalidAuthority,
    ProviderRotationIntent,
    RotationAuthority,
    Signature,
    StaleAuthority,
    ThresholdNotMet,
    ThresholdProof,
    mac,
    sha,
    verify_threshold,
)
from experiments.provider_threshold_rotation.strict import require_canonical_authority
from experiments.provider_threshold_rotation.supported import (
    SupportedThresholdAuthorizedAsymmetricProviderLedger,
)

from .protocol import DurableRecoveryController, RecoveryAuthority, RecoveryError


class SupportedRecoveryThresholdProviderLedger(
    SupportedThresholdAuthorizedAsymmetricProviderLedger
):
    """LAB-084 supported surface with mixed normal/recovery authority history.

    Provider rotation, normal authority rotation, and break-glass recovery all
    serialize against unresolved LAB-080 PREPARED work under one SQLite write
    transaction. Recovery is a distinct proof edge; it never retroactively turns
    a recovery edge into a normal LAB-083 quorum edge.
    """

    def __init__(
        self,
        path,
        attested,
        bootstrap,
        signer,
        rotation_authority,
        enablement,
        recovery_authority: RecoveryAuthority,
    ):
        if type(recovery_authority) is not RecoveryAuthority:
            raise TypeError("exact LAB-084 RecoveryAuthority required")
        super().__init__(
            path, attested, bootstrap, signer, rotation_authority, enablement
        )
        self.recovery = DurableRecoveryController(
            path, self.rotation_authority, recovery_authority
        )
        self.verify_durable()

    @staticmethod
    def _reject_prepared_locked(q):
        pending = q.execute(
            "SELECT COUNT(*) FROM shared_anchor_intents WHERE status='PREPARED'"
        ).fetchone()[0]
        if pending:
            raise PendingRotationBlocked("unresolved PREPARED anchor intent")

    def rotate_rotation_authority(
        self,
        new_authority: RotationAuthority,
        old_signatures: tuple[Signature, ...],
        new_signatures: tuple[Signature, ...],
    ):
        require_canonical_authority(new_authority)
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._reject_prepared_locked(q)
            result = self.rotation_authority.rotate_authority_locked(
                q, new_authority, old_signatures, new_signatures
            )
            q.commit()
            return result
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def recover_rotation_authority(
        self,
        new_authority: RotationAuthority,
        recovery_signatures: tuple[Signature, ...],
    ):
        require_canonical_authority(new_authority)
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._reject_prepared_locked(q)
            result = self.recovery.recover_locked(
                q, new_authority, recovery_signatures
            )
            q.commit()
            return result
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def _verify_normal_edge_locked(self, q, old, new):
        row = q.execute(
            "SELECT old_authority_id,payload_digest,old_signatures_json,new_signatures_json "
            "FROM provider_rotation_authority_transitions WHERE new_authority_id=?",
            (new.authority_id,),
        ).fetchone()
        if row is None or row[0] != old.authority_id:
            raise InvalidAuthority("missing/incorrect normal authority transition")
        payload = self.rotation_authority.authority_rotation_payload(old, new)
        if row[1] != sha(payload):
            raise InvalidAuthority("normal authority transition digest mismatch")
        for authority, raw in ((old, row[2]), (new, row[3])):
            seen = set()
            valid = 0
            for sig in self.rotation_authority._decode_signatures(raw):
                if sig.signer_id in seen or sig.signer_id in set(authority.revoked):
                    continue
                seen.add(sig.signer_id)
                hx = authority.keys.get(sig.signer_id)
                if hx and hmac.compare_digest(
                    mac(bytes.fromhex(hx), payload), sig.signature
                ):
                    valid += 1
            if valid < authority.threshold:
                raise ThresholdNotMet(
                    "persisted normal authority transition below threshold"
                )

    def _verify_mixed_authority_history_locked(self, q, provider_transitions):
        rows = q.execute(
            "SELECT authority_id FROM provider_rotation_authorities ORDER BY version"
        ).fetchall()
        if not rows:
            raise InvalidAuthority("missing authority history")
        authorities = [
            self.rotation_authority._load_locked(q, row[0]) for row in rows
        ]
        if authorities[0].authority_id != self.rotation_authority.bootstrap.authority_id:
            raise StaleAuthority("authority bootstrap changed")
        for old, new in zip(authorities, authorities[1:]):
            normal = q.execute(
                "SELECT COUNT(*) FROM provider_rotation_authority_transitions "
                "WHERE new_authority_id=?",
                (new.authority_id,),
            ).fetchone()[0]
            recovery = q.execute(
                "SELECT COUNT(*) FROM provider_rotation_recovery_transitions "
                "WHERE new_rotation_authority_id=?",
                (new.authority_id,),
            ).fetchone()[0]
            if normal + recovery != 1:
                raise RecoveryError(
                    "authority edge must have exactly one normal or recovery proof"
                )
            if normal:
                self._verify_normal_edge_locked(q, old, new)
            else:
                self.recovery.verify_recovery_transition_locked(q, old, new)
        head = self.rotation_authority.current_locked(q)
        if head.authority_id != authorities[-1].authority_id:
            raise StaleAuthority("authority head rollback")

        by_id = {a.authority_id: a for a in authorities}
        for provider_id, old_gid, new_gid in provider_transitions:
            row = q.execute(
                "SELECT authority_id,authority_version,authority_generation,intent_digest,signatures_json "
                "FROM provider_rotation_threshold_proofs WHERE new_provider_generation_id=?",
                (new_gid,),
            ).fetchone()
            if row is None:
                raise ThresholdNotMet("provider transition missing threshold proof")
            authority = by_id.get(row[0])
            if authority is None:
                raise InvalidAuthority(
                    "threshold proof references unknown historical authority"
                )
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
        # Deliberately bypass LAB-083's normal-only authority-history verifier;
        # LAB-082 still verifies provider/receipt history first.
        SupportedAsymmetricHistoricalSharedAnchorLedger.verify_durable(self)
        if not hasattr(self, "rotation_authority"):
            return True
        q = self._con()
        try:
            q.execute("BEGIN")
            enablement = self._load_enablement_locked(q)
            rows = q.execute(
                "SELECT t.provider_id,t.old_generation_id,t.new_generation_id,g.generation "
                "FROM asymmetric_provider_transitions t "
                "JOIN asymmetric_provider_generations g "
                "ON g.generation_id=t.new_generation_id "
                "WHERE g.generation>? ORDER BY g.generation",
                (enablement.start_provider_generation,),
            ).fetchall()
            transitions = [(r[0], r[1], r[2]) for r in rows]
            if hasattr(self, "recovery"):
                self.recovery.current_recovery_locked(q)
                self._verify_mixed_authority_history_locked(q, transitions)
            else:
                self.rotation_authority.verify_durable_locked(q, transitions)
            q.commit()
            return True
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
