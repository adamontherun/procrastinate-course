"""Chapter 9: a fully synchronous program that only defers.

No asyncio anywhere. This is the shape of a cron script or a legacy WSGI
app that hands work to procrastinate workers running elsewhere.

    uv run python -m examples.ch09_sync_defer
"""

import procrastinate

from examples.common import DSN

app = procrastinate.App(
    connector=procrastinate.SyncPsycopgConnector(conninfo=DSN),
)


def main() -> None:
    with app.open():
        job_id = app.configure_task(name="examples.hello_world.greet").defer(name="from sync land")
        print(f"deferred job {job_id} without an event loop")

        # A sync connector defers; it does not work.
        try:
            app.run_worker(wait=False)
        except procrastinate.exceptions.SyncConnectorConfigurationError as exc:
            print(f"running a worker here: {type(exc).__name__}")


if __name__ == "__main__":
    main()
