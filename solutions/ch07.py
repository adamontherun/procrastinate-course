"""Reference solution for chapter 7."""

import procrastinate
from procrastinate import exceptions


async def defer_account_steps(app: procrastinate.App, account: str, steps: list[int]) -> list[int]:
    deferrer = app.configure_task(name="ch07.step", lock=f"account-{account}")
    return [await deferrer.defer_async(account=account, step=step) for step in steps]


async def defer_cleanup_once(app: procrastinate.App) -> int | None:
    try:
        return await app.tasks["ch07.cleanup"].defer_async()
    except exceptions.AlreadyEnqueued:
        return None
