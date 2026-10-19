import os.path
import time
from collections import abc

import pytest
import RestrictedPython

from nest_server import security


class TestCheckSecurity:
    @pytest.fixture
    def secure(self, monkeypatch):
        monkeypatch.setattr(security, "AUTH_DISABLED", False)
        monkeypatch.setattr(security, "CORS_ORIGINS", ["http://localhost:*"])
        monkeypatch.setattr(security, "EXEC_CALL_ENABLED", False)
        monkeypatch.setattr(security, "RESTRICTION_DISABLED", False)

    def test_secure_settings_print_nothing(self, secure, capsys):
        security._check_security()
        assert capsys.readouterr().out == ""

    def test_auth_disabled(self, secure, monkeypatch, capsys):
        monkeypatch.setattr(security, "AUTH_DISABLED", True)
        security._check_security()
        out = capsys.readouterr().out
        assert "WARNING" in out
        assert "AUTH:" in out
        assert "CORS:" not in out

    def test_cors_wildcard(self, secure, monkeypatch, capsys):
        monkeypatch.setattr(security, "CORS_ORIGINS", ["*"])
        security._check_security()
        assert "CORS:" in capsys.readouterr().out

    def test_exec_call_enabled(self, secure, monkeypatch, capsys):
        monkeypatch.setattr(security, "EXEC_CALL_ENABLED", True)
        security._check_security()
        out = capsys.readouterr().out
        assert "EXEC CALL:" in out
        assert "RESTRICTION:" not in out

    def test_restriction_disabled_only_warns_with_exec_call(self, secure, monkeypatch, capsys):
        monkeypatch.setattr(security, "RESTRICTION_DISABLED", True)
        security._check_security()
        assert capsys.readouterr().out == ""

        monkeypatch.setattr(security, "EXEC_CALL_ENABLED", True)
        security._check_security()
        assert "RESTRICTION:" in capsys.readouterr().out


class TestGetRestrictedGlobals:
    def test_contains_guards(self):
        globals_ = security.get_restricted_globals()
        assert globals_["_print_"] is RestrictedPython.PrintCollector
        assert globals_["_getattr_"] is RestrictedPython.Guards.safer_getattr
        assert globals_["_getiter_"] is iter
        assert globals_["_write_"] is RestrictedPython.Guards.full_write_guard
        assert callable(globals_["_getitem_"])

    def test_builtins(self):
        builtins = security.get_restricted_globals()["__builtins__"]
        assert builtins["max"] is max
        assert builtins["min"] is min
        assert builtins["sum"] is sum
        assert builtins["time"] is time
        assert "open" not in builtins
        assert "__import__" not in builtins

    def test_builtins_do_not_leak_into_safe_builtins(self):
        security.get_restricted_globals()
        assert "time" not in RestrictedPython.safe_builtins

    @pytest.mark.parametrize(("obj", "index", "expected"), [([1, 2], 1, 2), ((1, 2), 0, 1), ({"a": 3}, "a", 3)])
    def test_getitem_allowed_types(self, obj, index, expected):
        getitem = security.get_restricted_globals()["_getitem_"]
        assert getitem(obj, index) == expected

    @pytest.mark.parametrize("obj", [None, "abc", b"abc", range(3)])
    def test_getitem_rejects_other_types(self, obj):
        getitem = security.get_restricted_globals()["_getitem_"]
        with pytest.raises(TypeError, match="unidentified object"):
            getitem(obj, 0)

    def test_getitem_rejects_subclasses(self):
        class MyList(list):
            pass

        getitem = security.get_restricted_globals()["_getitem_"]
        with pytest.raises(TypeError):
            getitem(MyList([1]), 0)

    def test_getitem_extra_types(self):
        class Indexable:
            def __getitem__(self, index):
                return index * 2

        getitem = security.get_restricted_globals([Indexable])["_getitem_"]
        assert getitem(Indexable(), 3) == 6

    def test_restricted_code_runs(self):
        source = "x = [1, 2, 3]\ny = sum(x)\nz = x[0]\nprint(y)"
        code = RestrictedPython.compile_restricted(source, "<inline>", "exec")
        globals_ = security.get_restricted_globals()
        exec(code, globals_)  # noqa: S102
        assert globals_["y"] == 6
        assert globals_["z"] == 1
        assert globals_["_print"].txt == ["6", "\n"]

    def test_restricted_code_blocks_open(self):
        code = RestrictedPython.compile_restricted("open('/etc/passwd')", "<inline>", "exec")
        with pytest.raises(NameError):
            exec(code, security.get_restricted_globals())  # noqa: S102


class TestGetModulesFromEnv:
    def test_import(self, monkeypatch):
        monkeypatch.setattr(security, "MODULES", "import time")
        assert security.get_modules_from_env() == {"time": time}

    def test_import_as(self, monkeypatch):
        monkeypatch.setattr(security, "MODULES", "import os.path as osp")
        assert security.get_modules_from_env() == {"osp": os.path}

    def test_dotted_import_uses_full_name(self, monkeypatch):
        monkeypatch.setattr(security, "MODULES", "import os.path")
        assert security.get_modules_from_env() == {"os.path": os.path}

    def test_from_import(self, monkeypatch):
        monkeypatch.setattr(security, "MODULES", "from collections import abc")
        assert security.get_modules_from_env() == {"abc": abc}

    def test_from_import_as(self, monkeypatch):
        monkeypatch.setattr(security, "MODULES", "from collections import abc as cabc")
        assert security.get_modules_from_env() == {"cabc": abc}

    def test_multiple_statements(self, monkeypatch):
        monkeypatch.setattr(security, "MODULES", "import time; import os.path as osp\nfrom collections import abc")
        assert security.get_modules_from_env() == {"time": time, "osp": os.path, "abc": abc}

    def test_multiple_names_in_one_statement(self, monkeypatch):
        monkeypatch.setattr(security, "MODULES", "import time, os")
        assert set(security.get_modules_from_env()) == {"time", "os"}

    def test_non_import_statements_are_ignored(self, monkeypatch):
        monkeypatch.setattr(security, "MODULES", "x = 1; import time; print('hi')")
        assert security.get_modules_from_env() == {"time": time}

    def test_empty(self, monkeypatch):
        monkeypatch.setattr(security, "MODULES", "")
        assert security.get_modules_from_env() == {}

    def test_syntax_error(self, monkeypatch):
        monkeypatch.setattr(security, "MODULES", "import")
        with pytest.raises(SyntaxError, match="contains syntax errors"):
            security.get_modules_from_env()

    def test_null_byte_raises_syntax_error(self, monkeypatch):
        monkeypatch.setattr(security, "MODULES", "import time\0")
        with pytest.raises(SyntaxError):
            security.get_modules_from_env()

    def test_missing_module(self, monkeypatch):
        monkeypatch.setattr(security, "MODULES", "import does_not_exist_xyz")
        with pytest.raises(ModuleNotFoundError):
            security.get_modules_from_env()
