import unittest
from autonomous_agent import AutonomousAgent

class TestAutonomousAgent(unittest.TestCase):
    def setUp(self):
        self.agent = AutonomousAgent(name="TestAgent", goal="Test goal")

    def test_initialization(self):
        self.assertEqual(self.agent.name, "TestAgent")
        self.assertEqual(self.agent.goal, "Test goal")
        self.assertIsInstance(self.agent.memory, list)
        self.assertEqual(self.agent.memory, [])

    def test_add_to_memory(self):
        self.agent.add_to_memory("First memory")
        self.assertIn("First memory", self.agent.memory)
        self.agent.add_to_memory("Second memory")
        self.assertEqual(self.agent.memory, ["First memory", "Second memory"])

    def test_clear_memory(self):
        self.agent.add_to_memory("Some memory")
        self.agent.clear_memory()
        self.assertEqual(self.agent.memory, [])

    def test_act_returns_str(self):
        result = self.agent.act("Test input")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_act_appends_to_memory(self):
        initial_len = len(self.agent.memory)
        self.agent.act("Remember this")
        self.assertEqual(len(self.agent.memory), initial_len + 1)
        self.assertIn("Remember this", self.agent.memory[-1])

if __name__ == "__main__":
    unittest.main()