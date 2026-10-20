import unittest

from nova_core import (
    PolicyDenied, Risk, TaskSpec, TaskState, ToolPolicy, authorize_tool,
    parallel_waves, transition, validate_task_graph,
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


if __name__ == "__main__":
    unittest.main()
