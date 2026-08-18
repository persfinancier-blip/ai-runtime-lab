import unittest
from experiments.orchestration_topologies.benchmark import SCENARIOS, aggregate, benchmark, run_scenario

class TopologyTests(unittest.TestCase):
    def test_all_three_topologies_cover_all_seeded_scenarios(self):
        rows = benchmark()
        self.assertEqual(len(rows), len(SCENARIOS)*3)

    def test_manager_helps_decomposable_task(self):
        self.assertFalse(run_scenario(SCENARIOS[1], 'single').correct)
        self.assertTrue(run_scenario(SCENARIOS[1], 'manager').correct)

    def test_manager_contains_stale_specialist(self):
        r = run_scenario(SCENARIOS[2], 'manager')
        self.assertTrue(r.correct); self.assertEqual(r.failures_contained,1); self.assertEqual(r.recoveries,1)

    def test_fixed_idempotency_prevents_duplicate_work_in_every_topology(self):
        for t in ('single','manager','peer'):
            r = run_scenario(SCENARIOS[3], t)
            self.assertTrue(r.correct); self.assertEqual(r.duplicated_work,0)

    def test_manager_resolves_conflicting_evidence(self):
        self.assertTrue(run_scenario(SCENARIOS[4], 'manager').correct)
        self.assertFalse(run_scenario(SCENARIOS[4], 'peer').correct)

    def test_worker_failure_recovery_differs_by_topology(self):
        self.assertTrue(run_scenario(SCENARIOS[5], 'single').correct)
        self.assertTrue(run_scenario(SCENARIOS[5], 'manager').correct)
        self.assertFalse(run_scenario(SCENARIOS[5], 'peer').correct)

    def test_multi_agent_hurts_simple_task_via_overhead(self):
        single = run_scenario(SCENARIOS[0], 'single')
        manager = run_scenario(SCENARIOS[0], 'manager')
        self.assertTrue(single.correct and manager.correct)
        self.assertGreater(manager.cost, single.cost)

    def test_manager_has_highest_correctness_but_not_lowest_cost(self):
        a = aggregate(benchmark())
        self.assertGreater(a['manager']['correct_rate'], a['single']['correct_rate'])
        self.assertGreater(a['manager']['mean_cost'], a['single']['mean_cost'])

if __name__ == '__main__': unittest.main()
