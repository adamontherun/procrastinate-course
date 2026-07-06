"""Chapter 10 challenge: the lifespan plumbing, without the framework.

Implement:

  * embedded_worker(app) — an ASYNC CONTEXT MANAGER (hint:
    @contextlib.asynccontextmanager) that starts an embedded worker as an
    asyncio task on entry and shuts it down cleanly on exit (cancel, then
    await with a timeout, swallowing the cancellation). The app is already
    open; don't open or close it. Remember which worker flag keeps it from
    fighting over signal handlers.
  * signup(app, email) — the 202-style handler body: defer the task named
    "ch10.welcome" with kwargs email=<email> and return the dict
    {"job_id": <id>}.

The test enters your context manager, calls your handler, and polls the
job's status until the embedded worker has run it. Run:

    uv run pytest challenges/ch10
"""

import procrastinate


def embedded_worker(app: procrastinate.App):
    raise NotImplementedError


async def signup(app: procrastinate.App, email: str) -> dict:
    raise NotImplementedError
