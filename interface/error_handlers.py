# interface/error_handlers.py

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from application.exceptions import (
    InvalidExpectedVersionError,
    VersionConflictError,
)
from domain.common.base_aggregate import DomainError


def error_envelope(
    code: str,
    message: str,
    details: dict | None = None,
):
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }


# -------------------------------
# 409 — Version Conflict
# -------------------------------
async def version_conflict_handler(
    request: Request,
    exc: VersionConflictError,
):
    return JSONResponse(
        status_code=409,
        content=error_envelope(
            code="VERSION_CONFLICT",
            message="Version conflict",
            details={
                "aggregate_id": str(exc.aggregate_id),
                "expected": exc.expected,
                "actual": exc.actual,
            },
        ),
    )


# -------------------------------
# 400 — Domain errors
# -------------------------------
async def domain_error_handler(
    request: Request,
    exc: DomainError,
):
    return JSONResponse(
        status_code=400,
        content=error_envelope(
            code="DOMAIN_ERROR",
            message=str(exc),
        ),
    )


# -------------------------------
# 400 — Invalid expected version
# -------------------------------
async def invalid_expected_version_handler(
    request: Request,
    exc: InvalidExpectedVersionError,
):
    return JSONResponse(
        status_code=400,
        content=error_envelope(
            code="INVALID_EXPECTED_VERSION",
            message=str(exc),
        ),
    )


# -------------------------------
# 422 — Validation errors
# -------------------------------
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content=error_envelope(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            details=exc.errors(),
        ),
    )


# -------------------------------
# 500 — Fallback
# -------------------------------
async def fallback_handler(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content=error_envelope(
            code="INTERNAL_ERROR",
            message="Internal server error",
        ),
    )