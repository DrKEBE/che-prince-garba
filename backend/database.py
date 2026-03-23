# backend\database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import StaticPool
import os
from core.config import settings


from contextlib import contextmanager
from typing import Generator

# Configuration
DATABASE_URL = settings.DATABASE_URL


# Pour SQLite, éviter les problèmes de threads
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Création de l'engine avec configuration optimisée
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=True if os.getenv("DEBUG") == "True" else False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()

# Dépendance pour FastAPI
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Gestionnaire de contexte pour les transactions
@contextmanager
def transaction(db: Session):
    try:
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise