"""Reference solution for chapter 12."""

import procrastinate


async def recover_stalled(app: procrastinate.App, seconds_since_heartbeat: float) -> int:
    stalled = list(
        await app.job_manager.get_stalled_jobs(seconds_since_heartbeat=seconds_since_heartbeat)
    )
    for job in stalled:
        await app.job_manager.retry_job(job)
    return len(stalled)


async def sweep_old_jobs(app: procrastinate.App, max_hours: int) -> None:
    # The same call the builtin remove_old_jobs task makes. Deferring that
    # builtin periodically is the usual production shape (see the chapter),
    # but the underlying API is public and plain.
    await app.job_manager.delete_old_jobs(nb_hours=max_hours)
