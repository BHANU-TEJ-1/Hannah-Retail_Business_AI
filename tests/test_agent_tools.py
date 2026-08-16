import unittest

from app.tools.agent_tools import agent_tools


class AgentToolTests(unittest.TestCase):
    def test_all_specialized_agents_are_registered_as_tools(self):
        tool_names = {tool.name for tool in agent_tools}
        self.assertEqual(
            tool_names,
            {
                "sql_tool",
                "analysis_tool",
                "rag_tool",
                "browser_tool",
                "calculator_tool",
                "mail_tool",
                "payment_tool",
            },
        )


if __name__ == "__main__":
    unittest.main()