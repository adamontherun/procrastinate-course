"""Chapter 7: locks serialize execution; queueing locks deduplicate the queue.

uv run python -m examples.ch07_locks
"""

import asyncio
import contextlib
import time

import procrastinate

from examples.common import make_app

app = make_app()


@app.task
async def sync_account(account: str, step: int) -> None:
    await asyncio.sleep(0.5)
    print(f"  [sync_account] {account} step {step} done")


@app.task(queueing_lock="nightly-cleanup")
async def cleanup() -> None:
    print("  [cleanup] ran")


async def wait_until_done(job_ids: list[int]) -> None:
    while True:
        statuses = [(await app.job_manager.get_job_status_async(i)).value for i in job_ids]
        if all(s == "succeeded" for s in statuses):
            return
        await asyncio.sleep(0.05)


async def main() -> None:
    async with app.open_async():
        # A worker that keeps running while we time job pairs against it.
        worker = asyncio.create_task(
            app.run_worker_async(concurrency=2, install_signal_handlers=False)
        )

        # Same lock: these two jobs cannot overlap, even with concurrency=2.
        start = time.perf_counter()
        ids = [
            await sync_account.configure(lock="account-42").defer_async(account="42", step=1),
            await sync_account.configure(lock="account-42").defer_async(account="42", step=2),
        ]
        await wait_until_done(ids)
        print(f"same lock, concurrency=2:       {time.perf_counter() - start:.1f}s")

        # Different locks: the same two jobs overlap freely.
        start = time.perf_counter()
        ids = [
            await sync_account.configure(lock="account-1").defer_async(account="1", step=1),
            await sync_account.configure(lock="account-2").defer_async(account="2", step=1),
        ]
        await wait_until_done(ids)
        print(f"different locks, concurrency=2: {time.perf_counter() - start:.1f}s")

        worker.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await worker

        # Why was the same-lock pair so slow? Releasing a lock doesn't send a
        # notification, so the second job waits for the worker's next poll
        # (5s by default). A tighter fetch_job_polling_interval closes the gap.
        worker = asyncio.create_task(
            app.run_worker_async(
                concurrency=2,
                fetch_job_polling_interval=0.2,
                install_signal_handlers=False,
            )
        )
        start = time.perf_counter()
        ids = [
            await sync_account.configure(lock="account-42").defer_async(account="42", step=3),
            await sync_account.configure(lock="account-42").defer_async(account="42", step=4),
        ]
        await wait_until_done(ids)
        print(f"same lock, 0.2s polling:        {time.perf_counter() - start:.1f}s")

        worker.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await worker

        # Queueing lock: with no worker running, the first cleanup job sits in
        # "todo" — and a second defer with the same queueing lock is refused.
        await cleanup.defer_async()
        try:
            await cleanup.defer_async()
        except procrastinate.exceptions.AlreadyEnqueued as exc:
            print(f"second defer refused: {exc}")

        await app.run_worker_async(wait=False)

        # Once the queue is drained, deferring works again.
        await cleanup.defer_async()
        print("after the queue drained, deferring cleanup worked again")
        await app.run_worker_async(wait=False)


if __name__ == "__main__":
    asyncio.run(main())
