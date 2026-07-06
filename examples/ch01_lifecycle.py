"""Chapter 1: watch a job move through its lifecycle in the database.

A deferred job is just a row in the procrastinate_jobs table. This script
defers two jobs (one that succeeds, one that fails), and reads their status
straight out of Postgres before and after a worker runs.

    uv run python -m examples.ch01_lifecycle
"""

import asyncio

from examples.common import make_app

app = make_app()


@app.task
async def send_confirmation(order_id: int) -> None:
    print(f"  [task] sending confirmation for order {order_id}")


@app.task
async def flaky_export(report: str) -> None:
    raise RuntimeError(f"export of {report!r} blew up")


async def show_status(label: str, job_ids: list[int]) -> None:
    statuses = [(await app.job_manager.get_job_status_async(job_id)).value for job_id in job_ids]
    print(f"{label}: {statuses}")


async def main() -> None:
    async with app.open_async():
        job_ids = [
            await send_confirmation.defer_async(order_id=1042),
            await flaky_export.defer_async(report="q2-revenue"),
        ]
        await show_status("before the worker runs", job_ids)

        await app.run_worker_async(wait=False)

        await show_status("after the worker runs ", job_ids)


if __name__ == "__main__":
    asyncio.run(main())
