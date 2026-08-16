from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI

from app.llm.token_budget import TokenBudget

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    GOOGLE_API_KEY,
    QWEN_MODEL,
    DEEPSEEK_MODEL,
    GEMINI_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    LLM_TIMEOUT,
    LLM_MAX_RETRIES,
    LLM_TOP_P,
    LLM_STREAMING,
    LLM_EFFECTIVE_PROMPT_TOKEN_BUDGET,
)


class BudgetedLLM:
    """Delegate an LLM while applying the shared prompt budget to every call."""

    def __init__(self, llm, token_budget: TokenBudget):
        self._llm = llm
        self._token_budget = token_budget

    def invoke(self, input, config=None, **kwargs):
        return self._llm.invoke(self._token_budget.enforce(input), config=config, **kwargs)

    async def ainvoke(self, input, config=None, **kwargs):
        return await self._llm.ainvoke(self._token_budget.enforce(input), config=config, **kwargs)

    def stream(self, input, config=None, **kwargs):
        return self._llm.stream(self._token_budget.enforce(input), config=config, **kwargs)

    async def astream(self, input, config=None, **kwargs):
        async for chunk in self._llm.astream(self._token_budget.enforce(input), config=config, **kwargs):
            yield chunk

    def batch(self, inputs, config=None, **kwargs):
        return self._llm.batch(
            [self._token_budget.enforce(i) for i in inputs],
            config=config,
            **kwargs,
        )

    async def abatch(self, inputs, config=None, **kwargs):
        return await self._llm.abatch(
            [self._token_budget.enforce(i) for i in inputs],
            config=config,
            **kwargs,
        )

    def bind_tools(self, *args, **kwargs):
        return BudgetedLLM(self._llm.bind_tools(*args, **kwargs), self._token_budget)

    def with_structured_output(self, *args, **kwargs):
        return BudgetedLLM(
            self._llm.with_structured_output(*args, **kwargs),
            self._token_budget,
        )

    def __getattr__(self, name):
        return getattr(self._llm, name)


class LLMFactory:

    def __init__(self):

        token_budget = TokenBudget(LLM_EFFECTIVE_PROMPT_TOKEN_BUDGET)

        common_kwargs = dict(
            model_provider="openai",
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            temperature=LLM_TEMPERATURE,
            max_completion_tokens=LLM_MAX_TOKENS,
            timeout=LLM_TIMEOUT,
            max_retries=LLM_MAX_RETRIES,
            top_p=LLM_TOP_P,
            streaming=LLM_STREAMING,
        )

        self.qwen = BudgetedLLM(
            init_chat_model(
                model=QWEN_MODEL,
                **common_kwargs,
            ),
            token_budget,
        )

        self.deepseek = BudgetedLLM(
            init_chat_model(
                model=DEEPSEEK_MODEL,
                **common_kwargs,
            ),
            token_budget,
        )

        self.gemini = BudgetedLLM(
            ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                google_api_key=GOOGLE_API_KEY,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
                request_timeout=LLM_TIMEOUT,
                retries=LLM_MAX_RETRIES,
                top_p=LLM_TOP_P,
                disable_streaming=not LLM_STREAMING,
            ),
            token_budget,
        )

    def get_qwen(self):
        return self.deepseek

    def get_deepseek(self):
        return self.deepseek

    def get_gemini(self):
        return self.deepseek

    # -------- Retail AI defaults --------

    def get_sql_generator(self):
        return self.deepseek

    def get_sql_verifier(self):
        return self.deepseek

    def get_rag_llm(self):
        return self.deepseek

    def get_response_generator(self):
        return self.deepseek


llm_factory = LLMFactory()