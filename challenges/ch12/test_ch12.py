import psycopg
import pytest

from challenges.conftest import DSN, load_impl

impl = load_impl("ch12")


@pytest.fixture
async def ch12_app(pg_app):
    @pg_app.task(name="ch12.report", queue="ch12")
    async def report() -> None:
        pass

    return pg_app


def _manufacture_stalled_job() -> int:
    """Fake a dead worker: a 'doing' job owned by a worker whose heartbeat
    stopped ten minutes ago."""
    with psycopg.connect(DSN, autocommit=True) as conn:
        worker_row = conn.execute(
            "INSERT INTO procrastinate_workers (last_heartbeat) "
            "VALUES (NOW() - INTERVAL '10 minutes') RETURNING id"
        ).fetchone()
        assert worker_row is not None
        job_row = conn.execute(
            "INSERT INTO procrastinate_jobs "
            "(queue_name, task_name, args, status, worker_id) "
            "VALUES ('ch12', 'ch12.report', '{}', 'doing', %s) RETURNING id",
            (worker_row[0],),
        ).fetchone()
        assert job_row is not None
    return job_row[0]


def _manufacture_finished_job(hours_ago: int) -> int:
    """A succeeded job whose 'succeeded' event is `hours_ago` hours old."""
    with psycopg.connect(DSN, autocommit=True) as conn:
        job_row = conn.execute(
            "INSERT INTO procrastinate_jobs (queue_name, task_name, args, status) "
            "VALUES ('ch12', 'ch12.report', '{}', 'succeeded') RETURNING id"
        ).fetchone()
        assert job_row is not None
        conn.execute(
            "INSERT INTO procrastinate_events (job_id, type, at) "
            "VALUES (%s, 'succeeded', NOW() - make_interval(hours => %s))",
            (job_row[0], hours_ago),
        )
    return job_row[0]


async def test_recover_stalled(ch12_app):
    job_id = _manufacture_stalled_job()

    count = await impl.recover_stalled(ch12_app, seconds_since_heartbeat=30)
    assert count == 1

    status = await ch12_app.job_manager.get_job_status_async(job_id)
    assert status.value == "todo", "a recovered job goes back in line"

    # Nothing left to recover on a second pass.
    assert await impl.recover_stalled(ch12_app, seconds_since_heartbeat=30) == 0


async def test_sweep_deletes_only_old_finished_jobs(ch12_app):
    old_id = _manufacture_finished_job(hours_ago=48)
    fresh_id = _manufacture_finished_job(hours_ago=0)
    pending_id = await ch12_app.tasks["ch12.report"].defer_async()

    await impl.sweep_old_jobs(ch12_app, max_hours=24)

    remaining = {j.id for j in await ch12_app.job_manager.list_jobs_async(queue="ch12")}
    assert old_id not in remaining, "the 48h-old succeeded job should be gone"
    assert fresh_id in remaining, "a recent succeeded job stays"
    assert pending_id in remaining, "a todo job is never swept"
