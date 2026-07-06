"""Reference solution for chapter 10."""

import asyncio
import contextlib

import procrastinate


@contextlib.asynccontextmanager
async def embedded_worker(app: procrastinate.App):
    worker = asyncio.create_task(app.run_worker_async(install_signal_handlers=False))
    try:
        yield
    finally:
        worker.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await asyncio.wait_for(worker, timeout=10)


async def signup(app: procrastinate.App, email: str) -> dict:
    job_id = await app.configure_task(name="ch10.welcome").defer_async(email=email)
    return {"job_id": job_id}
