from random import shuffle


def test_api_simulate_single_spike_recorder_no_event(client):
    response = client.post("/api/Create", json={"model": "spike_recorder"})
    assert response.status_code == 200
    sr_ids = response.json

    assert client.post("/api/Simulate", json={"t": 100}).status_code == 200

    response = client.post("/api/GetStatus", json={"nodes_or_conns": sr_ids, "keys": "n_events"})
    assert response.status_code == 200
    assert isinstance(response.json, int)
    assert response.json == 0


def test_api_simulate_single_spike_recorder_one_event(client):
    spike_times = [10]

    response = client.post("/api/Create", json={"model": "spike_generator", "params": {"spike_times": spike_times}})
    assert response.status_code == 200
    sg_ids = response.json

    response = client.post("/api/Create", json={"model": "spike_recorder"})
    assert response.status_code == 200
    sr_ids = response.json

    assert client.post("/api/Connect", json={"pre": sg_ids, "post": sr_ids}).status_code == 200
    assert client.post("/api/Simulate", json={"t": 100}).status_code == 200

    response = client.post("/api/GetStatus", json={"nodes_or_conns": sr_ids})
    assert response.status_code == 200

    sr_status = response.json
    assert isinstance(sr_status, dict)

    n_events = sr_status["n_events"]
    assert isinstance(n_events, int)
    assert n_events == len(spike_times)

    times = sr_status["events"]["times"]
    assert isinstance(times, list)
    assert len(times) == len(spike_times)
    assert times == spike_times


def test_api_simulate_single_spike_recorder_ranged_events(client):
    spike_times = list(range(10, 100, 10))

    response = client.post("/api/Create", json={"model": "spike_generator", "params": {"spike_times": spike_times}})
    assert response.status_code == 200
    sg_ids = response.json

    response = client.post("/api/Create", json={"model": "spike_recorder"})
    assert response.status_code == 200
    sr_ids = response.json

    assert client.post("/api/Connect", json={"pre": sg_ids, "post": sr_ids}).status_code == 200
    assert client.post("/api/Simulate", json={"t": 100}).status_code == 200

    response = client.post("/api/GetStatus", json={"nodes_or_conns": sr_ids})
    assert response.status_code == 200

    sr_status = response.json
    assert isinstance(sr_status, dict)

    n_events = sr_status["n_events"]
    assert isinstance(n_events, int)
    assert n_events == len(spike_times)

    times = sr_status["events"]["times"]
    assert isinstance(times, list)
    assert len(times) == len(spike_times)
    assert times == spike_times


def test_api_simulate_single_spike_recorder_random_events(client):
    times = list(range(1, 100))
    shuffle(times)
    spike_times = times[:10]
    spike_times.sort()

    response = client.post("/api/Create", json={"model": "spike_generator", "params": {"spike_times": spike_times}})
    assert response.status_code == 200
    sg_ids = response.json

    response = client.post("/api/Create", json={"model": "spike_recorder"})
    assert response.status_code == 200
    sr_ids = response.json

    assert client.post("/api/Connect", json={"pre": sg_ids, "post": sr_ids}).status_code == 200
    assert client.post("/api/Simulate", json={"t": 100}).status_code == 200

    response = client.post("/api/GetStatus", json={"nodes_or_conns": sr_ids})
    assert response.status_code == 200

    sr_status = response.json
    assert isinstance(sr_status, dict)

    n_events = sr_status["n_events"]
    assert isinstance(n_events, int)
    assert n_events == len(spike_times)

    times = sr_status["events"]["times"]
    assert isinstance(times, list)
    assert len(times) == len(spike_times)
    assert times == spike_times


def test_api_simulate_multiple_spike_recorders_no_events(client):
    response = client.post("/api/Create", json={"model": "spike_recorder", "n": 2})
    assert response.status_code == 200
    sr_ids = response.json

    assert client.post("/api/Simulate", json={"t": 100}).status_code == 200

    response = client.post("/api/GetStatus", json={"nodes_or_conns": sr_ids, "keys": "n_events"})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert all(n_events == 0 for n_events in response.json)
