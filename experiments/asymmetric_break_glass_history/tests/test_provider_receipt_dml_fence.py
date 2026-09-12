import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    assert_public_mutation_fence_locked,
    install_public_mutation_fence_locked,
)
from experiments.asymmetric_break_glass_history.tests.test_strict_fence import (
    StrictPublicMutationFenceTests,
)


class ProviderReceiptDmlFenceTests(unittest.TestCase):
    def make_db(self):
        q = StrictPublicMutationFenceTests().make_db()
        q.executescript(
            """
            CREATE TABLE asymmetric_provider_receipts(
              request_id TEXT PRIMARY KEY,
              provider_id TEXT NOT NULL,
              generation INTEGER NOT NULL,
              position INTEGER NOT NULL,
              kind TEXT NOT NULL,
              challenge TEXT NOT NULL,
              signature TEXT NOT NULL,
              stable_binding TEXT NOT NULL
            );
            INSERT INTO asymmetric_provider_receipts
            VALUES('r1','anchor-A',1,1,'RECONCILE','c1','sig1','bind1');
            """
        )
        # Re-install after the real LAB-082 receipt table exists.  The corrected
        # LAB-086 policy must discover it dynamically and add append-only history
        # protection without blocking a new distinct receipt.
        install_public_mutation_fence_locked(q)
        q.commit()
        return q

    def test_existing_receipt_is_immutable_and_not_replaceable(self):
        q = self.make_db()
        statements = (
            "UPDATE asymmetric_provider_receipts SET stable_binding='evil' WHERE request_id='r1'",
            "DELETE FROM asymmetric_provider_receipts WHERE request_id='r1'",
            "INSERT OR REPLACE INTO asymmetric_provider_receipts "
            "VALUES('r1','anchor-A',1,1,'RECONCILE','c2','sig2','bind2')",
            "INSERT INTO asymmetric_provider_receipts "
            "VALUES('r1','anchor-A',1,1,'RECONCILE','c2','sig2','bind2') "
            "ON CONFLICT(request_id) DO UPDATE SET stable_binding='evil'",
        )
        for statement in statements:
            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(statement)
            q.rollback()
        self.assertEqual(
            q.execute(
                "SELECT provider_id,generation,position,kind,challenge,signature,stable_binding "
                "FROM asymmetric_provider_receipts WHERE request_id='r1'"
            ).fetchone(),
            ('anchor-A', 1, 1, 'RECONCILE', 'c1', 'sig1', 'bind1'),
        )

    def test_new_distinct_receipt_remains_allowed(self):
        q = self.make_db()
        q.execute(
            "INSERT INTO asymmetric_provider_receipts "
            "VALUES('r2','anchor-A',1,2,'RECONCILE','c2','sig2','bind2')"
        )
        q.commit()
        self.assertEqual(
            q.execute("SELECT request_id FROM asymmetric_provider_receipts ORDER BY request_id").fetchall(),
            [('r1',), ('r2',)],
        )
        self.assertTrue(assert_public_mutation_fence_locked(q))


if __name__ == '__main__':
    unittest.main()
