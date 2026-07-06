import asyncio
import contextlib

import pytest

from challenges.conftest import load_impl

impl = load_impl("ch08")


@pytest.fixture
async def ch08_app(pg_app):
    @pg_app.task(name="ch08.fine", queue="ch08")
    async def fine() -> None:
        pass

    @pg_app.task(name="ch08.broken", queue="ch08")
    async def broken() -> None:
        raise RuntimeError("boom")

    @pg_app.task(name="ch08.slow", queue="ch08")
    async def slow() -> None:
        await asyncio.sleep(30)

    return pg_app


async def test_audit_middleware_records_both_outcomes(ch08_app):
    events: list[tuple[str, str]] = []
    middleware = impl.make_audit_middleware(events)

    await ch08_app.tasks["ch08.fine"].defer_async()
    await ch08_app.tasks["ch08.broken"].defer_async()
    await ch08_app.run_worker_async(queues=["ch08"], wait=False, task_middleware=[middleware])

    assert ("ch08.fine", "start") in events
    assert ("ch08.fine", "ok") in events
    assert ("ch08.broken", "start") in events
    assert ("ch08.broken", "error") in events

    # The middleware must not have swallowed the failure.
    jobs = list(await ch08_app.job_manager.list_jobs_async(task="ch08.broken"))
    assert jobs[0].status == "failed"


async def test_abort_stops_a_running_job(ch08_app):
    worker = asyncio.create_task(
        ch08_app.run_worker_async(
            queues=["ch08"],
            abort_job_polling_interval=0.2,
            install_signal_handlers=False,
        )
    )
    job_id = await ch08_app.tasks["ch08.slow"].defer_async()
    await asyncio.sleep(0.5)  # let the worker pick it up

    assert await impl.abort_job(ch08_app, job_id) is True

    for _ in range(50):
        await asyncio.sleep(0.1)
        status = await ch08_app.job_manager.get_job_status_async(job_id)
        if status.value == "aborted":
            break
    assert status.value == "aborted"

    worker.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await worker
