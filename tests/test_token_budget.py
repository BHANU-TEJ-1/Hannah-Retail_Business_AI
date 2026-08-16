import unittest

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm.token_budget import TokenBudget


class TokenBudgetTests(unittest.TestCase):
    def test_keeps_system_instructions_and_short_user_message(self):
        budget = TokenBudget(max_prompt_tokens=100)
        messages = [SystemMessage(content="You are RetailAI."), HumanMessage(content="hello")]

        retained = budget.enforce(messages)

        self.assertEqual(retained[0].content, "You are RetailAI.")
        self.assertEqual(retained[-1].content, "hello")


if __name__ == "__main__":
    unittest.main()
