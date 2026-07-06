from challenges.conftest import load_impl

impl = load_impl("ch02")


async def test_greet_round_trip(clean_db):
    app = impl.build_app()
    async with app.open_async():
        job_id = await app.configure_task(name="ch02.greet").defer_async(name="tester")
        await app.run_worker_async(queues=["ch02"], wait=False)

        status = await app.job_manager.get_job_status_async(job_id)
        assert status.value == "succeeded"


async def test_task_is_on_the_ch02_queue(clean_db):
    app = impl.build_app()
    async with app.open_async():
        await app.configure_task(name="ch02.greet").defer_async(name="tester")
        jobs = await app.job_manager.list_jobs_async(queue="ch02")
        assert len(list(jobs)) == 1
