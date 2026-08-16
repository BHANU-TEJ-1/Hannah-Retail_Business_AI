import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class ApiTests(unittest.TestCase):
    def test_chat_returns_the_reasoner_answer(self):
        with patch("app.api.chat.reasoner.invoke") as invoke:
            invoke.return_value = {
                "answer": "There are 42 products.",
                "tools_used": ["sql_verifier", "sql_executor"],
            }
            response = TestClient(app).post("/chat", json={"question": "How many products do we have?"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "answer": "There are 42 products.",
                "tools_used": ["sql_verifier", "sql_executor"],
            },
        )

    def test_chat_rejects_an_empty_question_before_invoking_the_reasoner(self):
        with patch("app.api.chat.reasoner.invoke") as invoke:
            response = TestClient(app).post("/chat", json={"question": ""})

        self.assertEqual(response.status_code, 422)
        invoke.assert_not_called()

    def test_chat_returns_a_safe_message_on_reasoner_failure(self):
        with patch("app.api.chat.reasoner.invoke") as invoke:
            invoke.side_effect = Exception("timeout")
            response = TestClient(app).post("/chat", json={"question": "Hello"})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["tools_used"], [])
        self.assertIn("try again", body["answer"].lower())


if __name__ == "__main__":
    unittest.main()
