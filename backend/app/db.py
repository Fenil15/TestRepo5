"""Database setup: SQLAlchemy engine, session factory, and ORM models.

Uses a persistent store so customer records survive backend restarts and
deployments. The connection target is controlled by the ``DATABASE_URL``
environment variable:

- Local dev (default): SQLite file at ``backend/customers.db``.
- Production: set ``DATABASE_URL`` to a Postgres URL, e.g.
  ``postgresql+psycopg://user:pass@host:5432/dbname``.
"""

import os
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# Default to a local SQLite file living alongside the backend package so local
# development is zero-config. Production overrides this with a Postgres URL.
_DEFAULT_SQLITE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "customers.db"
)
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{_DEFAULT_SQLITE_PATH}")

# ``check_same_thread`` is a SQLite-only flag; FastAPI's threadpool may touch a
# session from a different thread than the one that created it.
_connect_args = (
    {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Declarative base for ORM models."""


class Customer(Base):
    """A customer record persisted in the database."""

    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    company: Mapped[str | None] = mapped_column(String, nullable=True)
    address: Mapped[str | None] = mapped_column(String, nullable=True)
    # Used only to preserve a stable, insertion-ordered listing across restarts
    # and database backends; not part of the serialized API response.
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict:
        """Serialize the customer to the dict shape returned by the API."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "company": self.company,
            "address": self.address,
        }


def init_db() -> None:
    """Create database tables if they do not already exist."""
    Base.metadata.create_all(bind=engine)
