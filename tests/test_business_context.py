"""Tests that business location config is centralized, configurable, and
actually reaches the Reasoner's prompt - the thing that lets it resolve
"our business" / "our warehouse" / "our city" without the user restating
Chennai every time.
"""

from app.business_context import BusinessContext, business_context
from app.reasoner.prompts import SYSTEM_PROMPT


def test_default_deployment_is_configured_for_chennai():
    assert business_context.city == "Chennai"
    assert business_context.state == "Tamil Nadu"
    assert business_context.country == "India"
    assert business_context.timezone == "Asia/Kolkata"


def test_prompt_block_tells_the_model_how_to_resolve_our_business():
    block = business_context.prompt_block()

    assert "Chennai" in block
    assert "Tamil Nadu" in block
    assert "India" in block
    assert "our warehouse" in block
    assert "our city" in block


def test_system_prompt_includes_business_context_and_location_guidance():
    assert "Chennai" in SYSTEM_PROMPT
    assert "LOCATION-AWARE REASONING" in SYSTEM_PROMPT
    assert "our warehouse" in SYSTEM_PROMPT


def test_business_context_is_configuration_driven_not_hardcoded():
    # A differently-configured deployment must produce a different prompt
    # block - proving the location isn't hardcoded into the prompt text.
    other = BusinessContext(
        name="Test Co",
        business_type="Retail",
        headquarters="Hyderabad, Telangana, India",
        city="Hyderabad",
        state="Telangana",
        country="India",
        warehouse_locations="Hyderabad",
        service_locations="Hyderabad",
        timezone="Asia/Kolkata",
        business_hours="",
        currency="INR",
        store_info="",
    )
    block = other.prompt_block()

    assert "Hyderabad" in block
    assert "Chennai" not in block
