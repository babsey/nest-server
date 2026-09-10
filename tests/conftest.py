# https://flask.palletsprojects.com/en/stable/testing/

import pytest

from nest_server.main import create_app

nest_server_app = create_app()


@pytest.fixture
def app():
    app = nest_server_app
    app.config.update(
        {
            "TESTING": True,
        }
    )

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture
def client(app):
    client = app.test_client()
    client.get("/api/ResetKernel")
    return client


# @pytest.fixture
# def runner(app):
#     return app.test_cli_runner()
