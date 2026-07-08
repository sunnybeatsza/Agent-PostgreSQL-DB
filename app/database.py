from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()

engine_options = {"pool_pre_ping": True}
if settings.sqlalchemy_database_url.startswith("sqlite"):
    engine_options.update({"connect_args": {"check_same_thread": False}, "poolclass": StaticPool})
else:
    engine_options.update({"pool_size": 5, "max_overflow": 10})

engine = create_engine(settings.sqlalchemy_database_url, **engine_options)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
