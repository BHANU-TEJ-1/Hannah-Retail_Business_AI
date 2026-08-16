from unittest.mock import MagicMock

from langchain_core.documents import Document

from app.rag.rag_retriever import RAGRetriever


def _document(content, source="Chapter_1.md", chapter="Chapter_1"):
    return Document(page_content=content, metadata={"source": source, "chapter": chapter})


def test_exact_retrieval():
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = [
        _document("Store hours are 9 AM to 9 PM every day.")
    ]

    rag = RAGRetriever(retriever=mock_retriever)
    result = rag.invoke("What are the store hours?")

    assert result["success"] is True
    assert result["result_count"] == 1
    assert "store hours" in result["results"][0]["content"].lower()
    mock_retriever.retrieve.assert_called_once_with("What are the store hours?", k=5)


def test_semantic_retrieval():
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = [
        _document("Employees should greet every customer within 30 seconds of entry.")
    ]

    rag = RAGRetriever(retriever=mock_retriever)
    result = rag.invoke("How quickly should staff welcome shoppers?")

    assert result["success"] is True
    assert result["result_count"] == 1
    assert "greet" in result["results"][0]["content"].lower()


def test_irrelevant_query_returns_no_results():
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = []

    rag = RAGRetriever(retriever=mock_retriever)
    result = rag.invoke("What is the airspeed velocity of an unladen swallow?")

    assert result["success"] is True
    assert result["result_count"] == 0
    assert result["results"] == []


def test_multi_document_retrieval():
    mock_retriever = MagicMock()
    mock_retriever.retrieve.return_value = [
        _document("Suppliers are paid net-30.", source="Chapter_3.md", chapter="Chapter_3"),
        _document("Purchase orders require manager approval.", source="Chapter_3.md", chapter="Chapter_3"),
        _document("Inventory is counted weekly.", source="Chapter_2.md", chapter="Chapter_2"),
    ]

    rag = RAGRetriever(retriever=mock_retriever)
    result = rag.invoke("Tell me about suppliers and inventory")

    assert result["success"] is True
    assert result["result_count"] == 3
    sources = {item["source"] for item in result["results"]}
    assert sources == {"Chapter_3.md", "Chapter_2.md"}


def test_empty_query():
    mock_retriever = MagicMock()

    rag = RAGRetriever(retriever=mock_retriever)
    result = rag.invoke("")

    assert result["success"] is False
    assert "error" in result
    mock_retriever.retrieve.assert_not_called()


def test_retrieval_failure_returns_structured_error():
    mock_retriever = MagicMock()
    mock_retriever.retrieve.side_effect = Exception("chroma unavailable")

    rag = RAGRetriever(retriever=mock_retriever)
    result = rag.invoke("What are the store hours?")

    assert result["success"] is False
    assert "error" in result
