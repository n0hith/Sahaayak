import re

import pytest
from httpx import AsyncClient

REFERENCE_PATTERN = re.compile(r"^SHY-\d{4}-[A-Z2-7]{5}$")


@pytest.mark.asyncio
async def test_full_journey_session_to_reference(session_client: AsyncClient):
    """create session -> demo profile -> match -> create plan -> toggle
    tasks -> handoff -> fetch reference back, exactly as specced."""
    demo = await session_client.post("/api/profile/demo")
    assert demo.status_code == 200

    match = await session_client.post("/api/match")
    assert match.status_code == 200
    assert any(m["level"] == "strong" for m in match.json()["matches"])

    plan_response = await session_client.post("/api/plans/kaushal-nayi-raah")
    plan_id = plan_response.json()["id"]

    await session_client.patch(f"/api/plans/{plan_id}/tasks/official-instructions")
    await session_client.patch(f"/api/plans/{plan_id}/tasks/provider-check")

    handoff = await session_client.post(
        "/api/handoff",
        json={"schemeId": "kaushal-nayi-raah", "planId": plan_id, "route": "online"},
    )
    assert handoff.status_code == 200
    body = handoff.json()
    assert REFERENCE_PATTERN.match(body["referenceCode"])
    assert body["route"] == "online"
    assert body["completedTasks"] == 3  # doc-identity auto + the two toggled
    assert body["totalTasks"] == 4

    fetched = await session_client.get(f"/api/references/{body['referenceCode']}")
    assert fetched.status_code == 200
    assert fetched.json()["referenceCode"] == body["referenceCode"]


@pytest.mark.asyncio
async def test_handoff_for_mismatched_plan_and_scheme_404s(session_client: AsyncClient):
    await session_client.post("/api/profile/demo")
    plan_response = await session_client.post("/api/plans/kaushal-nayi-raah")
    plan_id = plan_response.json()["id"]

    response = await session_client.post(
        "/api/handoff",
        json={"schemeId": "nayi-disha", "planId": plan_id, "route": "online"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_reference_lookup_is_scoped_to_owning_session(client: AsyncClient):
    await client.post("/api/session")
    await client.post("/api/profile/demo")
    plan_response = await client.post("/api/plans/kaushal-nayi-raah")
    plan_id = plan_response.json()["id"]
    handoff = await client.post(
        "/api/handoff",
        json={"schemeId": "kaushal-nayi-raah", "planId": plan_id, "route": "centre"},
    )
    code = handoff.json()["referenceCode"]

    from httpx import ASGITransport, AsyncClient as FreshAsyncClient

    from app.main import app

    async with FreshAsyncClient(transport=ASGITransport(app=app), base_url="http://test") as other:
        await other.post("/api/session")
        response = await other.get(f"/api/references/{code}")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_reference_codes_are_deterministic_for_identical_inputs():
    from datetime import datetime

    from app.services.reference_generator import generate_reference_code

    now = datetime(2026, 1, 1, 12, 0, 0)
    code_a = generate_reference_code("session-1", "kaushal-nayi-raah", now, attempt=0)
    code_b = generate_reference_code("session-1", "kaushal-nayi-raah", now, attempt=0)
    code_c = generate_reference_code("session-1", "kaushal-nayi-raah", now, attempt=1)

    assert code_a == code_b
    assert code_a != code_c
    assert REFERENCE_PATTERN.match(code_a)
