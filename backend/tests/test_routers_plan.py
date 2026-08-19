import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_plan_generates_tasks_from_profile(session_client: AsyncClient):
    await session_client.post("/api/profile/demo")
    response = await session_client.post("/api/plans/kaushal-nayi-raah")
    assert response.status_code == 200
    body = response.json()
    assert body["schemeId"] == "kaushal-nayi-raah"
    by_id = {task["id"]: task for task in body["tasks"]}
    assert by_id["doc-identity"]["status"] == "available"
    assert by_id["doc-identity"]["done"] is True
    assert "official-instructions" in by_id


@pytest.mark.asyncio
async def test_create_plan_for_missing_scheme_404s(session_client: AsyncClient):
    await session_client.post("/api/profile/demo")
    response = await session_client.post("/api/plans/does-not-exist")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_toggle_task_flips_done_and_persists(session_client: AsyncClient):
    await session_client.post("/api/profile/demo")
    create = await session_client.post("/api/plans/kaushal-nayi-raah")
    plan_id = create.json()["id"]

    toggled = await session_client.patch(f"/api/plans/{plan_id}/tasks/official-instructions")
    assert toggled.status_code == 200
    by_id = {task["id"]: task for task in toggled.json()["tasks"]}
    assert by_id["official-instructions"]["done"] is True

    toggled_again = await session_client.patch(f"/api/plans/{plan_id}/tasks/official-instructions")
    by_id_again = {task["id"]: task for task in toggled_again.json()["tasks"]}
    assert by_id_again["official-instructions"]["done"] is False


@pytest.mark.asyncio
async def test_recreating_plan_preserves_manual_checkbox_state(session_client: AsyncClient):
    await session_client.post("/api/profile/demo")
    create = await session_client.post("/api/plans/nayi-disha")
    plan_id = create.json()["id"]

    # doc-income starts "needed" / not done - manually check it.
    await session_client.patch(f"/api/plans/{plan_id}/tasks/doc-income")

    # Recreate (simulates re-running the questionnaire and regenerating).
    recreated = await session_client.post("/api/plans/nayi-disha")
    by_id = {task["id"]: task for task in recreated.json()["tasks"]}
    assert by_id["doc-income"]["done"] is True


@pytest.mark.asyncio
async def test_explain_task_endpoint(session_client: AsyncClient):
    await session_client.post("/api/profile/demo")
    create = await session_client.post("/api/plans/kaushal-nayi-raah")
    plan_id = create.json()["id"]

    response = await session_client.post(
        f"/api/plans/{plan_id}/explain", json={"taskId": "provider-check", "question": "why"}
    )
    assert response.status_code == 200
    assert "official provider" in response.json()["explanation"]


@pytest.mark.asyncio
async def test_list_plans_returns_only_this_sessions_plans(client: AsyncClient):
    a = client
    await a.post("/api/session")
    await a.post("/api/profile/demo")
    await a.post("/api/plans/kaushal-nayi-raah")

    listed = await a.get("/api/plans")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["schemeId"] == "kaushal-nayi-raah"


@pytest.mark.asyncio
async def test_other_session_cannot_toggle_someone_elses_plan_task(client: AsyncClient):
    await client.post("/api/session")
    await client.post("/api/profile/demo")
    created = await client.post("/api/plans/kaushal-nayi-raah")
    plan_id = created.json()["id"]

    # A brand new client = a brand new anonymous session, no shared cookies.
    from httpx import ASGITransport, AsyncClient as FreshAsyncClient

    from app.main import app

    async with FreshAsyncClient(transport=ASGITransport(app=app), base_url="http://test") as other:
        await other.post("/api/session")
        response = await other.patch(f"/api/plans/{plan_id}/tasks/official-instructions")
        assert response.status_code == 404
