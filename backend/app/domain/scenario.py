"""Pure scenario business rules; no HTTP, database or other-layer imports."""
from decimal import Decimal

from app.domain.errors import EquipmentNotFound, InvalidRequest, InvalidUnitCount

MIN_UNITS = 1
MAX_UNITS = 15


def validate_unit_count(value) -> int:
    if isinstance(value, bool):
        raise InvalidUnitCount()
    if type(value) is not int:
        raise InvalidUnitCount()
    if not MIN_UNITS <= value <= MAX_UNITS:
        raise InvalidUnitCount()
    return value


def validate_entry(entry: dict) -> None:
    """Shared by POST and PUT. Missing unitCount is a format error, not a bad quantity."""
    if not isinstance(entry, dict) or "unitCount" not in entry:
        raise InvalidRequest()
    validate_unit_count(entry["unitCount"])


def to_number(value) -> int | float:
    """Whole numbers come back as int (JSON 4, not "4.00" or 4.0)."""
    value = Decimal(str(value))
    return int(value) if value == value.to_integral_value() else float(value)


def calculate_result(saved_entries: list[dict], stored_catalogue: list[dict]) -> dict:
    """saved_entries: [{"equipmentCode", "unitCount"}]; stored_catalogue: database rows."""
    catalogue = {row["equipment_code"]: row for row in stored_catalogue}
    lines, total = [], Decimal(0)
    for entry in saved_entries:
        row = catalogue.get(entry["equipmentCode"])
        if row is None:
            raise EquipmentNotFound()
        unit_mass = Decimal(str(row["unit_mass_kg"]))
        line_mass = Decimal(entry["unitCount"]) * unit_mass
        total += line_mass
        lines.append({
            "equipmentCode": entry["equipmentCode"],
            "name": row["name"],
            "unitCount": entry["unitCount"],
            "unitMassKg": to_number(unit_mass),
            "lineMassKg": to_number(line_mass),
        })
    return {"items": lines, "totalMassKg": to_number(total)}