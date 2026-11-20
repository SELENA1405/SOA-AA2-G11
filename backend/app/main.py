"""Composition root and common error translation."""
import logging
import os
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.application.service import build_service
from app.domain.errors import (
    DomainError, DUPLICATE_ITEM, EQUIPMENT_NOT_FOUND,
    INVALID_REQUEST, INVALID_UNIT_COUNT, PLAN_NOT_FOUND,
)
from app.presentation.api import routes

STATUS_BY_CODE = {
    INVALID_UNIT_COUNT: 400,
    INVALID_REQUEST: 400,
    EQUIPMENT_NOT_FOUND: 404,
    PLAN_NOT_FOUND: 404,
    DUPLICATE_ITEM: 409,
}

def create_app(service=None):
    app = FastAPI(title="AA-02 S18 Club Equipment Transport Planner", docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.include_router(routes(service or build_service(os.environ["DATABASE_URL"])))

    @app.exception_handler(DomainError)
    async def domain_error(request: Request, exc: DomainError):
        return JSONResponse(
            status_code=STATUS_BY_CODE.get(exc.error_code, 400),
            content={"error_code": exc.error_code, "message": exc.message},
        )
    @app.exception_handler(RequestValidationError)
    async def invalid(request: Request, exc):
        return JSONResponse(status_code=400, content={"error_code": "INVALID_REQUEST", "message": "Check request fields and X-Session-Code."})
    @app.exception_handler(Exception)
    async def unavailable(request: Request, exc):
        logging.exception("Request failed: %s", request.url.path)
        return JSONResponse(status_code=503, content={"error_code": "SERVICE_UNAVAILABLE", "message": "Check API/database logs."})
    return app

app = create_app()