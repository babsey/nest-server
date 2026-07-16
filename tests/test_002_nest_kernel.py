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
    return app.test_client()


def test_api_reset_kernel(client):
    assert client.get("/api/ResetKernel").status_code == 200


def test_api_get_kernel_status(client):
    response = client.get("/api/GetKernelStatus")
    assert response.status_code == 200
    assert isinstance(response.json, dict)


def test_api_get_kernel_local_num_threads_defaults(client):
    response = client.get("/api/GetKernelStatus", data={"keys": "local_num_threads"})
    assert response.status_code == 200
    assert isinstance(response.json, int)
    assert response.json == 1


def test_api_get_kernel_resolution_defaults(client):
    response = client.get("/api/GetKernelStatus", data={"keys": "resolution"})
    assert response.status_code == 200
    assert isinstance(response.json, float)
    assert response.json == 0.1


def test_api_get_kernel_rng_seed_defaults(client):
    response = client.get("/api/GetKernelStatus", data={"keys": "rng_seed"})
    assert response.status_code == 200
    assert isinstance(response.json, int)


def test_api_set_kernel_local_num_threads(client):
    local_num_threads = 4

    assert (
        client.post("/api/SetKernelStatus", json={"params": {"local_num_threads": local_num_threads}}).status_code
        == 200
    )

    response = client.get("/api/GetKernelStatus", data={"keys": "local_num_threads"})
    assert response.status_code == 200
    assert isinstance(response.json, int)
    assert response.json == local_num_threads


def test_api_set_kernel_resolution(client):
    resolution = 1

    assert client.post("/api/SetKernelStatus", json={"params": {"resolution": resolution}}).status_code == 200

    response = client.get("/api/GetKernelStatus", data={"keys": "resolution"})
    assert response.status_code == 200
    assert isinstance(response.json, float)
    assert response.json == resolution


def test_api_set_kernel_rng_seed(client):
    rng_seed = 123456789

    assert client.post("/api/SetKernelStatus", json={"params": {"rng_seed": rng_seed}}).status_code == 200

    response = client.get("/api/GetKernelStatus", data={"keys": "rng_seed"})
    assert response.status_code == 200
    assert isinstance(response.json, int)
    assert response.json == rng_seed
