"""Chapter 11: testing without Postgres.

uv run python -m examples.ch11_testing
"""

from procrastinate import testing

from examples.common import make_app

app = make_app()  # the "production" app: real PsycopgConnector

sent: list[str] = []


@app.task(queue="emails")
async def send_invoice(customer: str) -> None:
    sent.append(customer)


def main() -> None:
    in_memory = testing.InMemoryConnector()
    with app.replace_connector(in_memory) as test_app:
        # Defer without a database: the "rows" are dicts in a dict.
        send_invoice.defer(customer="ada")
        send_invoice.defer(customer="charles")

        jobs = in_memory.jobs
        print(f"jobs recorded in memory: {len(jobs)}")
        print(f"first job: task={jobs[1]['task_name']} kwargs={jobs[1]['args']}")

        # Run everything currently queued, synchronously, no worker process.
        test_app.run_worker(wait=False, listen_notify=False)
        print(f"after run_worker: sent={sent}")
        print(f"statuses: {[j['status'] for j in in_memory.jobs.values()]}")

        # Start fresh between tests.
        in_memory.reset()
        print(f"after reset: {len(in_memory.jobs)} jobs")

    print(f"outside the context, the connector is real again: {type(app.connector).__name__}")


if __name__ == "__main__":
    main()
