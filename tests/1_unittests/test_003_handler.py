import sys

import pytest

from nest_server.handler import Capturing, ErrorHandler, get_or_error


class TestCapturing:
    def test_captures_printed_lines(self):
        with Capturing() as stdout:
            print("hello")
            print("world")
        assert stdout == ["hello", "world"]

    def test_restores_stdout(self):
        original = sys.stdout
        with Capturing():
            assert sys.stdout is not original
        assert sys.stdout is original

    def test_empty_output(self):
        with Capturing() as stdout:
            pass
        assert stdout == []

    def test_restores_stdout_on_exception(self):
        original = sys.stdout
        with pytest.raises(RuntimeError), Capturing():
            raise RuntimeError("boom")
        assert sys.stdout is original


class TestErrorHandler:
    def test_defaults(self):
        err = ErrorHandler("Something failed")
        assert err.status_code == 400
        assert err.lineno == -1
        assert err.to_dict() == {"message": "Something failed"}

    def test_custom_status_code_and_lineno(self):
        err = ErrorHandler("Bad", lineno=7, status_code=500)
        assert err.status_code == 500
        assert err.to_dict() == {"message": "Bad", "lineNumber": 7}

    def test_lineno_zero_is_kept(self):
        assert ErrorHandler("Bad", lineno=0).to_dict() == {"message": "Bad", "lineNumber": 0}

    def test_payload_is_merged(self):
        err = ErrorHandler("Bad", payload={"extra": 1})
        assert err.to_dict() == {"extra": 1, "message": "Bad"}

    def test_message_overrides_payload(self):
        err = ErrorHandler("Bad", payload={"message": "ignored"})
        assert err.to_dict() == {"message": "Bad"}

    def test_class_defaults_not_mutated(self):
        ErrorHandler("Bad", lineno=3, status_code=500)
        assert ErrorHandler.status_code == 400
        assert ErrorHandler.lineno == -1


class TestGetOrError:
    def test_returns_result(self):
        assert get_or_error(lambda x, y: x + y)(1, y=2) == 3

    def test_key_error(self):
        def func(_):
            return {}["missing"]

        with pytest.raises(ErrorHandler) as exc_info:
            get_or_error(func)(None)

        assert exc_info.value.message.startswith("KeyError at line")
        assert exc_info.value.message.endswith(": missing")
        assert exc_info.value.status_code == 400

    def test_value_error_reports_line_of_wrapped_function(self):
        def func(_):
            raise ValueError("bad value")

        with pytest.raises(ErrorHandler) as exc_info:
            get_or_error(func)(None)

        lineno = func.__code__.co_firstlineno + 1
        assert exc_info.value.lineno == lineno
        assert exc_info.value.message == f"ValueError at line {lineno}: bad value"

    def test_syntax_error_uses_its_lineno(self):
        with pytest.raises(ErrorHandler) as exc_info:
            get_or_error(exec)("x = 1\ny = (\n", {})

        assert exc_info.value.message.startswith("SyntaxError at line ")
        assert exc_info.value.lineno == exc_info.value.to_dict()["lineNumber"]

    def test_type_error_in_exec_reports_source_line(self):
        with pytest.raises(ErrorHandler) as exc_info:
            get_or_error(exec)("a = 1\nb = 2\nc = a + 'x'\n", {})

        assert exc_info.value.lineno == 3
        assert exc_info.value.message.startswith("TypeError at line 3:")

    def test_other_exception_reports_innermost_line(self):
        with pytest.raises(ErrorHandler) as exc_info:
            get_or_error(exec)("a = 1\nb = undefined_name\n", {})

        assert exc_info.value.lineno == 2
        assert exc_info.value.message == "NameError at line 2: name 'undefined_name' is not defined"
