import pytest

from challenges.conftest import load_impl

impl = load_impl("ch03")


@pytest.fixture
async def ch03_app(pg_app):
    @pg_app.task(name="ch03.send", queue="ch03")
    async def send(to: str, subject: str) -> None:
        pass

    return pg_app


async def test_defer_welcome(ch03_app):
    job_id = await impl.defer_welcome(ch03_app, to="ada@example.com")
    (job,) = await ch03_app.job_manager.list_jobs_async(id=job_id)
    assert job.task_name == "ch03.send"
    assert job.task_kwargs == {"to": "ada@example.com", "subject": "Welcome"}
    assert job.queue == "ch03"


async def test_defer_urgent_reroutes_queue(ch03_app):
    job_id = await impl.defer_urgent(ch03_app, to="ops@example.com", subject="Disk full")
    (job,) = await ch03_app.job_manager.list_jobs_async(id=job_id)
    assert job.queue == "ch03-urgent"
    assert job.task_kwargs == {"to": "ops@example.com", "subject": "Disk full"}


async def test_defer_campaign_batches(ch03_app):
    recipients = [f"user{i}@example.com" for i in range(5)]
    ids = await impl.defer_campaign(ch03_app, recipients)
    assert len(ids) == 5

    jobs = list(await ch03_app.job_manager.list_jobs_async(task="ch03.send"))
    assert len(jobs) == 5
    assert {j.task_kwargs["to"] for j in jobs} == set(recipients)
    assert {j.task_kwargs["subject"] for j in jobs} == {"Big launch"}
