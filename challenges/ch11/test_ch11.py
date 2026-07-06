import procrastinate
import pytest

from challenges.conftest import load_impl

impl = load_impl("ch11")

DSN = "postgresql://nobody:nothing@nowhere:5432/never_connected"


@pytest.fixture
def prod_app():
    """A 'production' app whose real connector must never be touched."""
    processed: list[tuple[str, int]] = []
    app = procrastinate.App(
        connector=procrastinate.PsycopgConnector(conninfo=DSN),
    )

    @app.task(name="ch11.charge", queue="billing")
    async def charge(customer: str, cents: int) -> None:
        processed.append((customer, cents))

    return app, processed


def test_capture_and_assert(prod_app):
    app, _ = prod_app
    with impl.capture_jobs(app) as connector:
        app.tasks["ch11.charge"].defer(customer="ada", cents=1200)

        impl.assert_deferred(connector, "ch11.charge", customer="ada", cents=1200)
        impl.assert_deferred(connector, "ch11.charge")

        with pytest.raises(AssertionError):
            impl.assert_deferred(connector, "ch11.refund")
        with pytest.raises(AssertionError):
            impl.assert_deferred(connector, "ch11.charge", customer="ada", cents=9999)


def test_run_pending_executes_without_postgres(prod_app):
    app, processed = prod_app
    with impl.capture_jobs(app):
        app.tasks["ch11.charge"].defer(customer="ada", cents=1200)
        app.tasks["ch11.charge"].defer(customer="charles", cents=800)

        statuses = impl.run_pending(app)

        assert statuses == ["succeeded", "succeeded"]
        assert processed == [("ada", 1200), ("charles", 800)]

    # Outside the context manager the real (never-opened) connector is back.
    assert isinstance(app.connector, procrastinate.PsycopgConnector)
