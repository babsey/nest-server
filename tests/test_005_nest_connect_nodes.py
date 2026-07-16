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


def test_api_connect_node_self(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha"})
    assert response.status_code == 200
    node_id = response.json

    assert client.post("/api/Connect", json={"pre": node_id, "post": node_id}).status_code == 200
