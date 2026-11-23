from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import config


@lru_cache
def get_engine():
    if not config.DATABASE_URL:
        raise RuntimeError("DATABASE_URL não definida. Configure o arquivo .env")
    return create_engine(config.DATABASE_URL, pool_pre_ping=True)


def get_session() -> Session:
    return Session(get_engine(), expire_on_commit=False)