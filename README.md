# RetailAI

RetailAI is a retail business intelligence assistant that answers questions using:
- **SQL** — operational database queries
- **Analysis** — Pandas-based business analytics (dynamic code generation)
- **RAG** — company documentation via hybrid semantic + BM25 retrieval
- **Browser** — live web research via Tavily
- **Calculator** — mathematical calculations
- **Mail** — email sending via SMTP
- **Payment** — payment collection reminders

## Current Status

**Phase 4 (Backend Validated)** — RetailAI plans each request, executes one validated specialized tool, and returns a final response. The backend has offline coverage for routing, tool facades, structured output, error handling, latency instrumentation, and FastAPI validation.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full component map and target architecture.

## Quick Start

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --reload
```

Open Swagger at `http://127.0.0.1:8000/docs`.

## API

`POST /api/chat` — accepts `{"question": "..."}`, returns the planner's workflow decision.

## Project Structure

```
app/
├── agents/          # Agent facades (planner, sql, analysis, knowledge, browser, etc.)
├── analysis/        # Pandas analytics (to be replaced with dynamic code gen)
├── api/             # FastAPI endpoints
├── database/        # PostgreSQL connection + schema introspection
├── graph/           # LangGraph state machine
├── llm/             # LLM factory + token budget
├── pipelines/       # SQL sub-workflow
├── prompts/         # Prompt templates
├── rag/             # Hybrid RAG pipeline (BM25 + semantic)
├── schemas/         # Pydantic response models
└── tools/           # LangChain tool wrappers + implementations
```
