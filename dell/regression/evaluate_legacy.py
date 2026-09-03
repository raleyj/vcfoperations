"""Normalize the legacy iDRAC Power/Thermal responses for regression tests.

This intentionally does not perform network requests.  It lets the management
pack's missing/null and component identity rules be tested without credentials.
"""

from __future__ import annotations

from typing import Any


def _state(value: Any) -> Any:
    """Preserve missing and null values; never coerce them to zero."""
    return value if value is not None else None


def normalize(system: dict[str, Any], power: dict[str, Any], thermal: dict[str, Any]) -> dict[str, Any]:
    power_control = (power.get("PowerControl") or [{}])[0]
    temperatures = thermal.get("Temperatures") or []
    fans = thermal.get("Fans") or []
    supplies = power.get("PowerSupplies") or []

    def component_id(kind: str, item: dict[str, Any]) -> str | None:
        # MemberId is preferred because serial numbers may change on replacement.
        member = item.get("MemberId")
        name = item.get("FanName") or item.get("Name")
        return f"{kind}:{member if member is not None else name}" if (member is not None or name) else None

    return {
        "server": {
            "id": system.get("UUID") or system.get("Id"),
            "power_state": system.get("PowerState"),
            "health": _state((system.get("Status") or {}).get("Health")),
        },
        "power": {
            "watts": _state(power_control.get("PowerConsumedWatts")),
        },
        "temperatures": [
            {
                "id": component_id("temperature", item),
                "reading_c": _state(item.get("ReadingCelsius")),
                "health": _state((item.get("Status") or {}).get("Health")),
            }
            for item in temperatures
        ],
        "fans": [
            {
                "id": component_id("fan", item),
                "rpm": _state(item.get("Reading")),
                "units": item.get("ReadingUnits"),
                "health": _state((item.get("Status") or {}).get("Health")),
                "serial": item.get("SerialNumber"),
            }
            for item in fans
        ],
        "supplies": [
            {
                "id": component_id("supply", item),
                "health": _state((item.get("Status") or {}).get("Health")),
            }
            for item in supplies
        ],
    }
