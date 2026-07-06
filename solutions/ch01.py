"""Reference solution for chapter 1."""

_TRANSITIONS: dict[tuple[str, str], str] = {
    ("todo", "fetched"): "doing",
    ("doing", "succeeded"): "succeeded",
    ("doing", "failed"): "failed",
    ("doing", "failed_retryable"): "todo",
    ("doing", "aborted"): "aborted",
    ("todo", "cancelled"): "cancelled",
}


def next_status(current: str, event: str) -> str:
    try:
        return _TRANSITIONS[(current, event)]
    except KeyError:
        raise ValueError(f"no transition for {event!r} while {current!r}") from None
