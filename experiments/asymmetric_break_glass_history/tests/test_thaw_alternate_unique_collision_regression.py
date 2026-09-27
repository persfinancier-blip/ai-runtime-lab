import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    install_public_mutation_fence_locked,
    remove_public_mutation_fence_locked,
)


class ThawAlternateUniqueCollisionRegressionTests(unittest.TestCase):
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

            CREATE TABLE asymmetric_provider_generations(
              generation_id TEXT PRIMARY KEY,
              provider_id TEXT NOT NULL,
              generation INTEGER NOT NULL,
              public_key_hex TEXT NOT NULL,
              UNIQUE(provider_id,generation)
            );
            INSERT INTO asymmetric_provider_generations
            VALUES('generation-1-id','anchor-A',1,'original-key');
            """
        )
        install_public_mutation_fence_locked(q)
        q.commit()
        return q

    def test_thaw_cannot_replace_existing_generation_via_alternate_unique_identity(self):
        q = self.make_db()
        try:
            q.execute("BEGIN IMMEDIATE")
            remove_public_mutation_fence_locked(q)

            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "INSERT OR REPLACE INTO asymmetric_provider_generations "
                    "VALUES('attacker-generation-id','anchor-A',1,'attacker-key')"
                )

            self.assertEqual(
                q.execute(
                    "SELECT generation_id,provider_id,generation,public_key_hex "
                    "FROM asymmetric_provider_generations WHERE provider_id='anchor-A' AND generation=1"
                ).fetchone(),
                ('generation-1-id', 'anchor-A', 1, 'original-key'),
            )

            # The verified final writer must still be able to create the real
            # successor when neither the content identity nor the semantic
            # (provider_id,generation) identity already exists.
            q.execute(
                "INSERT INTO asymmetric_provider_generations "
                "VALUES('generation-2-id','anchor-A',2,'successor-key')"
            )
            self.assertEqual(
                q.execute(
                    "SELECT generation_id FROM asymmetric_provider_generations "
                    "WHERE provider_id='anchor-A' AND generation=2"
                ).fetchone()[0],
                'generation-2-id',
            )
            q.rollback()
        finally:
            q.close()


if __name__ == "__main__":
    unittest.main()
