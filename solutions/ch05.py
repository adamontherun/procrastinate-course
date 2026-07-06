"""Reference solution for chapter 5."""

import procrastinate

_attempts: dict[str, int] = {}


def register(app: procrastinate.App) -> None:
    @app.task(
        name="ch05.fetch",
        queue="ch05",
        # max_attempts counts RETRIES: 2 retries = 3 total executions.
        retry=procrastinate.RetryStrategy(
            max_attempts=2,
            retry_exceptions={ConnectionError},
        ),
    )
    async def fetch(key: str, fail_times: int, kind: str = "net") -> None:
        if kind == "value":
            raise ValueError("bad input")
        _attempts[key] = _attempts.get(key, 0) + 1
        if _attempts[key] <= fail_times:
            raise ConnectionError(f"attempt {_attempts[key]} failed")
