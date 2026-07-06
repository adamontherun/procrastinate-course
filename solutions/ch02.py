"""Reference solution for chapter 2."""

import procrastinate

DSN = "postgresql://postgres:password@localhost:5441/procrastinate_course"


def build_app() -> procrastinate.App:
    app = procrastinate.App(
        connector=procrastinate.PsycopgConnector(conninfo=DSN),
    )

    @app.task(name="ch02.greet", queue="ch02")
    async def greet(name: str) -> str:
        return f"Hello, {name}!"

    return app
