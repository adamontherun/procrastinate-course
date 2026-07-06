"""Chapter 9: sync tasks run in threads; sync defer has a boundary.

uv run python -m examples.ch09_sync_tasks
"""

import asyncio
import threading
import time

from examples.common import make_app

app = make_app()


# A plain `def` task: procrastinate runs each one in its own thread, so
# blocking calls (time.sleep, requests, heavy CPU) don't freeze the worker.
@app.task
def blocking_call(n: int) -> None:
    time.sleep(0.5)
    print(f"  [blocking_call] {n} ran on thread {threading.current_thread().name!r}")


async def main() -> None:
    async with app.open_async():
        for n in range(3):
            await blocking_call.defer_async(n=n)

        start = time.perf_counter()
        await app.run_worker_async(concurrency=3, wait=False)
        print(f"3 blocking half-second tasks, concurrency=3: {time.perf_counter() - start:.1f}s")

        # The trap: calling the SYNC defer from inside a running event loop.
        try:
            blocking_call.defer(n=99)
        except RuntimeError as exc:
            print(f"sync defer inside the event loop: RuntimeError: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
