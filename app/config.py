import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Models
QWEN_MODEL = os.getenv("QWEN_MODEL")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL")

# LLM defaults. Providers receive these values through ``LLMFactory`` so every
# current and future model uses the same operational limits.
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))
# A short business response should not reserve an entire context window. These
# defaults preserve room for the planner instructions, history, and tool output.
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "60"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))
LLM_TOP_P = float(os.getenv("LLM_TOP_P", "1"))
LLM_STREAMING = os.getenv("LLM_STREAMING", "false").lower() == "true"
GRAPH_RECURSION_LIMIT = int(os.getenv("GRAPH_RECURSION_LIMIT", "12"))
TOOL_TIMEOUT = float(os.getenv("TOOL_TIMEOUT", "30"))
TAVILY_MAX_RESULTS = int(os.getenv("TAVILY_MAX_RESULTS", "5"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Reserve enough room for a complete response and provider overhead. The prompt
# budget can be lowered per deployment, but it cannot consume the context window.
LLM_CONTEXT_WINDOW = int(os.getenv("LLM_CONTEXT_WINDOW", "32768"))
LLM_CONTEXT_SAFETY_MARGIN = int(os.getenv("LLM_CONTEXT_SAFETY_MARGIN", "512"))
LLM_PROMPT_TOKEN_BUDGET = int(os.getenv("LLM_PROMPT_TOKEN_BUDGET", "12000"))
LLM_EFFECTIVE_PROMPT_TOKEN_BUDGET = max(
    1,
    min(
        LLM_PROMPT_TOKEN_BUDGET,
        LLM_CONTEXT_WINDOW - LLM_MAX_TOKENS - LLM_CONTEXT_SAFETY_MARGIN,
    ),
)

# OpenRouter
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# SMTP Configuration

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

# Business profile. Location fields default to this deployment's actual
# operating location so the Reasoner can resolve "our business" / "our
# warehouse" / "our city" without the user restating it every time. Override
# any of these via .env for a different deployment.
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "RetailAI business")
BUSINESS_TYPE = os.getenv("BUSINESS_TYPE", "Retail / distribution")
BUSINESS_HEADQUARTERS = os.getenv("BUSINESS_HEADQUARTERS", "Chennai, Tamil Nadu, India")
BUSINESS_CITY = os.getenv("BUSINESS_CITY", "Chennai")
BUSINESS_STATE = os.getenv("BUSINESS_STATE", "Tamil Nadu")
BUSINESS_COUNTRY = os.getenv("BUSINESS_COUNTRY", "India")
BUSINESS_WAREHOUSE_LOCATIONS = os.getenv("BUSINESS_WAREHOUSE_LOCATIONS", "Chennai, Tamil Nadu")
BUSINESS_SERVICE_LOCATIONS = os.getenv("BUSINESS_SERVICE_LOCATIONS", "Chennai and surrounding Tamil Nadu")
BUSINESS_TIMEZONE = os.getenv("BUSINESS_TIMEZONE", "Asia/Kolkata")
BUSINESS_HOURS = os.getenv("BUSINESS_HOURS", "")
BUSINESS_CURRENCY = os.getenv("BUSINESS_CURRENCY", "INR")
BUSINESS_STORE_INFO = os.getenv("BUSINESS_STORE_INFO", "")
