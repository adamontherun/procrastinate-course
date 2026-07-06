"""Reference solution for chapter 3."""

import procrastinate
from procrastinate.types import JSONDict


async def defer_welcome(app: procrastinate.App, to: str) -> int:
    return await app.configure_task(name="ch03.send").defer_async(to=to, subject="Welcome")


async def defer_urgent(app: procrastinate.App, to: str, subject: str) -> int:
    return await app.configure_task(name="ch03.send", queue="ch03-urgent").defer_async(
        to=to, subject=subject
    )


async def defer_campaign(app: procrastinate.App, recipients: list[str]) -> list[int]:
    payloads: list[JSONDict] = [{"to": to, "subject": "Big launch"} for to in recipients]
    return await app.configure_task(name="ch03.send").batch_defer_async(*payloads)
