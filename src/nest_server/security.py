# security.py
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

import ast
import importlib
import os
import time

import RestrictedPython

from nest_server.helpers import str2bool

_default_origins = "http://localhost:*,http://127.0.0.1:*"
ACCESS_TOKEN = os.getenv("NEST_SERVER_ACCESS_TOKEN", "")
AUTH_DISABLED = str2bool(os.getenv("NEST_SERVER_DISABLE_AUTH"))
CORS_ORIGINS = os.getenv("NEST_SERVER_CORS_ORIGINS", _default_origins).split(",")
EXEC_CALL_ENABLED = str2bool(os.getenv("NEST_SERVER_ENABLE_EXEC_CALL"))
MODULES = os.getenv("NEST_SERVER_MODULES", "import nest")
RESTRICTION_DISABLED = str2bool(os.getenv("NEST_SERVER_DISABLE_RESTRICTION"))


def _check_security() -> None:
    """
    Checks the security level of the NEST Server instance.
    """

    msg = []
    if AUTH_DISABLED:
        msg.append("AUTH:\tThe authorization settings are disabled.")
    if "*" in CORS_ORIGINS:
        msg.append("CORS:\tThe allowed origins are not restricted.")
    if EXEC_CALL_ENABLED:
        msg.append("EXEC CALL:\tThe exec route is enabled and scripts can be executed.")
        if RESTRICTION_DISABLED:
            msg.append("RESTRICTION: The execution of scripts is not protected by RestrictedPython.")

    if len(msg) > 0:
        print(
            "WARNING: You chose to disable important access restrictions!\n"
            " This allows other computers to execute code on this machine as the current user!\n"
            " Be sure you understand the implications of these settings and take"
            " appropriate measures to protect your runtime environment!"
        )
        print("\n - ".join([" "] + msg) + "\n")


def get_restricted_globals(extra_types: list | None = None) -> dict:
    """Get restricted globals for exec function."""

    if extra_types is None:
        extra_types = []

    def getitem(obj, index):
        typelist = [list, tuple, dict] + extra_types
        if obj is not None and type(obj) in typelist:
            return obj[index]
        msg = f"Error getting restricted globals: unidentified object '{obj}'."
        raise TypeError(msg)

    restricted_builtins = RestrictedPython.safe_builtins.copy()
    restricted_builtins.update(RestrictedPython.limited_builtins)
    restricted_builtins.update(RestrictedPython.utility_builtins)
    restricted_builtins.update(
        {
            "max": max,
            "min": min,
            "sum": sum,
            "time": time,
        }
    )

    restricted_globals = {
        "__builtins__": restricted_builtins,
        "_print_": RestrictedPython.PrintCollector,
        "_getattr_": RestrictedPython.Guards.safer_getattr,
        "_getitem_": getitem,
        "_getiter_": iter,
        "_unpack_sequence_": RestrictedPython.Guards.guarded_unpack_sequence,
        "_write_": RestrictedPython.Guards.full_write_guard,
    }

    return restricted_globals


def get_modules_from_env() -> dict:
    """Get modules from environment variable NEST_SERVER_MODULES.

    This function converts the content of the environment variable
    NEST_SERVER_MODULES:
    to a formatted dictionary for updating the Python `globals`.

    Here is an example:
        `NEST_SERVER_MODULES="import nest; import numpy as np; from numpy import random"`
    is converted to the following dictionary:
        `{'nest': <module 'nest'> 'np': <module 'numpy'>, 'random': <module 'numpy.random'>}`
    """
    modules = {}

    try:
        parsed = ast.iter_child_nodes(ast.parse(MODULES))
    except (SyntaxError, ValueError) as exc:
        raise SyntaxError("The NEST server module environment variables contains syntax errors.") from exc

    for node in parsed:
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules[alias.asname or alias.name] = importlib.import_module(alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                modules[alias.asname or alias.name] = importlib.import_module(f"{node.module}.{alias.name}")

    return modules
