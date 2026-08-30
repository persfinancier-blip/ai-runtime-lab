from __future__ import annotations

from .adoption_extra_columns import validate_no_required_extra_columns
from .adoption_foreign_keys import validate_no_foreign_key_constraints
from .adoption_schema_domains import validate_required_not_null_contract
from .adoption_secondary_indexes import validate_secondary_index_collations
from .adoption_trigger_surface import validate_protected_trigger_surface
from .adoption_validation import validate_existing_mutable_state_locked
from .binary_identity_provider_history import BinaryIdentityIntegratedAsymmetricProviderHistory
from .cross_table_guards import install_cross_table_guards
from .full_operation_guards import install_full_operation_guards
from .history_binding_guards import install_history_binding_guards
from .restart_safe_schema import initialize_shared_anchor_schema
from .state_machine_operation_scoped import (
    SupportedStateMachineOperationScopedAsymmetricSharedAnchorLedger,
)
from .state_machine_udfs import install_state_machine_udfs


class SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger(
    SupportedStateMachineOperationScopedAsymmetricSharedAnchorLedger
):
    """LAB-091 candidate with deterministic request IDs and history-bound watermarks."""

    def __init__(self, path, attested, bootstrap, signer):
        super().__init__(path, attested, bootstrap, signer)
        self._ensure_binary_provider_history()
        self._require_runtime_matches_durable_head()

    def _ensure_binary_provider_history(self):
        # LAB-082 installs IntegratedAsymmetricProviderHistory before entering
        # LAB-091's parent constructor. Dynamic dispatch then reaches this
        # class's _install_guards() before this class's __init__ resumes. Upgrade
        # the helper before adoption/restart verification so receipt identities
        # never inherit a legacy column's non-BINARY collation.
        if not isinstance(
            self.provider_history, BinaryIdentityIntegratedAsymmetricProviderHistory
        ):
            self.provider_history = BinaryIdentityIntegratedAsymmetricProviderHistory(
                self.path, self.provider_history.bootstrap
            )
        return self.provider_history

    def _con(self):
        q = super()._con()
        install_state_machine_udfs(q)
        return q

    def _init(self):
        # SharedAnchorLedger._init() replays INSERT OR IGNORE on every reopen.
        # Persistent LAB-091 BEFORE INSERT guards intentionally fire before
        # conflict resolution, so the historical initializer is incompatible
        # with an already protected database. Dynamic dispatch reaches this
        # override from the LAB-080 base constructor.
        q = self._con()
        try:
            initialize_shared_anchor_schema(q)
        finally:
            q.close()

    def entry(self, intent_id):
        q = self._con()
        try:
            return self._row_entry(
                q.execute(
                    "SELECT intent_id,component_id,intent_type,payload_digest,"
                    "provider_id,provider_generation,predecessor_position,position,"
                    "request_id,status,receipt_binding FROM shared_anchor_intents "
                    "WHERE intent_id COLLATE BINARY = ? COLLATE BINARY",
                    (intent_id,),
                ).fetchone()
            )
        finally:
            q.close()

    def watermark(self, component_id):
        q = self._con()
        try:
            row = q.execute(
                "SELECT position FROM component_anchor_watermarks "
                "WHERE component_id COLLATE BINARY = ? COLLATE BINARY",
                (component_id,),
            ).fetchone()
            return 0 if row is None else row[0]
        finally:
            q.close()

    def _install_guards(self):
        self._ensure_binary_provider_history()
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            # Re-run the complete inherited LAB-082 durable verifier while this
            # connection holds the SQLite writer reservation. The verifier uses
            # a sibling read-only transaction, so it sees committed state while
            # concurrent legacy writers remain blocked until guard commit/rollback.
            # This closes first-adoption TOCTOU without duplicating a subset of
            # LAB-082's history/receipt/watermark verification contract here.
            self.verify_durable()
            install_full_operation_guards(q)
            install_cross_table_guards(q)
            install_history_binding_guards(q)
            # Unknown persisted triggers attached to a protected table execute
            # inside an otherwise authorized LAB-091 statement. Reject that
            # confused-deputy surface before accepting first adoption/restart.
            validate_protected_trigger_surface(q)
            # CREATE TABLE IF NOT EXISTS cannot restore canonical field-domain
            # constraints on an existing legacy table. Reject weakened NOT NULL
            # declarations before accepting the database as LAB-091 protected.
            validate_required_not_null_contract(q)
            # Canonical protected tables declare no foreign keys. A legacy
            # REFERENCES clause can reject an otherwise valid supported write
            # whenever foreign-key enforcement is enabled on the connection.
            validate_no_foreign_key_constraints(q)
            # Additive legacy columns are harmless only when the canonical writer
            # can omit them. A NOT NULL extra column without a DEFAULT otherwise
            # makes adoption succeed and the next supported INSERT fail.
            validate_no_required_extra_columns(q)
            # Non-UNIQUE indexes still execute on writes. A legacy index using a
            # custom/non-BINARY collation can make a supported write fail after
            # restart when that collation is not registered on this connection.
            validate_secondary_index_collations(q)
            # Persistent triggers can constrain only future statements. Before
            # completing first adoption/restart, reject preexisting rows that
            # could not have been created by the supported LAB-091 state machine.
            validate_existing_mutable_state_locked(q)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
