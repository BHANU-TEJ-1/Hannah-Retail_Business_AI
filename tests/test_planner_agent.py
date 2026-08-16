import unittest

from app.agents.planner_agent import PlannerAgent
from app.prompts.workflow_descriptions import WORKFLOW_DESCRIPTIONS, format_workflow_descriptions
from app.schemas.router_response import RouterResponse


class StructuredPlanner:
    def __init__(self) -> None:
        self.prompt = ""

    def invoke(self, prompt: str) -> dict:
        self.prompt = prompt
        return {
            "workflow": "chat",
            "confidence": 1.0,
            "reason": "Greeting detected.",
            "followup": None,
        }


class PlannerModel:
    def __init__(self, planner: StructuredPlanner) -> None:
        self.planner = planner

    def with_structured_output(self, schema):
        self.schema = schema
        return self.planner


class PlannerAgentTests(unittest.TestCase):
    def test_planner_receives_only_prompt_and_user_question(self):
        structured_planner = StructuredPlanner()
        agent = PlannerAgent(llm=PlannerModel(structured_planner))

        decision = agent.invoke("Hello")

        self.assertIsInstance(decision, RouterResponse)
        self.assertEqual(decision.workflow, "chat")
        self.assertIn("USER REQUEST\nHello", structured_planner.prompt)
        self.assertNotIn("DATABASE_SCHEMA", structured_planner.prompt)
        self.assertNotIn("SELECT *", structured_planner.prompt)

    def test_workflow_descriptions_cover_every_supported_workflow(self):
        self.assertEqual(
            set(WORKFLOW_DESCRIPTIONS),
            {"sql", "analysis", "rag", "browser", "calculator", "mail", "payment", "chat"},
        )
        for description in WORKFLOW_DESCRIPTIONS.values():
            self.assertEqual(
                set(description),
                {"name", "purpose", "use_for", "avoid_for", "examples", "keywords"},
            )

        rendered = format_workflow_descriptions()
        self.assertIn("Keywords (hints only)", rendered)
        self.assertIn("sql — SQL Agent", rendered)

    def test_empty_question_returns_safe_clarification(self):
        structured_planner = StructuredPlanner()
        agent = PlannerAgent(llm=PlannerModel(structured_planner))

        decision = agent.invoke("  ")

        self.assertEqual(decision.workflow, "chat")
        self.assertTrue(decision.needs_clarification)
        self.assertEqual(structured_planner.prompt, "")

    def test_invalid_planner_response_returns_safe_clarification(self):
        class InvalidPlanner(StructuredPlanner):
            def invoke(self, prompt: str) -> dict:
                return {"workflow": "not-a-workflow"}

        agent = PlannerAgent(llm=PlannerModel(InvalidPlanner()))
        decision = agent.invoke("Show inventory")

        self.assertEqual(decision.workflow, "chat")
        self.assertTrue(decision.needs_clarification)

    def test_planner_contract_includes_structured_tool_input(self):
        structured_planner = StructuredPlanner()
        agent = PlannerAgent(llm=PlannerModel(structured_planner))

        decision = agent.invoke("Hello")

        self.assertEqual(decision.tool_input, {})
        self.assertIn('"tool_input"', structured_planner.prompt)


if __name__ == "__main__":
    unittest.main()
