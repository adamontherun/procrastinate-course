# Research notes — Procrastinate course

Target: **procrastinate 3.9.0** (verified via PyPI JSON API, 2026-07-05), Python >= 3.10,
PostgreSQL >= 13. Docs: https://procrastinate.readthedocs.io/en/stable/
Source: https://github.com/procrastinate-org/procrastinate/

Local verification setup: Docker Postgres 17 on port 5441, creds
postgres/password, db `procrastinate_course`. Round trip verified in
`examples/hello_world.py` (schema apply via CLI, defer, worker run,
status readback = `succeeded`).

Rule of thumb used throughout: where docs are vague about a default value,
the installed 3.9.0 package in `.venv` is the primary source — inspect
signatures rather than trusting prose.

## Ch 1 — Why a task queue / why Postgres

- Landing page: "Procrastinate is an open-source Python 3.10+ distributed task
  processing library, leveraging PostgreSQL 13+ to store task definitions,
  manage locks and dispatch tasks."
  https://procrastinate.readthedocs.io/en/stable/
- Discussions (https://procrastinate.readthedocs.io/en/stable/discussions.html):
  - Why Postgres over RabbitMQ/Redis: maintaining a broker alongside the DB is
    "double the trouble"; a queue in the DB is browsable/editable with normal SQL.
  - Celery comparison: feature-rich but not natively Postgres; dramatiq-pg exists
    but its paradigm makes procrastinate-style locks hard.
  - Under the hood: `SELECT FOR UPDATE`-style row locking so "when a worker starts
    executing a job, it's the only one"; `LISTEN/NOTIFY` for realtime wakeup;
    polling fallback ("each worker still polls the database every now and then,
    just in case") via `fetch_job_polling_interval`.
  - Job state machine: todo → doing → succeeded/failed/aborted; todo → cancelled;
    failed-but-retryable goes back to todo.
- Core queries are stored procedures (language-agnostic by design).

## Ch 2 — Setup, App, connectors, schema

- Quickstart: https://procrastinate.readthedocs.io/en/stable/quickstart.html
  - `pip install procrastinate`; `App(connector=PsycopgConnector(kwargs={...}))`
  - `export PYTHONPATH=.` needed for CLI to find your module (documented!).
  - `procrastinate --app=tutorial.app schema --apply`; `healthchecks`; `shell`.
- Connectors: https://procrastinate.readthedocs.io/en/stable/howto/basics/connector.html
  - Async: `PsycopgConnector` (psycopg3), `AiopgConnector`.
  - Sync: `SyncPsycopgConnector`, `Psycopg2Connector`, `SQLAlchemyPsycopg2Connector`.
  - Config via libpq env vars (PGHOST...), `conninfo` DSN, or `kwargs={}`.
  - Pool args pass through to `psycopg_pool.AsyncConnectionPool` / `ConnectionPool`.
  - Workers require an async connector. `pool_factory` for NullConnectionPool/PgBouncer.
- App placement: https://procrastinate.readthedocs.io/en/stable/howto/basics/app.html
  - Dedicated module preferred; `import_paths=[...]` for task discovery.
  - Top-level app trap (discussions): app defined in `__main__` module + tasks
    importing that module ⇒ **two distinct App instances**. We reproduced the
    warning in hello_world.py.
- Opening: https://procrastinate.readthedocs.io/en/stable/howto/basics/open_connection.html
  - `app.open()` / `await app.open_async()`, context-manager forms auto-close.
  - Can pass external pool to open().

## Ch 3 — Tasks and deferring

- Tasks: https://procrastinate.readthedocs.io/en/stable/howto/basics/tasks.html
  - `@app.task` or `@app.task(...)`; sync tasks run each in own thread; "All async
    tasks run in the same event loop."
  - Decorator params incl. queue, lock, queueing_lock, priority, retry, pass_context, name.
- Defer: https://procrastinate.readthedocs.io/en/stable/howto/basics/defer.html
  - `t.defer(a=1)` / `await t.defer_async(a=1)`; returns job id (verified locally).
  - `t.configure(lock=..., schedule_in={...}, queue=...)` then defer; reusable
    patterns via `configure(task_kwargs={...})`.
  - By name without task object: `app.configure_task(name="mod.task", ...)`.
  - CLI: `procrastinate defer my_module.my_task '{"a": 1}'`, `--unknown` flag.
- Batch: https://procrastinate.readthedocs.io/en/stable/howto/basics/batch_defer.html
  - `batch_defer({...}, {...})` / async; gotcha: same queueing_lock inside one
    batch ⇒ `AlreadyEnqueued` + whole transaction rolls back.
- Custom JSON: https://procrastinate.readthedocs.io/en/stable/howto/advanced/custom_json_encoder_decoder.html
  - connector `json_dumps`/`json_loads`, functools.partial pattern.
- Blueprints: https://procrastinate.readthedocs.io/en/stable/howto/advanced/blueprints.html
  - `Blueprint()`, `@bp.task`, `app.add_tasks_from(bp, namespace="x")` prefixes names.

## Ch 4 — Workers

- Worker: https://procrastinate.readthedocs.io/en/stable/howto/basics/worker.html
  - CLI `procrastinate --app=... worker [--name=...] [queues...]`; no queues = all.
  - `run_worker` opens/closes app + loop itself; `run_worker_async` needs open app.
  - `install_signal_handlers=False` when embedded.
  - Official FastAPI lifespan example (docs/howto/basics/worker.md on GitHub):
    open_async ctx mgr + `asyncio.create_task(run_worker_async(install_signal_handlers=False))`,
    on shutdown `worker.cancel()` + `asyncio.wait_for(worker, timeout=10)`;
    CancelledError = graceful, TimeoutError = ungraceful.
- CLI: https://procrastinate.readthedocs.io/en/stable/howto/basics/command_line.html
  - Subcommands worker/defer/schema/healthchecks/shell; `python -m procrastinate`;
    `PROCRASTINATE_APP` env var; `-v`/`-vv`; env vars `PROCRASTINATE_*`.
- Concurrency: https://procrastinate.readthedocs.io/en/stable/howto/production/concurrency.html
  - Default: one job at a time; `concurrency=30` → async sub-workers; free CPU
    during awaited I/O.
- Connections: https://procrastinate.readthedocs.io/en/stable/howto/production/connections.html
  - LISTEN/NOTIFY costs one dedicated connection; `listen_notify=False` (or
    `--no-listen-notify`) to disable; `worker_defaults={"listen_notify": False}`.
  - CORRECTION (fact-check, verified against installed psycopg_pool): the docs'
    "up to 10 parallel connections" figure is about AiopgConnector. For
    PsycopgConnector the pool default is psycopg_pool's min_size=4 /
    max_size=None (=> 4), and procrastinate doesn't override it.
  - CORRECTION (fact-check): procrastinate_workers table has only id +
    last_heartbeat columns; the worker name is NOT stored in the DB.
  - CORRECTION (fact-check): /en/stable/api.html is a 404; the API reference
    lives at /en/stable/reference.html.

## Ch 5 — Retries

- https://procrastinate.readthedocs.io/en/stable/howto/advanced/retry.html
  - `retry=5` ⇒ up to 6 total attempts; `retry=True` ⇒ retry forever.
  - `RetryStrategy(max_attempts, wait, linear_wait, exponential_wait, retry_exceptions)`
    (exponential example: 5, 25, 125 s).
  - Custom: subclass `BaseRetryStrategy`, implement `get_retry_decision(...)` →
    `RetryDecision(retry_in={...}|retry_at=dt, priority=, queue=, lock=)` or None.
  - Manual retry: `job_manager.retry_job_by_id(_async)`.
- Failed job = event `failed`; retryable failure = `deferred_for_retry`
  (events page).

## Ch 6 — Scheduling

- Future jobs: https://procrastinate.readthedocs.io/en/stable/howto/advanced/schedule.html
  - `configure(schedule_at=aware_datetime)` or `schedule_in={timedelta kwargs}`.
  - "If a job is configured with a date in the future, it will run at the first
    opportunity after that date."
  - CLI `--at=ISO` / `--in=seconds`.
- Periodic: https://procrastinate.readthedocs.io/en/stable/howto/advanced/cron.html
  - `@app.periodic(cron="0 * * * *")` stacked over `@app.task`; task receives
    `timestamp: int` (unix ts of the scheduled time).
  - Optional 6th cron column = seconds.
  - Multiple schedules: call `app.periodic(...)` with `task_kwargs` + unique
    `periodic_id`.
  - Dedup: workers defer, database guarantees once per period across workers.
  - Missed schedules: on start, defers missed ones unless >10 min late
    (configurable on App — `periodic_defaults`).

## Ch 7 — Locks, queueing locks, priorities

- Locks: https://procrastinate.readthedocs.io/en/stable/howto/advanced/locks.html
  - Same lock string ⇒ serial execution, "the second task cannot run before the
    first one has ended (successfully or not)". Order: priority then age.
  - Caveats: scheduled-in-future locked job blocks the rest; a stuck `doing` job
    (dead worker) blocks the lock until manually resolved; one lock per job
    (no deadlocks by construction).
  - Lock is a plain string; UUIDs of business objects recommended (discussions).
- Queueing locks: https://procrastinate.readthedocs.io/en/stable/howto/advanced/queueing_locks.html
  - At most one job with that lock in `todo` (doing doesn't count!); raises
    `AlreadyEnqueued`; CLI `--queueing-lock=... --ignore-already-enqueued`.
- Priorities: https://procrastinate.readthedocs.io/en/stable/howto/advanced/priorities.html
  - `priority` int (pos or neg), default 0, larger = higher; only among *available*
    jobs (no waiting for locked high-prio); starvation warning for low prio.

## Ch 8 — Context, cancellation, middleware

- Context: https://procrastinate.readthedocs.io/en/stable/howto/advanced/context.html
  - `pass_context=True` → first arg `JobContext` (job, task, worker info);
    `additional_context` dict passed at run_worker, shared/mutable across jobs,
    not for task→task data passing.
- Cancellation: https://procrastinate.readthedocs.io/en/stable/howto/advanced/cancellation.html
  - `job_manager.cancel_job_by_id(33)` (todo only), `delete_job=True` to remove row,
    `abort=True` for running jobs (notify + `abort_job_polling_interval`).
  - Sync task: poll `context.should_abort()`, raise `exceptions.JobAborted`.
  - Async task: asyncio cancellation (CancelledError); `asyncio.shield` pattern for
    critical sections.
  - Aborted-and-failed job is NOT retried regardless of retry strategy.
- Middleware: https://procrastinate.readthedocs.io/en/stable/howto/advanced/middleware.html
  - Task middleware (sync w/ sync task, async w/ async task) + worker middleware
    (always async). Signature `(call_next, context, worker)`. Chain: worker mw →
    worker-wide task mw → per-task mw → task. Registered via
    `@app.task(task_middleware=[...])` or `run_worker(task_middleware=..., worker_middleware=...)`.
    Never swallow exceptions (breaks retry/status); `worker.stop()` available.
  - NOTE: middleware is recent — verify availability/signature against installed
    3.9.0 before writing the chapter.

## Ch 9 — Sync ↔ async

- https://procrastinate.readthedocs.io/en/stable/howto/advanced/sync_defer.html
  - Async connectors auto-provide a sync counterpart for sync defer.
  - After app open, sync ops on an async connector only work inside
    `asgiref.sync.sync_to_async`-wrapped code (e.g., inside a sync job);
    otherwise RuntimeError.
  - Pure-sync programs: `SyncPsycopgConnector` — **defer only**; other ops error.
  - `SQLAlchemyPsycopg2Connector` shares an SQLAlchemy engine (`app.open(engine)`).
- Discussions: sync tasks run via `asgiref.sync.sync_to_async` in threads; sync
  `App.run_worker()` creates its own event loop.

## Ch 10 — FastAPI

- Official example in worker howto (verbatim in git: docs/howto/basics/worker.md).
- FastAPI lifespan docs: https://fastapi.tiangolo.com/advanced/events/
- Pattern: single App used for both defer (endpoints) and embedded worker;
  or separate worker process (recommended for real deployments — ch13).

## Ch 11 — Testing

- https://procrastinate.readthedocs.io/en/stable/howto/production/testing.html
  - `procrastinate.testing.InMemoryConnector`; `app.replace_connector(in_memory)`
    is a context manager; inspect `app.connector.jobs` (dict); run pending jobs
    with `app.run_worker(wait=False)`; `app.connector.reset()` between tests.

## Ch 12 — Production ops

- Deployment page is thin (authors say so) — course leans on shutdown/monitoring/
  migrations/stalled/cleanup pages + ECS chapter.
- Shutdown: https://procrastinate.readthedocs.io/en/stable/howto/advanced/shutdown.html
  - SIGINT/SIGTERM with install_signal_handlers=True (default); graceful = wait for
    running jobs; `shutdown_graceful_timeout` → abort leftovers
    (`should_abort` returns `AbortReason.SHUTDOWN`, async tasks cancelled);
    jobs ignoring abort still block shutdown; second signal = immediate stop,
    possibly leaving `doing` jobs ⇒ stalled.
- Stalled jobs: https://procrastinate.readthedocs.io/en/stable/howto/production/retry_stalled_jobs.html
  - Worker heartbeat every ~10s (`update_heartbeat_interval`); stalled after ~30s
    without heartbeat (`seconds_since_heartbeat` / `stalled_worker_timeout`);
    `JobManager.get_stalled_jobs()` + `retry_job()`; docs recommend periodic task
    with queueing_lock (verbatim example on page).
- Cleanup: https://procrastinate.readthedocs.io/en/stable/howto/production/delete_finished_jobs.html
  - `delete_jobs`: never (default) / successful / always; builtin
    `builtin_tasks.remove_old_jobs` (`max_hours=`, `remove_failed=`,
    `remove_cancelled=`, `remove_aborted=`), defer w/ queueing_lock.
- Migrations: https://procrastinate.readthedocs.io/en/stable/howto/production/migrations.html
  - SQL files in `procrastinate/sql/migrations`; `procrastinate schema --migrations-path`;
    naming `{version}_{serial}_{pre|post}_desc.sql`; simple (downtime) vs
    zero-downtime (pre → deploy → post, per intermediate version); manual tracking.
- Monitoring: https://procrastinate.readthedocs.io/en/stable/howto/production/monitoring.html
  - `healthchecks` cmd; `shell` (list_jobs/list_tasks/list_queues/list_locks,
    retry, cancel; non-interactive: `procrastinate shell list_jobs`); Sentry via
    logging; events table `procrastinate_events` (deferred/started/
    deferred_for_retry/failed/succeeded/cancelled/scheduled) — "early-stage" API.
- Logging: https://procrastinate.readthedocs.io/en/stable/howto/production/logging.html
  - Logger name "procrastinate"; every record has `action` extra; structlog
    recipe on page.
- Custom schema: https://procrastinate.readthedocs.io/en/stable/howto/production/schema.html
  - `kwargs={"options": "-c search_path=myschema"}` then `schema --apply`.

## Ch 13 — ECS

- ECS task definition params (fetched 2026-07-05):
  https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html
  - `stopTimeout`: "Time duration (in seconds) to wait before the container is
    forcefully killed if it doesn't exit normally on its own." Default 30s if
    unspecified; max **120 s** on Fargate.
  - ECS stop sequence: SIGTERM, then SIGKILL after stopTimeout (verify exact
    wording on the stopping-tasks page when writing ch13).
- Mapping: SIGTERM → procrastinate graceful shutdown; set
  `shutdown_graceful_timeout < stopTimeout`; stalled-job retry covers SIGKILL.
- Also to verify when writing ch13: ECS service vs scheduled task, Fargate task
  sizing, Secrets Manager for DB creds, awslogs driver.

## Verified against installed procrastinate 3.9.0 (inspect.signature, 2026-07-05)

- `Worker.__init__` defaults: `queues=None`, `name='worker'`, `concurrency=1`,
  `wait=True`, `fetch_job_polling_interval=5.0`, `abort_job_polling_interval=5.0`,
  `shutdown_graceful_timeout=None`, `listen_notify=True`, `delete_jobs=None`,
  `additional_context=None`, `install_signal_handlers=True`,
  `update_heartbeat_interval=10.0`, `stalled_worker_timeout=30.0`,
  `task_middleware=None`, `worker_middleware=None`.
- Middleware IS in 3.9.0 (`task_middleware`/`worker_middleware` params exist;
  `procrastinate.middleware` module exported).
- `RetryStrategy(*, max_attempts=None, wait=0, linear_wait=0, exponential_wait=0,
  retry_exceptions=None)`.
- **max_attempts semantics (verified empirically + in retry.py source):**
  despite the name, it's the max number of RETRIES — the guard is
  `job.attempts >= max_attempts` where attempts counts *prior* attempts, so
  `max_attempts=3` allows 4 total executions. Docstring: "The maximum number
  of attempts the job should be retried". Consistent with the howto's
  "retry=5 → 6 times total". A course gotcha callout covers this.
- Locks + polling (verified empirically, ch07 example): releasing a lock does
  NOT notify waiting workers; the next locked job waits for the next poll.
  Same-lock handoff latency ≈ fetch_job_polling_interval (measured 5.6s at
  default, 1.2s at 0.2s polling, for two 0.5s jobs).
- wait=False + locks (verified empirically): a run_worker(wait=False) worker
  can exit while a lock-blocked job is still `todo` — "queue empty" means
  "nothing fetchable right now".
- `Task.defer_async(...) -> int` (job id). Verified live: hello_world returned 1.
- `App(*, connector, import_paths=None, worker_defaults=None, periodic_defaults=None)`.
