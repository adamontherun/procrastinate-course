import asyncio
import contextlib

import pytest

from challenges.conftest import load_impl

impl = load_impl("ch07")


@pytest.fixture
async def ch07_app(pg_app):
    pg_app.executed_steps = []

    @pg_app.task(name="ch07.step", queue="ch07")
    async def step(account: str, step: int) -> None:
        await asyncio.sleep(0.15)
        pg_app.executed_steps.append((account, step))

    @pg_app.task(name="ch07.cleanup", queue="ch07", queueing_lock="ch07-cleanup")
    async def cleanup() -> None:
        pass

    return pg_app


async def test_steps_share_a_lock_and_run_in_order(ch07_app):
    ids = await impl.defer_account_steps(ch07_app, account="acme", steps=[1, 2, 3])
    assert len(ids) == 3

    jobs = list(await ch07_app.job_manager.list_jobs_async(task="ch07.step"))
    locks = {j.lock for j in jobs}
    assert len(locks) == 1 and None not in locks, "all steps must share one lock"

    worker = asyncio.create_task(
        ch07_app.run_worker_async(
            queues=["ch07"],
            concurrency=2,
            fetch_job_polling_interval=0.1,
            install_signal_handlers=False,
        )
    )
    for _ in range(100):
        await asyncio.sleep(0.1)
        if len(ch07_app.executed_steps) == 3:
            break
    worker.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await worker

    assert ch07_app.executed_steps == [("acme", 1), ("acme", 2), ("acme", 3)]


async def test_cleanup_is_deduplicated(ch07_app):
    first = await impl.defer_cleanup_once(ch07_app)
    second = await impl.defer_cleanup_once(ch07_app)
    assert isinstance(first, int)
    assert second is None

    await ch07_app.run_worker_async(queues=["ch07"], wait=False)
    third = await impl.defer_cleanup_once(ch07_app)
    assert isinstance(third, int), "after the queue drains, deferring works again"
