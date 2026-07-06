"""Chapter 3: a task collection defined on a Blueprint, app-agnostic.

This module never touches the App — it can live in a separate package,
be tested alone, and be registered onto any app with add_tasks_from().
"""

from procrastinate import Blueprint

reports = Blueprint()


@reports.task
async def build(name: str) -> None:
    print(f"  [reports.build] building report {name!r}")
