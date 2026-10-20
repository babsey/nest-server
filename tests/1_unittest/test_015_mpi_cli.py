import importlib
import subprocess
from unittest import mock

import pytest
from click.testing import CliRunner

from nest_server import __version__
from nest_server.mpi import cli


@pytest.fixture(autouse=True)
def logfile(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "LOGFILE", str(tmp_path / "nest-server-mpi.log"))


@pytest.fixture
def run(monkeypatch):
    mocked = mock.Mock()
    monkeypatch.setattr(cli.subprocess, "run", mocked)
    return mocked


def invoke(*args):
    return CliRunner().invoke(cli.main, args, prog_name="nest-server-mpi")


def test_filepath_points_to_runner():
    assert cli.filepath.name == "runner.py"
    assert cli.filepath.is_file()


def test_env_defaults(monkeypatch):
    monkeypatch.setenv("NEST_SERVER_HOST", "0.0.0.0")
    monkeypatch.setenv("NEST_SERVER_PORT", "1234")
    monkeypatch.setenv("NEST_SERVER_MPI_NUM_PROCESSES", "4")
    monkeypatch.setenv("NEST_SERVER_MPI_LOGFILE", "/tmp/custom.log")
    try:
        importlib.reload(cli)
        assert cli.HOST == "0.0.0.0"
        assert cli.PORT == 1234
        assert cli.NUM_PROCESSES == 4
        assert cli.LOGFILE == "/tmp/custom.log"
    finally:
        monkeypatch.undo()
        importlib.reload(cli)


def test_no_arguments_prints_help(run):
    result = invoke()
    assert result.exit_code == 2
    assert "Usage: nest-server-mpi" in result.output
    for command in ["log", "pid", "start", "stop", "version"]:
        assert command in result.output
    run.assert_not_called()


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
    assert run.call_args.args[0] == f"pgrep -fo '{cli.filepath} --host {cli.HOST} --port {cli.PORT}'"


def test_pid_with_options(run):
    result = invoke("pid", "-h", "0.0.0.0", "-p", "8000")
    assert result.exit_code == 0
    assert run.call_args.args[0] == f"pgrep -fo '{cli.filepath} --host 0.0.0.0 --port 8000'"


def test_pid_no_process(run):
    run.side_effect = subprocess.CalledProcessError(1, "pgrep")
    result = invoke("pid")
    assert result.exit_code == 0
    assert result.output.strip() == "No such process"


def test_start(run):
    result = invoke("start")
    assert result.exit_code == 0
    cmd = run.call_args.args[0]
    assert cmd == f"mpirun -n {cli.NUM_PROCESSES} {cli.filepath} --host {cli.HOST} --port {cli.PORT}"
    kwargs = run.call_args.kwargs
    assert kwargs["shell"] is True
    assert kwargs["check"] is True
    assert kwargs["stdout"].name == cli.LOGFILE
    assert f"NEST Server is now running at http://{cli.HOST}:{cli.PORT}." in result.output


def test_start_truncates_logfile(run):
    with open(cli.LOGFILE, "w") as f:
        f.write("old content")
    invoke("start")
    with open(cli.LOGFILE) as f:
        assert f.read() == ""


@pytest.mark.parametrize(
    "args",
    [
        ["-n", "4", "-h", "0.0.0.0", "-p", "8000"],
        ["--np", "4", "--host", "0.0.0.0", "--port", "8000"],
    ],
)
def test_start_with_options(run, args):
    result = invoke("start", *args)
    assert result.exit_code == 0
    assert run.call_args.args[0] == f"mpirun -n 4 {cli.filepath} --host 0.0.0.0 --port 8000"


@pytest.mark.parametrize("option", ["--np", "--port"])
def test_start_invalid_integer(run, option):
    result = invoke("start", option, "abc")
    assert result.exit_code == 2
    assert "is not a valid integer" in result.output
    run.assert_not_called()


def test_stop(run):
    result = invoke("stop", "--port", "8000")
    assert result.exit_code == 0
    assert run.call_args.args[0] == f"pgrep -fo '{cli.filepath} --host {cli.HOST} --port 8000' | xargs kill"
    assert f"NEST Server MPI running at http://{cli.HOST}:8000 has stopped." in result.output


def test_stop_not_running(run):
    run.side_effect = subprocess.CalledProcessError(1, "pgrep")
    result = invoke("stop")
    assert result.exit_code == 0
    assert f"NEST Server MPI is not running at http://{cli.HOST}:{cli.PORT}." in result.output
