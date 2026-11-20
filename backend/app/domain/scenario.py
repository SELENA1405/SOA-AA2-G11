"""Pure scenario business rules; no HTTP, database or other-layer imports."""
from decimal import Decimal

from app.domain.errors import EquipmentNotFound, InvalidRequest, InvalidUnitCount

MIN_UNITS = 1
MAX_UNITS = 15


def validate_unit_count(value) -> int:
    """Single quantity check shared by POST and PUT."""
    if isinstance(value, bool):          # bool is a subclass of int: reject first
        raise InvalidUnitCount()
    if type(value) is not int:           # rejects 1.5, 2.0, "3", None, lists
        raise InvalidUnitCount()
    if not MIN_UNITS <= value <= MAX_UNITS:
        raise InvalidUnitCount()
    return value


def validate_entry(entry: dict) -> None:
    """Used for POST and PUT bodies. Only unitCount is checked here;
    equipmentCode existence is checked by the service against the catalogue."""
    if not isinstance(entry, dict):
        raise InvalidRequest()
    validate_unit_count(entry.get("unitCount"))


def _to_number(value: Decimal) -> int | float:
    """Whole numbers come back as int (JSON 4, not "4.00" or 4.0)."""
    return int(value) if value == value.to_integral_value() else float(value)


def calculate_result(saved_entries: list[dict], stored_catalogue: list[dict]) -> dict:
    """saved_entries: [{"equipmentCode", "unitCount"}] (saved items only)
    stored_catalogue: [{"equipment_code", "unit_mass_kg", ...}] from the database."""
    masses = {row["equipment_code"]: Decimal(str(row["unit_mass_kg"])) for row in stored_catalogue}
    lines, total = [], Decimal(0)
    for entry in saved_entries:
        code = entry["equipmentCode"]
        if code not in masses:
            raise EquipmentNotFound()
        unit_mass = masses[code]
        line_mass = Decimal(entry["unitCount"]) * unit_mass
        total += line_mass
        lines.append({
            "equipmentCode": code,
            "unitCount": entry["unitCount"],
            "unitMassKg": _to_number(unit_mass),
            "lineMassKg": _to_number(line_mass),
        })
    return {"items": lines, "totalMassKg": _to_number(total)}