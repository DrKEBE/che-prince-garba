# backend\database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os
from core.config import settings
from contextlib import contextmanager
from typing import Generator

DATABASE_URL = settings.DATABASE_URL

# Configuration des connect_args selon le type de DB
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}  # SQLite
elif DATABASE_URL.startswith("postgresql"):
    connect_args = {"sslmode": "require"}       # PostgreSQL sur Render
else:
    connect_args = {}

# Création de l'engine SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=True if os.getenv("DEBUG") == "True" else False,
    pool_pre_ping=True
)

# Session maker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Base déclarative
Base = declarative_base()

# Dépendance FastAPI
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Gestionnaire de transactions
@contextmanager
def transaction(db: Session):
    try:
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise