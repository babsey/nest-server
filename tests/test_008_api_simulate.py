def test_api_simulate(client):  # noqa: F811
    response = client.post("/api/GetKernelStatus", json={"keys": "biological_time"})
    assert response.status_code == 200
    assert isinstance(response.json, float)
    assert response.json == 0

    assert client.post("/api/Simulate", json={"t": 100}).status_code == 200

    response = client.post("/api/GetKernelStatus", json={"keys": "biological_time"})
    assert response.status_code == 200
    assert isinstance(response.json, float)
    assert response.json == 100


def test_api_simulate_spike_recorder(client):  # noqa: F811
    response = client.post("/api/Create", json={"model": "spike_recorder"})
    assert response.status_code == 200
    sr_ids = response.json

    assert client.post("/api/Simulate", json={"t": 100}).status_code == 200

    response = client.post("/api/GetStatus", json={"nodes_or_conns": sr_ids, "keys": "n_events"})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert response.json[0] == 0


def test_api_simulate_spikes(client):  # noqa: F811
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "params": {"I_e": 376}})
    assert response.status_code == 200
    neuron_ids = response.json

    response = client.post("/api/Create", json={"model": "spike_recorder"})
    assert response.status_code == 200
    sr_ids = response.json

    assert client.post("/api/Connect", json={"pre": neuron_ids, "post": sr_ids}).status_code == 200
    assert client.post("/api/Simulate", json={"t": 100}).status_code == 200

    response = client.post("/api/GetStatus", json={"nodes_or_conns": sr_ids, "keys": "n_events"})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert response.json[0] > 0
