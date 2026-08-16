from app.agents.contracts import success, error
from app.agents.mail_agent import MailAgent, mail_agent
from app.agents.sql_agent import SQLAgent, sql_agent
from app.error_messages import log_failure, user_friendly_error
from app.logging_config import get_logger


logger = get_logger(__name__)


class PaymentCollectionsAgent:
    """Find unpaid customer balances and send payment reminder emails."""

    def __init__(
        self,
        sql: SQLAgent = sql_agent,
        mail: MailAgent = mail_agent,
    ) -> None:
        self._sql = sql
        self._mail = mail

    def invoke(self, question: str) -> dict:
        """Run the existing SQL workflow, then send one reminder per customer."""
        try:
            sql_result = self._sql.invoke(self._collection_query(question))
            if sql_result["status"] != "success":
                return error("payment", sql_result.get("summary", "Data retrieval failed.")).to_dict()

            customers = (sql_result.get("data") or [])
            if not customers:
                return success(
                    "payment",
                    summary="No customers with unpaid balances were found.",
                    data=[],
                ).to_dict()

            reminders = [self._send_reminder(customer) for customer in customers]
            sent_count = sum(reminder["success"] for reminder in reminders)
            failed_count = len(reminders) - sent_count
            response = f"Sent {sent_count} payment reminder(s)."
            if failed_count:
                response += f" {failed_count} reminder(s) could not be sent."

            metadata = sql_result.get("metadata", {}).copy()
            return success(
                "payment",
                data={"customers": customers, "reminders": reminders},
                summary=response,
                metadata=metadata,
            ).to_dict()
        except Exception as exc:
            log_failure(logger, "payment_collection", exc)
            return error("payment", user_friendly_error(exc, "Payment collection")).to_dict()

    def _collection_query(self, question: str) -> str:
        return (
            "Find customers with unpaid bills for this collections request: "
            f"{question}. Return customer_name, contact_email, and due_amount for each "
            "customer. Use the database schema and payment status fields correctly."
        )

    def _send_reminder(self, customer: dict) -> dict:
        customer_name = customer.get("customer_name", customer.get("name", "Customer"))
        email = customer.get("contact_email", customer.get("email"))
        due_amount = customer.get("due_amount", customer.get("current_credit", "the outstanding amount"))

        if not email:
            return {
                "success": False,
                "customer": customer_name,
                "response": "Customer email address is missing.",
            }

        body = (
            f"Dear {customer_name},\n\n"
            f"Our records show an outstanding balance of {due_amount}. "
            "Please arrange payment at your earliest convenience.\n\n"
            "Regards,\nRetailAI"
        )
        mail_result = self._mail.invoke(
            recipient=email,
            subject="Payment reminder: outstanding balance",
            body=body,
        )
        return {
            "success": mail_result["status"] == "success",
            "customer": customer_name,
            "email": email,
            "due_amount": due_amount,
            "response": mail_result.get("summary", mail_result.get("error", "")),
        }


payment_agent = PaymentCollectionsAgent()
