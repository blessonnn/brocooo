"""Database setup with SQLModel."""

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

# SQLite needs check_same_thread=False for FastAPI
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}
engine = create_engine(settings.database_url, echo=False, connect_args=connect_args)


def create_db_and_tables():
    """Create all tables on startup."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency: yields a DB session."""
    with Session(engine) as session:
        yield session
