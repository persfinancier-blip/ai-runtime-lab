import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.adoption_validation import _unique_key_sets


class AdoptionExpressionUniqueRegressionTests(unittest.TestCase):
    def test_expression_unique_index_does_not_establish_single_column_identity(self):
        q = sqlite3.connect(":memory:")
        q.executescript(
            """
            CREATE TABLE legacy_identity(
              id TEXT NOT NULL,
              scope TEXT NOT NULL
            );
            CREATE UNIQUE INDEX legacy_identity_expr_uq
              ON legacy_identity(id, lower(scope));
            """
        )

        # The expression term appears as cid=-2/name=NULL in PRAGMA index_info.
        # Dropping that term must not collapse this weaker compound index into
        # a false table-wide UNIQUE(id) guarantee.
        self.assertNotIn(("id",), _unique_key_sets(q, "legacy_identity"))

        q.execute("INSERT INTO legacy_identity VALUES('same-id', 'A')")
        q.execute("INSERT INTO legacy_identity VALUES('same-id', 'B')")
        self.assertEqual(
            q.execute(
                "SELECT COUNT(*) FROM legacy_identity WHERE id='same-id'"
            ).fetchone()[0],
            2,
        )


if __name__ == "__main__":
    unittest.main()
