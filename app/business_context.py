"""Single source of business identity supplied to RetailAI prompts and tools.

This is what lets the Reasoner understand phrases like "our business", "our
warehouse", or "our city" without the user restating the location every
time. Add or change values via .env - never hardcode a location in a prompt.
"""

from dataclasses import dataclass

from app.config import (
    BUSINESS_CITY,
    BUSINESS_COUNTRY,
    BUSINESS_CURRENCY,
    BUSINESS_HEADQUARTERS,
    BUSINESS_HOURS,
    BUSINESS_NAME,
    BUSINESS_SERVICE_LOCATIONS,
    BUSINESS_STATE,
    BUSINESS_STORE_INFO,
    BUSINESS_TIMEZONE,
    BUSINESS_TYPE,
    BUSINESS_WAREHOUSE_LOCATIONS,
)


@dataclass(frozen=True)
class BusinessContext:
    name: str
    business_type: str
    headquarters: str
    city: str
    state: str
    country: str
    warehouse_locations: str
    service_locations: str
    timezone: str
    business_hours: str
    currency: str
    store_info: str

    def prompt_block(self) -> str:
        fields = {
            "Business": self.name,
            "Business type": self.business_type or "Not configured",
            "Headquarters": self.headquarters or "Not configured — do not assume a location",
            "Operating city": self.city or "Not configured",
            "Operating state": self.state or "Not configured",
            "Operating country": self.country or "Not configured",
            "Warehouse location(s)": self.warehouse_locations or "Not configured",
            "Service area": self.service_locations or "Not configured",
            "Timezone": self.timezone or "Not configured",
            "Business hours": self.business_hours or "Not configured",
            "Currency": self.currency or "Not configured",
            "Store information": self.store_info or "Not configured",
        }
        lines = [f"{label}: {value}" for label, value in fields.items()]

        location = self.city or self.headquarters
        if location:
            lines.append(
                "\nUnless the user names a different place, resolve \"our business\", "
                f"\"our warehouse\", \"our city\", \"our customers\", and \"our deliveries\" "
                f"to {location}"
                + (f", {self.state}" if self.state else "")
                + (f", {self.country}" if self.country else "")
                + ". Use this location for any live lookup (weather, traffic, holidays, "
                "local events, road closures) unless the user specifies somewhere else."
            )

        return "\n".join(lines)


business_context = BusinessContext(
    name=BUSINESS_NAME,
    business_type=BUSINESS_TYPE,
    headquarters=BUSINESS_HEADQUARTERS,
    city=BUSINESS_CITY,
    state=BUSINESS_STATE,
    country=BUSINESS_COUNTRY,
    warehouse_locations=BUSINESS_WAREHOUSE_LOCATIONS,
    service_locations=BUSINESS_SERVICE_LOCATIONS,
    timezone=BUSINESS_TIMEZONE,
    business_hours=BUSINESS_HOURS,
    currency=BUSINESS_CURRENCY,
    store_info=BUSINESS_STORE_INFO,
)
