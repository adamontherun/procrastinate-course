"""Chapter 11 challenge: your own testing toolkit.

Implement three helpers a test suite would import:

  * capture_jobs(app) — a context manager that swaps the app's connector
    for a fresh InMemoryConnector (hint: procrastinate.testing +
    app.replace_connector, which is itself a context manager) and yields
    the in-memory connector.
  * assert_deferred(connector, task_name, **kwargs) — raise AssertionError
    unless the in-memory connector holds at least one job with that task
    name and (if given) exactly those task kwargs. connector.jobs is a
    dict of job-id -> job-row dicts; kwargs live under the "args" key.
  * run_pending(app) — execute everything currently queued and return the
    list of statuses afterwards. No Postgres, no waiting.

Run:  uv run pytest challenges/ch11   (no database needed!)
"""

import procrastinate
from procrastinate import testing


def capture_jobs(app: procrastinate.App):
    raise NotImplementedError


def assert_deferred(connector: testing.InMemoryConnector, task_name: str, **kwargs) -> None:
    raise NotImplementedError


def run_pending(app: procrastinate.App) -> list[str]:
    raise NotImplementedError
