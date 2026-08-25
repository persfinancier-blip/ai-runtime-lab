import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    install_public_mutation_fence_locked,
    remove_public_mutation_fence_locked,
)


class TransactionScopedThawMinimalityTests(unittest.TestCase):
    def test_thaw_keeps_inherited_history_immutable(self):
        q = sqlite3.connect(":memory:")
        try:
            q.executescript(
                """
                CREATE TABLE provider_asymmetric_break_glass_boundary(
                  singleton INTEGER PRIMARY KEY
                );
                INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1);

                CREATE TABLE provider_rotation_authority_transitions(
                  new_authority_id TEXT PRIMARY KEY,
                  marker TEXT NOT NULL
                );
                INSERT INTO provider_rotation_authority_transitions VALUES('root-2','original');
                """
            )
            install_public_mutation_fence_locked(q)

            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "UPDATE provider_rotation_authority_transitions "
                    "SET marker='tampered' WHERE new_authority_id='root-2'"
                )

            # The final writer needs permission to INSERT a new authenticated
            # transition, but it never needs permission to rewrite/delete an
            # already committed transition. Transaction-scoped thaw must
            # therefore remove only creation-deny triggers, not history guards.
            remove_public_mutation_fence_locked(q)

            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "UPDATE provider_rotation_authority_transitions "
                    "SET marker='tampered' WHERE new_authority_id='root-2'"
                )
            self.assertEqual(
                q.execute(
                    "SELECT marker FROM provider_rotation_authority_transitions "
                    "WHERE new_authority_id='root-2'"
                ).fetchone()[0],
                "original",
            )
        finally:
            q.close()


if __name__ == "__main__":
    unittest.main()
