import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    install_public_mutation_fence_locked,
    remove_public_mutation_fence_locked,
)


def make_db():
    q = sqlite3.connect(":memory:")
    q.executescript(
        """
        CREATE TABLE provider_asymmetric_break_glass_boundary(
          singleton INTEGER PRIMARY KEY
        );
        INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1);

        CREATE TABLE provider_recovery_public_authorities(
          authority_id TEXT PRIMARY KEY,
          marker TEXT NOT NULL
        );
        INSERT INTO provider_recovery_public_authorities VALUES('public-1','original');

        CREATE TABLE provider_recovery_public_transitions(
          new_authority_id TEXT PRIMARY KEY,
          marker TEXT NOT NULL
        );
        INSERT INTO provider_recovery_public_transitions VALUES('public-2','original');

        CREATE TABLE provider_recovery_public_head(
          singleton INTEGER PRIMARY KEY,
          authority_id TEXT NOT NULL
        );
        INSERT INTO provider_recovery_public_head VALUES(1,'public-2');

        CREATE TABLE provider_rotation_authority_transitions(
          new_authority_id TEXT PRIMARY KEY,
          marker TEXT NOT NULL
        );
        INSERT INTO provider_rotation_authority_transitions VALUES('root-2','original');

        CREATE TABLE provider_rotation_authority_head(
          singleton INTEGER PRIMARY KEY,
          authority_id TEXT NOT NULL,
          version INTEGER NOT NULL,
          generation INTEGER NOT NULL
        );
        INSERT INTO provider_rotation_authority_head VALUES(1,'root-2',2,2);

        CREATE TABLE asymmetric_provider_head(
          singleton INTEGER PRIMARY KEY,
          generation_id TEXT NOT NULL,
          generation INTEGER NOT NULL
        );
        INSERT INTO asymmetric_provider_head VALUES(1,'provider-2',2);
        """
    )
    install_public_mutation_fence_locked(q)
    return q


class TransactionScopedThawMinimalityTests(unittest.TestCase):
    def test_thaw_keeps_inherited_history_immutable(self):
        q = make_db()
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "UPDATE provider_rotation_authority_transitions "
                    "SET marker='tampered' WHERE new_authority_id='root-2'"
                )

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

    def test_thaw_keeps_existing_public_recovery_history_immutable(self):
        q = make_db()
        try:
            remove_public_mutation_fence_locked(q)

            for table, key, value in (
                ("provider_recovery_public_authorities", "authority_id", "public-1"),
                ("provider_recovery_public_transitions", "new_authority_id", "public-2"),
            ):
                with self.assertRaises(sqlite3.IntegrityError):
                    q.execute(
                        f"UPDATE {table} SET marker='tampered' WHERE {key}=?",
                        (value,),
                    )
                self.assertEqual(
                    q.execute(
                        f"SELECT marker FROM {table} WHERE {key}=?",
                        (value,),
                    ).fetchone()[0],
                    "original",
                )
        finally:
            q.close()

    def test_thaw_keeps_unneeded_head_insert_delete_guards(self):
        q = make_db()
        try:
            remove_public_mutation_fence_locked(q)

            # Supported writers only UPDATE these singleton heads. They never
            # need INSERT/REPLACE or DELETE capability during normal rotation.
            for table, replacement in (
                (
                    "provider_recovery_public_head",
                    "INSERT OR REPLACE INTO provider_recovery_public_head VALUES(1,'attacker')",
                ),
                (
                    "provider_rotation_authority_head",
                    "INSERT OR REPLACE INTO provider_rotation_authority_head VALUES(1,'attacker',99,99)",
                ),
                (
                    "asymmetric_provider_head",
                    "INSERT OR REPLACE INTO asymmetric_provider_head VALUES(1,'attacker',99)",
                ),
            ):
                with self.assertRaises(sqlite3.IntegrityError):
                    q.execute(replacement)
                with self.assertRaises(sqlite3.IntegrityError):
                    q.execute(f"DELETE FROM {table} WHERE singleton=1")
        finally:
            q.close()


if __name__ == "__main__":
    unittest.main()
