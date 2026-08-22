import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.provider_generation_history.protocol import (
    CurrentGenerationRequired,
    DurableProviderHistory,
    GenerationDescriptor,
    HistoricalReceipt,
    HistoricalVerificationError,
    HistoryRollback,
    InvalidTransition,
    PendingRotationBlocked,
    UnsafeCallerHistoricalKeyring,
    mac,
)


def desc(generation, key, provider='anchor-A'):
    return GenerationDescriptor(provider, generation, key.hex())


def receipt(provider, generation, key, position, request_id, challenge='challenge'):
    r = HistoricalReceipt(provider, generation, position, request_id, 'RECONCILE', challenge, '')
    return HistoricalReceipt(provider, generation, position, request_id, 'RECONCILE', challenge, mac(key, r.unsigned))


class Tests(unittest.TestCase):
    def setUp(self):
        self.k1 = b'provider-key-1'
        self.k2 = b'provider-key-2'
        self.g1 = desc(1, self.k1)
        self.g2 = desc(2, self.k2)

    def history(self, td):
        return DurableProviderHistory(Path(td) / 'history.db', self.g1)

    def test_historical_receipt_survives_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            h = self.history(td)
            r1 = receipt('anchor-A', 1, self.k1, 1, 'req-1')
            h.store_receipt(r1)
            h.rotate(self.g2, h.make_transition(self.g1, self.g2))
            loaded = h.load_receipt('req-1')
            self.assertEqual(loaded.stable_binding, r1.stable_binding)
            self.assertEqual(h.current(), self.g2)

    def test_old_generation_cannot_authorize_new_effect(self):
        with tempfile.TemporaryDirectory() as td:
            h = self.history(td)
            h.rotate(self.g2, h.make_transition(self.g1, self.g2))
            with self.assertRaises(CurrentGenerationRequired):
                h.require_current('anchor-A', 1)
            self.assertEqual(h.require_current('anchor-A', 2), self.g2)

    def test_same_generation_key_substitution_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            h = self.history(td)
            bad = desc(1, b'other')
            with self.assertRaises(InvalidTransition):
                h.rotate(bad, h.make_transition(self.g1, desc(2, b'x')))

    def test_cross_provider_rotation_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            self.history(td)
            bad = desc(2, self.k2, provider='anchor-B')
            with self.assertRaises(InvalidTransition):
                DurableProviderHistory.make_transition(self.g1, bad)

    def test_pending_prepared_blocks_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            h = self.history(td)
            with self.assertRaises(PendingRotationBlocked):
                h.rotate(self.g2, h.make_transition(self.g1, self.g2), pending_prepared=1)
            self.assertEqual(h.current(), self.g1)

    def test_missing_transition_proof_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'history.db'
            h = DurableProviderHistory(p, self.g1)
            h.rotate(self.g2, h.make_transition(self.g1, self.g2))
            q = sqlite3.connect(p)
            q.execute('DELETE FROM provider_generation_transitions')
            q.commit(); q.close()
            with self.assertRaises(HistoricalVerificationError):
                DurableProviderHistory(p, self.g1)

    def test_corrupt_transition_proof_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'history.db'
            h = DurableProviderHistory(p, self.g1)
            h.rotate(self.g2, h.make_transition(self.g1, self.g2))
            q = sqlite3.connect(p)
            q.execute("UPDATE provider_generation_transitions SET old_mac=?", ('0'*64,))
            q.commit(); q.close()
            with self.assertRaises(HistoricalVerificationError):
                DurableProviderHistory(p, self.g1)

    def test_head_rollback_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'history.db'
            h = DurableProviderHistory(p, self.g1)
            h.rotate(self.g2, h.make_transition(self.g1, self.g2))
            q = sqlite3.connect(p)
            q.execute('UPDATE provider_generation_head SET generation_id=?,generation=?', (self.g1.generation_id, 1))
            q.commit(); q.close()
            with self.assertRaises(HistoryRollback):
                DurableProviderHistory(p, self.g1)

    def test_forged_historical_key_material_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            h = self.history(td)
            forged = receipt('anchor-A', 1, b'attacker-key', 1, 'req-1')
            with self.assertRaises(HistoricalVerificationError):
                h.store_receipt(forged)

    def test_receipt_request_or_position_substitution_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            h = self.history(td)
            r = receipt('anchor-A', 1, self.k1, 1, 'req-1')
            h.store_receipt(r)
            rebound = HistoricalReceipt(r.provider_id, r.generation, 2, 'req-2', r.kind, r.challenge, r.signature)
            with self.assertRaises(HistoricalVerificationError):
                h.verify_receipt(rebound)

    def test_restart_old_and_new_receipts(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'history.db'
            h = DurableProviderHistory(p, self.g1)
            h.store_receipt(receipt('anchor-A', 1, self.k1, 1, 'req-1'))
            h.rotate(self.g2, h.make_transition(self.g1, self.g2))
            h.store_receipt(receipt('anchor-A', 2, self.k2, 2, 'req-2'))
            r = DurableProviderHistory(p, self.g1)
            self.assertEqual(r.load_receipt('req-1').generation, 1)
            self.assertEqual(r.load_receipt('req-2').generation, 2)
            self.assertEqual(r.current().generation, 2)

    def test_unsafe_caller_keyring_accepts_attacker_history(self):
        attacker = b'attacker'
        forged = receipt('anchor-A', 1, attacker, 1, 'req-1')
        self.assertTrue(UnsafeCallerHistoricalKeyring.verify(forged, attacker))


if __name__ == '__main__':
    unittest.main()
