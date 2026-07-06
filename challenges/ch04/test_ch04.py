import asyncio

import pytest

from challenges.conftest import load_impl

impl = load_impl("ch04")


@pytest.fixture
async def ch04_app(pg_app):
    @pg_app.task(name="ch04.nap", queue="ch04")
    async def nap() -> None:
        await asyncio.sleep(0.5)

    @pg_app.task(name="ch04.other", queue="ch04-other")
    async def other() -> None:
        pass

    return pg_app


async def test_drain_runs_concurrently_and_respects_queues(ch04_app):
    nap = ch04_app.tasks["ch04.nap"]
    await nap.batch_defer_async(*[{} for _ in range(4)])
    other_id = await ch04_app.tasks["ch04.other"].defer_async()

    elapsed = await impl.drain_queue(ch04_app, queue="ch04", concurrency=4)

    # Four 0.5s jobs, four sub-workers: well under the 2s serial floor.
    assert elapsed < 1.5, f"took {elapsed:.2f}s — did concurrency actually apply?"

    done = await ch04_app.job_manager.list_jobs_async(queue="ch04", status="succeeded")
    assert len(list(done)) == 4

    other_status = await ch04_app.job_manager.get_job_status_async(other_id)
    assert other_status.value == "todo", "the other queue should be untouched"
