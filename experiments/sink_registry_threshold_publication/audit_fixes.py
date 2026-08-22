from __future__ import annotations

from experiments.sink_registry_binding import audit_fixes as registry_audited
from experiments.sink_registry_binding import protocol as registry_base
from experiments.sink_registry_threshold_publication.integration import (
    ThresholdLifecycleRegistryBoundJournal,
    ThresholdLifecycleRegistryBrokerWorker,
)
from experiments.sink_registry_threshold_publication.protocol import ThresholdEnvelope


class CorrectedThresholdLifecycleRegistryBoundJournal(
    ThresholdLifecycleRegistryBoundJournal
):
    """Audited LAB-077 request/publication ordering.

    Existing durable requests are resolved before any candidate envelope is allowed
    to create new registry publication. In particular, a CONFIRMED retry is a pure
    receipt read and cannot move the registry head as a side effect.
    """

    def reserve(self, request, capability, envelope, *, now):
        q = self.journal._con()
        try:
            row = q.execute(
                "SELECT request_digest,status FROM broker_requests WHERE request_id=?",
                (request.request_id,),
            ).fetchone()
        finally:
            q.close()

        if row is not None:
            if row[0] != request.digest:
                raise registry_base.RegistryBindingError(
                    "request_id reused with different content"
                )
            # CorrectedRegistryBoundJournal checks CONFIRMED before touching the
            # caller-provided registry entry. For INTENT/UNKNOWN, the envelope's
            # entry must already be historical; observe(entry) is historical-only
            # on LAB-077 and can never create publication authority.
            entry = envelope.entry if isinstance(envelope, ThresholdEnvelope) else envelope
            return registry_audited.CorrectedRegistryBoundJournal.reserve(
                self, request, capability, entry, now=now
            )

        if not isinstance(envelope, ThresholdEnvelope):
            raise registry_base.RegistryBindingError(
                "new LAB-077 reservations require a threshold envelope"
            )
        entry = self.observe(envelope)
        return registry_audited.CorrectedRegistryBoundJournal.reserve(
            self, request, capability, entry, now=now
        )


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
