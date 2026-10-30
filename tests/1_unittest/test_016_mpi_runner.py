"""Tests for the MPI runner script.

The runner executes everything at import time and needs mpi4py, docopt and a
running MPI environment. Here, these dependencies are replaced by fakes and the
script is executed with runpy.
"""

import runpy
import sys
import types
from unittest import mock

import pytest

from nest_server.mpi import cli, state

RUNNER = str(cli.filepath)


class StopWorker(Exception):
    """Raised by the fake communicator to leave the worker loop."""


def make_comm(rank, calls=()):
    """Fake communicator; bcast yields (call_name, (args, kwargs)) pairs, then stops."""
    sequence = [item for call_name, args, kwargs in calls for item in (call_name, (args, kwargs))]

    def bcast(obj, root=0):
        if not sequence:
            raise StopWorker
        return sequence.pop(0)

    comm = mock.Mock()
    comm.Get_rank.return_value = rank
    comm.bcast.side_effect = bcast
    return comm


@pytest.fixture
def fakes(monkeypatch):
    original_comm = state.mpi_comm

    mpi = types.ModuleType("mpi4py.MPI")
    mpi.COMM_WORLD = mock.Mock()
    mpi4py = types.ModuleType("mpi4py")
    mpi4py.MPI = mpi
    monkeypatch.setitem(sys.modules, "mpi4py", mpi4py)
    monkeypatch.setitem(sys.modules, "mpi4py.MPI", mpi)

    docopt = types.ModuleType("docopt")
    docopt.docopt = mock.Mock(return_value={"--host": "0.0.0.0", "--port": "8000"})
    monkeypatch.setitem(sys.modules, "docopt", docopt)

    nest = types.ModuleType("nest")
    nest.serialize_data = mock.Mock(side_effect=lambda data: {"serialized": data})
    monkeypatch.setitem(sys.modules, "nest", nest)

    kernel = types.ModuleType("nest_server.kernel")
    kernel.do_call = mock.Mock(return_value="call-response")
    kernel.do_exec = mock.Mock(return_value={"data": "exec-response"})
    kernel.nestify = mock.Mock(side_effect=lambda call_name, args, kwargs: (call_name.upper(), args, kwargs))
    monkeypatch.setitem(sys.modules, "nest_server.kernel", kernel)

    app = mock.Mock()
    main = types.ModuleType("nest_server.main")
    main.create_app = mock.Mock(return_value=app)
    monkeypatch.setitem(sys.modules, "nest_server.main", main)

    monkeypatch.setattr(sys, "argv", [RUNNER])

    yield types.SimpleNamespace(mpi=mpi, docopt=docopt, nest=nest, kernel=kernel, main=main, app=app)

    state.mpi_comm = original_comm


def run_runner(fakes, comm):
    fakes.mpi.COMM_WORLD.Clone.return_value = comm
    return runpy.run_path(RUNNER, run_name="__main__")


def test_master_starts_flask_app(fakes):
    comm = make_comm(0)

    namespace = run_runner(fakes, comm)

    assert namespace["rank"] == 0
    assert state.get_mpi_comm() is comm
    fakes.docopt.docopt.assert_called_once()
    fakes.main.create_app.assert_called_once_with()
    fakes.app.run.assert_called_once_with(host="0.0.0.0", port="8000", threaded=False)
    comm.bcast.assert_not_called()


def test_worker_executes_calls_and_gathers_responses(fakes):
    comm = make_comm(1, [("Create", ["iaf_psc_alpha"], {"n": 2})])

    with pytest.raises(StopWorker):
        run_runner(fakes, comm)

    assert state.get_mpi_comm() is comm
    fakes.app.run.assert_not_called()
    fakes.kernel.nestify.assert_called_once_with("Create", ["iaf_psc_alpha"], {"n": 2})
    fakes.kernel.do_call.assert_called_once_with("CREATE", ["iaf_psc_alpha"], {"n": 2})
    fakes.kernel.do_exec.assert_not_called()
    comm.gather.assert_called_once_with({"serialized": "call-response"}, root=0)


def test_worker_executes_exec(fakes):
    comm = make_comm(2, [("exec", [], {"source": "x = 1", "return": "x"})])

    with pytest.raises(StopWorker):
        run_runner(fakes, comm)

    fakes.kernel.do_exec.assert_called_once_with([], {"source": "x = 1", "return": "x"})
    fakes.kernel.nestify.assert_not_called()
    fakes.kernel.do_call.assert_not_called()
    comm.gather.assert_called_once_with({"serialized": {"data": "exec-response"}}, root=0)


def test_worker_handles_multiple_calls(fakes):
    comm = make_comm(1, [("ResetKernel", [], {}), ("exec", [], {}), ("Simulate", [10.0], {})])

    with pytest.raises(StopWorker):
        run_runner(fakes, comm)

    assert fakes.kernel.do_call.call_count == 2
    assert fakes.kernel.do_exec.call_count == 1
    assert comm.gather.call_count == 3


def test_worker_skips_gather_on_failed_call(fakes):
    fakes.kernel.do_call.side_effect = [RuntimeError("boom"), "ok"]
    comm = make_comm(1, [("Simulate", [-1.0], {}), ("Simulate", [10.0], {})])

    with pytest.raises(StopWorker):
        run_runner(fakes, comm)

    assert fakes.kernel.do_call.call_count == 2
    comm.gather.assert_called_once_with({"serialized": "ok"}, root=0)


def test_worker_log_message(fakes, caplog, monkeypatch):
    monkeypatch.setenv("NEST_SERVER_LOGGER_LEVEL", "DEBUG")
    comm = make_comm(3)

    with pytest.raises(StopWorker), caplog.at_level("DEBUG"):
        run_runner(fakes, comm)

    assert any("==> WORKER 3/" in r.getMessage() and "(spinwait)" in r.getMessage() for r in caplog.records)
