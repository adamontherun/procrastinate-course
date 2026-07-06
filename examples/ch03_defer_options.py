"""Chapter 3: every way to defer a job, and the JSON rule.

uv run python -m examples.ch03_defer_options
"""

import asyncio
import datetime

from examples.ch03_blueprint_tasks import reports
from examples.common import make_app

app = make_app()
app.add_tasks_from(reports, namespace="reports")


@app.task(queue="emails")
async def send_email(to: str, subject: str) -> None:
    print(f"  [send_email] to={to!r} subject={subject!r}")


async def main() -> None:
    async with app.open_async():
        # Plain defer: arguments must be keyword arguments.
        job_id = await send_email.defer_async(to="ada@example.com", subject="Welcome")
        print(f"deferred job {job_id} on queue 'emails'")

        # configure() overrides task defaults for one deferral.
        await send_email.configure(queue="urgent").defer_async(
            to="ops@example.com", subject="Disk is full"
        )

        # A reusable pattern: pre-bind some kwargs, defer the rest.
        weekly = send_email.configure(task_kwargs={"subject": "Your weekly digest"})
        await weekly.defer_async(to="ada@example.com")
        await weekly.defer_async(to="charles@example.com")

        # Deferring by name, without importing the task. A blueprint task's
        # name is "<namespace>:<its original dotted name>".
        await app.configure_task(name="reports:examples.ch03_blueprint_tasks.build").defer_async(
            name="q2-revenue"
        )

        # Batch defer: one round trip for many jobs.
        ids = await send_email.batch_defer_async(
            {"to": "u1@example.com", "subject": "hi"},
            {"to": "u2@example.com", "subject": "hi"},
        )
        print(f"batch deferred jobs {ids}")

        # Task arguments travel as JSON. Anything json.dumps can't handle
        # fails at defer time, not at execution time.
        try:
            # (mypy flags this line too — the type checker catches at review
            # time what json.dumps would only catch at defer time.)
            await send_email.defer_async(
                to="ada@example.com",
                subject=datetime.date(2026, 7, 5),  # type: ignore[arg-type]
            )
        except TypeError as exc:
            print(f"defer with a date object failed: {exc}")

        await app.run_worker_async(wait=False)


if __name__ == "__main__":
    asyncio.run(main())
