"""Database configuration and session management."""

from pathlib import Path
from typing import Generator

from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, create_engine, Session

# Ensure data directory exists
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Create database engine
DATABASE_URL = f"sqlite:///{DATA_DIR / 'app.db'}"
engine: Engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables(engine: Engine = engine) -> None:
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency to get a database session."""
    with Session(engine) as session:
        yield session
