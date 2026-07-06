"""Chapter 9 challenge: both sides of the sync/async wall.

Implement:

  * defer_from_sync(dsn, task_name, queue=..., **kwargs) — a PLAIN function
    (no asyncio) that builds an app around the right connector for
    synchronous code, opens it, defers `task_name` by name onto `queue`
    with the given kwargs, and returns the job id. The queue parameter is
    not optional decoration: this app never registered the task, so it has
    no idea what the task's default queue is — a by-name defer that doesn't
    say lands on "default".
  * register_thumbnailer(app, log) — register a SYNC task (plain def) named
    "ch09.thumbnail" on queue "ch09" that sleeps 0.3s (time.sleep — it's a
    sync task, blocking is fine) and then appends the current thread's name
    to `log`. The test runs three at concurrency=3 and expects them to
    overlap and to use three different threads.

Run:  uv run pytest challenges/ch09
"""

import procrastinate


def defer_from_sync(dsn: str, task_name: str, *, queue: str, **kwargs) -> int:
    raise NotImplementedError


def register_thumbnailer(app: procrastinate.App, log: list[str]) -> None:
    raise NotImplementedError
