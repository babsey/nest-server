# kernel.py
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


import inspect
import logging
import os
import time
from collections.abc import Callable

import nest
import RestrictedPython
from flask.logging import default_handler

from nest_server.handler import Capturing, get_or_error
from nest_server.helpers import clean_code
from nest_server.mpi.helpers import combine
from nest_server.mpi.main import master_receive_gather, master_send_bcast
from nest_server.mpi.state import get_mpi_comm
from nest_server.security import RESTRICTION_DISABLED, get_modules_from_env, get_restricted_globals

logger = logging.getLogger(__name__)
logger.addHandler(default_handler)
logger.setLevel(os.getenv("NEST_SERVER_LOGGER_LEVEL", "INFO"))

nest_calls = dir(nest)
nest_calls = list(filter(lambda x: not x.startswith("_"), nest_calls))
nest_calls.sort()

nest_types = [nest.NodeCollection, nest.SynapseCollection]
nest_version = nest.build_info["version"]


def mpi_master_log(call_name: str, msg: str) -> None:
    msg = f"==> MASTER 0/{time.time():.7f} ({call_name}): {msg}"
    logger.debug(msg)


@get_or_error
def api_client(call_name: str, args: list, kwargs: dict) -> dict | None:
    """API Client to call function in NEST."""
    logger.debug(f"api_client - {call_name}, {args}, {kwargs}")

    call = getattr(nest, call_name)

    if not callable(call):
        return call

    elif "inspect" in kwargs:
        response = {"data": getattr(inspect, kwargs["inspect"])(call)}

    else:
        response = master_call(call_name, args, kwargs)

    return nest.serialize_data(response)


def do_call(call: Callable, args: list, kwargs: dict):
    logger.debug(f"do_call - {call.__name__}({args}, {kwargs})")

    if call.__name__ == "GetStatus":
        nodes_or_conns = kwargs.get("nodes_or_conns", [])
        if len(args) >= 1:
            nodes_or_conns = args[0]

        keys = kwargs.get("keys")
        if len(args) >= 2:
            keys = args[1]

        logger.debug(f"GetStatus - {nodes_or_conns}.get({keys})")
        response = nodes_or_conns.get(keys) if keys else nodes_or_conns.get()

    elif call.__name__ == "SetStatus":
        nodes_or_conns = kwargs.get("nodes_or_conns", [])
        if len(args) >= 1:
            nodes_or_conns = args[0]

        params = kwargs.get("params", {})
        if len(args) >= 2:
            params = args[1]

        logger.debug(f"SetStatus - {nodes_or_conns}.set({params})")
        response = nodes_or_conns.set(params)

    else:
        response = call(*args, **kwargs)

    return response


def do_exec(args: list, kwargs: dict) -> dict:
    source_code = kwargs.get("source", "")
    source_cleaned = clean_code(source_code)

    response = {}
    if RESTRICTION_DISABLED:
        with Capturing() as stdout:
            globals_ = globals().copy()
            globals_.update(get_modules_from_env())
            get_or_error(exec)(source_cleaned, globals_)

        if len(stdout) > 0:
            response["stdout"] = "\n".join(stdout)

    else:
        code = RestrictedPython.compile_restricted(source_cleaned, "<inline>", "exec")
        globals_ = get_restricted_globals(nest_types)
        globals_.update(get_modules_from_env())
        get_or_error(exec)(code, globals_)

        if "_print" in globals_:
            response["stdout"] = "".join(globals_["_print"].txt)

    if "return" in kwargs:
        if isinstance(kwargs["return"], (list, tuple)):
            data = {variable: globals_.get(variable, None) for variable in kwargs["return"]}
        else:
            data = globals_.get(kwargs["return"], None)

        response["data"] = get_or_error(nest.serialize_data)(data)

    return response


def master_call(call_name: str, args: list | None = None, kwargs: dict | None = None):
    """Call a PYNEST function or execute a script within the server.

    If the server is run serially (i.e., without MPI), this function
    will do one of two things: If call_name is "exec", it will execute
    the script given in args via do_exec(). If call_name is the name
    of a PyNEST API function, it will call that function and pass args
    and kwargs to it.

    If the server is run with MPI, this function will first communicate
    the call type ("exec" or API call) and the args and kwargs to all
    worker processes. Only then will it execute the call in the same
    way as described above for the serial case. After the call, all
    worker responses are collected, combined and returned.

    Please note that this function must only be called on the master
    process (i.e., the task with rank 0) in a distributed scenario.

    """

    if args is None:
        args = []

    if kwargs is None:
        kwargs = {}

    mpi_comm = get_mpi_comm()

    if mpi_comm is not None:
        master_send_bcast(mpi_master_log, mpi_comm, call_name, args, kwargs)

    if call_name == "exec":
        response = do_exec(args, kwargs)
    else:
        call, args, kwargs = nestify(call_name, args, kwargs)
        mpi_master_log(call_name, f"local call, args={args}, kwargs={kwargs}")

        try:
            response = do_call(call, args, kwargs)
            logger.debug(f"call response - {response}")

        except Exception as e:  # noqa: BLE001
            logger.error(f"Master - Failed to execute call: {e}")
            response = None

    if mpi_comm is not None:
        response = master_receive_gather(mpi_master_log, mpi_comm, call_name, nest.serialize_data(response))
        response = combine(response)
        logger.debug(f"combined - {response}")
        return response

    return nest.serialize_data(response)


def nestify(call_name: str, args: list, kwargs: dict) -> tuple[Callable, list, dict]:
    """Get the NEST API call and convert arguments if neccessary."""
    logger.debug(f"nestify - {call_name}, {args}, {kwargs}")

    call = getattr(nest, call_name)
    objectnames = ["nodes", "nodes_or_conns", "pre", "post", "source", "target"]
    paramKeys = list(inspect.signature(call).parameters.keys())
    args = [nest.NodeCollection(arg) if paramKeys[idx] in objectnames else arg for (idx, arg) in enumerate(args)]

    for key, value in kwargs.items():
        if key in objectnames:
            kwargs[key] = nest.NodeCollection(value)

        # if mpi_comm is not None:
        #     if key == "params":
        #         kwargs[key] = {k: mpi_comm.scatter(value, root=0) for (k, v) in value.items()}

    logger.debug(f"nestified - {call}, {args}, {kwargs}")

    return call, args, kwargs
