import unittest

from nova_core import (
    PolicyDenied, Risk, TaskSpec, TaskState, ToolPolicy, authorize_tool,
    checkpoint_to_dict, make_checkpoint, parallel_waves, transition,
    validate_task_graph,
)


class NovaCoreTests(unittest.TestCase):
    def test_parallel_waves_respect_dependencies(self):
        tasks = [
            TaskSpec("a", "inspect"),
            TaskSpec("b", "analyze"),
            TaskSpec("c", "combine", depends_on=("a", "b")),
            TaskSpec("d", "report", depends_on=("c",)),
        ]
        self.assertEqual(parallel_waves(tasks), [["a", "b"], ["c"], ["d"]])

    def test_cycle_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_task_graph([
                TaskSpec("a", "x", depends_on=("b",)),
                TaskSpec("b", "y", depends_on=("a",)),
            ])

    def test_external_write_requires_approval(self):
        policy = ToolPolicy("publish", Risk.EXTERNAL_WRITE, requires_approval=True)
        with self.assertRaises(PolicyDenied):
            authorize_tool(policy)
        authorize_tool(policy, approval_granted=True)

    def test_disabled_tool_is_denied(self):
        with self.assertRaises(PolicyDenied):
            authorize_tool(ToolPolicy("browser", Risk.READ, enabled=False))

    def test_state_machine_rejects_skipping_running(self):
        with self.assertRaises(ValueError):
            transition(TaskState.QUEUED, TaskState.SUCCEEDED)
        self.assertEqual(transition(TaskState.QUEUED, TaskState.LEASED), TaskState.LEASED)


    def test_checkpoint_is_json_ready_and_resumable(self):
        tasks = [
            TaskSpec("a", "inspect"),
            TaskSpec("b", "report", depends_on=("a",)),
        ]
        checkpoint = make_checkpoint("run-1", tasks, ["a"], {"a": {"ok": True}})
        payload = checkpoint_to_dict(checkpoint)
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["completed_task_ids"], ("a",))
        self.assertEqual(payload["pending_task_ids"], ("b",))
        self.assertEqual(len(payload["graph_digest"]), 64)

    def test_checkpoint_rejects_unknown_completed_task(self):
        with self.assertRaises(ValueError):
            make_checkpoint("run-1", [TaskSpec("a", "inspect")], ["missing"])


if __name__ == "__main__":
    unittest.main()
