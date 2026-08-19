import os
import tempfile
from typing import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session, SQLModel, create_engine

# Point at a throwaway SQLite file before importing anything that reads
# settings, so the app never touches the real dev/prod database in tests.
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_db_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"
os.environ["SESSION_SECRET"] = "test-secret"
os.environ["CORS_ORIGINS"] = "http://localhost:5173"

from app import db as db_module  # noqa: E402
from app.main import app  # noqa: E402
from app.seed.schemes_seed import seed_schemes  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _prepare_database():
    SQLModel.metadata.create_all(db_module.engine)
    seed_schemes()
    yield
    db_module.engine.dispose()
    try:
        os.remove(_db_path)
    except OSError:
        pass  # best-effort cleanup; Windows may still hold a brief lock


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


@pytest_asyncio.fixture
async def session_client(client: AsyncClient) -> AsyncIterator[AsyncClient]:
    """An AsyncClient that already has an anonymous session cookie set."""
    response = await client.post("/api/session")
    assert response.status_code == 200
    yield client


def get_session() -> Session:
    return Session(db_module.engine)
