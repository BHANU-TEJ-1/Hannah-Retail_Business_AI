"""Offline unit tests for every specialized RetailAI tool facade."""

import unittest
from unittest.mock import Mock

from app.agents.browser_agent import BrowserAgent
from app.agents.calculator_agent import CalculatorAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.mail_agent import MailAgent
from app.agents.payment_agent import PaymentCollectionsAgent
from app.agents.sql_agent import SQLAgent


class ToolAgentTests(unittest.TestCase):
    def test_sql_tool_returns_the_pipeline_contract(self):
        pipeline = Mock()
        pipeline.run.return_value = {"status": "success", "tool": "sql", "data": [], "summary": "Done", "error": None, "metadata": {}}
        result = SQLAgent(pipeline=pipeline).invoke("List products")
        self.assertEqual(result["tool"], "sql")
        pipeline.run.assert_called_once_with("List products")

    def test_rag_tool_wraps_knowledge_answer(self):
        pipeline = Mock()
        pipeline.invoke.return_value = "The return window is 30 days."
        result = KnowledgeAgent(pipeline=pipeline).invoke("What is the return policy?")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tool"], "rag")

    def test_browser_tool_wraps_search_and_model_answer(self):
        search = Mock()
        search.search.return_value = {"answer": "Delhi is sunny.", "results": []}
        llm = Mock()
        llm.invoke.return_value = type("Message", (), {"content": "Delhi is sunny."})()
        result = BrowserAgent(llm=llm, search_tool=search).invoke("Weather in Delhi")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tool"], "browser")

    def test_calculator_tool_returns_a_safe_result(self):
        tool = Mock()
        tool.invoke.return_value = "42"
        result = CalculatorAgent(tool=tool).invoke("6 * 7")
        self.assertEqual(result["data"]["result"], "42")
        self.assertEqual(result["tool"], "calculator")

    def test_mail_tool_requires_complete_delivery_fields(self):
        result = MailAgent(tool=Mock()).invoke("customer@example.com")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["tool"], "mail")

    def test_payment_tool_sends_a_reminder_for_each_customer(self):
        sql = Mock()
        sql.invoke.return_value = {
            "status": "success", "tool": "sql",
            "data": [{"customer_name": "Asha", "contact_email": "asha@example.com", "due_amount": 500}],
            "summary": "Retrieved 1 matching record(s).", "error": None, "metadata": {},
        }
        mail = Mock()
        mail.invoke.return_value = {"status": "success", "summary": "Email sent successfully."}

        result = PaymentCollectionsAgent(sql=sql, mail=mail).invoke("Send reminders")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tool"], "payment")
        self.assertEqual(result["data"]["reminders"][0]["success"], True)


if __name__ == "__main__":
    unittest.main()
