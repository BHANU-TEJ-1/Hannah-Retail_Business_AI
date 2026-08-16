from app.rag.vector_store import vector_store


class Retriever:

    def __init__(self):
        vector_store.load()

    def retrieve(self, question: str, k: int = 5):

        return vector_store.similarity_search(
            question,
            k=k
        )


retriever = Retriever()