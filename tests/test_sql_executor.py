from unittest.mock import MagicMock, patch

from app.tools.sql_executor import sql_executor


def _mock_connection(columns, rows):
    cursor = MagicMock()
    cursor.description = [(col,) for col in columns]
    cursor.fetchall.return_value = rows
    connection = MagicMock()
    connection.cursor.return_value = cursor
    return connection


@patch("app.tools.sql_executor.get_connection")
def test_valid_select(mock_get_connection):
    mock_get_connection.return_value = _mock_connection(
        ["id", "name"], [(1, "Milk"), (2, "Bread")]
    )

    result = sql_executor.invoke("SELECT id, name FROM products")

    assert result["success"] is True
    assert result["columns"] == ["id", "name"]
    assert result["row_count"] == 2
    assert result["rows"][0] == {"id": 1, "name": "Milk"}


@patch("app.tools.sql_executor.get_connection")
def test_aggregate_query(mock_get_connection):
    mock_get_connection.return_value = _mock_connection(
        ["total"], [(42,)]
    )

    result = sql_executor.invoke("SELECT COUNT(*) AS total FROM orders")

    assert result["success"] is True
    assert result["row_count"] == 1
    assert result["rows"] == [{"total": 42}]


@patch("app.tools.sql_executor.get_connection")
def test_invalid_sql_returns_structured_error(mock_get_connection):
    connection = MagicMock()
    cursor = MagicMock()
    cursor.execute.side_effect = Exception("syntax error at or near SELCT")
    connection.cursor.return_value = cursor
    mock_get_connection.return_value = connection

    result = sql_executor.invoke("SELCT * FROM products")

    assert result["success"] is False
    assert "error" in result


@patch("app.tools.sql_executor.get_connection")
def test_database_connection_error(mock_get_connection):
    mock_get_connection.side_effect = Exception("could not connect to server")

    result = sql_executor.invoke("SELECT * FROM products")

    assert result["success"] is False
    assert "error" in result
