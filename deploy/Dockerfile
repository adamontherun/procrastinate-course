# The worker image for chapter 13. Built and exercised locally in the
# chapter; the same image is what the ECS task definition points at.
FROM python:3.12-slim

# psycopg[binary] matters: procrastinate's base dependency is pure-python
# psycopg, which needs a system libpq that slim images don't have. The
# binary wheel bundles it. (Without this, the worker dies on startup with
# "ImportError: no pq wrapper available".)
RUN pip install --no-cache-dir "procrastinate==3.9.0" "psycopg[binary]>=3.2"

WORKDIR /app
COPY worker_app.py .

ENV PROCRASTINATE_APP=worker_app.app \
    PYTHONPATH=/app

# SIGTERM (what `docker stop` and ECS send) triggers procrastinate's
# graceful shutdown: finish running jobs, then exit. The exec-form CMD
# matters — a shell-form CMD would make PID 1 a shell that swallows
# SIGTERM instead of the worker.
CMD ["procrastinate", "worker", "--concurrency=10", "--shutdown-graceful-timeout=90"]
