import logging

import pytest

from nest_server.main import app as nest_server_app

logger = logging.getLogger()


@pytest.fixture
def app():
    nest_server_app.config.update(
        {
            "TESTING": True,
        }
    )

    # other setup can go here

    yield nest_server_app

    # clean up / reset resources here


@pytest.fixture
def client(app):
    client = app.test_client()
    client.get("/api/ResetKernel")
    return client


# @pytest.fixture
# def runner(app):
#     return app.test_cli_runner()
