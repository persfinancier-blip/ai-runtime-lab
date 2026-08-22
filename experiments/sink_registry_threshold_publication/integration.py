from __future__ import annotations

import json

from experiments.sink_registry_authority_lifecycle import audit_fixes as lifecycle_audited
from experiments.sink_registry_authority_lifecycle import protocol as lifecycle_base
from experiments.sink_registry_binding import audit_fixes as registry_audited
from experiments.sink_registry_binding import protocol as registry_base
from experiments.sink_registry_threshold_publication.protocol import (
    AuthorityMismatch,
    ProofSubstitution,
    ThresholdEnvelope,
    ThresholdProof,
    verify_envelope,
)
from experiments.anchor_threshold_root.protocol import Signature


class ThresholdHistoricalMissing(ProofSubstitution):
    pass


class _ThresholdHistoricalAuthorityAdapter:
    """Read-only authority adapter for already threshold-published entries."""

    def __init__(self, owner):
        self.owner = owner

    def verify(self, entry):
        historical = self.owner.verify_historical_entry(entry.entry_digest)
        if historical != entry:
            raise ProofSubstitution(
                "entry bytes differ from durable threshold publication"
            )
        return historical


class ThresholdLifecycleRegistryBoundJournal(
    lifecycle_audited.CorrectedLifecycleRegistryBoundJournal
):
    """Supported LAB-077 publication boundary.

    A never-before-published mapping is accepted only as a ``ThresholdEnvelope``.
    The exact current LAB-076 root, threshold proof, historical binding, registry
    row and registry head are checked/persisted in one SQLite ``BEGIN IMMEDIATE``
    transaction. A bare ``RegistryEntry`` is historical/read-only and can never
    create publication authority.
    """

    def __init__(self, bound, lifecycle):
        if type(lifecycle) is not lifecycle_audited.ConsistentDurableRegistryAuthority:
            raise registry_base.RegistryBindingError(
                "LAB-077 requires the audited LAB-076 lifecycle authority"
            )
        super().__init__(bound, lifecycle)
        self._migrate_threshold_proofs()
        self.authority = _ThresholdHistoricalAuthorityAdapter(self)

    def _migrate_threshold_proofs(self):
        q = self.journal._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            q.execute(
                """
                CREATE TABLE IF NOT EXISTS registry_threshold_publications(
                  entry_digest TEXT PRIMARY KEY,
                  proof_json TEXT NOT NULL,
                  proof_digest TEXT NOT NULL,
                  authority_id TEXT NOT NULL,
                  authority_version INTEGER NOT NULL
                )
                """
            )
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    @staticmethod
    def _proof_json(proof):
        return json.dumps(
            proof.canonical, sort_keys=True, separators=(",", ":")
        )

    @staticmethod
    def _parse_proof(raw):
        try:
            p = json.loads(raw)
            if not isinstance(p, dict):
                raise TypeError("proof object")
            signatures = p["signatures"]
            if not isinstance(signatures, list):
                raise TypeError("signature list")
            return ThresholdProof(
                p["authority_id"],
                p["authority_version"],
                tuple(
                    Signature(item["signer_id"], item["signature"])
                    for item in signatures
                ),
            )
        except Exception as exc:
            raise ProofSubstitution("malformed durable threshold proof") from exc

    def _current_locked(self, q):
        row = q.execute(
            "SELECT authority_id,version,epoch FROM registry_authority_head "
            "WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise lifecycle_base.AuthoritySubstitution(
                "missing registry authority head"
            )
        root = self.lifecycle._load_root(q, row[0])
        if (root.version, root.authority_epoch) != (row[1], row[2]):
            raise lifecycle_base.AuthoritySubstitution(
                "registry authority head relational mismatch"
            )
        return row[0], root

    def _historical_locked(self, q, entry_digest):
        row = q.execute(
            "SELECT proof_json,proof_digest,authority_id,authority_version "
            "FROM registry_threshold_publications WHERE entry_digest=?",
            (entry_digest,),
        ).fetchone()
        if row is None:
            raise ThresholdHistoricalMissing(entry_digest)
        entry = self._load_entry(q, entry_digest)
        proof = self._parse_proof(row[0])
        if proof.proof_digest != row[1] or entry.signature != row[1]:
            raise ProofSubstitution("durable threshold proof digest mismatch")
        root = self.lifecycle._load_root(q, row[2])
        if root.version != row[3]:
            raise ProofSubstitution("historical threshold authority version mismatch")
        envelope = ThresholdEnvelope(entry, proof)
        verify_envelope(root, envelope)
        return envelope

    def verify_historical_entry(self, entry_digest):
        q = self.journal._con()
        try:
            return self._historical_locked(q, entry_digest).entry
        finally:
            q.close()

    def _observe_historical_only(self, entry):
        q = self.journal._con()
        try:
            q.execute("BEGIN")
            envelope = self._historical_locked(q, entry.entry_digest)
            if envelope.entry != entry:
                raise ProofSubstitution(
                    "historical entry differs from threshold-published bytes"
                )
            head = q.execute(
                "SELECT entry_digest,generation FROM sink_registry_heads "
                "WHERE sink_id=?",
                (entry.sink_id,),
            ).fetchone()
            if head is None or entry.generation > head[1]:
                raise registry_base.CorruptRegistry(
                    "historical entry is not represented by registry history"
                )
            q.commit()
            return entry
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def observe(self, candidate):
        if not isinstance(candidate, ThresholdEnvelope):
            # Bare entries are never publication authority on the supported surface.
            return self._observe_historical_only(candidate)

        envelope = candidate
        entry = envelope.entry
        entry_digest = entry.entry_digest
        q = self.journal._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            registry_row = q.execute(
                "SELECT entry_digest,sink_id,generation,adapter_digest,endpoint_origin,"
                "operation_profile,predecessor_entry_digest,issuer_id,issuer_generation,signature "
                "FROM sink_registry_entries WHERE entry_digest=?",
                (entry_digest,),
            ).fetchone()
            proof_row = q.execute(
                "SELECT proof_json,proof_digest,authority_id,authority_version "
                "FROM registry_threshold_publications WHERE entry_digest=?",
                (entry_digest,),
            ).fetchone()

            if registry_row is not None:
                if proof_row is None:
                    raise ProofSubstitution(
                        "published registry row lacks durable threshold proof"
                    )
                stored = self._row_entry(registry_row)
                historical = self._historical_locked(q, entry_digest)
                if historical.entry != stored or stored != entry:
                    raise registry_base.RegistrySubstitution(
                        "stored registry row differs from threshold envelope"
                    )
                if self._proof_json(historical.proof) != self._proof_json(envelope.proof):
                    raise ProofSubstitution(
                        "historical publication presented with different proof set"
                    )
            else:
                if proof_row is not None:
                    # A proof collected/persisted outside publication is not a right
                    # to activate an entry later under an old authority.
                    raise ProofSubstitution(
                        "unpublished registry mapping has orphan threshold proof"
                    )
                authority_id, current = self._current_locked(q)
                verify_envelope(current, envelope)
                if envelope.proof.authority_id != authority_id:
                    raise AuthorityMismatch(
                        "threshold proof does not name current durable authority"
                    )

            head = q.execute(
                "SELECT entry_digest,generation FROM sink_registry_heads WHERE sink_id=?",
                (entry.sink_id,),
            ).fetchone()
            if head is None:
                if entry.generation != 1 or entry.predecessor_entry_digest is not None:
                    raise registry_base.RegistryRollback("invalid registry bootstrap")
            else:
                if entry.generation < head[1]:
                    raise registry_base.RegistryRollback("registry generation rollback")
                if entry.generation == head[1]:
                    if entry_digest != head[0]:
                        raise registry_base.RegistrySubstitution(
                            "same-generation registry substitution"
                        )
                    q.commit()
                    return entry
                if (
                    entry.generation != head[1] + 1
                    or entry.predecessor_entry_digest != head[0]
                ):
                    raise registry_base.RegistryRollback(
                        "successor must name exact current predecessor"
                    )

            if registry_row is None:
                q.execute(
                    "INSERT INTO sink_registry_entries VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (
                        entry_digest,
                        entry.sink_id,
                        entry.generation,
                        entry.adapter_digest,
                        entry.endpoint_origin,
                        entry.operation_profile,
                        entry.predecessor_entry_digest,
                        entry.issuer_id,
                        entry.issuer_generation,
                        entry.signature,
                    ),
                )
                q.execute(
                    "INSERT INTO registry_threshold_publications VALUES(?,?,?,?,?)",
                    (
                        entry_digest,
                        self._proof_json(envelope.proof),
                        envelope.proof.proof_digest,
                        envelope.proof.authority_id,
                        envelope.proof.authority_version,
                    ),
                )

            stored = self._load_entry(q, entry_digest)
            historical = self._historical_locked(q, entry_digest)
            if historical.entry != stored or stored != entry:
                raise registry_base.RegistrySubstitution(
                    "registry row / threshold proof mismatch before activation"
                )

            if head is None:
                q.execute(
                    "INSERT INTO sink_registry_heads VALUES(?,?,?)",
                    (entry.sink_id, entry_digest, entry.generation),
                )
            elif entry.generation > head[1]:
                changed = q.execute(
                    "UPDATE sink_registry_heads SET entry_digest=?,generation=? "
                    "WHERE sink_id=? AND entry_digest=? AND generation=?",
                    (
                        entry_digest,
                        entry.generation,
                        entry.sink_id,
                        head[0],
                        head[1],
                    ),
                ).rowcount
                if changed != 1:
                    raise registry_base.RegistryRollback(
                        "registry head changed before threshold activation"
                    )
            q.commit()
            return entry
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def reserve(self, request, capability, envelope, *, now):
        if not isinstance(envelope, ThresholdEnvelope):
            raise registry_base.RegistryBindingError(
                "new LAB-077 reservations require a threshold envelope"
            )
        entry = self.observe(envelope)
        # The audited LAB-075 reserve path calls self.observe(entry) again. Our
        # bare-entry branch is historical-only, so it cannot recreate publication
        # authority and only re-verifies the proof already committed above.
        return registry_audited.CorrectedRegistryBoundJournal.reserve(
            self, request, capability, entry, now=now
        )

    def verify_durable(self):
        guard = self.journal._con()
        try:
            guard.execute("BEGIN IMMEDIATE")
            lifecycle_base.DurableRegistryAuthority.verify_durable(self.lifecycle)
            registry_audited.CorrectedRegistryBoundJournal.verify_durable(self)

            entries = {
                row[0]
                for row in guard.execute(
                    "SELECT entry_digest FROM sink_registry_entries"
                ).fetchall()
            }
            proofs = {
                row[0]
                for row in guard.execute(
                    "SELECT entry_digest FROM registry_threshold_publications"
                ).fetchall()
            }
            if entries != proofs:
                raise ProofSubstitution(
                    "registry entries and threshold proof set differ"
                )
            for entry_digest in sorted(entries):
                self._historical_locked(guard, entry_digest)
            guard.commit()
            return True
        except:
            if guard.in_transaction:
                guard.rollback()
            raise
        finally:
            guard.close()


class ThresholdLifecycleRegistryBrokerWorker(
    registry_audited.CorrectedRegistryBrokerWorker
):
    """Exact-type-gated worker; no single-signature publication surface."""

    def __init__(self, registry, runtime, secret):
        if type(registry) is not ThresholdLifecycleRegistryBoundJournal:
            raise registry_base.RegistryBindingError(
                "LAB-077 worker requires threshold-aware audited journal"
            )
        registry_base.RegistryBrokerWorker.__init__(self, registry, runtime, secret)
