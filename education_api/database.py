
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Directory for the SQLite database
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# SQLite database file
DATABASE_URL = f"sqlite:///{(DATA_DIR / 'education.db').as_posix()}"

# Create the database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# Session factory for database operations
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


# Base class for database models
class Base(DeclarativeBase):
    pass


# Dependency for obtaining and closing database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()