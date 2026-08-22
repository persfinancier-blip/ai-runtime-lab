from __future__ import annotations

from experiments.sink_registry_binding import audit_fixes as registry_audited
from experiments.sink_registry_binding import protocol as registry_base
from experiments.sink_registry_authority_lifecycle import integration as lifecycle_integration
from experiments.sink_registry_authority_lifecycle import protocol as lifecycle_base


class _StrictHistoricalAuthorityAdapter:
    """Supported read-path authority.

    Publication is owned by ``LifecycleRegistryBoundJournal.observe``. Any entry
    reaching inherited LAB-075 read/reserve/verification paths must already have
    an exact durable historical binding. Missing history is corruption, not an
    invitation to reinterpret the entry under current publication authority.
    """

    def __init__(self, lifecycle):
        self.lifecycle = lifecycle

    def verify(self, entry):
        historical = self.lifecycle.verify_historical_entry(entry.entry_digest)
        if historical != entry:
            raise lifecycle_base.AuthoritySubstitution(
                "historical entry bytes differ from durable authority binding"
            )
        return historical


class ConsistentDurableRegistryAuthority(lifecycle_base.DurableRegistryAuthority):
    """Audited standalone lifecycle with one stable SQLite verification window."""

    def verify_durable(self, bootstrap=None, recovery=None):
        guard = self._con()
        try:
            # BEGIN IMMEDIATE prevents a concurrent rotation/recovery commit while
            # the base verifier performs its multiple read queries on another
            # connection. This converts the prototype's mixed-autocommit reads
            # into one stable verification window without duplicating its logic.
            guard.execute("BEGIN IMMEDIATE")
            result = lifecycle_base.DurableRegistryAuthority.verify_durable(
                self, bootstrap, recovery
            )
            guard.commit()
            return result
        except:
            if guard.in_transaction:
                guard.rollback()
            raise
        finally:
            guard.close()


class CorrectedLifecycleRegistryBoundJournal(
    lifecycle_integration.LifecycleRegistryBoundJournal
):
    """Supported LAB-076 registry/journal composition.

    It removes current-authority fallback from inherited read paths and verifies
    lifecycle + LAB-075 durable state while one SQLite writer guard prevents a
    concurrent authority/publication transition from changing the database.
    """

    def __init__(self, bound, lifecycle):
        if type(lifecycle) is not ConsistentDurableRegistryAuthority:
            raise registry_base.RegistryBindingError(
                "supported LAB-076 journal requires audited lifecycle authority"
            )
        super().__init__(bound, lifecycle)
        self.authority = _StrictHistoricalAuthorityAdapter(lifecycle)

    def verify_durable(self):
        guard = self.journal._con()
        try:
            guard.execute("BEGIN IMMEDIATE")
            # The guard already excludes competing commits. Call the base
            # lifecycle verifier directly to avoid trying to acquire a second
            # BEGIN IMMEDIATE through the standalone audited wrapper.
            lifecycle_base.DurableRegistryAuthority.verify_durable(self.lifecycle)
            result = registry_audited.CorrectedRegistryBoundJournal.verify_durable(
                self
            )
            guard.commit()
            return result
        except:
            if guard.in_transaction:
                guard.rollback()
            raise
        finally:
            guard.close()


class CorrectedLifecycleRegistryBrokerWorker(
    registry_audited.CorrectedRegistryBrokerWorker
):
    """Exact-type-gated worker for the audited LAB-076 composition."""

    def __init__(self, registry, runtime, secret):
        if type(registry) is not CorrectedLifecycleRegistryBoundJournal:
            raise registry_base.RegistryBindingError(
                "supported LAB-076 worker requires audited lifecycle journal"
            )
        registry_base.RegistryBrokerWorker.__init__(self, registry, runtime, secret)
