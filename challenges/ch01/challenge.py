"""Chapter 1 challenge: the job lifecycle, from memory.

A procrastinate job is a row in the procrastinate_jobs table, and its
`status` column moves through a small state machine:

    todo ──(fetched)──▶ doing ──(succeeded)──────▶ succeeded
                        doing ──(failed)──────────▶ failed
                        doing ──(failed_retryable)─▶ todo      (a retry!)
                        doing ──(aborted)──────────▶ aborted
    todo ──(cancelled)─▶ cancelled

Implement next_status so every valid (current, event) pair above returns
the new status, and every other combination raises ValueError. Run:

    uv run pytest challenges/ch01
"""


def next_status(current: str, event: str) -> str:
    """Return the status a job moves to when `event` happens in `current`."""
    raise NotImplementedError("Implement me! See the transition table above.")
