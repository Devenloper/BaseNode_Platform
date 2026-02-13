# interface/main.py

from fastapi import FastAPI

from interface.stay.router import router as stay_router
from interface.error_handlers import (
    version_conflict_handler,
    domain_error_handler,
    invalid_expected_version_handler,
    fallback_handler,
)

from application.exceptions import (
    VersionConflictError,
    InvalidExpectedVersionError,
)
from domain.common.base_aggregate import DomainError


def create_app() -> FastAPI:
    app = FastAPI(title="BaseNode Platform")

    # Routers
    app.include_router(stay_router)

    # Exception handlers (centralized HTTP contract)
    app.add_exception_handler(
        VersionConflictError,
        version_conflict_handler,
    )

    app.add_exception_handler(
        DomainError,
        domain_error_handler,
    )

    app.add_exception_handler(
        InvalidExpectedVersionError,
        invalid_expected_version_handler,
    )

    app.add_exception_handler(
        Exception,
        fallback_handler,
    )

    return app


# ASGI entrypoint
app = create_app()