"""Reference solution for chapter 9."""

import threading
import time

import procrastinate


def defer_from_sync(dsn: str, task_name: str, *, queue: str, **kwargs) -> int:
    app = procrastinate.App(
        connector=procrastinate.SyncPsycopgConnector(conninfo=dsn),
    )
    with app.open():
        # This app never registered the task, so it knows nothing about the
        # task's default queue — deferring by name must state it explicitly,
        # or the job lands on "default".
        return app.configure_task(name=task_name, queue=queue).defer(**kwargs)


def register_thumbnailer(app: procrastinate.App, log: list[str]) -> None:
    @app.task(name="ch09.thumbnail", queue="ch09")
    def thumbnail() -> None:
        time.sleep(0.3)
        log.append(threading.current_thread().name)
