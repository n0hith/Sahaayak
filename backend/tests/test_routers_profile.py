import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_session_required_for_profile(client: AsyncClient):
    response = await client.get("/api/profile")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_session_sets_cookie_and_blank_profile(session_client: AsyncClient):
    response = await session_client.get("/api/profile")
    assert response.status_code == 200
    body = response.json()
    assert body["incomeBand"] == "unknown"
    assert body["documents"] == []


@pytest.mark.asyncio
async def test_put_profile_updates_fields(session_client: AsyncClient):
    payload = {
        "age": 22,
        "region": "Nadi State (demo)",
        "language": "en",
        "householdSize": 3,
        "incomeBand": "under15",
        "location": "rural",
        "cleanCooking": "no",
        "situations": ["farmer"],
        "educationStage": "unknown",
        "enrolled": "unknown",
        "landholding": "marginal",
        "trainingArea": None,
        "planningBusiness": "unknown",
        "documents": ["identity", "land"],
    }
    response = await session_client.put("/api/profile", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["age"] == 22
    assert body["situations"] == ["farmer"]
    assert body["documents"] == ["identity", "land"]


@pytest.mark.asyncio
async def test_put_profile_rejects_pii_shaped_fields(session_client: AsyncClient):
    payload = {
        "language": "en",
        "incomeBand": "unknown",
        "location": "unknown",
        "cleanCooking": "unknown",
        "situations": [],
        "documents": [],
        "name": "Real Name",
        "phoneNumber": "9999999999",
    }
    response = await session_client.put("/api/profile", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_load_demo_profile(session_client: AsyncClient):
    response = await session_client.post("/api/profile/demo")
    assert response.status_code == 200
    body = response.json()
    assert body["age"] == 20
    assert body["location"] == "town"
    assert body["incomeBand"] == "15to3"
    assert set(body["situations"]) == {"student", "jobseeker"}
    assert set(body["documents"]) == {"identity", "education"}
