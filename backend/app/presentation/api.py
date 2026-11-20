"""HTTP translation only; project dependencies are application-only."""
from typing import Annotated
from fastapi import APIRouter, Header, HTTPException, Response
from app.application.service import PlannerService

Session = Annotated[str, Header(alias="X-Session-Code", min_length=1, max_length=128)]


def routes(service: PlannerService):
    router = APIRouter(prefix="/api")

    @router.get("/health")
    def health():
        if not service.health(): raise HTTPException(503, "Database unavailable")
        return {"status": "ok", "database": "connected"}

    @router.get("/equipment-types")
    def equipment_types(): return service.equipment_types()          # plain array

    @router.get("/equipment-types/{equipment_code}")
    def equipment_type(equipment_code: str): return service.equipment_type(equipment_code)

    @router.post("/load-plans")
    def create_plan(session_code: Session): return service.create_plan(session_code)

    @router.get("/load-plans/{plan_code}")
    def read_plan(plan_code: str, session_code: Session): return service.read_plan(plan_code, session_code)

    @router.post("/load-plans/{plan_code}/items", status_code=201)
    def add_item(plan_code: str, entry: dict, session_code: Session):
        service.add_item(plan_code, session_code, entry)
        return service.read_plan(plan_code, session_code)

    @router.put("/load-plans/{plan_code}/items/{equipment_code}")
    def edit_item(plan_code: str, equipment_code: str, entry: dict, session_code: Session):
        service.edit_item(plan_code, session_code, equipment_code, entry)
        return service.read_plan(plan_code, session_code)

    @router.delete("/load-plans/{plan_code}/items/{equipment_code}", status_code=204, response_class=Response)
    def remove_item(plan_code: str, equipment_code: str, session_code: Session):
        service.remove_item(plan_code, session_code, equipment_code)
        return Response(status_code=204)

    return router