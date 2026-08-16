import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import (
    EMAIL_ADDRESS,
    EMAIL_PASSWORD,
    SMTP_SERVER,
    SMTP_PORT,
    TOOL_TIMEOUT,
)
from app.error_messages import log_failure, user_friendly_error
from app.logging_config import get_logger


logger = get_logger(__name__)

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class GmailTool:
    """Sends an email to a single recipient. Does not decide who to email,
    query the database, or generate content - the Reasoner decides that."""

    name = "mail"
    description = "Sends an email with a given recipient, subject, and body."

    def invoke(self, recipient: str, subject: str, body: str) -> dict:
        if not recipient or not _EMAIL_PATTERN.match(recipient.strip()):
            return {"success": False, "error": "Recipient email address is invalid."}

        if not subject or not subject.strip():
            return {"success": False, "error": "Email subject is required."}

        if not body or not body.strip():
            return {"success": False, "error": "Email body is required."}

        if not all((EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_SERVER)):
            return {
                "success": False,
                "error": "Mail is not configured correctly. Please contact an administrator.",
            }

        try:
            message = MIMEMultipart()
            message["From"] = EMAIL_ADDRESS
            message["To"] = recipient
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=TOOL_TIMEOUT) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.sendmail(EMAIL_ADDRESS, recipient, message.as_string())

            return {"success": True, "message": "Email sent successfully."}

        except Exception as error:
            log_failure(logger, "email_delivery", error)
            return {"success": False, "error": user_friendly_error(error, "Email delivery")}


gmail_tool = GmailTool()
