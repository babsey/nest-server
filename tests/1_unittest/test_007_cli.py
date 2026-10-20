import subprocess
from unittest import mock

import pytest
from click.testing import CliRunner

from nest_server import __version__, cli


@pytest.fixture
def run(monkeypatch):
    mocked = mock.Mock()
    monkeypatch.setattr(cli.subprocess, "run", mocked)
    return mocked


@pytest.fixture
def standalone_app(monkeypatch):
    mocked = mock.Mock()
    monkeypatch.setattr(cli, "StandaloneApplication", mocked)
    return mocked


def invoke(*args):
    return CliRunner().invoke(cli.main, args, prog_name="nest-server")


def test_no_arguments_prints_help(run):
    result = invoke()
    assert result.exit_code == 2
    assert "Usage: nest-server" in result.output
    for command in ["log", "pid", "start", "stop", "version"]:
        assert command in result.output
    run.assert_not_called()


def test_help():
    result = invoke("--help")
    assert result.exit_code == 0
    assert "Usage: nest-server" in result.output


def test_invalid_operation(run):
    result = invoke("restart")
    assert result.exit_code == 2
    assert "No such command 'restart'" in result.output
    run.assert_not_called()


def test_version(run):
    result = invoke("version")
    assert result.exit_code == 0
    assert result.output.strip() == __version__
    run.assert_not_called()


def test_log(run):
    result = invoke("log")
    assert result.exit_code == 0
    run.assert_called_once_with(f"tail -f {cli.LOGFILE}", shell=True, executable="/bin/bash", check=True)


def test_pid(run):
    result = invoke("pid")
    assert result.exit_code == 0
    assert run.call_args.args[0] == "pgrep -fo 'nest-server start'"


def test_pid_no_process(run):
    run.side_effect = subprocess.CalledProcessError(1, "pgrep")
    result = invoke("pid")
    assert result.exit_code == 0
    assert result.output.strip() == "No such process"


def test_stop(run):
    result = invoke("stop")
    assert result.exit_code == 0
    assert run.call_args.args[0] == "pgrep -fo 'nest-server start' | xargs kill"
    assert f"NEST Server running at http://{cli.HOST}:{cli.PORT} has stopped." in result.output


@pytest.mark.parametrize("args", [["-h", "0.0.0.0", "-p", "8000"], ["--host", "0.0.0.0", "--port", "8000"]])
def test_stop_with_options(run, args):
    result = invoke("stop", *args)
    assert result.exit_code == 0
    assert "NEST Server running at http://0.0.0.0:8000 has stopped." in result.output


def test_stop_not_running(run):
    run.side_effect = subprocess.CalledProcessError(1, "pgrep")
    result = invoke("stop", "-p", "8000")
    assert result.exit_code == 0
    assert result.output.strip() == f"NEST Server is not running at http://{cli.HOST}:8000."


def test_start_defaults(standalone_app):
    result = invoke("start")
    assert result.exit_code == 0

    app_uri, options = standalone_app.call_args.args
    assert app_uri == "nest_server.main:create_app()"
    assert options == {
        "bind": f"{cli.HOST}:{cli.PORT}",
        "capture_output": not cli.STDOUT,
        "daemon": cli.DAEMON,
        "errorlog": cli.LOGFILE,
        "pidfile": cli.PIDFILE,
        "timeout": cli.TIMEOUT,
        "workers": cli.WORKERS,
    }
    standalone_app.return_value.run.assert_called_once_with()

    msg = f"NEST Server is now running at http://{cli.HOST}:{cli.PORT}."
    assert msg in result.output
    assert "Use CTRL + C to stop this service." in result.output
    assert len(msg) * "-" in result.output


@pytest.mark.parametrize(
    "args",
    [
        ["-d", "-h", "0.0.0.0", "-p", "9000", "-o", "-t", "60", "-w", "4"],
        ["--daemon", "--host", "0.0.0.0", "--port", "9000", "--outputs", "--timeout", "60", "--workers", "4"],
    ],
)
def test_start_with_options(standalone_app, args):
    result = invoke("start", *args)
    assert result.exit_code == 0

    options = standalone_app.call_args.args[1]
    assert options["bind"] == "0.0.0.0:9000"
    assert options["daemon"] is True
    assert options["capture_output"] is False
    assert options["timeout"] == 60
    assert options["workers"] == 4
    assert "NEST Server is now running at http://0.0.0.0:9000." in result.output


@pytest.mark.parametrize("option", ["--port", "--timeout", "--workers"])
def test_start_invalid_integer(standalone_app, option):
    result = invoke("start", option, "abc")
    assert result.exit_code == 2
    assert "is not a valid integer" in result.output
    standalone_app.assert_not_called()


class TestStandaloneApplication:
    def test_load_config_applies_known_options(self):
        app = cli.StandaloneApplication("nest_server.main:create_app()", {"bind": "1.2.3.4:5678", "workers": 3})
        assert app.app_uri == "nest_server.main:create_app()"
        assert app.cfg.bind == ["1.2.3.4:5678"]
        assert app.cfg.workers == 3

    def test_load_config_skips_unknown_and_none(self):
        default_timeout = cli.StandaloneApplication("x:y").cfg.timeout
        app = cli.StandaloneApplication("x:y", {"unknown_option": 1, "timeout": None})
        assert app.cfg.timeout == default_timeout
        assert "unknown_option" not in app.cfg.settings

    def test_options_default_to_empty(self):
        assert cli.StandaloneApplication("x:y").options == {}
