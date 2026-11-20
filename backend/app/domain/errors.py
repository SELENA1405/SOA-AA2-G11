"""Domain errors; no dependencies on other project layers."""

INVALID_UNIT_COUNT = "INVALID_UNIT_COUNT"
INVALID_REQUEST = "INVALID_REQUEST"
EQUIPMENT_NOT_FOUND = "EQUIPMENT_NOT_FOUND"
PLAN_NOT_FOUND = "PLAN_NOT_FOUND"
DUPLICATE_ITEM = "DUPLICATE_ITEM"

UNIT_COUNT_MESSAGE = "unitCount must be a whole number from 1 to 15."


class DomainError(Exception):
    error_code = "DOMAIN_ERROR"
    default_message = "Domain rule violated."

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class InvalidUnitCount(DomainError):
    error_code = INVALID_UNIT_COUNT
    default_message = UNIT_COUNT_MESSAGE


class InvalidRequest(DomainError):
    error_code = INVALID_REQUEST
    default_message = "Check request fields and X-Session-Code."


class EquipmentNotFound(DomainError):
    error_code = EQUIPMENT_NOT_FOUND
    default_message = "Equipment type not found."


class PlanNotFound(DomainError):
    error_code = PLAN_NOT_FOUND
    default_message = "Load plan not found."


class DuplicateItem(DomainError):
    error_code = DUPLICATE_ITEM
    default_message = "Equipment type is already in this load plan."