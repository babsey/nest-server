def test_get_request(client):
    assert client.get("/").status_code == 200
