"""Chapter 4: what queues and concurrency actually do.

uv run python -m examples.ch04_worker_tour
"""

import asyncio
import time

from procrastinate.types import JSONDict

from examples.common import make_app

app = make_app()


@app.task(queue="slow")
async def simulate_io(call_id: int) -> None:
    await asyncio.sleep(1)  # stands in for an HTTP call or a big query


@app.task(queue="reports")
async def nightly_report() -> None:
    print("  [nightly_report] ran")


async def main() -> None:
    async with app.open_async():
        payloads: list[JSONDict] = [{"call_id": i} for i in range(4)]
        await simulate_io.batch_defer_async(*payloads)
        report_job = await nightly_report.defer_async()

        # Process ONLY the "slow" queue, one job at a time.
        start = time.perf_counter()
        await app.run_worker_async(queues=["slow"], wait=False)
        print(f"concurrency=1: 4 one-second jobs took {time.perf_counter() - start:.1f}s")

        status = await app.job_manager.get_job_status_async(report_job)
        print(f"job on the 'reports' queue is still: {status.value}")

        await simulate_io.batch_defer_async(*payloads)

        # Same 4 jobs, but 4 async sub-workers share the event loop.
        start = time.perf_counter()
        await app.run_worker_async(queues=["slow"], concurrency=4, wait=False)
        print(f"concurrency=4: 4 one-second jobs took {time.perf_counter() - start:.1f}s")

        # Drain everything else (no queues argument = listen to all queues).
        await app.run_worker_async(wait=False)


if __name__ == "__main__":
    asyncio.run(main())
