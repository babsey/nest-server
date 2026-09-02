from random import randint

size = randint(2, 10)


def test_api_create_single_node(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha"})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 1
    assert response.json == [1]


def test_api_create_multiple_nodes(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": size})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == size
    assert response.json == list(range(1, size + 1))


def test_api_create_node_with_params(client):
    I_e = 376

    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "params": {"I_e": I_e}})
    assert response.status_code == 200

    response = client.post("/api/GetStatus", json={"nodes_or_conns": response.json, "keys": "I_e"})
    assert response.status_code == 200
    assert isinstance(response.json, float)
    assert response.json == I_e


def test_api_create_multiple_nodes_with_params(client):
    I_e = 375

    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": size, "params": {"I_e": I_e}})
    assert response.status_code == 200

    response = client.post("/api/GetStatus", json={"nodes_or_conns": response.json, "keys": "I_e"})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == size
    assert response.json == size * [I_e]


def test_api_create_multiple_nodes_with_various_params(client):
    I_e = [375, 376]

    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": 2, "params": {"I_e": I_e}})
    assert response.status_code == 200

    response = client.post("/api/GetStatus", json={"nodes_or_conns": response.json, "keys": "I_e"})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 2
    assert response.json == I_e
