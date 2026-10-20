import unittest
from nova_evolution import ChangeRisk, Metric, Observation, propose_next_iteration, proposal_to_dict

class NovaEvolutionTests(unittest.TestCase):
    def test_failed_metric_generates_bounded_proposal(self):
        obs = Observation("run-42", "retrieval evaluation", (Metric("recall_at_5", 0.4, 0.8),))
        p = propose_next_iteration(obs, iteration=1, max_iterations=3)
        self.assertIn("recall_at_5", p.objective)
        self.assertFalse(p.execution_allowed)
        self.assertEqual(p.change_risk, ChangeRisk.TESTS)
        self.assertTrue(p.proposal_id)

    def test_known_failure_prioritized(self):
        obs = Observation("run-43", "API validation", (), ("checkpoint restore failed",))
        p = propose_next_iteration(obs, iteration=2)
        self.assertIn("checkpoint restore failed", p.evidence)
        self.assertIn("regression test", p.objective)

    def test_passing_metrics_require_regression_contract(self):
        obs = Observation("run-44", "stable build", (Metric("tests_passed", 10, 10),))
        p = propose_next_iteration(obs, iteration=1)
        self.assertIn("regression/contract test", p.objective)
        self.assertFalse(p.execution_allowed)

    def test_recursion_budget_is_enforced(self):
        obs = Observation("run-45", "test", (Metric("coverage", 40, 80),))
        with self.assertRaises(ValueError):
            propose_next_iteration(obs, iteration=4, max_iterations=3)

    def test_empty_observation_is_rejected(self):
        with self.assertRaises(ValueError):
            propose_next_iteration(Observation("run-46", "nothing", ()), iteration=1)

    def test_json_safe_serialization(self):
        obs = Observation("run-47", "test", (Metric("latency_ms", 120, 100, "lower"),))
        p = proposal_to_dict(propose_next_iteration(obs, iteration=1))
        self.assertEqual(p["change_risk"], "tests")
        self.assertFalse(p["execution_allowed"])

if __name__ == "__main__":
    unittest.main()
