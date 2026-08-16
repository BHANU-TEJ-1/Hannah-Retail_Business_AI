from unittest.mock import patch

from app.tools.browser_tool import browser_tool


@patch.object(browser_tool, "client")
def test_valid_request(mock_client):
    mock_client.search.return_value = {
        "answer": "It is sunny.",
        "results": [{"title": "Weather", "url": "https://example.com"}],
    }

    result = browser_tool.invoke("weather in Chennai")

    assert result["success"] is True
    assert result["answer"] == "It is sunny."
    assert len(result["results"]) == 1


def test_empty_query():
    result = browser_tool.invoke("")
    assert result["success"] is False
    assert "error" in result


@patch.object(browser_tool, "client")
def test_search_failure(mock_client):
    mock_client.search.side_effect = Exception("timeout")

    result = browser_tool.invoke("weather in Chennai")

    assert result["success"] is False
    assert "error" in result
