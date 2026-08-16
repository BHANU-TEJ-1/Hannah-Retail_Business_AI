from app.tools.sql_validator import sql_validator


def test_valid_query():
    result = sql_validator.invoke("SELECT * FROM products")
    assert result["success"] is True


def test_invalid_query_non_select():
    result = sql_validator.invoke("UPDATE products SET price = 0")
    assert result["success"] is False
    assert "SELECT" in result["error"]


def test_dangerous_query_blocked():
    result = sql_validator.invoke("SELECT * FROM products; DROP TABLE products;")
    assert result["success"] is False
    assert "DROP" in result["error"] or "Multiple" in result["error"]


def test_malformed_query_empty():
    result = sql_validator.invoke("   ")
    assert result["success"] is False
    assert "empty" in result["error"].lower()
