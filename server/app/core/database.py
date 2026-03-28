from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

# Create the synchronous engine
engine = create_engine(settings.DATABASE_URL, echo=True)


def create_db_and_tables() -> None:
    """Create all SQLModel tables in the database. Called on startup."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a SQLModel Session.
    Usage: session: Session = Depends(get_session)
    """
    with Session(engine) as session:
        yield session
