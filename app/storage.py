"""SQLAlchemy storage with PostgreSQL row locks and a portable SQLite fallback."""

from __future__ import annotations

import re
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Index, MetaData, Table, create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema, DropSchema

from app.models import Base


class Storage:
    def __init__(
        self, path: str | Path, *, repaired: bool = True, schema: str | None = None
    ) -> None:
        value = str(path)
        if "://" not in value:
            value = "sqlite+pysqlite:///" + str(Path(value).resolve())
        if value.startswith("postgresql://"):
            value = value.replace("postgresql://", "postgresql+psycopg://", 1)
        self.repaired = repaired
        self.schema = schema
        if schema and not re.fullmatch(r"veltryq_[a-z0-9_]{1,48}", schema):
            raise ValueError("test schemas must have a generated veltryq_ name")
        sqlite = value.startswith("sqlite")
        options = {"timeout": 15, "check_same_thread": False} if sqlite else {}
        self.engine = create_engine(value, connect_args=options, pool_pre_ping=True)
        if self.engine.dialect.name not in {"sqlite", "postgresql"}:
            raise ValueError("only PostgreSQL and SQLite are supported")
        if sqlite:

            @event.listens_for(self.engine, "connect")
            def sqlite_pragmas(connection, _record) -> None:
                connection.execute("PRAGMA foreign_keys=ON")
                connection.execute("PRAGMA busy_timeout=15000")
        elif schema:
            self.engine = self.engine.execution_options(schema_translate_map={None: schema})

    @property
    def dialect(self) -> str:
        return self.engine.dialect.name

    def initialize(self) -> None:
        if self.dialect == "postgresql" and self.schema:
            with self.engine.begin() as connection:
                connection.execute(CreateSchema(self.schema, if_not_exists=True))
        Base.metadata.create_all(self.engine)
        if self.repaired:
            # Reflection keeps fixture-specific indexes out of shared model metadata.
            table = Table("refunds", MetaData(), schema=self.schema, autoload_with=self.engine)
            Index(
                "refunds_idempotency_unique",
                table.c.payment_id,
                table.c.idempotency_key,
                unique=True,
            ).create(self.engine, checkfirst=True)

    @contextmanager
    def session(self) -> Iterator[Session]:
        with Session(self.engine, expire_on_commit=False) as session:
            yield session

    @contextmanager
    def transaction(self) -> Iterator[Session]:
        with self.session() as session:
            try:
                if self.dialect == "sqlite":
                    session.connection().exec_driver_sql("BEGIN IMMEDIATE")
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    def close(self, *, drop_test_schema: bool = False) -> None:
        try:
            if drop_test_schema and self.dialect == "postgresql" and self.schema:
                with self.engine.begin() as connection:
                    connection.execute(DropSchema(self.schema, cascade=True, if_exists=True))
        finally:
            self.engine.dispose()
