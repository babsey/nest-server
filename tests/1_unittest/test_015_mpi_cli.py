import importlib
import subprocess
import sys
from unittest import mock

import pytest

from nest_server import __version__
from nest_server.mpi import cli


@pytest.fixture(autouse=True)
def defaults(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "HOST", "127.0.0.1")
    monkeypatch.setattr(cli, "PORT", 52425)
    monkeypatch.setattr(cli, "NUM_PROCESSES", 1)
    monkeypatch.setattr(cli, "LOGFILE", str(tmp_path / "nest-server-mpi.log"))


@pytest.fixture
def run(monkeypatch):
    mocked = mock.Mock()
    monkeypatch.setattr(cli.subprocess, "run", mocked)
    return mocked


def call_main(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["nest-server-mpi", *args])
    cli.main()


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


def test_no_arguments_prints_help(monkeypatch, capsys, run):
    with pytest.raises(SystemExit) as exc:
        call_main(monkeypatch)
    assert exc.value.code == 0
    assert "A MPI server for the NEST Simulator" in capsys.readouterr().out
    run.assert_not_called()


def test_invalid_operation(monkeypatch, run):
    with pytest.raises(SystemExit) as exc:
        call_main(monkeypatch, "restart")
    assert exc.value.code == 2
    run.assert_not_called()


def test_version(monkeypatch, capsys, run):
    call_main(monkeypatch, "version")
    assert capsys.readouterr().out.strip() == __version__
    run.assert_not_called()


def test_log(monkeypatch, run):
    call_main(monkeypatch, "log")
    run.assert_called_once_with(f"tail -f {cli.LOGFILE}", shell=True, executable="/bin/bash", check=True)


def test_pid(monkeypatch, run):
    call_main(monkeypatch, "pid")
    cmd = run.call_args.args[0]
    assert cmd == f"pgrep -fo '{cli.filepath} --host 127.0.0.1 --port 52425'"


def test_pid_no_process(monkeypatch, capsys, run):
    run.side_effect = subprocess.CalledProcessError(1, "pgrep")
    call_main(monkeypatch, "pid")
    assert capsys.readouterr().out.strip() == "No such process"


def test_start(monkeypatch, run):
    call_main(monkeypatch, "start")
    cmd = run.call_args.args[0]
    assert cmd == f"mpirun -n 1 {cli.filepath} --host 127.0.0.1 --port 52425"
    kwargs = run.call_args.kwargs
    assert kwargs["shell"] is True
    assert kwargs["check"] is True
    assert kwargs["stdout"].name == cli.LOGFILE


def test_start_truncates_logfile(monkeypatch, run):
    with open(cli.LOGFILE, "w") as f:
        f.write("old content")
    call_main(monkeypatch, "start")
    with open(cli.LOGFILE) as f:
        assert f.read() == ""


@pytest.mark.parametrize(
    "args",
    [
        ["-n", "4", "-h", "0.0.0.0", "-p", "8000"],
        ["--np", "4", "--host", "0.0.0.0", "--port", "8000"],
    ],
)
def test_start_with_options(monkeypatch, run, args):
    call_main(monkeypatch, "start", *args)
    cmd = run.call_args.args[0]
    assert cmd == f"mpirun -n 4 {cli.filepath} --host 0.0.0.0 --port 8000"
    assert cli.HOST == "0.0.0.0"
    assert cli.PORT == 8000
    assert cli.NUM_PROCESSES == 4


def test_start_with_invalid_port(monkeypatch, run):
    with pytest.raises(SystemExit) as exc:
        call_main(monkeypatch, "start", "--port", "abc")
    assert exc.value.code == 2
    run.assert_not_called()


def test_stop(monkeypatch, capsys, run):
    call_main(monkeypatch, "stop", "--port", "8000")
    cmd = run.call_args.args[0]
    assert cmd == f"pgrep -fo '{cli.filepath} --host 127.0.0.1 --port 8000' | xargs kill"
    assert "NEST Server MPI running at http://127.0.0.1:8000 has stopped." in capsys.readouterr().out


def test_stop_not_running(monkeypatch, capsys, run):
    run.side_effect = subprocess.CalledProcessError(1, "pgrep")
    call_main(monkeypatch, "stop")
    assert "NEST Server MPI is not running at http://127.0.0.1:52425." in capsys.readouterr().out
