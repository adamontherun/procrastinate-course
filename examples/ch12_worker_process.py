"""Chapter 12: a worker meant to be killed.

Started as a subprocess by ch12_ops.py, then SIGKILLed mid-job to
manufacture a stalled job on purpose.
"""

import asyncio

from examples.common import make_app

app = make_app()


@app.task(name="ch12.long_job", queue="ch12")
async def long_job() -> None:
    await asyncio.sleep(60)


if __name__ == "__main__":
    # Heartbeat every second so the demo doesn't wait long to detect death.
    app.run_worker(queues=["ch12"], update_heartbeat_interval=1)
