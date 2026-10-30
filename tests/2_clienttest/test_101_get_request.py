def test_get_request(client):
    response = client.get("/")
    assert response.status_code == 200
    assert isinstance(response.json, dict)


def test_get_api_request(client):
    response = client.get("/api")
    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_get_api_request_version(client):
    response = client.get("/api/__version__")
    assert response.status_code == 200
    assert isinstance(response.json, str)


def test_get_exec_request(client):
    response = client.get("/exec")
    assert response.status_code == 200
    assert isinstance(response.json, dict)
