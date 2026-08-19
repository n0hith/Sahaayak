import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_schemes_includes_all_six_and_document_labels(client: AsyncClient):
    response = await client.get("/api/schemes")
    assert response.status_code == 200
    body = response.json()
    ids = {scheme["id"] for scheme in body["schemes"]}
    assert ids == {
        "nayi-disha",
        "swasthya-saathi",
        "kisan-sahayog",
        "udyam-shuru",
        "ghar-urja",
        "kaushal-nayi-raah",
    }
    assert body["documentLabels"]["identity"].endswith("(example)")


@pytest.mark.asyncio
async def test_get_single_scheme(client: AsyncClient):
    response = await client.get("/api/schemes/kaushal-nayi-raah")
    assert response.status_code == 200
    assert response.json()["name"] == "Kaushal Nayi Raah Training Voucher"


@pytest.mark.asyncio
async def test_get_missing_scheme_404s(client: AsyncClient):
    response = await client.get("/api/schemes/does-not-exist")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_match_with_demo_profile_produces_expected_levels(session_client: AsyncClient):
    await session_client.post("/api/profile/demo")
    response = await session_client.post("/api/match")
    assert response.status_code == 200
    body = response.json()
    levels = {match["scheme"]["id"]: match["level"] for match in body["matches"]}

    assert levels["kaushal-nayi-raah"] == "strong"
    assert levels["nayi-disha"] == "possible"
    assert levels["kisan-sahayog"] == "explore"
    assert "simpleTerms" in body and len(body["simpleTerms"]) > 0

    # sort order: strong before possible/moreInfo before explore
    order = {"strong": 0, "possible": 1, "moreInfo": 2, "explore": 3}
    ranks = [order[match["level"]] for match in body["matches"]]
    assert ranks == sorted(ranks)


@pytest.mark.asyncio
async def test_scheme_explanation_endpoint(session_client: AsyncClient):
    await session_client.post("/api/profile/demo")
    response = await session_client.get("/api/schemes/kaushal-nayi-raah/explanation")
    assert response.status_code == 200
    assert "match the main demo conditions" in response.json()["explanation"]
