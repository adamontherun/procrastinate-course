"""Chapter 4 challenge: run a worker on your terms.

Implement drain_queue: run a worker that

  * processes ONLY the given queue,
  * runs `concurrency` jobs at a time,
  * stops as soon as the queue is empty instead of waiting for new jobs,

and returns the elapsed wall-clock seconds. The test defers four jobs that
each sleep half a second, then checks that concurrency=4 actually made them
overlap — and that a job sitting on a different queue was left alone. Run:

    uv run pytest challenges/ch04
"""

import procrastinate


async def drain_queue(app: procrastinate.App, queue: str, concurrency: int) -> float:
    """Process everything currently on `queue`, then return elapsed seconds."""
    raise NotImplementedError
