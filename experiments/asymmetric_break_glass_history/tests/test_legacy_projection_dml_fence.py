import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    assert_public_mutation_fence_locked,
    install_public_mutation_fence_locked,
    remove_public_mutation_fence_locked,
)


class LegacyProjectionDmlFenceTests(unittest.TestCase):
    def setUp(self):
        self.q = sqlite3.connect(":memory:")
        self.q.executescript(
            """
            CREATE TABLE provider_asymmetric_break_glass_boundary(
              singleton INTEGER PRIMARY KEY, legacy_digest TEXT
            );
            CREATE TABLE provider_asymmetric_break_glass_proofs(x TEXT);
            CREATE TABLE provider_asymmetric_recovery_public_root_proofs(x TEXT);

            CREATE TABLE provider_recovery_public_authorities(authority_id TEXT PRIMARY KEY);
            CREATE TABLE provider_recovery_public_transitions(new_authority_id TEXT PRIMARY KEY);
            CREATE TABLE provider_recovery_public_head(
              singleton INTEGER PRIMARY KEY,authority_id TEXT,version INTEGER,generation INTEGER
            );

            CREATE TABLE provider_rotation_recovery_transitions(
              new_rotation_authority_id TEXT PRIMARY KEY,old_rotation_authority_id TEXT,
              old_rotation_version INTEGER,old_rotation_generation INTEGER,
              recovery_authority_id TEXT,recovery_generation INTEGER,
              intent_digest TEXT,signatures_json TEXT
            );
            CREATE TABLE provider_rotation_recovery_authorities(
              authority_id TEXT PRIMARY KEY,name TEXT,generation INTEGER,threshold INTEGER,
              keys_json TEXT,revoked_json TEXT
            );
            CREATE TABLE provider_rotation_recovery_head(
              singleton INTEGER PRIMARY KEY,authority_id TEXT,generation INTEGER
            );
            CREATE TABLE provider_recovery_lifecycle_authorities(
              authority_id TEXT PRIMARY KEY,version INTEGER,name TEXT,generation INTEGER,
              threshold INTEGER,keys_json TEXT,revoked_json TEXT
            );
            CREATE TABLE provider_recovery_lifecycle_head(
              singleton INTEGER PRIMARY KEY,authority_id TEXT,version INTEGER,generation INTEGER
            );
            CREATE TABLE provider_recovery_lifecycle_transitions(
              new_authority_id TEXT PRIMARY KEY,old_authority_id TEXT,root_authority_id TEXT,
              root_version INTEGER,root_generation INTEGER,intent_digest TEXT,
              old_signatures_json TEXT,new_signatures_json TEXT,root_signatures_json TEXT
            );
            CREATE TABLE provider_recovery_custody_bindings(
              symmetric_authority_id TEXT PRIMARY KEY,public_authority_id TEXT,
              version INTEGER,generation INTEGER
            );
            CREATE TABLE provider_rotation_recovery_custody_proofs(
              new_rotation_authority_id TEXT PRIMARY KEY,public_authority_id TEXT,
              symmetric_authority_id TEXT,compatibility_intent_digest TEXT,
              custody_intent_digest TEXT,public_signatures_json TEXT
            );
            CREATE TABLE provider_recovery_custody_enablement(
              singleton INTEGER PRIMARY KEY,start_rotation_authority_id TEXT,
              start_rotation_version INTEGER,start_rotation_generation INTEGER,
              symmetric_authority_id TEXT,public_authority_id TEXT
            );
            CREATE TABLE provider_recovery_custody_enablement_proof(
              singleton INTEGER PRIMARY KEY,enablement_digest TEXT,public_signatures_json TEXT
            );

            INSERT INTO provider_rotation_recovery_transitions
              VALUES('new','old',1,1,'rec',1,'digest','["sig"]');
            INSERT INTO provider_rotation_recovery_authorities
              VALUES('rec','recovery',1,1,'{"k":"v"}','[]');
            INSERT INTO provider_rotation_recovery_head VALUES(1,'rec',1);
            INSERT INTO provider_recovery_lifecycle_authorities
              VALUES('life',1,'recovery',1,1,'{"k":"v"}','[]');
            INSERT INTO provider_recovery_lifecycle_head VALUES(1,'life',1,1);
            INSERT INTO provider_recovery_lifecycle_transitions
              VALUES('life2','life','root',1,1,'intent','["a"]','["b"]','["c"]');
            INSERT INTO provider_recovery_custody_bindings VALUES('life','public',1,1);
            INSERT INTO provider_rotation_recovery_custody_proofs
              VALUES('new','public','life','legacy','custody','["p"]');
            INSERT INTO provider_recovery_custody_enablement
              VALUES(1,'root',1,1,'life','public');
            INSERT INTO provider_recovery_custody_enablement_proof VALUES(1,'enable','["p"]');
            """
        )
        install_public_mutation_fence_locked(self.q)

    def tearDown(self):
        self.q.close()

    def _cutoff(self):
        self.q.execute(
            "INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1,'boundary')"
        )

    def _blocked(self, sql):
        with self.assertRaises(sqlite3.IntegrityError):
            self.q.execute(sql)

    def test_pre_cutoff_legacy_semantics_remain_live(self):
        self.q.execute(
            "UPDATE provider_recovery_custody_bindings SET generation=2 "
            "WHERE symmetric_authority_id='life'"
        )
        self.assertEqual(
            self.q.execute(
                "SELECT generation FROM provider_recovery_custody_bindings"
            ).fetchone()[0],
            2,
        )

    def test_cutoff_allows_only_canonical_hmac_scrub(self):
        self._cutoff()
        self.q.execute(
            "UPDATE provider_rotation_recovery_transitions SET signatures_json='[]'"
        )
        self.q.execute(
            "UPDATE provider_rotation_recovery_authorities SET keys_json='{}'"
        )
        self.q.execute(
            "UPDATE provider_recovery_lifecycle_authorities SET keys_json='{}'"
        )
        self.q.execute(
            "UPDATE provider_recovery_lifecycle_transitions "
            "SET old_signatures_json='[]',new_signatures_json='[]',root_signatures_json='[]'"
        )
        self.assertEqual(
            self.q.execute(
                "SELECT signatures_json FROM provider_rotation_recovery_transitions"
            ).fetchone()[0],
            "[]",
        )
        self.assertEqual(
            self.q.execute(
                "SELECT keys_json FROM provider_rotation_recovery_authorities"
            ).fetchone()[0],
            "{}",
        )

    def test_projected_legacy_semantics_are_immutable_after_cutoff(self):
        self._cutoff()
        self._blocked(
            "UPDATE provider_rotation_recovery_transitions SET old_rotation_version=999"
        )
        self._blocked("DELETE FROM provider_rotation_recovery_transitions")
        self._blocked(
            "INSERT INTO provider_rotation_recovery_transitions "
            "VALUES('other','old',1,1,'rec',1,'digest','[]')"
        )
        self._blocked(
            "UPDATE provider_rotation_recovery_authorities SET generation=999"
        )
        self._blocked("DELETE FROM provider_rotation_recovery_authorities")
        self._blocked("UPDATE provider_rotation_recovery_head SET generation=999")
        self._blocked(
            "UPDATE provider_recovery_lifecycle_authorities SET generation=999"
        )
        self._blocked(
            "UPDATE provider_recovery_lifecycle_transitions SET root_version=999"
        )
        self._blocked(
            "UPDATE provider_recovery_custody_bindings SET generation=999"
        )
        self._blocked("DELETE FROM provider_recovery_custody_bindings")
        self._blocked(
            "UPDATE provider_rotation_recovery_custody_proofs "
            "SET compatibility_intent_digest='evil'"
        )
        self._blocked(
            "UPDATE provider_recovery_custody_enablement SET start_rotation_version=999"
        )
        self._blocked(
            "UPDATE provider_recovery_custody_enablement_proof SET enablement_digest='evil'"
        )
        assert_public_mutation_fence_locked(self.q)

    def test_final_writer_thaw_does_not_thaw_legacy_projection(self):
        self._cutoff()
        remove_public_mutation_fence_locked(self.q)
        self._blocked(
            "UPDATE provider_recovery_custody_bindings SET generation=999"
        )
        self._blocked(
            "UPDATE provider_rotation_recovery_transitions SET old_rotation_version=999"
        )


if __name__ == "__main__":
    unittest.main()
