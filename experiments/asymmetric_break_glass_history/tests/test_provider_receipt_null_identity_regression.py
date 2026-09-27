import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    install_public_mutation_fence_locked,
)


class ProviderReceiptNullIdentityRegressionTests(unittest.TestCase):
    def make_db(self):
        q = sqlite3.connect(":memory:")
        q.executescript(
            """
            CREATE TABLE provider_asymmetric_break_glass_boundary(
              singleton INTEGER PRIMARY KEY
            );
            INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1);

            CREATE TABLE provider_recovery_public_authorities(
              authority_id TEXT PRIMARY KEY
            );
            CREATE TABLE provider_recovery_public_transitions(
              new_authority_id TEXT PRIMARY KEY
            );
            CREATE TABLE provider_recovery_public_head(
              singleton INTEGER PRIMARY KEY
            );

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
            """
        )
        install_public_mutation_fence_locked(q)
        q.commit()
        return q

    def test_post_cutoff_null_request_id_is_denied(self):
        q = self.make_db()
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
                    (
                        None,
                        "anchor-A",
                        1,
                        1,
                        "RECONCILE",
                        "challenge",
                        "00" * 64,
                        "11" * 32,
                    ),
                )
            q.rollback()
            self.assertEqual(
                q.execute("SELECT COUNT(*) FROM asymmetric_provider_receipts").fetchone()[0],
                0,
            )

            # LAB-082 must remain appendable for a genuinely new, non-NULL
            # request identity; authorization of arbitrary new request IDs is a
            # separate LAB-091 writer-boundary concern.
            q.execute(
                "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
                (
                    "request-2",
                    "anchor-A",
                    1,
                    2,
                    "RECONCILE",
                    "challenge-2",
                    "22" * 64,
                    "33" * 32,
                ),
            )
            self.assertEqual(
                q.execute(
                    "SELECT request_id FROM asymmetric_provider_receipts"
                ).fetchone()[0],
                "request-2",
            )
        finally:
            q.close()


if __name__ == "__main__":
    unittest.main()
