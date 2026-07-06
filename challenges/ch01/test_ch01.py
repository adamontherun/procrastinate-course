import pytest

from challenges.conftest import load_impl

impl = load_impl("ch01")


@pytest.mark.parametrize(
    ("current", "event", "expected"),
    [
        ("todo", "fetched", "doing"),
        ("doing", "succeeded", "succeeded"),
        ("doing", "failed", "failed"),
        ("doing", "failed_retryable", "todo"),
        ("doing", "aborted", "aborted"),
        ("todo", "cancelled", "cancelled"),
    ],
)
def test_valid_transitions(current, event, expected):
    assert impl.next_status(current, event) == expected


@pytest.mark.parametrize(
    ("current", "event"),
    [
        ("succeeded", "fetched"),  # finished jobs don't restart
        ("todo", "succeeded"),  # a job can't succeed without being fetched
        ("doing", "cancelled"),  # cancellation only works before a worker has it
        ("failed", "failed"),
        ("todo", "nonsense"),
    ],
)
def test_invalid_transitions_raise(current, event):
    with pytest.raises(ValueError):
        impl.next_status(current, event)
