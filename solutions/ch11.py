"""Reference solution for chapter 11."""

import contextlib

import procrastinate
from procrastinate import testing


@contextlib.contextmanager
def capture_jobs(app: procrastinate.App):
    in_memory = testing.InMemoryConnector()
    with app.replace_connector(in_memory):
        yield in_memory


def assert_deferred(connector: testing.InMemoryConnector, task_name: str, **kwargs) -> None:
    for job in connector.jobs.values():
        if job["task_name"] == task_name and (not kwargs or job["args"] == kwargs):
            return
    raise AssertionError(
        f"no job for task {task_name!r} with kwargs {kwargs!r}; "
        f"recorded: {[(j['task_name'], j['args']) for j in connector.jobs.values()]}"
    )


def run_pending(app: procrastinate.App) -> list[str]:
    app.run_worker(wait=False, listen_notify=False)
    assert isinstance(app.connector, testing.InMemoryConnector)
    return [job["status"] for job in app.connector.jobs.values()]
