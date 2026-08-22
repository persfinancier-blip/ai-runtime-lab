from __future__ import annotations

from experiments.sink_capability_contract import protocol as cap
from experiments.sink_registry_binding import protocol as registry_base
from experiments.sink_registry_threshold_publication.audit_fixes import (
    CorrectedThresholdLifecycleRegistryBoundJournal,
    CorrectedThresholdLifecycleRegistryBrokerWorker,
)
from experiments.sink_registry_threshold_publication.protocol import ThresholdEnvelope
from experiments.transactional_broker_journal.protocol import StaleCredential


class FinalThresholdLifecycleRegistryBoundJournal(
    CorrectedThresholdLifecycleRegistryBoundJournal
):
    """Final audited LAB-077 request/publication boundary.

    One write transaction decides whether the request already exists. CONFIRMED is
    returned without interpreting caller capability/envelope. INTENT/UNKNOWN still
    require a currently authenticated capability but cannot publish caller-provided
    registry state. Only a genuinely absent request may threshold-publish a new
    mapping, and that publication is committed atomically with capability head and
    broker INTENT creation.
    """

    @staticmethod
    def _same_capability(plan, capability):
        claim = capability.claim
        att = capability.attestation
        return (
            claim.generation == plan.capability_generation
            and att.claim_digest == plan.claim_digest
            and att.probe_generation == plan.probe_generation
            and att.issuer_id == plan.issuer_id
        )

    def reserve(self, request, capability, envelope, *, now):
        if type(now) is not int or now < 0:
            raise registry_base.RegistryBindingError("invalid time")

        q = self.journal._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            existing = self._existing_request_locked(q, request)
            if existing is not None:
                status, capplan, rplan, receipt = existing
                if status == "CONFIRMED":
                    q.commit()
                    return existing

                # Nonterminal work still depends on current authenticated sink
                # capability. The caller's envelope is ignored: registry identity is
                # already durable in rplan and cannot be republished on retry.
                claim = self.bound.verifier.verify(capability)
                if claim.sink_id != rplan.sink_id:
                    raise cap.StaleCapability(
                        "current capability sink differs from durable request"
                    )

                if status == "INTENT":
                    # An effect that has not reached UNKNOWN/commit ambiguity may
                    # execute only under the exact capability that authorized it.
                    if not self._same_capability(capplan, capability):
                        raise cap.StaleCapability(
                            "pending INTENT cannot inherit rotated capability authority"
                        )
                    policy = cap.derive_policy(
                        capability,
                        self.bound.verifier,
                        now=now,
                        key_created_at=capplan.key_created_at,
                    )
                    if policy in {"READ_ONLY", "NO_AUTOMATIC_RETRY"}:
                        raise registry_base.HistoricalExecutionBlocked(
                            "current capability no longer permits pending execution"
                        )
                elif status == "UNKNOWN":
                    if claim.generation < capplan.capability_generation:
                        raise cap.StaleCapability(
                            "UNKNOWN reconciliation cannot use older capability"
                        )
                    if claim.generation == capplan.capability_generation:
                        if not self._same_capability(capplan, capability):
                            raise cap.StaleCapability(
                                "same-generation capability changed after UNKNOWN"
                            )
                        policy = cap.derive_policy(
                            capability,
                            self.bound.verifier,
                            now=now,
                            key_created_at=capplan.key_created_at,
                        )
                        if policy != "SAFE_RETRY_RECONCILE":
                            raise registry_base.HistoricalExecutionBlocked(
                                "UNKNOWN requires reconciliation authority"
                            )
                    else:
                        # A later capability may reconcile evidence of a possibly
                        # committed effect, but cannot grant re-execution authority.
                        if claim.reconcile_by_key is not True:
                            raise registry_base.HistoricalExecutionBlocked(
                                "rotated capability does not authorize reconciliation"
                            )
                else:
                    raise registry_base.CorruptRegistry(
                        "unexpected nonterminal broker status"
                    )

                self._observe_capability_locked(q, capability)
                q.commit()
                return existing

            if not isinstance(envelope, ThresholdEnvelope):
                raise registry_base.RegistryBindingError(
                    "new LAB-077 reservations require a threshold envelope"
                )

            # Cryptographic verification is pure. Durable capability observation,
            # threshold publication, and request reservation remain under this same
            # SQL writer transaction.
            claim = self.bound.verifier.verify(capability)
            policy = cap.derive_policy(
                capability, self.bound.verifier, now=now, key_created_at=now
            )
            if policy in {"READ_ONLY", "NO_AUTOMATIC_RETRY"}:
                raise registry_base.RegistryBindingError(
                    "new execution lacks safe retry authority"
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


class FinalThresholdLifecycleRegistryBrokerWorker(
    CorrectedThresholdLifecycleRegistryBrokerWorker
):
    """Exact-type gate for the final LAB-077 journal."""

    def __init__(self, registry, runtime, secret):
        if type(registry) is not FinalThresholdLifecycleRegistryBoundJournal:
            raise registry_base.RegistryBindingError(
                "supported LAB-077 worker requires final threshold journal"
            )
        registry_base.RegistryBrokerWorker.__init__(self, registry, runtime, secret)
