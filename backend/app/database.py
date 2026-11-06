from pathlib import Path

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from app import models  # noqa: F401


def make_engine(database_url: str):
    if ":memory:" not in database_url:
        Path(database_url.removeprefix("sqlite:///")).expanduser().parent.mkdir(parents=True, exist_ok=True)
    options = {"connect_args": {"check_same_thread": False}}
    if database_url == "sqlite:///:memory:":
        options["poolclass"] = StaticPool
    return create_engine(database_url, **options)


def initialize_database(engine):
    SQLModel.metadata.create_all(engine)
