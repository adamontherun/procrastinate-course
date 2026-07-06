"""Shared test plumbing for all chapter challenges.

Run against the skeletons (the default — tests fail until you implement them):

    uv run pytest challenges/ch03

Run against the reference solutions (used by CI to prove the tests are honest):

    COURSE_SOLUTIONS=1 uv run pytest challenges
"""

import importlib
import os
from types import ModuleType

import procrastinate
import psycopg
import pytest

DSN = "postgresql://postgres:password@localhost:5441/procrastinate_course"


def load_impl(chapter: str) -> ModuleType:
    """Import the reader's challenge module, or the reference solution."""
    if os.environ.get("COURSE_SOLUTIONS") == "1":
        return importlib.import_module(f"solutions.{chapter}")
    return importlib.import_module(f"challenges.{chapter}.challenge")


def _ensure_schema(conn: psycopg.Connection) -> None:
    row = conn.execute("SELECT to_regclass('procrastinate_jobs')").fetchone()
    if row is None or row[0] is None:
        schema_app = procrastinate.App(connector=procrastinate.SyncPsycopgConnector(conninfo=DSN))
        with schema_app.open():
            schema_app.schema_manager.apply_schema()


_TRUNCATE = (
    "TRUNCATE procrastinate_jobs, procrastinate_events, "
    "procrastinate_periodic_defers RESTART IDENTITY CASCADE"
)


@pytest.fixture
def clean_db():
    """Guarantee the schema exists and the job tables start and end empty.

    Cleaning up afterwards matters too: a leftover `todo` job from a test
    would be picked up by the next example script's worker, which has no
    idea what a "ch04.other" task is.
    """
    with psycopg.connect(DSN, autocommit=True) as conn:
        _ensure_schema(conn)
        conn.execute(_TRUNCATE)
    yield
    with psycopg.connect(DSN, autocommit=True) as conn:
        conn.execute(_TRUNCATE)


@pytest.fixture
async def pg_app(clean_db):
    """An open procrastinate App connected to the course database."""
    app = procrastinate.App(
        connector=procrastinate.PsycopgConnector(conninfo=DSN),
    )
    async with app.open_async():
        yield app
