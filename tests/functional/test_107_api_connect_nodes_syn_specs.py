from random import randint


def test_api_selfconnect_static_synapse(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha"})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post(
        "/api/Connect",
        json={"pre": node_ids, "post": node_ids, "syn_spec": "static_synapse", "return_synapsecollection": True},
    )
    assert response.status_code == 200
    assert response.json["synapse_model"] == "static_synapse"


def test_api_selfconnect_synapse_weight(client):
    weight = randint(-10, 10)

    response = client.post("/api/Create", json={"model": "iaf_psc_alpha"})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post(
        "/api/Connect",
        json={"pre": node_ids, "post": node_ids, "syn_spec": {"weight": weight}, "return_synapsecollection": True},
    )
    assert response.status_code == 200
    assert response.json["weight"] == weight


def test_api_selfconnect_synapse_delay(client):
    delay = randint(1, 10)

    response = client.post("/api/Create", json={"model": "iaf_psc_alpha"})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post(
        "/api/Connect",
        json={"pre": node_ids, "post": node_ids, "syn_spec": {"delay": delay}, "return_synapsecollection": True},
    )
    assert response.status_code == 200
    assert response.json["delay"] == delay
