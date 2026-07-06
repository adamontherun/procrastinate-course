"""The worker image's app module. Self-contained: no course code needed.

Connection settings come from the standard libpq environment variables
(PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE) — locally they're set by
`docker run -e`, on ECS by the task definition's environment and secrets.
"""

import asyncio

import procrastinate

app = procrastinate.App(
    connector=procrastinate.PsycopgConnector(),  # reads PG* env vars
)


@app.task(name="ch13.resize_image", queue="images")
async def resize_image(key: str) -> None:
    print(f"resizing {key} ...", flush=True)
    await asyncio.sleep(5)  # long enough to be mid-flight during a deploy
    print(f"resized {key}", flush=True)
