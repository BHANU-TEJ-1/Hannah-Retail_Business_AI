"""The existing SQL generation, validation, verification, and response flow."""

from app.database.schema_manager import SchemaManager
from app.agents.contracts import success, error
from app.llm.llm_factory import LLMFactory
from app.prompts.business_rules import BUSINESS_RULES
from app.business_context import business_context
from app.prompts.sql_examples import SQL_EXAMPLES
from app.prompts.sql_prompt import SQL_PROMPT
from app.prompts.verifier_prompt import VERIFIER_PROMPT
from app.schemas.sql_response import SQLResponse
from app.schemas.verifier_response import VerifierResponse
from app.tools.sql_executor import SQLExecutor
from app.tools.sql_validator import SQLValidator
from app.error_messages import log_failure, user_friendly_error
from app.logging_config import get_logger


logger = get_logger(__name__)


class SQLPipeline:
    """Private implementation of the established read-only SQL workflow."""

    def __init__(
        self,
        llm_factory: LLMFactory,
        schema_manager: SchemaManager,
        validator: SQLValidator,
        executor: SQLExecutor,
    ) -> None:
        self._schema_manager = schema_manager
        self._validator = validator
        self._executor = executor
        self._sql_generator = llm_factory.get_sql_generator().with_structured_output(SQLResponse)
        self._sql_verifier = llm_factory.get_sql_verifier().with_structured_output(VerifierResponse)

    def run(self, question: str) -> dict:
        try:
            sql_response = self._generate_sql(question)
            sql = sql_response.sql

            is_valid, validation_message = self._validator.validate(sql)
            if not is_valid:
                logger.warning("sql_validation_failed")
                return error("sql", validation_message, metadata={"sql": sql}).to_dict()

            verification = self._verify_sql(question, sql)
            if not verification.is_valid:
                logger.warning("sql_verification_failed")
                return error("sql", "The requested database query could not be verified safely.").to_dict()

            # Preserve the generated SQL execution behavior; verification remains a gate.
            result = self._executor.execute(sql)
            return success(
                "sql",
                data=result,
                summary=f"Retrieved {len(result)} matching record(s).",
                metadata={"sql": sql},
            ).to_dict()
        except Exception as exc:
            log_failure(logger, "sql_agent", exc)
            return error("sql", user_friendly_error(exc, "Database lookup")).to_dict()

    def _generate_sql(self, question: str) -> SQLResponse:
        prompt = SQL_PROMPT.format(
            schema=self._schema_manager.schema,
            business_rules=BUSINESS_RULES,
            business_context=business_context.prompt_block(),
            examples=SQL_EXAMPLES,
            question=question,
        )
        return self._sql_generator.invoke(prompt)

    def _verify_sql(self, question: str, sql: str) -> VerifierResponse:
        prompt = VERIFIER_PROMPT.format(
            schema=self._schema_manager.schema,
            business_rules=BUSINESS_RULES,
            business_context=business_context.prompt_block(),
            question=question,
            sql=sql,
        )
        return self._sql_verifier.invoke(prompt)
