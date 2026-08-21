import os, unittest
from experiments.memfd_descendant_authority.protocol import *

class Tests(unittest.TestCase):
    def test_unsafe_target_can_pass_fd_to_grandchild(self):
        self.assertTrue(unsafe_propagation(b'lab070-secret'))

    def test_capabilities_are_observed(self):
        c=probe_capabilities()
        self.assertTrue(c.arch_x86_64)
        self.assertTrue(c.seccomp)
        self.assertTrue(c.user_pidns)
        self.assertFalse(c.cgroup_delegated)

    def test_single_process_denies_descendant_creation(self):
        e=run_single_process(b'alpha-secret',7)
        self.assertEqual(e.outcome,'ENFORCED')
        self.assertIn('process-creation-denied',e.facts)
        self.assertIn('same-process-thread-allowed',e.facts)

    def test_single_process_fails_closed_without_seccomp(self):
        with self.assertRaises(UnsupportedMode):
            run_single_process(b'x',1,CapabilityReport(True,False,True,False))

    def test_supervised_tree_descendant_dies_with_namespace_init(self):
        e=run_supervised_tree(b'beta-secret',8)
        self.assertIn('namespace-init-exit-killed-descendant',e.facts)

    def test_supervised_tree_fails_closed_without_pidns(self):
        with self.assertRaises(UnsupportedMode):
            run_supervised_tree(b'x',1,CapabilityReport(True,True,False,False))

    def test_rotation_is_not_revocation(self):
        fd=sealed_memfd(b'gamma-secret')
        try:
            self.assertTrue(rotation_is_not_revocation(fd,99))
        finally:
            os.close(fd)

    def test_evidence_has_no_raw_secret(self):
        s=b'delta-secret'
        self.assertFalse(evidence_contains_secret(run_single_process(s,2),s))
        self.assertFalse(evidence_contains_secret(run_supervised_tree(s,2),s))

if __name__=='__main__':
    unittest.main()
