import asyncio

import pytest

from challenges.conftest import load_impl

impl = load_impl("ch10")


@pytest.fixture
async def ch10_app(pg_app):
    pg_app.sent = []

    @pg_app.task(name="ch10.welcome", queue="ch10")
    async def welcome(email: str) -> None:
        pg_app.sent.append(email)

    return pg_app


async def test_embedded_worker_runs_deferred_jobs(ch10_app):
    async with impl.embedded_worker(ch10_app):
        response = await impl.signup(ch10_app, email="ada@example.com")
        assert set(response) == {"job_id"}
        job_id = response["job_id"]

        status = None
        for _ in range(100):
            await asyncio.sleep(0.05)
            status = await ch10_app.job_manager.get_job_status_async(job_id)
            if status.value == "succeeded":
                break
        assert status is not None and status.value == "succeeded"

    assert ch10_app.sent == ["ada@example.com"]

    # After the context manager exits, the worker must be gone: a new job
    # stays in todo.
    job_id = (await impl.signup(ch10_app, email="charles@example.com"))["job_id"]
    await asyncio.sleep(0.5)
    status = await ch10_app.job_manager.get_job_status_async(job_id)
    assert status.value == "todo", "worker should have shut down with the context"
