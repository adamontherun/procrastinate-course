import asyncio
import contextlib
import datetime

import pytest

from challenges.conftest import load_impl

impl = load_impl("ch06")


@pytest.fixture
async def ch06_app(pg_app):
    @pg_app.task(name="ch06.remind", queue="ch06")
    async def remind(text: str) -> None:
        pass

    return pg_app


async def test_defer_reminder_in(ch06_app):
    before = datetime.datetime.now(datetime.UTC)
    job_id = await impl.defer_reminder_in(ch06_app, text="stretch", seconds=120)
    (job,) = await ch06_app.job_manager.list_jobs_async(id=job_id)

    assert job.status == "todo"
    delay = (job.scheduled_at - before).total_seconds()
    assert 115 < delay < 125

    # A worker run right now must NOT execute it: it isn't due yet.
    await ch06_app.run_worker_async(queues=["ch06"], wait=False)
    (job,) = await ch06_app.job_manager.list_jobs_async(id=job_id)
    assert job.status == "todo"


async def test_defer_reminder_at(ch06_app):
    when = datetime.datetime(2038, 1, 19, 3, 14, 7, tzinfo=datetime.UTC)
    job_id = await impl.defer_reminder_at(ch06_app, text="party like it's 2038", when=when)
    (job,) = await ch06_app.job_manager.list_jobs_async(id=job_id)
    assert job.scheduled_at == when


async def test_heartbeat_fires_every_second(ch06_app):
    beats: list[int] = []
    impl.register_heartbeat(ch06_app, beats)

    worker = asyncio.create_task(
        ch06_app.run_worker_async(queues=["ch06"], install_signal_handlers=False)
    )
    await asyncio.sleep(2.5)
    worker.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await worker

    assert len(beats) >= 2
    assert len(set(beats)) == len(beats), "each firing gets a distinct timestamp"
