"""
SuperScout Backend — SQLAlchemy Declarative Base

All ORM models should inherit from Base defined here.
This ensures they share the same metadata object, which is required
for Alembic migrations and schema introspection.

Usage:
    from app.db.base import Base

    class MyModel(Base):
        __tablename__ = "my_table"
        ...
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base for all SuperScout ORM models.

    Inherit from this class when creating database models.
    Phase 2 (Cricket Data Architecture) will add the full schema here.
    """
    pass
