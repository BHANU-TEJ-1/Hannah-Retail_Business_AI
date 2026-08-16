from app.llm.llm_factory import llm_factory
from app.rag.prompt import RAG_PROMPT
from app.business_context import business_context
from app.rag.hybrid_retriever import hybrid_retriever
from app.logging_config import get_logger


logger = get_logger(__name__)


class RAGPipeline:

    def __init__(self):
        self.llm = llm_factory.get_rag_llm()

    def invoke(self, question: str):

        documents = hybrid_retriever.retrieve(question)
        if not documents:
            return "I could not find relevant information in the company handbook."

        context = "\n\n".join(
            doc.page_content
            for doc in documents
        )

        prompt = RAG_PROMPT.format(
            business_context=business_context.prompt_block(),
            context=context,
            question=question,
        )

        response = self.llm.invoke(prompt)

        if isinstance(response.content, str):
            return response.content
        if isinstance(response.content, list):
            return "".join(
                block.get("text", "")
                for block in response.content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        return str(response.content)


rag_pipeline = RAGPipeline()
