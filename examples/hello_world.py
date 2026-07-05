"""Smoke test: defer one job, run a worker until the queue is empty.

Run the schema setup first (once per fresh database):

    uv run procrastinate --app=examples.hello_world.app schema --apply

Then:

    uv run python -m examples.hello_world
"""

import asyncio

import procrastinate

app = procrastinate.App(
    connector=procrastinate.PsycopgConnector(
        conninfo="postgresql://postgres:password@localhost:5441/procrastinate_course",
    ),
)


@app.task
async def greet(name: str) -> None:
    print(f"Hello, {name}!")


async def main() -> None:
    async with app.open_async():
        job_id = await greet.defer_async(name="world")
        print(f"Deferred job {job_id}")
        await app.run_worker_async(wait=False)

        # Prove the round trip: read the job's final status back out.
        status = await app.job_manager.get_job_status_async(job_id)
        print(f"Job {job_id} finished with status: {status.value}")


if __name__ == "__main__":
    asyncio.run(main())
