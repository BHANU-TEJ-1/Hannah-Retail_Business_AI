from unittest.mock import MagicMock, patch

from app.tools.gmail_tool import gmail_tool


@patch("app.tools.gmail_tool.smtplib.SMTP")
@patch("app.tools.gmail_tool.EMAIL_ADDRESS", "sender@example.com")
@patch("app.tools.gmail_tool.EMAIL_PASSWORD", "secret")
@patch("app.tools.gmail_tool.SMTP_SERVER", "smtp.example.com")
def test_valid_input(mock_smtp):
    server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = server

    result = gmail_tool.invoke("customer@example.com", "Hello", "This is a test email.")

    assert result["success"] is True
    server.login.assert_called_once()
    server.sendmail.assert_called_once()


def test_invalid_recipient():
    result = gmail_tool.invoke("not-an-email", "Hello", "Body text")
    assert result["success"] is False
    assert "recipient" in result["error"].lower()


def test_missing_subject():
    result = gmail_tool.invoke("customer@example.com", "", "Body text")
    assert result["success"] is False
    assert "subject" in result["error"].lower()


def test_missing_body():
    result = gmail_tool.invoke("customer@example.com", "Hello", "")
    assert result["success"] is False
    assert "body" in result["error"].lower()


@patch("app.tools.gmail_tool.smtplib.SMTP")
@patch("app.tools.gmail_tool.EMAIL_ADDRESS", "sender@example.com")
@patch("app.tools.gmail_tool.EMAIL_PASSWORD", "secret")
@patch("app.tools.gmail_tool.SMTP_SERVER", "smtp.example.com")
def test_send_failure(mock_smtp):
    mock_smtp.side_effect = Exception("connection refused")

    result = gmail_tool.invoke("customer@example.com", "Hello", "Body text")

    assert result["success"] is False
    assert "error" in result
