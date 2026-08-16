import unittest

from app.graph.graph import create_graph
from app.schemas.router_response import RouterResponse


class StubPlanner:
    def __init__(self, decision: RouterResponse) -> None:
        self.decision = decision
        self.questions: list[str] = []

    def invoke(self, question: str) -> RouterResponse:
        self.questions.append(question)
        return self.decision


class StubResponder:
    def __init__(self) -> None:
        self.calls = []

    def invoke(self, **kwargs) -> str:
        self.calls.append(kwargs)
        return "There are 42 products."


def successful_sql(_: str) -> dict:
    return {"status": "success", "tool": "sql", "data": [{"count": 42}], "summary": "Retrieved 1 matching record(s).", "error": None, "metadata": {}}


class OrchestratorGraphTests(unittest.TestCase):
    def test_graph_runs_one_primary_tool_then_response_generator(self):
        planner = StubPlanner(RouterResponse(workflow="sql", confidence=0.98, reason="Database request."))
        responder = StubResponder()
        calls = []

        def sql(question: str) -> dict:
            calls.append(question)
            return successful_sql(question)

        result = create_graph(planner=planner, tool_registry={"sql": sql}, responder=responder).invoke({"question": "How many products do we have?"})

        self.assertEqual(planner.questions, ["How many products do we have?"])
        self.assertEqual(calls, ["How many products do we have?"])
        self.assertEqual(result["tool_result"]["data"], [{"count": 42}])
        self.assertIsInstance(result["tool_result"]["metadata"]["latency_ms"], float)
        self.assertEqual(result["answer"], "There are 42 products.")
        self.assertEqual(len(responder.calls), 1)

    def test_invalid_tool_output_is_converted_to_a_safe_error_before_response(self):
        planner = StubPlanner(RouterResponse(workflow="sql", confidence=0.98, reason="Database request."))
        responder = StubResponder()
        result = create_graph(planner=planner, tool_registry={"sql": lambda _: {"status": "success"}}, responder=responder).invoke({"question": "How many products do we have?"})

        self.assertEqual(result["tool_result"]["status"], "error")
        self.assertEqual(result["tool_result"]["tool"], "sql")
        self.assertIn("invalid result", result["tool_result"]["error"])

    def test_chat_skips_specialized_tool_execution_but_still_generates_a_response(self):
        planner = StubPlanner(RouterResponse(workflow="chat", confidence=1.0, reason="Greeting detected."))
        responder = StubResponder()
        result = create_graph(planner=planner, tool_registry={}, responder=responder).invoke({"question": "Hello"})

        self.assertEqual(result["tool_result"]["tool"], "chat")
        self.assertFalse(result["tool_result"]["metadata"]["tool_executed"])
        self.assertEqual(len(responder.calls), 1)

    def test_followup_is_not_executed_without_an_explicit_email_address(self):
        planner = StubPlanner(RouterResponse(workflow="sql", confidence=0.98, reason="Report request.", followup="mail"))
        responder = StubResponder()
        result = create_graph(planner=planner, tool_registry={"sql": successful_sql}, responder=responder).invoke({"question": "Show sales and email my manager"})

        self.assertEqual(result["tool_result"]["tool"], "sql")
        self.assertIn("followup_skipped", result["tool_result"]["metadata"])


if __name__ == "__main__":
    unittest.main()
