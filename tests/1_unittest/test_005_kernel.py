import inspect
from unittest import mock

import nest
import pytest

from nest_server import kernel
from nest_server.handler import ErrorHandler


@pytest.fixture(autouse=True)
def reset_kernel():
    nest.ResetKernel()


@pytest.fixture
def no_mpi(monkeypatch):
    monkeypatch.setattr(kernel, "get_mpi_comm", lambda: None)


class TestNestify:
    def test_converts_positional_node_args(self):
        nest.Create("iaf_psc_alpha", 2)
        call, args, kwargs = kernel.nestify("GetStatus", [[1, 2], "V_m"], {})

        assert call is nest.GetStatus
        assert isinstance(args[0], nest.NodeCollection)
        assert args[0].tolist() == [1, 2]
        assert args[1] == "V_m"
        assert kwargs == {}

    def test_converts_node_kwargs(self):
        nest.Create("iaf_psc_alpha", 2)
        _, args, kwargs = kernel.nestify("Connect", [], {"pre": [1], "post": [2], "conn_spec": "all_to_all"})

        assert args == []
        assert isinstance(kwargs["pre"], nest.NodeCollection)
        assert isinstance(kwargs["post"], nest.NodeCollection)
        assert kwargs["conn_spec"] == "all_to_all"

    def test_leaves_other_args_untouched(self):
        _, args, kwargs = kernel.nestify("Create", ["iaf_psc_alpha", 3], {"params": {"V_m": -70.0}})
        assert args == ["iaf_psc_alpha", 3]
        assert kwargs == {"params": {"V_m": -70.0}}

    def test_unknown_call(self):
        with pytest.raises(AttributeError):
            kernel.nestify("DoesNotExist", [], {})


class TestDoCall:
    def test_plain_call(self):
        nodes = kernel.do_call(nest.Create, ["iaf_psc_alpha", 3], {})
        assert len(nodes) == 3

    def test_get_status_positional(self):
        nodes = nest.Create("iaf_psc_alpha", 2, params={"V_m": -60.0})
        assert kernel.do_call(nest.GetStatus, [nodes, "V_m"], {}) == (-60.0, -60.0)

    def test_get_status_kwargs(self):
        nodes = nest.Create("iaf_psc_alpha", 1, params={"V_m": -60.0})
        assert kernel.do_call(nest.GetStatus, [], {"nodes_or_conns": nodes, "keys": "V_m"}) == -60.0

    def test_get_status_without_keys(self):
        nodes = nest.Create("iaf_psc_alpha", 1)
        response = kernel.do_call(nest.GetStatus, [nodes], {})
        assert isinstance(response, dict)
        assert "V_m" in response

    def test_set_status_positional(self):
        nodes = nest.Create("iaf_psc_alpha", 2)
        kernel.do_call(nest.SetStatus, [nodes, {"V_m": -55.0}], {})
        assert nodes.get("V_m") == (-55.0, -55.0)

    def test_set_status_kwargs(self):
        nodes = nest.Create("iaf_psc_alpha", 1)
        kernel.do_call(nest.SetStatus, [], {"nodes_or_conns": nodes, "params": {"V_m": -50.0}})
        assert nodes.get("V_m") == -50.0


class TestDoExecUnrestricted:
    @pytest.fixture(autouse=True)
    def unrestricted(self, monkeypatch):
        monkeypatch.setattr(kernel, "RESTRICTION_DISABLED", True)
        monkeypatch.setattr(kernel, "get_modules_from_env", lambda: {"nest": nest})

    def test_stdout(self):
        assert kernel.do_exec([], {"source": "print('hello')\nprint('world')"}) == {"stdout": "hello\nworld"}

    def test_no_stdout(self):
        assert kernel.do_exec([], {"source": "x = 1"}) == {}

    def test_empty_source(self):
        assert kernel.do_exec([], {}) == {}

    def test_return_single_variable(self):
        assert kernel.do_exec([], {"source": "x = 1 + 1", "return": "x"}) == {"data": 2}

    def test_return_missing_variable(self):
        assert kernel.do_exec([], {"source": "x = 1", "return": "y"}) == {"data": None}

    def test_modules_are_available(self):
        response = kernel.do_exec([], {"source": "n = nest.Create('iaf_psc_alpha', 2)", "return": "n"})
        assert response == {"data": [1, 2]}

    def test_imports_are_commented(self):
        response = kernel.do_exec([], {"source": "import os\nx = 1", "return": "x"})
        assert response == {"data": 1}

    def test_error_reports_line(self):
        with pytest.raises(ErrorHandler) as exc_info:
            kernel.do_exec([], {"source": "x = 1\ny = x + 'a'"})
        assert exc_info.value.lineno == 2


class TestDoExecRestricted:
    @pytest.fixture(autouse=True)
    def restricted(self, monkeypatch):
        monkeypatch.setattr(kernel, "RESTRICTION_DISABLED", False)

    def test_stdout(self):
        assert kernel.do_exec([], {"source": "print('hello')"}) == {"stdout": "hello\n"}

    def test_no_stdout(self):
        assert kernel.do_exec([], {"source": "x = 1"}) == {}

    def test_return_single_variable(self):
        assert kernel.do_exec([], {"source": "x = sum([1, 2, 3])", "return": "x"}) == {"data": 6}

    def test_return_variables(self):
        assert kernel.do_exec([], {"source": "x = sum([1, 2, 3])\ny = x//3", "return": ["x", "y"]}) == {
            "data": {"x": 6, "y": 2}
        }

    def test_node_collection_indexing(self):
        source = "n = nest.Create('iaf_psc_alpha', 3)\nm = n[1]"
        assert kernel.do_exec([], {"source": source, "return": "m"}) == {"data": [2]}

    def test_open_is_blocked(self):
        with pytest.raises(ErrorHandler) as exc_info:
            kernel.do_exec([], {"source": "open('/etc/passwd')"})
        assert exc_info.value.message.startswith("NameError")

    def test_private_attribute_is_blocked(self):
        # Rejected by RestrictedPython at compile time; this error is not wrapped by get_or_error.
        with pytest.raises(SyntaxError, match="invalid attribute name"):
            kernel.do_exec([], {"source": "x = (1).__class__"})


class TestMasterCall:
    def test_serial_call(self, no_mpi):
        assert kernel.master_call("Create", ["iaf_psc_alpha", 2]) == [1, 2]

    def test_defaults(self, no_mpi):
        assert kernel.master_call("GetKernelStatus", None, None)["network_size"] == 0

    def test_serial_exec(self, no_mpi, monkeypatch):
        monkeypatch.setattr(kernel, "RESTRICTION_DISABLED", True)
        assert kernel.master_call("exec", [], {"source": "x = 3", "return": "x"}) == {"data": 3}

    def test_failed_call_returns_none(self, no_mpi):
        assert kernel.master_call("Create", ["does_not_exist_model"]) is None

    def test_mpi_call(self, monkeypatch):
        comm = mock.Mock()
        send = mock.Mock()
        receive = mock.Mock(return_value=[[1, 2], [1, 2]])
        monkeypatch.setattr(kernel, "get_mpi_comm", lambda: comm)
        monkeypatch.setattr(kernel, "master_send_bcast", send)
        monkeypatch.setattr(kernel, "master_receive_gather", receive)
        monkeypatch.setattr(kernel, "combine", lambda response: response[0])

        assert kernel.master_call("Create", ["iaf_psc_alpha", 2], {}) == [1, 2]

        send.assert_called_once_with(kernel.mpi_master_log, comm, "Create", ["iaf_psc_alpha", 2], {})
        receive.assert_called_once()
        assert receive.call_args.args[1:3] == (comm, "Create")


class TestApiClient:
    def test_non_callable_attribute(self):
        assert kernel.api_client("resolution", [], {}) == nest.resolution

    def test_inspect(self):
        response = kernel.api_client("Create", [], {"inspect": "getdoc"})
        assert response == {"data": inspect.getdoc(nest.Create)}

    def test_call(self, no_mpi):
        assert kernel.api_client("Create", ["iaf_psc_alpha", 1], {}) == [1]

    def test_unknown_call_raises_error_handler(self):
        with pytest.raises(ErrorHandler) as exc_info:
            kernel.api_client("DoesNotExist", [], {})
        assert exc_info.value.message.startswith("AttributeError")


def test_nest_calls_are_public_and_sorted():
    assert kernel.nest_calls == sorted(kernel.nest_calls)
    assert not any(name.startswith("_") for name in kernel.nest_calls)
    assert "Create" in kernel.nest_calls


def test_mpi_master_log(caplog):
    with caplog.at_level("DEBUG", logger=kernel.logger.name):
        kernel.mpi_master_log("Create", "hello")
    assert "==> MASTER 0/" in caplog.text
    assert "(Create): hello" in caplog.text
