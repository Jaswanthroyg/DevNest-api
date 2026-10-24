"""Database setup: engine, session factory and the Base class for models."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# SQLite works out of the box. For PostgreSQL later, just set an env variable:
# DATABASE_URL=postgresql://user:password@localhost/community
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./community.db")

# SQLite needs this flag because FastAPI uses multiple threads.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """All our table classes (models) inherit from this."""


def get_db():
    """Dependency: gives each request its own DB session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
