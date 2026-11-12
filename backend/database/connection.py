
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool

from backend.core.config import settings


class Base(DeclarativeBase):
    pass


engine_options = {
    "pool_pre_ping": True,
}

if settings.DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {
        "check_same_thread": False
    }

    if settings.DATABASE_URL.endswith(":memory:"):
        engine_options["poolclass"] = StaticPool

engine = create_engine(
    settings.DATABASE_URL,
    **engine_options
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def init_db():
    from backend.database import models

    Base.metadata.create_all(bind=engine)


def check_database_connection() -> bool:
    from sqlalchemy import text

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
