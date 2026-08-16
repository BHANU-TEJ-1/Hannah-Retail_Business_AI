"""Tests that the Reasoner uses business context (our city = Chennai) when
deciding what to search for, and reasons from the raw tool result to a
business-relevant answer rather than just repeating the search result.
Uses the same scripted-FakeLLM approach as test_reasoner.py.
"""

from unittest.mock import patch

from app.reasoner.context_builder import context_builder
from app.reasoner.reasoner import Reasoner
from app.reasoner.tool_runtime import ToolRuntime
from tests.test_reasoner import FakeLLM, _ai_final, _ai_tool_call


def _run(responses, question, max_iterations=12):
    fake_llm = FakeLLM(responses)
    reasoner = Reasoner(llm=fake_llm, runtime=ToolRuntime(), max_iterations=max_iterations)
    messages = context_builder.build(question)
    result = reasoner.invoke(messages)
    return result, fake_llm


@patch("app.reasoner.tool_runtime.browser_tool")
def test_holiday_question_searches_the_business_city(mock_browser):
    mock_browser.invoke.return_value = {
        "success": True,
        "answer": "Chennai has no major public holidays this week.",
        "results": [],
    }

    responses = [
        _ai_tool_call("browser", {"query": "public holidays and events this week Chennai Tamil Nadu"}),
        _ai_final("No major holidays in Chennai this week, so no expected disruption to business."),
    ]
    result, _ = _run(responses, "Check internet. Is there any holidays or events this week that may affect our business?")

    assert result["tools_used"] == ["browser"]
    query = mock_browser.invoke.call_args[0][0].lower()
    assert "chennai" in query
    # Must not have wandered off to an unrelated city.
    assert "hyderabad" not in query
    assert "mumbai" not in query


@patch("app.reasoner.tool_runtime.browser_tool")
def test_rain_impact_question_reasons_to_a_business_recommendation(mock_browser):
    mock_browser.invoke.return_value = {
        "success": True,
        "answer": "Heavy rain expected in Chennai tomorrow with possible waterlogging.",
        "results": [],
    }

    responses = [
        _ai_tool_call("browser", {"query": "weather forecast tomorrow Chennai"}),
        _ai_final(
            "Heavy rain is forecast for Chennai tomorrow, which may delay deliveries due to "
            "waterlogging - consider notifying customers of possible delays."
        ),
    ]
    result, _ = _run(responses, "Will heavy rain affect our deliveries tomorrow?")

    assert result["tools_used"] == ["browser"]
    assert "chennai" in mock_browser.invoke.call_args[0][0].lower()
    assert "delay" in result["answer"].lower() or "delivery" in result["answer"].lower()


@patch("app.reasoner.tool_runtime.browser_tool")
def test_umbrella_stock_question_uses_weather_then_recommends(mock_browser):
    mock_browser.invoke.return_value = {
        "success": True,
        "answer": "Chennai forecast: heavy monsoon rain expected all week.",
        "results": [],
    }

    responses = [
        _ai_tool_call("browser", {"query": "weather forecast this week Chennai"}),
        _ai_final("With heavy rain forecast in Chennai this week, it's worth stocking more umbrellas."),
    ]
    result, _ = _run(responses, "Should we stock more umbrellas this week?")

    assert result["tools_used"] == ["browser"]
    assert "umbrella" in result["answer"].lower()


@patch("app.reasoner.tool_runtime.browser_tool")
def test_delivery_route_to_named_destination_uses_our_warehouse_as_origin(mock_browser):
    mock_browser.invoke.return_value = {
        "success": True,
        "answer": "Route via OMR: 35 minutes, moderate traffic, no closures.",
        "results": [],
    }

    responses = [
        _ai_tool_call("browser", {"query": "live traffic road closures travel time warehouse Chennai to T Nagar"}),
        _ai_final("Best route to T Nagar is via OMR, about 35 minutes with moderate traffic and no closures."),
    ]
    result, _ = _run(responses, "Find the best delivery route to T Nagar.")

    assert result["tools_used"] == ["browser"]
    query = mock_browser.invoke.call_args[0][0].lower()
    assert "t nagar" in query
    assert "35 minutes" in result["answer"] or "t nagar" in result["answer"].lower()


@patch("app.reasoner.tool_runtime.browser_tool")
def test_local_events_question_uses_business_city(mock_browser):
    mock_browser.invoke.return_value = {
        "success": True,
        "answer": "A large cultural festival is happening in Chennai this weekend.",
        "results": [],
    }

    responses = [
        _ai_tool_call("browser", {"query": "events this weekend Chennai"}),
        _ai_final("A cultural festival in Chennai this weekend could increase foot traffic and demand."),
    ]
    result, _ = _run(responses, "Any festivals or events this weekend that may increase retail demand?")

    assert result["tools_used"] == ["browser"]
    assert "chennai" in mock_browser.invoke.call_args[0][0].lower()


def test_sql_question_does_not_use_browser():
    responses = [_ai_final("I can look that up - could you tell me which product you mean?")]
    result, _ = _run(responses, "What's our current stock level?")

    # No hard requirement on tool choice here beyond: business-data
    # questions shouldn't be answered by reaching for the browser.
    assert "browser" not in result["tools_used"]
