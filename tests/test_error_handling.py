import unittest
from unittest.mock import Mock

from app.agents.browser_agent import BrowserAgent
from app.pipelines.sql_pipeline import SQLPipeline


class ErrorHandlingTests(unittest.TestCase):
    def test_browser_hides_provider_exception(self):
        tool = Mock()
        tool.search.side_effect = TimeoutError("provider timeout with secret detail")

        result = BrowserAgent(llm=Mock(), search_tool=tool).invoke("latest news")

        self.assertEqual(result["status"], "error")
        self.assertNotIn("secret detail", result.get("summary", result.get("error", "")))
        self.assertIn("timed out", result["error"])

    def test_sql_pipeline_hides_database_exception(self):
        factory = Mock()
        generator = Mock()
        generator.invoke.side_effect = RuntimeError("database password=do-not-expose")
        factory.get_sql_generator.return_value.with_structured_output.return_value = generator
        factory.get_sql_verifier.return_value.with_structured_output.return_value = Mock()
        factory.get_response_generator.return_value.with_structured_output.return_value = Mock()

        pipeline = SQLPipeline(factory, Mock(schema="schema"), Mock(), Mock())
        result = pipeline.run("count products")

        self.assertEqual(result["status"], "error")
        self.assertNotIn("password", result.get("summary", result.get("error", "")))


if __name__ == "__main__":
    unittest.main()