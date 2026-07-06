"""Chapter 8 challenge: an audit trail for every job, and an emergency stop.

Implement:

  * make_audit_middleware(events) — return an ASYNC task middleware
    (signature: call_next, context, worker) that appends
    (task_name, "start") before the task runs and (task_name, "ok") or
    (task_name, "error") after, depending on whether it raised. It must
    re-raise the exception — swallowing it would break retries and statuses.
  * abort_job(app, job_id) — request abortion of a job that may already be
    running (chapter 8 showed which flag does that), returning the bool
    procrastinate gives back.

Run:  uv run pytest challenges/ch08
"""

from collections.abc import Callable

import procrastinate


def make_audit_middleware(events: list[tuple[str, str]]) -> Callable:
    raise NotImplementedError


async def abort_job(app: procrastinate.App, job_id: int) -> bool:
    raise NotImplementedError
