"""Chapter 8: seeing into a running job, stopping one, wrapping them all.

uv run python -m examples.ch08_context_cancel_middleware
"""

import asyncio
import contextlib
import time

from procrastinate import JobContext

from examples.common import make_app

app = make_app()


@app.task(pass_context=True)
async def introspect(context: JobContext) -> None:
    job = context.job
    print(
        f"  [introspect] job {job.id} ({job.task_name}) on queue {job.queue!r}, "
        f"attempt {job.attempts}, run by worker {context.worker_name!r}"
    )


@app.task
async def long_running() -> None:
    try:
        await asyncio.sleep(30)
    except asyncio.CancelledError:
        print("  [long_running] cancelled mid-flight")
        raise


async def time_tasks(call_next, context, worker):  # noqa: ANN001 - middleware signature
    start = time.perf_counter()
    try:
        return await call_next()
    finally:
        elapsed = time.perf_counter() - start
        print(f"  [middleware] {context.task.name} took {elapsed:.2f}s")


async def main() -> None:
    async with app.open_async():
        # 1. Context: what a task can know about itself.
        await introspect.defer_async()
        await app.run_worker_async(wait=False, name="demo-worker")

        # 2. Cancel a job no worker has picked up yet.
        job_id = await introspect.defer_async()
        cancelled = await app.job_manager.cancel_job_by_id_async(job_id)
        status = await app.job_manager.get_job_status_async(job_id)
        print(f"cancel before pickup: cancelled={cancelled}, status={status.value}")

        # 3. Abort a job that is already running.
        worker = asyncio.create_task(
            app.run_worker_async(abort_job_polling_interval=0.5, install_signal_handlers=False)
        )
        job_id = await long_running.defer_async()
        await asyncio.sleep(0.5)  # let the worker pick it up
        await app.job_manager.cancel_job_by_id_async(job_id, abort=True)
        await asyncio.sleep(1.0)
        status = await app.job_manager.get_job_status_async(job_id)
        print(f"abort while running: status={status.value}")
        worker.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await worker

        # 4. Middleware: wrap every task with timing.
        await introspect.defer_async()
        await app.run_worker_async(wait=False, task_middleware=[time_tasks])


if __name__ == "__main__":
    asyncio.run(main())
