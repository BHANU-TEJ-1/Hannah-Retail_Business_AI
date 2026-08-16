import unittest
from unittest.mock import Mock, patch

from app.agents.browser_agent import BrowserAgent
from app.agents.response_generator import ResponseGenerator
from app.graph.nodes import create_tool_node
from app.schemas.router_response import RouterResponse


class BusinessBehaviorTests(unittest.TestCase):
    def test_browser_adds_configured_country_for_generic_local_request(self):
        search = Mock()
        search.search.return_value = {"answer": "Holiday data", "results": []}
        llm = Mock()
        llm.invoke.return_value = type("Message", (), {"content": "No public holidays."})()
        with patch("app.agents.browser_agent.business_context") as context:
            context.country = "India"
            result = BrowserAgent(llm=llm, search_tool=search).invoke("Are there holidays this week?")

        search.search.assert_called_once_with("Are there holidays this week? in India")
        self.assertEqual(result["metadata"]["search_query"], "Are there holidays this week? in India")

    def test_browser_respects_explicit_location(self):
        with patch("app.agents.browser_agent.business_context") as context:
            context.country = "India"
            self.assertEqual(BrowserAgent._search_query("Weather in Japan today"), "Weather in Japan today")

    def test_tool_node_uses_planner_extracted_calculator_expression(self):
        node = create_tool_node({"calculator": lambda _: self.fail("Registry calculator should not be called")})
        with patch("app.graph.nodes.calculator_agent.invoke") as calculator:
            calculator.return_value = {"status": "success", "tool": "calculator", "data": 42, "summary": "42", "error": None, "metadata": {}}
            result = node({"question": "What is six times seven?", "decision": RouterResponse(workflow="calculator", confidence=1, reason="Math", tool_input={"expression": "6 * 7"})})

        calculator.assert_called_once_with("6 * 7")
        self.assertEqual(result["tool_result"]["data"], 42)

    def test_mail_without_complete_planner_arguments_does_not_send(self):
        node = create_tool_node({"mail": lambda _: self.fail("Mail registry should not be called")})
        result = node({"question": "Email the supplier", "decision": RouterResponse(workflow="mail", confidence=1, reason="Email", needs_clarification=True)})
        self.assertEqual(result["tool_result"]["status"], "error")
        self.assertIn("recipient", result["tool_result"]["error"])


if __name__ == "__main__":
    unittest.main()
