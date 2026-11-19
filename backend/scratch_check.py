from app.domain.scenario import validate_unit_count, calculate_result
from app.domain.errors import InvalidUnitCount

for bad in (0, 16, 1.5, 2.0, True, "3", None, [1]):
    try:
        validate_unit_count(bad); print("FAIL accepted", repr(bad))
    except InvalidUnitCount:
        print("ok rejected", repr(bad))
for good in (1, 15):
    print("ok accepted", validate_unit_count(good))

cat = [{"equipment_code": "EQUIP-001", "unit_mass_kg": 4},
       {"equipment_code": "EQUIP-002", "unit_mass_kg": 7}]
def total(*items): return calculate_result(
    [{"equipmentCode": c, "unitCount": n} for c, n in items], cat)["totalMassKg"]

assert total(("EQUIP-001", 2), ("EQUIP-002", 1)) == 15
assert total(("EQUIP-001", 3), ("EQUIP-002", 1)) == 19
t = total(("EQUIP-001", 3)); assert t == 12 and type(t) is int
print("totals ok")