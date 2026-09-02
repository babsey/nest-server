from random import randint

size = randint(2, 10)


def test_api_selfconnect_single_node_all_to_all(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha"})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post(
        "/api/Connect",
        json={"pre": node_ids, "post": node_ids, "conn_spec": "all_to_all", "return_synapsecollection": True},
    )
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert isinstance(response.json["source"], int)
    assert response.json["source"] == response.json["target"] == node_ids[0]


def test_api_selfconnect_single_node_one_to_one(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha"})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post(
        "/api/Connect",
        json={"pre": node_ids, "post": node_ids, "conn_spec": "one_to_one", "return_synapsecollection": True},
    )
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert isinstance(response.json["source"], int)
    assert response.json["source"] == response.json["target"]


def test_api_selfconnect_all_to_all(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": size})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post(
        "/api/Connect",
        json={"pre": node_ids, "post": node_ids, "conn_spec": "all_to_all", "return_synapsecollection": True},
    )
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert isinstance(response.json["source"], list)
    assert response.json["source"] == [node_id for node_id in node_ids for _ in range(size)]  # [1,1,2,2]
    # assert response.json["target"] == size * node_ids
    # BUG: Why are target ids not ordered as expected, e.g. [1,2,1,2]?


def test_api_selfconnect_one_to_one(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": size})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post(
        "/api/Connect",
        json={"pre": node_ids, "post": node_ids, "conn_spec": "one_to_one", "return_synapsecollection": True},
    )
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert isinstance(response.json["source"], list)
    assert response.json["source"] == response.json["target"] == node_ids


def test_api_selfconnect_fixed_outdegree(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": size})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post(
        "/api/Connect",
        json={
            "pre": node_ids,
            "post": node_ids,
            "conn_spec": {
                "rule": "fixed_outdegree",
                "outdegree": 1,
            },
            "return_synapsecollection": True,
        },
    )
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert isinstance(response.json["source"], list)
    assert response.json["source"] == node_ids


def test_api_selfconnect_fixed_indegree(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": size})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post(
        "/api/Connect",
        json={
            "pre": node_ids,
            "post": node_ids,
            "conn_spec": {"rule": "fixed_indegree", "indegree": 1},
            "return_synapsecollection": True,
        },
    )
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert isinstance(response.json["target"], list)
    assert all((target_id in node_ids) for target_id in response.json["target"])


def test_api_selfconnect_fixed_total_number(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": size})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post(
        "/api/Connect",
        json={
            "pre": node_ids,
            "post": node_ids,
            "conn_spec": {"rule": "fixed_total_number", "N": 1},
            "return_synapsecollection": True,
        },
    )
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert isinstance(response.json["source"], int)
    assert response.json["source"] in node_ids


def test_api_selfconnect_fixed_total_numbers(client):
    N = randint(2, size)

    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": size})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post(
        "/api/Connect",
        json={
            "pre": node_ids,
            "post": node_ids,
            "conn_spec": {"rule": "fixed_total_number", "N": N},
            "return_synapsecollection": True,
        },
    )
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert isinstance(response.json["source"], list)
    assert len(response.json["source"]) == N


def test_api_selfconnect_pairwise_bernoulli(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": size})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post(
        "/api/Connect",
        json={
            "pre": node_ids,
            "post": node_ids,
            "conn_spec": {"rule": "pairwise_bernoulli", "p": 0.5},
            "return_synapsecollection": True,
        },
    )
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    if "source" in response.json:
        assert isinstance(response.json["source"], list)


def test_api_selfconnect_pairwise_bernoulli_no_autoapses_no_multapses(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": size})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post(
        "/api/Connect",
        json={
            "pre": node_ids,
            "post": node_ids,
            "conn_spec": {
                "rule": "pairwise_bernoulli",
                "p": 0.5,
                "allow_autapses": False,
                "allow_multapses": False,
            },
            "return_synapsecollection": True,
        },
    )
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    if "source" in response.json:
        assert isinstance(response.json["source"], list)


def test_api_selfconnect_symmetric_pairwise_bernoulli(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": size})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post(
        "/api/Connect",
        json={
            "pre": node_ids,
            "post": node_ids,
            "conn_spec": {
                "rule": "symmetric_pairwise_bernoulli",
                "p": 0.5,
                "allow_autapses": False,
                "make_symmetric": True,
            },
            "return_synapsecollection": True,
        },
    )
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    if "source" in response.json:
        assert isinstance(response.json["source"], list)


def test_api_selfconnect_pairwise_poisson(client):
    response = client.post("/api/Create", json={"model": "iaf_psc_alpha", "n": size})
    assert response.status_code == 200
    node_ids = response.json

    response = client.post(
        "/api/Connect",
        json={
            "pre": node_ids,
            "post": node_ids,
            "conn_spec": {"rule": "pairwise_poisson", "pairwise_avg_num_conns": 0.5},
            "return_synapsecollection": True,
        },
    )
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    if "source" in response.json:
        assert isinstance(response.json["source"], list)
