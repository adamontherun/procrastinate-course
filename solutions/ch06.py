"""Reference solution for chapter 6."""

import datetime

import procrastinate


async def defer_reminder_in(app: procrastinate.App, text: str, seconds: int) -> int:
    return await app.configure_task(
        name="ch06.remind", schedule_in={"seconds": seconds}
    ).defer_async(text=text)


async def defer_reminder_at(app: procrastinate.App, text: str, when: datetime.datetime) -> int:
    return await app.configure_task(name="ch06.remind", schedule_at=when).defer_async(text=text)


def register_heartbeat(app: procrastinate.App, beats: list[int]) -> None:
    @app.periodic(cron="* * * * * *")
    @app.task(name="ch06.heartbeat", queue="ch06")
    async def heartbeat(timestamp: int) -> None:
        beats.append(timestamp)
