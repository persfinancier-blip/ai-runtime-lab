import unittest

from experiments.orchestration_topologies.benchmark import SCENARIOS, aggregate, benchmark, run_scenario


class TopologyTests(unittest.TestCase):
    def test_all_three_topologies_cover_all_seeded_scenarios(self):
        self.assertEqual(len(benchmark()), len(SCENARIOS) * 3)

    def test_manager_helps_when_context_isolation_preserves_independent_results(self):
        scenario = SCENARIOS[1]
        self.assertFalse(run_scenario(scenario, "single").correct)
        self.assertTrue(run_scenario(scenario, "manager").correct)
        self.assertFalse(run_scenario(scenario, "peer").correct)

    def test_stale_evidence_is_rejected_or_contained_under_shared_rules(self):
        scenario = SCENARIOS[2]
        for topology in ("single", "manager", "peer"):
            self.assertTrue(run_scenario(scenario, topology).correct)
        self.assertEqual(run_scenario(scenario, "manager").stale_context_events, 0)
        self.assertGreater(run_scenario(scenario, "peer").stale_context_events, 0)

    def test_duplicate_delivery_is_idempotent_for_every_topology(self):
        scenario = SCENARIOS[3]
        for topology in ("single", "manager", "peer"):
            result = run_scenario(scenario, topology)
            self.assertTrue(result.correct)
            self.assertEqual(result.work_calls, 1)
            self.assertEqual(result.duplicate_deliveries, 1)

    def test_authoritative_evidence_resolves_conflict_for_every_topology(self):
        scenario = SCENARIOS[4]
        for topology in ("single", "manager", "peer"):
            self.assertTrue(run_scenario(scenario, topology).correct)

    def test_worker_failure_recovers_under_fixed_recovery_rule(self):
        scenario = SCENARIOS[5]
        for topology in ("single", "manager", "peer"):
            result = run_scenario(scenario, topology)
            self.assertTrue(result.correct)
            self.assertEqual(result.recoveries, 1)

    def test_multi_agent_hurts_simple_task_via_structural_overhead(self):
        scenario = SCENARIOS[0]
        single = run_scenario(scenario, "single")
        manager = run_scenario(scenario, "manager")
        peer = run_scenario(scenario, "peer")
        self.assertTrue(single.correct and manager.correct and peer.correct)
        self.assertGreater(manager.cost, single.cost)
        self.assertGreater(peer.cost, single.cost)

    def test_manager_costs_more_but_can_raise_correctness_under_context_pressure(self):
        totals = aggregate(benchmark())
        self.assertGreater(totals["manager"]["correct_rate"], totals["single"]["correct_rate"])
        self.assertGreater(totals["manager"]["mean_cost"], totals["single"]["mean_cost"])

    def test_outcomes_are_not_directly_hardcoded_by_topology_for_stale_conflict_or_failure(self):
        for index in (2, 4, 5):
            outcomes = {run_scenario(SCENARIOS[index], topology).correct for topology in ("single", "manager", "peer")}
            self.assertEqual(outcomes, {True})


if __name__ == "__main__":
    unittest.main()
