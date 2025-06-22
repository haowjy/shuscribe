# backend/src/database/base.py
"""
SQLAlchemy Base definition for models and Alembic
"""
from sqlalchemy.ext.declarative import declarative_base

# The base class which all our ORM models will inherit from
Base = declarative_base()