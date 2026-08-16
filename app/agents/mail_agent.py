from app.agents.contracts import success, error


class MailAgent:
    def __init__(self, tool=None) -> None:
        from app.tools.gmail_tool import gmail_tool
        self._tool = tool or gmail_tool

    def invoke(self, recipient: str, subject: str | None = None, body: str | None = None) -> dict:
        if subject is None or body is None:
            return error(
                "mail",
                "Mail requests need a recipient, subject, and body.",
            ).to_dict()

        result = self._tool.send_email(recipient=recipient, subject=subject, body=body)
        if result.startswith("Email failed:"):
            return error("mail", result).to_dict()

        return success(
            "mail",
            summary=result,
            metadata={"recipient": recipient},
        ).to_dict()


mail_agent = MailAgent()
