"""Shared helpers for the course examples.

Creating the App inside a function that lives in this module (rather than at
the top of each example script) avoids procrastinate's "App is instantiated
in the main Python module" warning — see chapter 2 for what that warning
protects you from.
"""

import procrastinate

DSN = "postgresql://postgres:password@localhost:5441/procrastinate_course"


def make_app() -> procrastinate.App:
    return procrastinate.App(
        connector=procrastinate.PsycopgConnector(conninfo=DSN),
    )
