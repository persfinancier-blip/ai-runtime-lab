from __future__ import annotations

from experiments.anchor_attestation.protocol import AttestedCatchup
from experiments.asymmetric_provider_history.integration import PendingRotationBlocked
from experiments.asymmetric_provider_history.protocol import (
    GenerationSigner,
    InvalidTransition,
    TransitionProof,
)
from experiments.asymmetric_provider_history.supported import (
    SupportedAsymmetricHistoricalSharedAnchorLedger,
)

from .enablement import ThresholdEnablement, verify_enablement
from .protocol import DurableRotationAuthority, RotationAuthority, Signature
from .strict import require_canonical_authority


class SupportedThresholdAuthorizedAsymmetricProviderLedger(
    SupportedAsymmetricHistoricalSharedAnchorLedger
):
    """Audited LAB-083 surface.

    The LAB-083 cutoff is itself threshold-authorized. This prevents durable SQL
    metadata from moving the cutoff forward and silently reclassifying new
    threshold-governed provider transitions as legacy LAB-082 history.
    """

    def __init__(
        self,
        path,
        attested: AttestedCatchup,
        bootstrap,
        signer: GenerationSigner,
        rotation_authority: RotationAuthority,
        enablement: ThresholdEnablement,
    ):
        require_canonical_authority(rotation_authority)
        if type(enablement) is not ThresholdEnablement:
            raise TypeError("exact LAB-083 ThresholdEnablement required")
        super().__init__(path, attested, bootstrap, signer)
        self.rotation_authority = DurableRotationAuthority(path, rotation_authority)
        q = self._con()
        try:
            q.execute(
                """
                CREATE TABLE IF NOT EXISTS provider_rotation_threshold_enablement(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  start_provider_generation_id TEXT NOT NULL,
                  start_provider_generation INTEGER NOT NULL,
                  authority_id TEXT NOT NULL,
                  authority_version INTEGER NOT NULL,
                  authority_generation INTEGER NOT NULL,
                  enablement_digest TEXT NOT NULL,
                  signatures_json TEXT NOT NULL
                )
                """
            )
            if q.execute(
                "SELECT COUNT(*) FROM provider_rotation_threshold_enablement"
            ).fetchone()[0] == 0:
                q.execute("BEGIN IMMEDIATE")
                if q.execute(
                    "SELECT COUNT(*) FROM provider_rotation_threshold_proofs"
                ).fetchone()[0]:
                    raise InvalidTransition(
                        "threshold enablement missing after threshold-governed history"
                    )
                head = self.provider_history._current_locked(q)
                authority = self.rotation_authority.current_locked(q)
                require_canonical_authority(authority)
                if (
                    enablement.start_provider_generation_id != head.generation_id
                    or enablement.start_provider_generation != head.generation
                ):
                    raise InvalidTransition(
                        "threshold enablement does not bind current provider head"
                    )
                verify_enablement(authority, enablement)
                q.execute(
                    "INSERT INTO provider_rotation_threshold_enablement VALUES(1,?,?,?,?,?,?,?)",
                    (
                        enablement.start_provider_generation_id,
                        enablement.start_provider_generation,
                        enablement.authority_id,
                        enablement.authority_version,
                        enablement.authority_generation,
                        enablement.enablement_digest,
                        self.rotation_authority._encode_signatures(
                            enablement.signatures
                        ),
                    ),
                )
                q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
        self.verify_durable()

    def _load_enablement_locked(self, q):
        rows = q.execute(
            "SELECT start_provider_generation_id,start_provider_generation,authority_id,"
            "authority_version,authority_generation,enablement_digest,signatures_json "
            "FROM provider_rotation_threshold_enablement WHERE singleton=1"
        ).fetchall()
        if len(rows) != 1:
            raise InvalidTransition("missing threshold enablement")
        row = rows[0]
        authority = self.rotation_authority._load_locked(q, row[2])
        require_canonical_authority(authority)
        enablement = ThresholdEnablement(
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            self.rotation_authority._decode_signatures(row[6]),
        )
        if enablement.enablement_digest != row[5]:
            raise InvalidTransition("threshold enablement digest mismatch")
        verify_enablement(authority, enablement)
        start = self.provider_history._public_locked(
            q, enablement.start_provider_generation_id
        )
        if start.generation != enablement.start_provider_generation:
            raise InvalidTransition("threshold enablement provider identity mismatch")
        return enablement

    def rotate_provider(
        self,
        new_signer: GenerationSigner,
        continuity_proof: TransitionProof,
        new_attested: AttestedCatchup,
        threshold_signatures: tuple[Signature, ...],
    ):
        if type(new_signer) is not GenerationSigner:
            raise TypeError("exact LAB-082 GenerationSigner required")
        if type(new_attested) is not AttestedCatchup:
            raise TypeError("exact LAB-036 AttestedCatchup required")
        new = new_signer.public
        expected = new_attested.verifier.expected
        if (expected.provider_id, expected.generation) != (
            new.provider_id,
            new.generation,
        ):
            raise InvalidTransition(
                "new LAB-036 provider does not match Ed25519 generation"
            )
        challenge = new_attested.challenge()
        observed = new_attested.authenticated_read(
            challenge=challenge,
            request_id=f"threshold-provider-rotation-read:{new.generation}",
        )
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            pending = q.execute(
                "SELECT COUNT(*) FROM shared_anchor_intents WHERE status='PREPARED'"
            ).fetchone()[0]
            if pending:
                raise PendingRotationBlocked("unresolved PREPARED anchor intent")
            reserved = q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchone()[0]
            if observed.position != reserved:
                raise InvalidTransition(
                    "new provider position does not match durable ledger tail"
                )
            old = self.provider_history._current_locked(q)
            self.rotation_authority.authorize_provider_rotation_locked(
                q,
                provider_id=old.provider_id,
                old_generation_id=old.generation_id,
                new_generation_id=new.generation_id,
                signatures=threshold_signatures,
            )
            self.provider_history._rotate_locked(q, new, continuity_proof)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
        self.attested = new_attested
        self.signer = new_signer
        self._require_runtime_matches_durable_head()
        return new

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

    def verify_durable(self):
        super().verify_durable()
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
            current = self.rotation_authority.verify_durable_locked(q, transitions)
            require_canonical_authority(current)
            q.commit()
            return True
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
