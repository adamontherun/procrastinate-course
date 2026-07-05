# Procrastinate: Task Queues on Postgres

A hands-on course on [Procrastinate](https://procrastinate.readthedocs.io/) 3.x,
the Python task queue that uses PostgreSQL as its broker — no Redis, no RabbitMQ.
Thirteen chapters, every example run against a real Postgres database, every
challenge backed by real failing tests.

[![Read the Book](https://img.shields.io/badge/📖_Read_the_Book-{{PAGES_HOST_PATH}}-b45309)]({{PAGES_URL}})

This repo is two things: **the book** (13 chapters of prose, nothing to
install) and **the code** (runnable examples and failing-test challenges,
which need an environment). Every chapter in the book links straight back to
Codespaces, so you're never more than one click from a terminal with Postgres
already running.

## What's covered

- **Part I · Foundations** — why a task queue at all, why Postgres can be the broker, and the core loop: define a task, defer a job, run a worker.
- **Part II · Controlling execution** — retries, scheduled and periodic jobs, locks and priorities, job context, cancellation, and middleware.
- **Part III · Sync and the web** — using Procrastinate from synchronous code, and wiring it into a FastAPI application.
- **Part IV · Production** — testing strategies, schema migrations, monitoring, graceful shutdown, and deploying workers on AWS ECS.

## Setup

Don't want to install anything? Open [the book]({{PAGES_URL}}) and click
"Launch Codespace" in any chapter's sidebar — it opens a cloud dev
environment with Postgres already running.

To run locally, you need [uv](https://docs.astral.sh/uv/) and
[Docker](https://docs.docker.com/get-started/get-docker/):

```sh
uv sync                     # install Python dependencies
docker compose up -d        # start Postgres
PYTHONPATH=. uv run procrastinate --app=examples.hello_world.app schema --apply
uv run python -m examples.hello_world
```

Postgres runs on port **5441** (not the default 5432) so it can't collide
with a Postgres you already have running. Credentials are
`postgres` / `password`, database `procrastinate_course` — fine for a local
throwaway container, obviously not a pattern for anything real.

## Doing challenges

Every chapter has a challenge under `challenges/`: a skeleton file with
failing tests. Edit the skeleton until the tests pass:

```sh
uv run pytest challenges/ch03
```

Reference solutions live in `solutions/`. No peeking until the tests pass.

## Resetting the database

Examples clean up after themselves, but if you ever want a pristine database:

```sh
docker compose down -v && docker compose up -d
PYTHONPATH=. uv run procrastinate --app=examples.hello_world.app schema --apply
```
