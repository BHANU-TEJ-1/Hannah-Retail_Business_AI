import unittest

from app.agents.response_generator import ResponseGenerator
from app.schemas.response import Response


class StructuredResponder:
    def __init__(self, value):
        self.value = value
        self.prompts = []

    def invoke(self, prompt):
        self.prompts.append(prompt)
        return self.value


class ResponseModel:
    def __init__(self, responder):
        self.responder = responder

    def with_structured_output(self, schema):
        self.schema = schema
        return self.responder


class ResponseGeneratorTests(unittest.TestCase):
    def test_validates_structured_model_output(self):
        responder = StructuredResponder({"answer": "There are 42 products."})
        generator = ResponseGenerator(llm=ResponseModel(responder))
        answer = generator.invoke("How many products?", {"status": "success", "tool": "sql", "data": [{"count": 42}], "summary": "Retrieved 1 record.", "error": None, "metadata": {}}, "sql")
        self.assertEqual(answer, "There are 42 products.")
        self.assertIn("VALIDATED TOOL RESULT", responder.prompts[0])

    def test_error_and_chat_paths_do_not_make_an_unnecessary_llm_call(self):
        responder = StructuredResponder(Response(answer="unused"))
        generator = ResponseGenerator(llm=ResponseModel(responder))
        error_answer = generator.invoke("query", {"status": "error", "error": "Database lookup timed out."}, "sql")
        chat_answer = generator.invoke("hello", {"status": "success"}, "chat")
        self.assertEqual(error_answer, "Database lookup timed out.")
        self.assertIn("Hello", chat_answer)
        self.assertEqual(responder.prompts, [])


if __name__ == "__main__":
    unittest.main()
