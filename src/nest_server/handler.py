# handler.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

import io
import sys
import traceback
from collections.abc import Callable


class Capturing(list):
    """Monitor stdout contents i.e. print."""

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = io.StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


class ErrorHandler(Exception):
    status_code = 400
    lineno = -1

    def __init__(self, message: str, lineno: int | None = None, status_code: int | None = None, payload=None):
        super().__init__()
        self.message = message

        if status_code is not None:
            self.status_code = status_code

        if lineno is not None:
            self.lineno = lineno

        self.payload = payload

    def to_dict(self) -> dict:
        rv = dict(self.payload or ())
        rv["message"] = self.message

        if self.lineno != -1:
            rv["lineNumber"] = self.lineno

        return rv


def get_lineno(err: Exception, tb_idx: int):
    lineno = -1

    if hasattr(err, "lineno") and err.lineno is not None:
        lineno = err.lineno

    else:
        tb = sys.exc_info()[2]
        lineno = traceback.extract_tb(tb)[tb_idx][1]

    return lineno


def get_or_error(func: Callable) -> Callable:
    """Wrapper to get data and status."""

    def func_wrapper(call: Callable, *args, **kwargs):
        try:
            return func(call, *args, **kwargs)

        except (KeyError, SyntaxError, TypeError, ValueError) as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            lineno = get_lineno(err, 1)

        except Exception as err:  # noqa: BLE001
            error_class = err.__class__.__name__
            detail = err.args[0]
            lineno = get_lineno(err, -1)

        for line in traceback.format_exception(*sys.exc_info()):
            print(line, flush=True)

        message = f"{error_class}: {detail}" if lineno == -1 else f"{error_class} at line {lineno}: {detail}"

        raise ErrorHandler(message, lineno)

    return func_wrapper
