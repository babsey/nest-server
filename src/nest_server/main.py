# main.py
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

import contextlib
import logging
import os

from flask import Flask, abort, jsonify, request
from flask.logging import default_handler
from flask_cors import CORS

from nest_server.handler import ErrorHandler
from nest_server.helpers import get_arguments
from nest_server.kernel import api_client, master_call, nest_calls, nest_version
from nest_server.mpi.state import has_mpi_comm
from nest_server.security import ACCESS_TOKEN, AUTH_DISABLED, CORS_ORIGINS, EXEC_CALL_ENABLED, _check_security

# This ensures that the logging information shows up in the console running the server,
# even when Flask's event loop is running.
logger = logging.getLogger(__name__)
logger.addHandler(default_handler)
logger.setLevel(os.getenv("NEST_SERVER_LOGGER_LEVEL", "INFO"))


def create_app():

    app = Flask(__name__)

    # Inform client-side user agents that they should not attempt to call our
    # server from any non-whitelisted domain.
    CORS(app, origins=CORS_ORIGINS, methods=["GET", "POST"])

    # https://flask.palletsprojects.com/en/2.3.x/errorhandling/
    @app.errorhandler(ErrorHandler)
    def error_handler(e):
        return jsonify(e.to_dict()), e.status_code

    @app.before_request
    def _setup_auth():
        """
        Authentication function that generates and validates the NESTServerAuth
        header with a bearer token.

        Cleans up references to itself and the running `app` from this module, as
        it may be accessible when the code execution sandbox fails.
        """
        try:
            # Import the modules inside of the auth function, so that if they fail
            # the auth returns a forbidden error.
            import gc
            import hashlib
            import inspect
            import time

            # Find our reference to the current function in the garbage collector.
            frame = inspect.currentframe()
            code = frame.f_code
            globs = frame.f_globals
            functype = type(lambda: 0)
            funcs = []
            for func in gc.get_referrers(code):
                if (
                    type(func) is functype
                    and getattr(func, "__code__", None) is code
                    and getattr(func, "__globals__", None) is globs
                ):
                    funcs.append(func)
                    if len(funcs) > 1:
                        return ("Unauthorized", 403)
            self = funcs[0]

            # Use the salted hash (unless `PYTHONHASHSEED` is fixed) of the
            # location of this function in the Python heap and the current
            # timestamp to create a SHA512 hash.
            if not hasattr(self, "_hash"):
                if ACCESS_TOKEN:
                    self._hash = ACCESS_TOKEN
                else:
                    hasher = hashlib.sha512()
                    hasher.update(str(hash(id(self))).encode("utf-8"))
                    hasher.update(str(time.perf_counter()).encode("utf-8"))
                    self._hash = hasher.hexdigest()[:48]
                if not AUTH_DISABLED:
                    print(f"   Access token to NEST Server: {self._hash}")
                    print("   Add this to the headers: {'NESTServerAuth': '<access_token>'}\n")

            if request.method == "OPTIONS":
                return

            # The first time we hit the line below is when below the function
            # definition we call `setup_auth` without any Flask request existing
            # yet, so the function errors and exits here after generating and
            # storing the auth hash.
            auth = request.headers.get("NESTServerAuth", None)

            # We continue here the next time this function is called, before the
            # Flask app handles the first request. At that point we also remove
            # this module's reference to the running app.
            try:
                del globals()["app"]
            except KeyError:
                contextlib.suppress(KeyError)

            # Things get more straightforward here: Every time a request is
            # handled, compare the NESTServerAuth header to the hash, with a
            # constant-time algorithm to avoid timing attacks.
            if not (AUTH_DISABLED or auth == self._hash):
                return ("Unauthorized", 403)

        # DON'T LINT! Intentional bare except clause! Even `KeyboardInterrupt` and
        # `SystemExit` exceptions should not bypass authentication!
        except Exception:  # noqa: BLE001
            return ("Unauthorized", 403)

    print(80 * "*")
    _check_security()
    _setup_auth()
    del _setup_auth
    print(80 * "*")

    # ------
    # Routes
    # ------

    @app.route("/", methods=["GET"])
    def index():
        """Route to get NEST version and mpi option."""

        response = {
            "nest": nest_version,
            "mpi": has_mpi_comm(),
        }

        return jsonify(response)

    @app.route("/api", methods=["GET"])
    def route_api():
        """Route to list call functions in NEST."""

        return jsonify(nest_calls)

    @app.route("/api/<call>", methods=["GET", "POST"])
    def route_api_call(call: str):
        """Route to call function in NEST."""

        args, kwargs = get_arguments(request)
        logger.debug(f"route_api_call - call={call}, args={args}, kwargs={kwargs}")

        return jsonify(api_client(call, args, kwargs))

    @app.route("/exec", methods=["GET", "POST"])
    def route_exec():
        """Route to execute script in Python."""

        if not EXEC_CALL_ENABLED:
            abort(
                403,
                "The route `/exec` has been disabled. Please contact the server administrator.",
            )

        args, kwargs = get_arguments(request)
        logger.debug(f"route_exec - args={args}, kwargs={kwargs}")

        response = master_call("exec", args, kwargs)
        return jsonify(response)

    return app
