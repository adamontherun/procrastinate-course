import time

import pytest

from challenges.conftest import DSN, load_impl

impl = load_impl("ch09")


@pytest.fixture
async def ch09_app(pg_app):
    @pg_app.task(name="ch09.notify", queue="ch09")
    async def notify(message: str) -> None:
        pass

    return pg_app


async def test_defer_from_sync_is_loop_free(ch09_app):
    # Called from async test code, but the implementation must not touch
    # our event loop — a sync connector does its own I/O. (If it tried to
    # reuse the running loop, asgiref would raise RuntimeError here.)
    job_id = impl.defer_from_sync(DSN, "ch09.notify", queue="ch09", message="over the wall")
    assert isinstance(job_id, int)

    (job,) = await ch09_app.job_manager.list_jobs_async(id=job_id)
    assert job.task_name == "ch09.notify"
    assert job.queue == "ch09"
    assert job.task_kwargs == {"message": "over the wall"}

    await ch09_app.run_worker_async(queues=["ch09"], wait=False)
    status = await ch09_app.job_manager.get_job_status_async(job_id)
    assert status.value == "succeeded"


async def test_sync_tasks_overlap_in_threads(pg_app):
    log: list[str] = []
    impl.register_thumbnailer(pg_app, log)

    task = pg_app.tasks["ch09.thumbnail"]
    for _ in range(3):
        await task.defer_async()

    start = time.perf_counter()
    await pg_app.run_worker_async(queues=["ch09"], concurrency=3, wait=False)
    elapsed = time.perf_counter() - start

    assert elapsed < 0.8, f"took {elapsed:.2f}s — three 0.3s sleeps should overlap"
    assert len(log) == 3
    assert len(set(log)) == 3, "each sync task should run in its own thread"
