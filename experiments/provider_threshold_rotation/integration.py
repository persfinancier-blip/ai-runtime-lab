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

from .protocol import (
    DurableRotationAuthority,
    RotationAuthority,
    Signature,
)


class ThresholdAuthorizedAsymmetricProviderLedger(
    SupportedAsymmetricHistoricalSharedAnchorLedger
):
    """LAB-083 supported integration.

    Provider generation rotation retains LAB-082 old/new Ed25519 continuity proof
    and additionally requires a separately durable threshold authorization. Both
    proofs and provider-head advancement are committed in the same SQLite write
    transaction that excludes PREPARED shared-anchor work.
    """

    def __init__(
        self,
        path,
        attested: AttestedCatchup,
        bootstrap,
        signer: GenerationSigner,
        rotation_authority: RotationAuthority,
    ):
        super().__init__(path, attested, bootstrap, signer)
        self.rotation_authority = DurableRotationAuthority(path, rotation_authority)
        q = self._con()
        try:
            q.execute(
                """
                CREATE TABLE IF NOT EXISTS provider_rotation_threshold_meta(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  start_provider_generation_id TEXT NOT NULL,
                  start_provider_generation INTEGER NOT NULL,
                  start_authority_id TEXT NOT NULL
                )
                """
            )
            if q.execute(
                "SELECT COUNT(*) FROM provider_rotation_threshold_meta"
            ).fetchone()[0] == 0:
                head = self.provider_history._current_locked(q)
                authority = self.rotation_authority.current_locked(q)
                q.execute(
                    "INSERT INTO provider_rotation_threshold_meta VALUES(1,?,?,?)",
                    (head.generation_id, head.generation, authority.authority_id),
                )
                q.commit()
        finally:
            q.close()
        self.verify_durable()

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
            meta = q.execute(
                "SELECT start_provider_generation_id,start_provider_generation,start_authority_id "
                "FROM provider_rotation_threshold_meta WHERE singleton=1"
            ).fetchall()
            if len(meta) != 1:
                raise InvalidTransition("missing threshold migration boundary")
            start_gid, start_generation, start_authority_id = meta[0]
            start = self.provider_history._public_locked(q, start_gid)
            if start.generation != start_generation:
                raise InvalidTransition("threshold start provider identity mismatch")
            if (
                q.execute(
                    "SELECT COUNT(*) FROM provider_rotation_authorities WHERE authority_id=?",
                    (start_authority_id,),
                ).fetchone()[0]
                != 1
            ):
                raise InvalidTransition("threshold start authority missing")

            rows = q.execute(
                "SELECT t.provider_id,t.old_generation_id,t.new_generation_id,g.generation "
                "FROM asymmetric_provider_transitions t "
                "JOIN asymmetric_provider_generations g "
                "ON g.generation_id=t.new_generation_id "
                "WHERE g.generation>? ORDER BY g.generation",
                (start_generation,),
            ).fetchall()
            transitions = [(r[0], r[1], r[2]) for r in rows]
            self.rotation_authority.verify_durable_locked(q, transitions)
            q.commit()
            return True
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
