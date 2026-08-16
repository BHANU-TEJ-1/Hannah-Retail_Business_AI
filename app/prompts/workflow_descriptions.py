"""Reusable workflow descriptions used by the RetailAI planner.

Keywords are routing hints only. The planner must use the full request, purpose,
and avoid rules when choosing a workflow.
"""

WORKFLOW_DESCRIPTIONS = {
    # SQL handles factual, operational records stored in PostgreSQL.
    "sql": {
        "name": "SQL Agent",
        "purpose": "Handle operational questions using the PostgreSQL database.",
        "use_for": [
            "products", "customers", "orders", "suppliers", "inventory",
            "stock", "payments", "sales orders", "purchase orders",
        ],
        "avoid_for": [
            "KPIs", "growth", "revenue analysis", "company policies",
            "internet information",
        ],
        "examples": [
            "How many products do we have?", "Show current stock for laptops.",
            "List today's orders.",
        ],
        "keywords": ["product", "customer", "order", "supplier", "inventory", "stock", "payment"],
    },
    # Analysis handles insights computed from cached business data, not raw rows.
    "analysis": {
        "name": "Analysis Agent",
        "purpose": "Answer analytical business questions using Pandas and cached DataFrames.",
        "use_for": [
            "revenue", "profit", "KPIs", "monthly sales", "weekly sales", "growth",
            "trends", "executive summaries", "top products", "top customers",
            "inventory turnover",
        ],
        "avoid_for": ["raw database lookups", "company documentation", "internet searches"],
        "examples": [
            "What were our top-selling products last month?", "How did revenue grow this quarter?",
            "Give me an executive sales summary.",
        ],
        "keywords": ["revenue", "profit", "KPI", "growth", "trend", "top", "summary", "turnover"],
    },
    # RAG is limited to the internal documentation indexed by Hybrid RAG.
    "rag": {
        "name": "RAG Tool",
        "purpose": "Answer questions using company documentation through the existing Hybrid RAG pipeline.",
        "use_for": [
            "SOPs", "company policies", "internal guidelines", "vendor rules",
            "reorder rules", "employee handbook",
        ],
        "avoid_for": ["SQL queries", "analytics", "live internet information"],
        "examples": [
            "What is our reorder policy?", "Explain the supplier onboarding SOP.",
            "What does the employee handbook say about leave?",
        ],
        "keywords": ["policy", "SOP", "guideline", "rule", "handbook", "reorder", "vendor"],
    },
    # Browser is only for information that must be current and public.
    "browser": {
        "name": "Browser Tool",
        "purpose": "Retrieve live information from the internet.",
        "use_for": ["news", "weather", "holidays", "market information", "recent announcements"],
        "avoid_for": ["internal company data", "database information", "company handbook"],
        "examples": [
            "What is the weather in Delhi today?", "Is there a public holiday tomorrow?",
            "What are the latest market prices?",
        ],
        "keywords": ["news", "weather", "holiday", "today", "latest", "market", "announcement"],
    },
    # Calculator is for math when the user has already supplied every number needed.
    "calculator": {
        "name": "Calculator Tool",
        "purpose": "Perform mathematical calculations.",
        "use_for": [
            "arithmetic", "percentages", "discounts", "growth calculations",
            "profit calculations when all numbers are provided",
        ],
        "avoid_for": ["database lookups", "business analytics requiring company data"],
        "examples": ["What is 15% of 2400?", "Calculate a 7% increase on 12 lakh."],
        "keywords": ["calculate", "percentage", "discount", "increase", "decrease", "margin"],
    },
    # Mail is for explicitly sending a message, never for drafting an answer.
    "mail": {
        "name": "Mail Tool",
        "purpose": "Send emails.",
        "use_for": ["supplier emails", "customer emails", "internal notifications"],
        "avoid_for": ["answering questions", "data retrieval"],
        "examples": ["Email the supplier about the delayed shipment.", "Notify the manager by email."],
        "keywords": ["email", "send mail", "notify", "send invoice"],
    },
    # Payment owns the specialized outstanding-payment reminder workflow.
    "payment": {
        "name": "Payment Agent",
        "purpose": "Handle payment reminder workflows.",
        "use_for": [
            "outstanding payment reminders", "payment follow-up", "payment notification workflows",
        ],
        "avoid_for": ["general email sending", "database analytics"],
        "examples": ["Send payment reminders to overdue customers.", "Follow up on outstanding invoices."],
        "keywords": ["overdue", "outstanding", "payment reminder", "collect payment", "follow-up"],
    },
    # Chat is the safe default for conversation and requests that need clarification.
    "chat": {
        "name": "Chat",
        "purpose": "Handle conversational interactions that do not require a business workflow.",
        "use_for": ["greetings", "small talk", "help", "capabilities", "thank you", "clarification requests"],
        "avoid_for": ["business operations", "analytics", "RAG", "SQL", "browser requests"],
        "examples": ["Hello", "What can you do?", "Tell me about laptops."],
        "keywords": ["hello", "hi", "thanks", "help", "what can you do"],
    },
}


def format_workflow_descriptions() -> str:
    """Render the descriptions in a compact, readable form for the planner prompt."""
    sections = []
    for workflow, description in WORKFLOW_DESCRIPTIONS.items():
        required_fields = {"name", "purpose", "use_for", "avoid_for", "examples", "keywords"}
        missing_fields = required_fields - set(description)
        if missing_fields:
            raise ValueError(f"Workflow '{workflow}' is missing: {', '.join(sorted(missing_fields))}")
        sections.append(
            "\n".join(
                [
                    f"{workflow} — {description['name']}",
                    f"Purpose: {description['purpose']}",
                    f"Use for: {', '.join(description['use_for'])}.",
                    f"Do NOT use for: {', '.join(description['avoid_for'])}.",
                    f"Typical requests: {'; '.join(description['examples'])}",
                    f"Keywords (hints only): {', '.join(description['keywords'])}.",
                ]
            )
        )
    return "\n\n".join(sections)
