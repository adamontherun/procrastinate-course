"""Chapter 5 challenge: a retry policy that knows what's worth retrying.

Implement register(): it must register a task on `app` with

  * name "ch05.fetch", queue "ch05"
  * a retry strategy allowing at most 3 total executions, retrying ONLY
    ConnectionError. Careful: RetryStrategy's max_attempts counts retries,
    not executions — chapter 5 covers this off-by-one trap.

The task body is prescribed (the test relies on it):

  * signature: (key: str, fail_times: int, kind: str = "net")
  * if kind == "value": raise ValueError("bad input")
  * otherwise, count calls per `key` in the module-level _attempts dict;
    raise ConnectionError while the count is <= fail_times, then print or
    pass (success).

Run:  uv run pytest challenges/ch05
"""

import procrastinate

_attempts: dict[str, int] = {}


def register(app: procrastinate.App) -> None:
    """Register the "ch05.fetch" task with the retry strategy described above."""
    raise NotImplementedError
