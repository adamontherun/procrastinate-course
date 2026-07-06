"""Chapter 12: keeping the table small, and surviving dead workers.

uv run python -m examples.ch12_ops
"""

import asyncio
import os
import signal
import subprocess
import sys

from examples.common import make_app

app = make_app()


@app.task(name="ch12.ping", queue="ch12-clean")
async def ping() -> None:
    pass


async def main() -> None:
    async with app.open_async():
        # --- Part A: delete jobs the moment they finish -------------------
        for _ in range(3):
            await ping.defer_async()
        await app.run_worker_async(queues=["ch12-clean"], wait=False, delete_jobs="always")
        remaining = list(await app.job_manager.list_jobs_async(queue="ch12-clean"))
        print(f"after delete_jobs='always': {len(remaining)} rows left")

        # --- Part B: manufacture a stalled job, then recover it -----------
        job_id = await app.configure_task(name="ch12.long_job", queue="ch12").defer_async()

        worker = subprocess.Popen(
            [sys.executable, "-m", "examples.ch12_worker_process"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        await asyncio.sleep(3)  # let it register, heartbeat, and grab the job

        status = await app.job_manager.get_job_status_async(job_id)
        print(f"worker (pid {worker.pid}) picked the job up: status={status.value}")

        os.kill(worker.pid, signal.SIGKILL)  # no graceful anything
        print("worker SIGKILLed mid-job")

        await asyncio.sleep(4)  # past the 1s heartbeat, well past 3s silence

        stalled = list(await app.job_manager.get_stalled_jobs(seconds_since_heartbeat=3))
        print(f"stalled jobs detected: {[j.id for j in stalled]}")
        for job in stalled:
            await app.job_manager.retry_job(job)

        status = await app.job_manager.get_job_status_async(job_id)
        print(f"after retry_job: status={status.value}")

        # Tidy up: drop the requeued 60s job so reruns start clean.
        await app.job_manager.cancel_job_by_id_async(job_id, delete_job=True)


if __name__ == "__main__":
    asyncio.run(main())
