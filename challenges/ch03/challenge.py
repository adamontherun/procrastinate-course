"""Chapter 3 challenge: deferring with intent.

You get an already-open app whose "ch03.send" task is registered for you
(see the test file). Implement three deferral helpers, each exercising a
different tool from the chapter:

  * defer_welcome         — one job, plain keyword arguments
  * defer_urgent          — one job, rerouted to the "ch03-urgent" queue
                            with configure()
  * defer_campaign        — one job per recipient, in a single round trip
                            (hint: batch_defer_async), all sharing the
                            subject "Big launch"

Each helper returns the new job id(s). Run:

    uv run pytest challenges/ch03
"""

import procrastinate


async def defer_welcome(app: procrastinate.App, to: str) -> int:
    """Defer "ch03.send" with kwargs to=<to>, subject="Welcome"."""
    raise NotImplementedError


async def defer_urgent(app: procrastinate.App, to: str, subject: str) -> int:
    """Defer "ch03.send" onto the "ch03-urgent" queue instead of its default."""
    raise NotImplementedError


async def defer_campaign(app: procrastinate.App, recipients: list[str]) -> list[int]:
    """Defer one "ch03.send" job per recipient with subject "Big launch"."""
    raise NotImplementedError
