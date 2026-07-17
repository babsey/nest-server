from app_test_client import app, client  # noqa: F401


def test_api_selfconnect_node(client):  # noqa: F811
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha"})
    assert response.status_code == 200
    node_id = response.json

    assert client.post("/api/Connect", json={"pre": node_id, "post": node_id}).status_code == 200


def test_api_selfconnect_nodes(client):  # noqa: F811
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": 2})
    assert response.status_code == 200
    nodes_id = response.json

    assert client.post("/api/Connect", json={"pre": nodes_id, "post": nodes_id}).status_code == 200


def test_api_connect_nodes(client):  # noqa: F811
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": 2})
    assert response.status_code == 200
    nodes_id = response.json

    assert client.post("/api/Connect", json={"pre": [nodes_id[0]], "post": [nodes_id[1]]}).status_code == 200


def test_api_connect_various_nodes(client):  # noqa: F811
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha"})
    assert response.status_code == 200
    source_id = response.json

    response = client.post("/api/Create", json={"model": "iaf_psc_alpha"})
    assert response.status_code == 200
    target_id = response.json

    assert client.post("/api/Connect", json={"pre": source_id, "post": target_id}).status_code == 200
