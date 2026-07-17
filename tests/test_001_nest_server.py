from app_test_client import app, client  # noqa: F401


def test_get_request(client):  # noqa: F811
    assert client.get("/").status_code == 200
