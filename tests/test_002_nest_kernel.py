from app_test_client import app, client  # noqa: F401


def test_api_reset_kernel(client):  # noqa: F811
    assert client.get("/api/ResetKernel").status_code == 200


def test_api_get_kernel_status(client):  # noqa: F811
    response = client.get("/api/GetKernelStatus")
    assert response.status_code == 200
    assert isinstance(response.json, dict)


def test_api_get_kernel_local_num_threads_defaults(client):  # noqa: F811
    response = client.get("/api/GetKernelStatus", data={"keys": "local_num_threads"})
    assert response.status_code == 200
    assert isinstance(response.json, int)
    assert response.json == 1


def test_api_get_kernel_resolution_defaults(client):  # noqa: F811
    response = client.get("/api/GetKernelStatus", data={"keys": "resolution"})
    assert response.status_code == 200
    assert isinstance(response.json, float)
    assert response.json == 0.1


def test_api_get_kernel_rng_seed_defaults(client):  # noqa: F811
    response = client.get("/api/GetKernelStatus", data={"keys": "rng_seed"})
    assert response.status_code == 200
    assert isinstance(response.json, int)


def test_api_set_kernel_local_num_threads(client):  # noqa: F811
    local_num_threads = 4

    assert (
        client.post("/api/SetKernelStatus", json={"params": {"local_num_threads": local_num_threads}}).status_code
        == 200
    )

    response = client.get("/api/GetKernelStatus", data={"keys": "local_num_threads"})
    assert response.status_code == 200
    assert isinstance(response.json, int)
    assert response.json == local_num_threads


def test_api_set_kernel_resolution(client):  # noqa: F811
    resolution = 1

    assert client.post("/api/SetKernelStatus", json={"params": {"resolution": resolution}}).status_code == 200

    response = client.get("/api/GetKernelStatus", data={"keys": "resolution"})
    assert response.status_code == 200
    assert isinstance(response.json, float)
    assert response.json == resolution


def test_api_set_kernel_rng_seed(client):  # noqa: F811
    rng_seed = 123456789

    assert client.post("/api/SetKernelStatus", json={"params": {"rng_seed": rng_seed}}).status_code == 200

    response = client.get("/api/GetKernelStatus", data={"keys": "rng_seed"})
    assert response.status_code == 200
    assert isinstance(response.json, int)
    assert response.json == rng_seed
