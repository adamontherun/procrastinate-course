"""Chapter 7 challenge: one account at a time, one cleanup in the queue.

The test registers "ch07.step" (queue "ch07") and "ch07.cleanup" (queue
"ch07", queueing lock "ch07-cleanup") for you. Implement:

  * defer_account_steps(app, account, steps) — defer one "ch07.step" job per
    step number in `steps` (kwargs: account=, step=), ALL sharing a lock
    unique to that account, so they can never run concurrently or out of
    order. Return the job ids.
  * defer_cleanup_once(app) — defer "ch07.cleanup"; if a cleanup job is
    already waiting (AlreadyEnqueued), return None instead of raising.

Run:  uv run pytest challenges/ch07
"""

import procrastinate


async def defer_account_steps(app: procrastinate.App, account: str, steps: list[int]) -> list[int]:
    raise NotImplementedError


async def defer_cleanup_once(app: procrastinate.App) -> int | None:
    raise NotImplementedError
