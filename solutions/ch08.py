"""Reference solution for chapter 8."""

from collections.abc import Callable

import procrastinate


def make_audit_middleware(events: list[tuple[str, str]]) -> Callable:
    async def audit(call_next, context, worker):  # noqa: ANN001 - middleware signature
        events.append((context.task.name, "start"))
        try:
            result = await call_next()
        except BaseException:
            events.append((context.task.name, "error"))
            raise
        events.append((context.task.name, "ok"))
        return result

    return audit


async def abort_job(app: procrastinate.App, job_id: int) -> bool:
    return await app.job_manager.cancel_job_by_id_async(job_id, abort=True)
