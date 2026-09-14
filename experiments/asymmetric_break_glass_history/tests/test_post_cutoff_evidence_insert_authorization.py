import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    install_public_mutation_fence_locked,
    remove_public_mutation_fence_locked,
)


class PostCutoffEvidenceInsertAuthorizationTests(unittest.TestCase):
    def _db(self):
        q = sqlite3.connect(":memory:")
        q.executescript(
            """
            CREATE TABLE provider_asymmetric_break_glass_boundary(singleton INTEGER PRIMARY KEY);
            INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1);
            CREATE TABLE provider_asymmetric_break_glass_legacy_projection(singleton INTEGER PRIMARY KEY);
            INSERT INTO provider_asymmetric_break_glass_legacy_projection VALUES(1);
            CREATE TABLE provider_asymmetric_break_glass_root_proof(singleton INTEGER PRIMARY KEY);
            INSERT INTO provider_asymmetric_break_glass_root_proof VALUES(1);

            CREATE TABLE provider_recovery_public_authorities(authority_id TEXT PRIMARY KEY);
            CREATE TABLE provider_recovery_public_transitions(new_authority_id TEXT PRIMARY KEY);
            CREATE TABLE provider_recovery_public_head(singleton INTEGER PRIMARY KEY);

            CREATE TABLE provider_asymmetric_break_glass_proofs(
              new_rotation_authority_id TEXT PRIMARY KEY,payload TEXT
            );
            CREATE TABLE provider_asymmetric_recovery_public_root_proofs(
              new_public_authority_id TEXT PRIMARY KEY,payload TEXT
            );
            """
        )
        install_public_mutation_fence_locked(q)
        q.commit()
        return q

    def test_new_break_glass_proof_requires_final_writer_thaw(self):
        q = self._db()
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "INSERT INTO provider_asymmetric_break_glass_proofs VALUES('attacker','junk')"
                )
            q.rollback()

            q.execute("BEGIN IMMEDIATE")
            remove_public_mutation_fence_locked(q)
            q.execute(
                "INSERT INTO provider_asymmetric_break_glass_proofs VALUES('legit','verified-proof')"
            )
            install_public_mutation_fence_locked(q)
            q.commit()

            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "INSERT INTO provider_asymmetric_break_glass_proofs VALUES('attacker-2','junk')"
                )
        finally:
            q.close()

    def test_new_public_rotation_root_proof_requires_final_writer_thaw(self):
        q = self._db()
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "INSERT INTO provider_asymmetric_recovery_public_root_proofs VALUES('attacker','junk')"
                )
            q.rollback()

            q.execute("BEGIN IMMEDIATE")
            remove_public_mutation_fence_locked(q)
            q.execute(
                "INSERT INTO provider_asymmetric_recovery_public_root_proofs VALUES('legit','verified-proof')"
            )
            install_public_mutation_fence_locked(q)
            q.commit()

            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "INSERT INTO provider_asymmetric_recovery_public_root_proofs VALUES('attacker-2','junk')"
                )
        finally:
            q.close()


if __name__ == "__main__":
    unittest.main()
