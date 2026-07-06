"""Chapter 6: run it later, run it every second.

uv run python -m examples.ch06_scheduling
"""

import asyncio
import datetime

from examples.common import make_app

app = make_app()


@app.task
async def reminder(text: str) -> None:
    print(f"  [reminder] {text}")


# A 6-column cron expression: the extra sixth (last) column is seconds,
# so this fires once per second — handy for a demo, silly in production.
@app.periodic(cron="* * * * * *")
@app.task
async def tick(timestamp: int) -> None:
    print(f"  [tick] scheduled for unix time {timestamp}")


async def main() -> None:
    async with app.open_async():
        job_id = await reminder.configure(schedule_in={"seconds": 2}).defer_async(
            text="2 seconds later"
        )
        (job,) = await app.job_manager.list_jobs_async(id=job_id)
        assert job.scheduled_at is not None
        now = datetime.datetime.now(datetime.UTC).replace(microsecond=0)
        print(
            f"deferred at {now.time()}, scheduled_at={job.scheduled_at.time()}, status={job.status}"
        )

        # A worker that stays up for ~3.5s: long enough to see the scheduled
        # job come due and the periodic task fire a few times.
        worker = asyncio.create_task(app.run_worker_async(install_signal_handlers=False))
        await asyncio.sleep(3.5)
        worker.cancel()
        try:
            await worker
        except asyncio.CancelledError:
            print("worker stopped")

        (job,) = await app.job_manager.list_jobs_async(id=job_id)
        print(f"reminder job is now: {job.status}")


if __name__ == "__main__":
    asyncio.run(main())
