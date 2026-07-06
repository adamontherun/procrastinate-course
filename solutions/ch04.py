"""Reference solution for chapter 4."""

import time

import procrastinate


async def drain_queue(app: procrastinate.App, queue: str, concurrency: int) -> float:
    start = time.perf_counter()
    await app.run_worker_async(queues=[queue], concurrency=concurrency, wait=False)
    return time.perf_counter() - start
