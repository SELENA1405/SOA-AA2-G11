"""Application adapters implement domain ports and orchestrate infrastructure."""
from app.domain.errors import (
    DuplicateItem, EquipmentNotFound, InvalidRequest, PlanNotFound,
)
from app.domain.ports import DataPort, LoadPlanPort
from app.domain.scenario import calculate_result, to_number, validate_entry
from app.infrastructure.postgres import PostgresData

STATUS_ERRORS = {
    "plan_not_found": PlanNotFound,
    "equipment_not_found": EquipmentNotFound,
    "item_not_found": EquipmentNotFound,
    "duplicate": DuplicateItem,
}


def raise_for_status(status) -> None:
    if status in (None, "ok"):
        return
    error = STATUS_ERRORS.get(status)
    if error is None:
        raise RuntimeError(f"Unexpected persistence status: {status!r}")
    raise error()


class DataAdapter(DataPort):
    def __init__(self, driver: PostgresData): self.driver = driver
    def health(self): return self.driver.health()
    def catalogue(self): return self.driver.catalogue()
    def catalogue_item(self, code): return self.driver.catalogue_item(code)


class LoadPlanAdapter(LoadPlanPort):
    """Only place that knows Selena's method names and status strings."""
    def __init__(self, driver: PostgresData): self.driver = driver

    def create_or_get(self, session_code):
        return self.driver.create_or_get_plan(session_code)["plan_code"]

    def read(self, plan_code, session_code):
        rows = self.driver.read_plan(plan_code, session_code)
        if rows is None:
            raise PlanNotFound()
        return [{"equipmentCode": r["equipment_code"], "unitCount": r["unit_count"]} for r in rows]

    def add(self, plan_code, session_code, equipment_code, unit_count):
        raise_for_status(self.driver.add_item(plan_code, session_code, equipment_code, unit_count))

    def edit(self, plan_code, session_code, equipment_code, unit_count):
        raise_for_status(self.driver.update_item(plan_code, session_code, equipment_code, unit_count))

    def remove(self, plan_code, session_code, equipment_code):
        raise_for_status(self.driver.delete_item(plan_code, session_code, equipment_code))


def _equipment_view(row: dict) -> dict:
    return {
        "equipmentCode": row["equipment_code"],
        "name": row["name"],
        "unitMassKg": to_number(row["unit_mass_kg"]),
        "handlingNotes": row["handling_notes"],
    }


class PlannerService:
    def __init__(self, data: DataPort, plans: LoadPlanPort):
        self.data = data
        self.plans = plans

    def health(self): return self.data.health()

    def equipment_types(self):
        return [_equipment_view(r) for r in self.data.catalogue()]

    def equipment_type(self, code):
        row = self.data.catalogue_item(code)
        if row is None:
            raise EquipmentNotFound()
        return _equipment_view(row)

    def create_plan(self, session_code):
        return {"planCode": self.plans.create_or_get(session_code)}

    def read_plan(self, plan_code, session_code):
        saved = self.plans.read(plan_code, session_code)
        result = calculate_result(saved, self.data.catalogue())
        return {"planCode": plan_code, **result}

    def add_item(self, plan_code, session_code, entry):
        code = entry.get("equipmentCode")
        if not isinstance(code, str) or not code.strip():
            raise InvalidRequest()
        validate_entry(entry)
        self.plans.add(plan_code, session_code, code, entry["unitCount"])

    def edit_item(self, plan_code, session_code, equipment_code, entry):
        validate_entry(entry)
        self.plans.edit(plan_code, session_code, equipment_code, entry["unitCount"])

    def remove_item(self, plan_code, session_code, equipment_code):
        self.plans.remove(plan_code, session_code, equipment_code)


def build_service(database_url: str):
    driver = PostgresData(database_url)
    return PlannerService(DataAdapter(driver), LoadPlanAdapter(driver))