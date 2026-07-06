"""Chapter 10: FastAPI with an embedded procrastinate worker.

uv run uvicorn examples.ch10_fastapi.web:api --port 8123
"""

import asyncio
import contextlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from examples.ch10_fastapi.tasks import app as task_queue
from examples.ch10_fastapi.tasks import send_welcome


@asynccontextmanager
async def lifespan(api: FastAPI) -> AsyncIterator[None]:
    async with task_queue.open_async():
        worker = asyncio.create_task(task_queue.run_worker_async(install_signal_handlers=False))
        yield
        worker.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await asyncio.wait_for(worker, timeout=10)


api = FastAPI(lifespan=lifespan)


@api.post("/signup", status_code=202)
async def signup(email: str) -> dict:
    job_id = await send_welcome.defer_async(email=email)
    return {"job_id": job_id}


@api.get("/jobs/{job_id}")
async def job_status(job_id: int) -> dict:
    status = await task_queue.job_manager.get_job_status_async(job_id)
    return {"job_id": job_id, "status": status.value}
