from fastapi import Request, status
from fastapi.responses import JSONResponse

# Application layer exceptions
from application.exceptions import (
    VersionConflictError,
    InvalidExpectedVersionError,
)

# Domain layer exception
from domain.common.base_aggregate import DomainError


def version_conflict_handler(
    request: Request,
    exc: VersionConflictError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": {
                "code": "VERSION_CONFLICT",
                "message": str(exc),
            }
        },
    )


def invalid_expected_version_handler(
    request: Request,
    exc: InvalidExpectedVersionError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "INVALID_EXPECTED_VERSION",
                "message": str(exc),
            }
        },
    )


def domain_error_handler(
    request: Request,
    exc: DomainError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "DOMAIN_ERROR",
                "message": str(exc),
            }
        },
    )


# CRITICAL: catches ALL unexpected errors
async def fallback_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error",
            }
        },
    )