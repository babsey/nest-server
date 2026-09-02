def test_api_simulate(client):
    response = client.post("/api/GetKernelStatus", json={"keys": "biological_time"})
    assert response.status_code == 200
    assert isinstance(response.json, float)
    assert response.json == 0

    assert client.post("/api/Simulate", json={"t": 100}).status_code == 200

    response = client.post("/api/GetKernelStatus", json={"keys": "biological_time"})
    assert response.status_code == 200
    assert isinstance(response.json, float)
    assert response.json == 100
