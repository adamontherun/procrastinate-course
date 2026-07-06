import copy
import json
import pathlib

from challenges.conftest import load_impl

impl = load_impl("ch13")

TASK_DEF = json.loads(
    (pathlib.Path(__file__).parents[2] / "deploy" / "ecs-task-definition.json").read_text()
)


def test_shipped_task_definition_is_clean():
    # The course's own artifact must pass its own review (worker runs with
    # --shutdown-graceful-timeout=90, see deploy/Dockerfile).
    assert impl.validate_worker_container(TASK_DEF, graceful_timeout=90) == []


def test_each_problem_is_caught():
    base = TASK_DEF

    td = copy.deepcopy(base)
    del td["containerDefinitions"][0]["stopTimeout"]
    assert "no stopTimeout" in impl.validate_worker_container(td, 90)

    td = copy.deepcopy(base)
    td["containerDefinitions"][0]["stopTimeout"] = 300
    assert "stopTimeout too large" in impl.validate_worker_container(td, 90)

    td = copy.deepcopy(base)
    td["containerDefinitions"][0]["stopTimeout"] = 60
    assert "no shutdown headroom" in impl.validate_worker_container(td, 90)

    td = copy.deepcopy(base)
    td["containerDefinitions"][0]["essential"] = False
    assert "not essential" in impl.validate_worker_container(td, 90)

    td = copy.deepcopy(base)
    td["containerDefinitions"][0]["environment"].append({"name": "PGPASSWORD", "value": "hunter2"})
    assert "password in plain environment" in impl.validate_worker_container(td, 90)

    td = copy.deepcopy(base)
    del td["containerDefinitions"][0]["logConfiguration"]
    assert "no log configuration" in impl.validate_worker_container(td, 90)


def test_clean_definition_stays_clean_when_tight_but_valid():
    td = copy.deepcopy(TASK_DEF)
    td["containerDefinitions"][0]["stopTimeout"] = 91
    assert impl.validate_worker_container(td, 90) == []
