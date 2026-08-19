from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import create_db_and_tables
from .routers import handoff, match, plan, profile, schemes, session
from .seed.schemes_seed import seed_schemes


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_schemes()
    yield


app = FastAPI(
    title="Sahaayak API",
    description=(
        "Backend for the Sahaayak demo: mock public-benefit scheme discovery "
        "and application-readiness preparation. All scheme data is fictional. "
        "No real government systems are contacted, and no PII fields are "
        "accepted (see schemas/profile.py)."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session.router)
app.include_router(profile.router)
app.include_router(schemes.router)
app.include_router(match.router)
app.include_router(plan.router)
app.include_router(handoff.router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
