import subprocess
import sys
from unittest import mock

import pytest

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


@pytest.fixture(autouse=True)
def restore_globals(monkeypatch):
    # main() rebinds module globals; pin defaults and let monkeypatch restore them afterwards.
    monkeypatch.setattr(cli, "DAEMON", False)
    monkeypatch.setattr(cli, "HOST", "127.0.0.1")
    monkeypatch.setattr(cli, "PORT", 52425)
    monkeypatch.setattr(cli, "STDOUT", False)
    monkeypatch.setattr(cli, "TIMEOUT", 30)
    monkeypatch.setattr(cli, "WORKERS", 1)


def call_main(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["nest-server", *args])
    cli.main()


def test_no_arguments_prints_help(monkeypatch, capsys):
    with pytest.raises(SystemExit) as exc_info:
        call_main(monkeypatch)
    assert exc_info.value.code == 0
    assert "usage:" in capsys.readouterr().out


def test_invalid_operation(monkeypatch):
    with pytest.raises(SystemExit) as exc_info:
        call_main(monkeypatch, "restart")
    assert exc_info.value.code == 2


def test_version(monkeypatch, capsys):
    call_main(monkeypatch, "version")
    assert capsys.readouterr().out.strip() == __version__


def test_log(monkeypatch, run):
    call_main(monkeypatch, "log")
    assert run.call_args.args[0] == f"tail -f {cli.LOGFILE}"


def test_pid(monkeypatch, run):
    call_main(monkeypatch, "pid")
    assert run.call_args.args[0] == "pgrep -fo 'nest-server start'"


def test_pid_no_process(monkeypatch, run, capsys):
    run.side_effect = subprocess.CalledProcessError(1, "pgrep")
    call_main(monkeypatch, "pid")
    assert capsys.readouterr().out.strip() == "No such process"


def test_stop(monkeypatch, run, capsys):
    call_main(monkeypatch, "stop")
    assert run.call_args.args[0] == "pgrep -fo 'nest-server start' | xargs kill"
    assert "has stopped" in capsys.readouterr().out


def test_stop_not_running(monkeypatch, run, capsys):
    run.side_effect = subprocess.CalledProcessError(1, "pgrep")
    call_main(monkeypatch, "stop", "-p", "8000")
    assert capsys.readouterr().out.strip() == "NEST Server is not running at http://127.0.0.1:8000."


def test_start_defaults(monkeypatch, standalone_app, capsys):
    call_main(monkeypatch, "start")

    app_uri, options = standalone_app.call_args.args
    assert app_uri == "nest_server.main:create_app()"
    assert options == {
        "bind": "127.0.0.1:52425",
        "capture_output": True,
        "daemon": False,
        "errorlog": cli.LOGFILE,
        "pidfile": cli.PIDFILE,
        "timeout": 30,
        "workers": 1,
    }
    standalone_app.return_value.run.assert_called_once_with()
    assert "NEST Server is now running at http://127.0.0.1:52425." in capsys.readouterr().out


def test_start_with_options(monkeypatch, standalone_app):
    call_main(monkeypatch, "start", "-d", "-h", "0.0.0.0", "-p", "9000", "-o", "-w", "4")

    options = standalone_app.call_args.args[1]
    assert options["bind"] == "0.0.0.0:9000"
    assert options["daemon"] is True
    assert options["capture_output"] is False
    assert options["workers"] == 4


def test_start_long_options(monkeypatch, standalone_app):
    call_main(monkeypatch, "start", "--daemon", "--host", "10.0.0.1", "--port", "1234", "--outputs", "--workers", "2")

    options = standalone_app.call_args.args[1]
    assert options["bind"] == "10.0.0.1:1234"
    assert options["daemon"] is True
    assert options["capture_output"] is False
    assert options["workers"] == 2


def test_invalid_port(monkeypatch):
    with pytest.raises(SystemExit):
        call_main(monkeypatch, "start", "-p", "abc")


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
