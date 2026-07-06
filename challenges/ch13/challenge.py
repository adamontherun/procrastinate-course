"""Chapter 13 challenge: review the task definition like an SRE.

Implement validate_worker_container(task_def, graceful_timeout): given a
parsed ECS task definition (a dict, like deploy/ecs-task-definition.json)
and the worker's --shutdown-graceful-timeout in seconds, return a list of
problem strings — empty when the definition is deploy-worthy. Check, for
the FIRST container definition:

  * "no stopTimeout"        — stopTimeout is missing (the 30s default will
                              cut off the graceful window)
  * "stopTimeout too large" — stopTimeout exceeds 120 (Fargate's maximum;
                              ECS would reject or ignore it)
  * "no shutdown headroom"  — stopTimeout is not strictly greater than
                              graceful_timeout (SIGKILL would land before
                              procrastinate finishes aborting)
  * "not essential"         — essential is not True (a dead worker
                              wouldn't stop the task, so ECS wouldn't
                              replace it)
  * "password in plain environment" — any environment variable name
                              containing "PASSWORD" (secrets belong in
                              the secrets block)
  * "no log configuration"  — logConfiguration is missing (a worker you
                              can't hear is a worker you can't operate)

Run:  uv run pytest challenges/ch13   (no AWS account needed)
"""


def validate_worker_container(task_def: dict, graceful_timeout: int) -> list[str]:
    raise NotImplementedError
