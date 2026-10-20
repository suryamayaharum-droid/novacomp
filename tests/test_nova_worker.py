import unittest
from unittest.mock import Mock, patch

from nova_worker import _validated_payload, process_task


class NovaWorkerPayloadTests(unittest.TestCase):
    def test_proposal_inherits_queue_run_id(self):
        endpoint, payload = _validated_payload({
            "action": "propose_improvement",
            "run_id": "run-1",
            "payload": {"summary": "health check", "iteration": 1},
        })
        self.assertEqual(endpoint, "/api/agent/evolve/propose")
        self.assertEqual(payload["run_id"], "run-1")

    def test_checkpoint_requires_tasks_list(self):
        with self.assertRaisesRegex(ValueError, "tasks list"):
            _validated_payload({
                "action": "record_checkpoint",
                "run_id": "run-2",
                "payload": {},
            })

    def test_mismatched_run_id_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            _validated_payload({
                "action": "propose_improvement",
                "run_id": "run-1",
                "payload": {"run_id": "run-other", "summary": "test"},
            })

    def test_unknown_action_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not allowlisted"):
            _validated_payload({
                "action": "run_shell",
                "run_id": "run-3",
                "payload": {},
            })

    @patch("nova_worker._headers", return_value={"Authorization": "Bearer test-token"})
    def test_process_posts_validated_payload(self, _headers):
        client = Mock()
        response = Mock()
        response.json.return_value = {"stored": True}
        client.post.return_value = response
        result = process_task(client, {
            "action": "propose_improvement",
            "run_id": "run-4",
            "payload": {"summary": "test result"},
        })
        client.post.assert_called_once_with(
            "/api/agent/evolve/propose",
            json={"summary": "test result", "run_id": "run-4"},
            headers={"Authorization": "Bearer test-token"},
        )
        response.raise_for_status.assert_called_once()
        self.assertEqual(result["response"], {"stored": True})


if __name__ == "__main__":
    unittest.main()
