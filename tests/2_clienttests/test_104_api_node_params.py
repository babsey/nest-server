def test_api_create_node_then_set_param(client):
    I_e = 376

    response = client.post("/api/Create", json={"model": "iaf_psc_alpha"})
    assert response.status_code == 200
    node_ids = response.json

    assert client.post("/api/SetStatus", json={"nodes_or_conns": node_ids, "params": {"I_e": I_e}}).status_code == 200

    response = client.post("/api/GetStatus", json={"nodes_or_conns": node_ids, "keys": "I_e"})
    assert response.status_code == 200
    assert isinstance(response.json, float)
    assert response.json == I_e


def test_api_create_multiple_nodes_then_set_params(client):
    I_e = 376

    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": 2})
    assert response.status_code == 200
    node_ids = response.json

    assert client.post("/api/SetStatus", json={"nodes_or_conns": node_ids, "params": {"I_e": I_e}}).status_code == 200

    response = client.post("/api/GetStatus", json={"nodes_or_conns": node_ids, "keys": "I_e"})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 2
    assert response.json == [I_e, I_e]


def test_api_create_multiple_nodes_then_set_various_params(client):
    I_e = [375, 376]

    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": 2})
    assert response.status_code == 200
    node_ids = response.json

    assert client.post("/api/SetStatus", json={"nodes_or_conns": node_ids, "params": {"I_e": I_e}}).status_code == 200

    response = client.post("/api/GetStatus", json={"nodes_or_conns": node_ids, "keys": "I_e"})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 2
    assert response.json == I_e
