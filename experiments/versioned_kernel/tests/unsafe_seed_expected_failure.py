import unittest
from experiments.versioned_kernel.protocol import v1_state, unsafe_migrate_v1_to_v2, semantic_projection

class UnsafeMigrationBaseline(unittest.TestCase):
    def test_unsafe_migration_should_preserve_semantics_but_does_not(self):
        before=v1_state(); after=unsafe_migrate_v1_to_v2(before)
        self.assertEqual(semantic_projection(before),semantic_projection(after),'unsafe migration rewrote durable external identities')
