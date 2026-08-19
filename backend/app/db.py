from sqlmodel import Session, SQLModel, create_engine

from .config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)


def create_db_and_tables() -> None:
    # Import models so they are registered on SQLModel.metadata before create_all.
    from .models import plan, profile, reference, scheme, session  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
