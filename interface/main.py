from fastapi import FastAPI
from starlette.middleware.exceptions import ExceptionMiddleware

from interface.stay.router import router as stay_router

from interface.error_handlers import (
    version_conflict_handler,
    invalid_expected_version_handler,
    domain_error_handler,
    fallback_handler,
)

from application.exceptions import (
    VersionConflictError,
    InvalidExpectedVersionError,
)

from domain.common.base_aggregate import DomainError


def create_app() -> FastAPI:
    app = FastAPI()

    # register routers
    app.include_router(stay_router)

    # register exception handlers
    app.add_exception_handler(
        VersionConflictError,
        version_conflict_handler,
    )

    app.add_exception_handler(
        InvalidExpectedVersionError,
        invalid_expected_version_handler,
    )

    app.add_exception_handler(
        DomainError,
        domain_error_handler,
    )

    app.add_exception_handler(
        Exception,
        fallback_handler,
    )

    # CRITICAL FIX: ensure exception middleware catches everything in tests
    app.add_middleware(
        ExceptionMiddleware,
        handlers=app.exception_handlers,
    )

    return app