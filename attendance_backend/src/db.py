"""
Database connection and utility functions for the attendance system.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base
import os

# PUBLIC_INTERFACE
def get_database_url():
    """Return the database URL from environment variable or fallback to default SQLite."""
    # In a real project, you might pull this from os.environ['DB_URL'], but we'll default to SQLite.
    return os.environ.get("SQLITE_DB_URL", "sqlite:///attendance.db")

# PUBLIC_INTERFACE
def create_db_engine():
    """Create and return an SQLAlchemy engine for SQLite."""
    database_url = get_database_url()
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    engine = create_engine(database_url, connect_args=connect_args)
    return engine

# SessionLocal: scoped/session factory tied to engine
engine = create_db_engine()
SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

# PUBLIC_INTERFACE
def init_db():
    """Initialize the database and create all tables."""
    Base.metadata.create_all(bind=engine)
