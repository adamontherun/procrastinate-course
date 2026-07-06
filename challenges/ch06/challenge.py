"""Chapter 6 challenge: schedule one job, and one heartbeat.

The test registers a task named "ch06.remind" (queue "ch06") for you.
Implement:

  * defer_reminder_in(app, text, seconds) — defer "ch06.remind" so it runs
    `seconds` seconds from now (schedule_in), returning the job id.
  * defer_reminder_at(app, text, when) — defer it for an exact datetime
    (schedule_at), returning the job id.
  * register_heartbeat(app, beats) — register a periodic task named
    "ch06.heartbeat" (queue "ch06") that fires EVERY SECOND (hint: cron has
    an optional 6th column) and appends its `timestamp` argument to the
    `beats` list.

Run:  uv run pytest challenges/ch06
"""

import datetime

import procrastinate


async def defer_reminder_in(app: procrastinate.App, text: str, seconds: int) -> int:
    raise NotImplementedError


async def defer_reminder_at(app: procrastinate.App, text: str, when: datetime.datetime) -> int:
    raise NotImplementedError


def register_heartbeat(app: procrastinate.App, beats: list[int]) -> None:
    raise NotImplementedError
