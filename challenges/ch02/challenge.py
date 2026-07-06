"""Chapter 2 challenge: wire up an app of your own.

Build a procrastinate App connected to the course database, with one task
registered under the explicit name "ch02.greet" on the queue "ch02". The
task takes a keyword argument `name` and returns the string "Hello, {name}!".

The test defers a job through your app by task name, runs a worker until the
queue is empty, and checks the job succeeded — the same end-to-end loop as
examples/hello_world.py, except this time you write the wiring. Run:

    uv run pytest challenges/ch02
"""

import procrastinate

DSN = "postgresql://postgres:password@localhost:5441/procrastinate_course"


def build_app() -> procrastinate.App:
    """Return an App with an async connector and the "ch02.greet" task."""
    raise NotImplementedError(
        "Create the App (which connector class do workers need?), register "
        "the task with @app.task(name=..., queue=...), and return the app."
    )
