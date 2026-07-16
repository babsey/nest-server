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


def test_api_create_single_node(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha"})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 1
    assert response.json == [1]


def test_api_create_multiple_nodes(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": 2})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 2
    assert response.json == [1, 2]


def test_api_create_node_with_params(client):
    I_e = 376

    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "params": {"I_e": I_e}})
    assert response.status_code == 200

    response = client.post("/api/GetStatus", json={"nodes_or_conns": response.json, "keys": "I_e"})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert response.json == [I_e]


def test_api_create_multiple_nodes_with_params(client):
    I_e = 375

    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": 2, "params": {"I_e": I_e}})
    assert response.status_code == 200

    response = client.post("/api/GetStatus", json={"nodes_or_conns": response.json, "keys": "I_e"})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert response.json == [I_e, I_e]


def test_api_create_multiple_nodes_with_various_params(client):
    I_e = [375, 376]

    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": 2, "params": {"I_e": I_e}})
    assert response.status_code == 200

    response = client.post("/api/GetStatus", json={"nodes_or_conns": response.json, "keys": "I_e"})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert response.json == I_e
