"""Reference solution for chapter 13."""


def validate_worker_container(task_def: dict, graceful_timeout: int) -> list[str]:
    problems: list[str] = []
    container = task_def["containerDefinitions"][0]

    stop_timeout = container.get("stopTimeout")
    if stop_timeout is None:
        problems.append("no stopTimeout")
    else:
        if stop_timeout > 120:
            problems.append("stopTimeout too large")
        if stop_timeout <= graceful_timeout:
            problems.append("no shutdown headroom")

    if container.get("essential") is not True:
        problems.append("not essential")

    for var in container.get("environment", []):
        if "PASSWORD" in var.get("name", ""):
            problems.append("password in plain environment")
            break

    if "logConfiguration" not in container:
        problems.append("no log configuration")

    return problems
