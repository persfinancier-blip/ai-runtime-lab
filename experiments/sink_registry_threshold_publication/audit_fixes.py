from __future__ import annotations

from experiments.sink_capability_contract import protocol as cap
from experiments.sink_registry_binding import protocol as registry_base
from experiments.sink_registry_threshold_publication.integration import (
    ThresholdLifecycleRegistryBoundJournal,
    ThresholdLifecycleRegistryBrokerWorker,
)
from experiments.sink_registry_threshold_publication.protocol import (
    AuthorityMismatch,
    ProofSubstitution,
    ThresholdEnvelope,
    verify_envelope,
)
from experiments.transactional_broker_journal.protocol import StaleCredential


class CorrectedThresholdLifecycleRegistryBoundJournal(
    ThresholdLifecycleRegistryBoundJournal
):
    """Audited LAB-077 request/publication ordering.

    For an existing request, durable request identity wins before the caller's
    candidate envelope is interpreted. A CONFIRMED retry is therefore a pure
    receipt read and cannot publish a new registry successor.

    For a genuinely new request, authenticated capability-head observation,
    threshold registry publication, registry-head activation, credential-generation
    check, and broker INTENT creation occur in one ``BEGIN IMMEDIATE`` transaction.
    This closes the race where another worker could create/confirm the request
    between a precheck and publication.
    """

    def _existing_request_locked(self, q, request):
        row = q.execute(
            """
            SELECT request_digest,status,receipt,registry_entry_digest,
                   registry_generation,capability_sink_id
            FROM broker_requests WHERE request_id=?
            """,
            (request.request_id,),
        ).fetchone()
        if row is None:
            return None
        if row[0] != request.digest:
            raise registry_base.RegistryBindingError(
                "request_id reused with different content"
            )
        status, receipt, entry_digest, registry_generation, sink_id = row[1:]
        if (
            not isinstance(entry_digest, str)
            or type(registry_generation) is not int
            or not isinstance(sink_id, str)
            or not sink_id
        ):
            raise registry_base.CorruptRegistry(
                "existing request lacks atomic registry binding"
            )
        # Reverify the exact historical threshold proof bound to this request.
        historical = self._historical_locked(q, entry_digest).entry
        if (
            historical.sink_id != sink_id
            or historical.generation != registry_generation
        ):
            raise registry_base.CorruptRegistry(
                "existing request registry identity mismatch"
            )
        capplan = self.bound._load_binding(q, request.request_id)
        rplan = registry_base.DurableRegistryPlan(
            sink_id, entry_digest, registry_generation
        )
        return status, capplan, rplan, receipt

    def _observe_capability_locked(self, q, capability):
        claim = self.bound.verifier.verify(capability)
        att = capability.attestation
        row = q.execute(
            "SELECT capability_generation,claim_digest,probe_generation,issuer_id "
            "FROM sink_capability_heads WHERE sink_id=?",
            (claim.sink_id,),
        ).fetchone()
        identity = (
            claim.generation,
            att.claim_digest,
            att.probe_generation,
            att.issuer_id,
        )
        if row is None:
            q.execute(
                "INSERT INTO sink_capability_heads VALUES(?,?,?,?,?)",
                (claim.sink_id, *identity),
            )
        else:
            if claim.generation < row[0]:
                raise cap.StaleCapability("sink capability generation rolled back")
            if claim.generation == row[0] and tuple(row) != identity:
                raise cap.StaleCapability(
                    "same-generation sink capability substitution"
                )
            if claim.generation > row[0]:
                q.execute(
                    "UPDATE sink_capability_heads SET capability_generation=?,"
                    "claim_digest=?,probe_generation=?,issuer_id=? WHERE sink_id=?",
                    (*identity, claim.sink_id),
                )
        return claim

    def _publish_locked(self, q, envelope):
        if not isinstance(envelope, ThresholdEnvelope):
            raise registry_base.RegistryBindingError(
                "new LAB-077 publication requires a threshold envelope"
            )
        entry = envelope.entry
        entry_digest = entry.entry_digest
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
        return entry

    def reserve(self, request, capability, envelope, *, now):
        if type(now) is not int or now < 0:
            raise registry_base.RegistryBindingError("invalid time")

        # Verify capability cryptography outside the SQL transaction; its durable
        # head is re-read/updated under the transaction below.
        claim = self.bound.verifier.verify(capability)
        policy = cap.derive_policy(
            capability, self.bound.verifier, now=now, key_created_at=now
        )
        if policy in {"READ_ONLY", "NO_AUTOMATIC_RETRY"}:
            raise registry_base.RegistryBindingError(
                "new execution lacks safe retry authority"
            )

        q = self.journal._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            existing = self._existing_request_locked(q, request)
            if existing is not None:
                q.commit()
                return existing

            if not isinstance(envelope, ThresholdEnvelope):
                raise registry_base.RegistryBindingError(
                    "new LAB-077 reservations require a threshold envelope"
                )
            entry = envelope.entry
            self._observe_capability_locked(q, capability)
            self._publish_locked(q, envelope)
            if claim.sink_id != entry.sink_id:
                raise registry_base.RegistryBindingError(
                    "capability sink differs from registry sink"
                )

            current_generation = q.execute(
                "SELECT credential_generation FROM broker_meta WHERE singleton=1"
            ).fetchone()[0]
            if request.credential_generation != current_generation:
                raise StaleCredential("new request uses stale credential generation")
            effect_key = self.journal._effect_key(request)
            att = capability.attestation
            q.execute(
                """
                INSERT INTO broker_requests(
                  request_id,request_digest,task_id,scope,credential_generation,
                  effect_key,status,receipt,capability_sink_id,
                  capability_generation,capability_claim_digest,
                  capability_probe_generation,capability_issuer_id,
                  capability_policy,capability_key_created_at,
                  registry_entry_digest,registry_generation
                ) VALUES(?,?,?,?,?,?,'INTENT',NULL,?,?,?,?,?,?,?,?,?)
                """,
                (
                    request.request_id,
                    request.digest,
                    request.task_id,
                    request.scope,
                    request.credential_generation,
                    effect_key,
                    claim.sink_id,
                    claim.generation,
                    att.claim_digest,
                    att.probe_generation,
                    att.issuer_id,
                    policy,
                    now,
                    entry.entry_digest,
                    entry.generation,
                ),
            )
            capplan = self.bound._load_binding(q, request.request_id)
            rplan = registry_base.DurableRegistryPlan(
                entry.sink_id, entry.entry_digest, entry.generation
            )
            q.commit()
            return "INTENT", capplan, rplan, None
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()


class CorrectedThresholdLifecycleRegistryBrokerWorker(
    ThresholdLifecycleRegistryBrokerWorker
):
    """Exact-type gate for the audited LAB-077 journal."""

    def __init__(self, registry, runtime, secret):
        if type(registry) is not CorrectedThresholdLifecycleRegistryBoundJournal:
            raise registry_base.RegistryBindingError(
                "supported LAB-077 worker requires audited threshold journal"
            )
        registry_base.RegistryBrokerWorker.__init__(self, registry, runtime, secret)
