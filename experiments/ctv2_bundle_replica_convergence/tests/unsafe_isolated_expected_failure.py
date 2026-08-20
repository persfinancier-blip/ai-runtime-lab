import unittest

from experiments.ctv2_bundle_replica_convergence.tests.test_protocol import bootstrap, bundle_successor
from experiments.ctv2_bundle_replica_convergence.protocol import UnsafeIsolatedReplica


class UnsafeIsolatedReplicaBaseline(unittest.TestCase):
    def test_two_locally_valid_forks_should_not_both_be_accepted_but_are(self):
        base = bootstrap(); left, right = base.copy(), base.copy()
        left.append(bundle_successor(left, "left-fork")); right.append(bundle_successor(right, "right-fork"))
        unsafe = UnsafeIsolatedReplica()
        unsafe.accept(left); unsafe.accept(right)
        self.assertEqual(len(set(unsafe.accepted)), 1, "isolated replica accepted two incompatible authenticated heads")


if __name__ == "__main__":
    unittest.main()
