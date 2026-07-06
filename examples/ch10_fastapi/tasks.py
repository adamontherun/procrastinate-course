"""Chapter 10: the task queue side, in its own module.

The web app imports from here; a standalone worker process could too
(procrastinate --app=examples.ch10_fastapi.tasks.app worker). That's the
whole point of keeping it out of the web module.
"""

import asyncio

import procrastinate

from examples.common import DSN

app = procrastinate.App(
    connector=procrastinate.PsycopgConnector(conninfo=DSN),
)


@app.task(queue="emails")
async def send_welcome(email: str) -> None:
    await asyncio.sleep(0.5)  # stands in for the SMTP conversation
    print(f"  [send_welcome] sent to {email}")
