from challenges.conftest import load_impl

impl = load_impl("ch05")


async def _run_and_status(app, job_id):
    await app.run_worker_async(queues=["ch05"], wait=False)
    (job,) = await app.job_manager.list_jobs_async(id=job_id)
    return job


async def test_transient_failures_are_retried(pg_app):
    impl.register(pg_app)
    task = pg_app.tasks["ch05.fetch"]

    job_id = await task.defer_async(key="t1", fail_times=2)
    job = await _run_and_status(pg_app, job_id)
    assert job.status == "succeeded"
    assert job.attempts == 3


async def test_gives_up_after_three_attempts(pg_app):
    impl.register(pg_app)
    task = pg_app.tasks["ch05.fetch"]

    job_id = await task.defer_async(key="t2", fail_times=99)
    job = await _run_and_status(pg_app, job_id)
    assert job.status == "failed"
    assert job.attempts == 3


async def test_value_errors_fail_immediately(pg_app):
    impl.register(pg_app)
    task = pg_app.tasks["ch05.fetch"]

    job_id = await task.defer_async(key="t3", fail_times=0, kind="value")
    job = await _run_and_status(pg_app, job_id)
    assert job.status == "failed"
    assert job.attempts == 1
