import pytest
from app.domain.errors import InvalidRequest, InvalidUnitCount
from app.domain.scenario import calculate_result, validate_entry, validate_unit_count

CAT = [
    {"equipment_code": "EQUIP-001", "name": "Foldable Chair", "unit_mass_kg": 4},
    {"equipment_code": "EQUIP-002", "name": "Portable Speaker", "unit_mass_kg": 7},
]

def total(*items):
    saved = [{"equipmentCode": c, "unitCount": n} for c, n in items]
    return calculate_result(saved, CAT)["totalMassKg"]

@pytest.mark.parametrize("bad", [0, 16, 1.5, 2.0, True, "3", None, [1]])
def test_bad_counts_rejected(bad):
    with pytest.raises(InvalidUnitCount):
        validate_unit_count(bad)

@pytest.mark.parametrize("good", [1, 15])
def test_bounds_accepted(good):
    assert validate_unit_count(good) == good

def test_missing_unit_count_is_invalid_request():
    with pytest.raises(InvalidRequest):
        validate_entry({})

def test_totals():
    assert total(("EQUIP-001", 2), ("EQUIP-002", 1)) == 15
    assert total(("EQUIP-001", 3), ("EQUIP-002", 1)) == 19
    t = total(("EQUIP-001", 3))
    assert t == 12 and type(t) is int

def test_plan_item_has_name():
    item = calculate_result([{"equipmentCode": "EQUIP-001", "unitCount": 2}], CAT)["items"][0]
    assert item["name"] == "Foldable Chair" and item["lineMassKg"] == 8