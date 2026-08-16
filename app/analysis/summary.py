"""Create structured executive summaries without using an LLM."""


def executive_summary(metrics: dict, top_products: list[dict], top_customers: list[dict]) -> dict:
    revenue = metrics.get("total_revenue")
    growth = metrics.get("growth_percentage")
    phrases = []
    if revenue is not None:
        phrases.append(f"Revenue was {revenue:,.2f}.")
    if growth is not None:
        phrases.append(f"Period growth was {growth:.2f}%.")
    if top_products:
        phrases.append(f"Top product: {top_products[0].get('product', top_products[0].get('name'))}.")
    if top_customers:
        phrases.append(f"Top customer: {top_customers[0].get('name')}.")
    return {"title": "Business Summary", "summary": " ".join(phrases) or "No summary data is available.", "metrics": metrics}
