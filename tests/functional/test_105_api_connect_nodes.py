def test_api_selfconnect_node(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha"})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post("/api/Connect", json={"pre": node_ids, "post": node_ids, "return_synapsecollection": True})
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert response.json["source"] == response.json["target"] == node_ids[0]


def test_api_selfconnect_nodes(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": 2})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post("/api/Connect", json={"pre": node_ids, "post": node_ids, "return_synapsecollection": True})
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert response.json["source"] == [node_id for node_id in node_ids for _ in range(2)]  # [1,1,2,2]
    assert response.json["target"] == 2 * node_ids  # [1,2,1,2]


def test_api_connect_multiple_nodes(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": 2})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post(
        "/api/Connect", json={"pre": [node_ids[0]], "post": [node_ids[1]], "return_synapsecollection": True}
    )
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert response.json["source"] == node_ids[0] and response.json["target"] == node_ids[1]


def test_api_connect_various_nodes(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha"})
    assert response.status_code == 200
    source_id = response.json

    response = client.post("/api/Create", json={"model": "iaf_psc_alpha"})
    assert response.status_code == 200
    target_id = response.json

    response = client.post("/api/Connect", json={"pre": source_id, "post": target_id, "return_synapsecollection": True})
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert response.json["source"] == source_id[0] and response.json["target"] == target_id[0]


def test_api_connect_various_multiple_nodes(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": 2})
    assert response.status_code == 200
    source_ids = response.json

    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": 2})
    assert response.status_code == 200
    target_ids = response.json

    response = client.post(
        "/api/Connect", json={"pre": source_ids, "post": target_ids, "return_synapsecollection": True}
    )
    assert response.status_code == 200
    assert isinstance(response.json, dict)

    assert response.json["source"] == [source_id for source_id in source_ids for _ in range(2)]  # [1,1,2,2]
    assert response.json["target"] == 2 * target_ids  # [1,2,1,2]
