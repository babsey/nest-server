"""Tests for the authentication and security settings of the Flask app.

The app reads its security settings at import time and its auth hook refuses
to work if more than one app instance exists in a process. Therefore each
scenario runs in a fresh interpreter.
"""

import json
import os
import subprocess
import sys

import pytest

SCRIPT = """
import json
from nest_server.main import create_app

app = create_app()
client = app.test_client()
results = {}
results["no_header"] = client.get("/").status_code
results["wrong_token"] = client.get("/", headers={"NESTServerAuth": "wrong"}).status_code
results["valid_token"] = client.get("/", headers={"NESTServerAuth": "secret-token"}).status_code
results["options"] = client.options("/").status_code
results["exec"] = client.post("/exec", json={"source": "x = 1"}, headers={"NESTServerAuth": "secret-token"}).status_code
print("RESULTS=" + json.dumps(results))
"""


def run_app(**env_overrides) -> tuple[dict, str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("NEST_SERVER_")}
    env["NEST_SERVER_MODULES"] = "import nest"
    env.update(env_overrides)
    proc = subprocess.run(
        [sys.executable, "-c", SCRIPT], check=False, env=env, capture_output=True, text=True, timeout=120
    )
    assert proc.returncode == 0, proc.stderr
    line = next(line for line in proc.stdout.splitlines() if line.startswith("RESULTS="))
    return json.loads(line.removeprefix("RESULTS=")), proc.stdout


@pytest.fixture(scope="module")
def secured():
    return run_app(NEST_SERVER_ACCESS_TOKEN="secret-token")


@pytest.fixture(scope="module")
def unsecured():
    return run_app(
        NEST_SERVER_ACCESS_TOKEN="secret-token",
        NEST_SERVER_DISABLE_AUTH="true",
        NEST_SERVER_ENABLE_EXEC_CALL="true",
        NEST_SERVER_CORS_ORIGINS="*",
    )


def test_request_without_token_is_forbidden(secured):
    assert secured[0]["no_header"] == 403


def test_request_with_wrong_token_is_forbidden(secured):
    assert secured[0]["wrong_token"] == 403


def test_request_with_valid_token_is_allowed(secured):
    assert secured[0]["valid_token"] == 200


def test_options_request_bypasses_auth(secured):
    assert secured[0]["options"] == 200


def test_exec_route_disabled_by_default(secured):
    assert secured[0]["exec"] == 403


def test_access_token_is_printed(secured):
    assert "Access token to NEST Server: secret-token" in secured[1]


def test_no_security_warning_by_default(secured):
    assert "WARNING" not in secured[1]


def test_disabled_auth_allows_all_requests(unsecured):
    assert unsecured[0]["no_header"] == 200
    assert unsecured[0]["wrong_token"] == 200


def test_exec_route_enabled(unsecured):
    assert unsecured[0]["exec"] == 200


def test_disabled_auth_hides_token_and_warns(unsecured):
    assert "Access token to NEST Server" not in unsecured[1]
    assert "WARNING" in unsecured[1]
    assert "AUTH:" in unsecured[1]
    assert "CORS:" in unsecured[1]
    assert "EXEC CALL:" in unsecured[1]


def test_generated_token_without_access_token():
    results, stdout = run_app()
    token = next(line for line in stdout.splitlines() if "Access token to NEST Server:" in line).split(": ")[-1]
    assert len(token) == 48
    assert results["no_header"] == 403
