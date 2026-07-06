"""Chapter 12 challenge: the two maintenance jobs every deployment needs.

Implement:

  * recover_stalled(app, seconds_since_heartbeat) — find every stalled job
    (chapter 12 showed the JobManager method) and retry each one; return
    how many you retried.
  * sweep_old_jobs(app, max_hours) — delete finished jobs older than
    max_hours. Call the same public JobManager API that the builtin
    remove_old_jobs task wraps (its argument is called nb_hours). Only
    successful jobs by default — don't turn on the include_* flags.

Run:  uv run pytest challenges/ch12
"""

import procrastinate


async def recover_stalled(app: procrastinate.App, seconds_since_heartbeat: float) -> int:
    raise NotImplementedError


async def sweep_old_jobs(app: procrastinate.App, max_hours: int) -> None:
    raise NotImplementedError
