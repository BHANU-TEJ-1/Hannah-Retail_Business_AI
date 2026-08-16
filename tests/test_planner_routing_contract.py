"""Offline contract tests for representative Sprint 1 planner routing decisions."""

import unittest

from app.agents.planner_agent import PlannerAgent
from app.schemas.router_response import RouterResponse


class FixturePlanner:
    """Deterministic structured-output substitute; no provider call is needed."""

    def __init__(self, decisions: dict[str, dict]) -> None:
        self._decisions = decisions

    def invoke(self, prompt: str) -> dict:
        for question, decision in self._decisions.items():
            if f"USER REQUEST\n{question}" in prompt:
                return decision
        raise AssertionError("The planner prompt did not contain a known test question.")


class FixtureModel:
    def __init__(self, decisions: dict[str, dict]) -> None:
        self._planner = FixturePlanner(decisions)

    def with_structured_output(self, schema):
        return self._planner


class PlannerRoutingContractTests(unittest.TestCase):
    def test_representative_requests_keep_the_expected_workflow_contract(self):
        cases = {
            "How many products do we have?": ("sql", False, None),
            "Show customer details for Acme.": ("sql", False, None),
            "Show current inventory for laptops.": ("sql", False, None),
            "List today's orders.": ("sql", False, None),
            "What was revenue last month?": ("analysis", False, None),
            "Show our sales KPIs.": ("analysis", False, None),
            "How did sales grow this quarter?": ("analysis", False, None),
            "What customer trends should I know?": ("analysis", False, None),
            "What is the return policy?": ("rag", False, None),
            "Explain the supplier onboarding SOP.": ("rag", False, None),
            "What is in the employee handbook?": ("rag", False, None),
            "What is the weather in Delhi today?": ("browser", False, None),
            "What is the latest business news?": ("browser", False, None),
            "Is there a public holiday tomorrow?": ("browser", False, None),
            "What is 15% of 4200?": ("calculator", False, None),
            "Calculate a 10% discount on 5000.": ("calculator", False, None),
            "What is 23 multiplied by 8?": ("calculator", False, None),
            "Email the supplier about the delayed shipment.": ("mail", False, None),
            "Send an invoice to the customer.": ("mail", False, None),
            "Send payment reminders to overdue customers.": ("payment", False, None),
            "Hi": ("chat", False, None),
            "Thank you": ("chat", False, None),
            "What can you do?": ("chat", False, None),
            "Tell me about laptops.": ("chat", True, None),
            "Show today's sales and email them to my manager.": ("analysis", False, "mail"),
        }
        decisions = {
            question: {
                "workflow": workflow,
                "confidence": 0.98,
                "reason": "Fixture routing decision.",
                "needs_clarification": clarification,
                "followup": followup,
            }
            for question, (workflow, clarification, followup) in cases.items()
        }
        agent = PlannerAgent(llm=FixtureModel(decisions))

        for question, (workflow, clarification, followup) in cases.items():
            with self.subTest(question=question):
                decision: RouterResponse = agent.invoke(question)
                self.assertEqual(decision.workflow, workflow)
                self.assertEqual(decision.needs_clarification, clarification)
                self.assertEqual(decision.followup, followup)


if __name__ == "__main__":
    unittest.main()
