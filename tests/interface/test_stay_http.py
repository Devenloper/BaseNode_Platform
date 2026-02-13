# tests/interface/test_stay_http.py

import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, timezone

from interface.main import create_app
from interface.dependencies import get_check_in_handler


# ----------------------------------------------------------
# Fake Handlers (dependency override)
# ----------------------------------------------------------

class FakeHandlerSuccess:
    async def handle(self, command):
        return None


class FakeHandlerVersionConflict:
    async def handle(self, command):
        from application.exceptions import VersionConflictError
        raise VersionConflictError(
            aggregate_id=command.stay_id,
            expected=0,
            actual=1,
        )


class FakeHandlerDomainError:
    async def handle(self, command):
        from domain.common.base_aggregate import DomainError
        raise DomainError("Domain rule violated")


class FakeHandlerInvalidExpected:
    async def handle(self, command):
        from application.exceptions import InvalidExpectedVersionError
        raise InvalidExpectedVersionError("Invalid expected version")


class FakeHandlerUnexpected:
    async def handle(self, command):
        raise RuntimeError("Unexpected failure")


# ----------------------------------------------------------
# Tests
# ----------------------------------------------------------

@pytest.mark.asyncio
async def test_check_in_success():
    app = create_app()
    app.dependency_overrides[get_check_in_handler] = lambda: FakeHandlerSuccess()

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/stays/check-in",
            json={
                "stay_id": str(uuid4()),
                "room_id": "101",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "expected_version": 0,
            },
        )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_version_conflict():
    app = create_app()
    app.dependency_overrides[get_check_in_handler] = lambda: FakeHandlerVersionConflict()

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/stays/check-in",
            json={
                "stay_id": str(uuid4()),
                "room_id": "101",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "expected_version": 0,
            },
        )

    body = response.json()
    assert response.status_code == 409
    assert body["error"]["code"] == "VERSION_CONFLICT"


@pytest.mark.asyncio
async def test_domain_error():
    app = create_app()
    app.dependency_overrides[get_check_in_handler] = lambda: FakeHandlerDomainError()

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/stays/check-in",
            json={
                "stay_id": str(uuid4()),
                "room_id": "101",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "expected_version": 0,
            },
        )

    body = response.json()
    assert response.status_code == 400
    assert body["error"]["code"] == "DOMAIN_ERROR"


@pytest.mark.asyncio
async def test_invalid_expected_version():
    app = create_app()
    app.dependency_overrides[get_check_in_handler] = lambda: FakeHandlerInvalidExpected()

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/stays/check-in",
            json={
                "stay_id": str(uuid4()),
                "room_id": "101",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "expected_version": 0,
            },
        )

    body = response.json()
    assert response.status_code == 400
    assert body["error"]["code"] == "INVALID_EXPECTED_VERSION"


@pytest.mark.asyncio
async def test_unexpected_error():
    app = create_app()
    app.dependency_overrides[get_check_in_handler] = lambda: FakeHandlerUnexpected()

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/stays/check-in",
            json={
                "stay_id": str(uuid4()),
                "room_id": "101",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "expected_version": 0,
            },
        )

    body = response.json()
    assert response.status_code == 500
    assert body["error"]["code"] == "INTERNAL_ERROR"