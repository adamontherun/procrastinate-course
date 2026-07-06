"""Chapter 5: retries, from the blunt instrument to a custom strategy.

uv run python -m examples.ch05_retries
"""

import asyncio

import procrastinate
from procrastinate import BaseRetryStrategy, RetryDecision, jobs

from examples.common import make_app

app = make_app()

ping_attempts = {"count": 0}


# retry=2 means "2 retries", so up to 3 attempts in total.
@app.task(retry=2)
async def flaky_ping() -> None:
    ping_attempts["count"] += 1
    if ping_attempts["count"] < 3:
        raise ConnectionError(f"attempt {ping_attempts['count']} failed")
    print(f"  [flaky_ping] attempt {ping_attempts['count']} succeeded")


# Only ConnectionError is worth retrying; a ValueError will fail immediately.
@app.task(
    retry=procrastinate.RetryStrategy(
        max_attempts=3,
        wait=1,
        retry_exceptions={ConnectionError},
    )
)
async def selective(kind: str) -> None:
    raise ValueError(f"bad input: {kind!r}")


class Escalate(BaseRetryStrategy):
    """Retry immediately, once, at a higher priority."""

    def get_retry_decision(
        self, *, exception: BaseException, job: jobs.Job
    ) -> RetryDecision | None:
        if job.attempts >= 1:
            return None  # give up
        return RetryDecision(retry_in={"seconds": 0}, priority=job.priority + 10)


# The retry= annotation only names bool | int | RetryStrategy, but custom
# BaseRetryStrategy subclasses work at runtime (see the output below).
@app.task(retry=Escalate())  # type: ignore[call-overload]
async def escalating() -> None:
    raise RuntimeError("always fails")


async def show(app: procrastinate.App, job_id: int, label: str) -> None:
    (job,) = await app.job_manager.list_jobs_async(id=job_id)
    print(f"{label}: status={job.status} attempts={job.attempts} priority={job.priority}")


async def main() -> None:
    async with app.open_async():
        ping_id = await flaky_ping.defer_async()
        bad_id = await selective.defer_async(kind="corrupt")
        esc_id = await escalating.defer_async()

        await app.run_worker_async(wait=False)

        await show(app, ping_id, "flaky_ping ")
        await show(app, bad_id, "selective  ")
        await show(app, esc_id, "escalating ")


if __name__ == "__main__":
    asyncio.run(main())
