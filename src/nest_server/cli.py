# cli.py
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

import argparse
import os
import subprocess
import sys
from pathlib import Path

from gunicorn.app.wsgiapp import WSGIApplication

from nest_server import __version__
from nest_server.helpers import get_boolean_environ

DAEMON = get_boolean_environ("NEST_SERVER_DAEMON")
HOST = os.getenv("NEST_SERVER_HOST", "127.0.0.1")
LOGFILE = os.getenv("NEST_SERVER_LOGFILE", "/tmp/nest-server.log")
PIDFILE = os.getenv("NEST_SERVER_PIDFILE", "/tmp/nest-server.pid")
PORT = int(os.getenv("NEST_SERVER_PORT", "52425"))
STDOUT = get_boolean_environ("NEST_SERVER_STDOUT")
TIMEOUT = int(os.getenv("NEST_SERVER_TIMEOUT", "30"))
WORKERS = int(os.getenv("NEST_SERVER_WORKERS", "1"))


def load_pid(file):
    if not Path(file).exists():
        return

    with open(file, "r") as f:
        pid = int(f.readline())

    return pid


class StandaloneApplication(WSGIApplication):
    def __init__(self, app_uri, options=None):
        self.options = options or {}
        self.app_uri = app_uri
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)


def main():
    global DAEMON, HOST, PORT, STDOUT, WORKERS

    parser = argparse.ArgumentParser(description="A Python-based API server for the NEST Simulator", add_help=False)
    parser.add_argument("operation", choices=["log", "pid", "start", "stop", "version"])

    parser.add_argument(
        "-d",
        "--daemon",
        action="store_true",
        help="run NEST Server in the background, i.e. daemonize the server process",
    )
    parser.add_argument(
        "-h", "--host", type=str, help="use hostname/IP address <HOST> for the server [default: 127.0.0.1]"
    )
    parser.add_argument("-o", "--outputs", action="store_true", help="print NEST outputs to the console")
    parser.add_argument("-p", "--port", type=int, help="use port <PORT> for opening the socket [default: 52425]")
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        help="workers silent for more than this many seconds are killed and restarted [default: 30]",
    )
    parser.add_argument(
        "-w", "--workers", type=int, help="the number of worker processes for handling requests [default: 1]"
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.daemon:
        DAEMON = args.daemon

    if args.host:
        HOST = args.host

    if args.port:
        PORT = args.port

    if args.outputs:
        STDOUT = args.outputs

    if args.workers:
        WORKERS = args.workers

    if args.operation == "log":
        subprocess.run(f"tail -f {LOGFILE}", shell=True, executable="/bin/bash", check=True)

    elif args.operation == "pid":
        pid = load_pid(PIDFILE)

        if pid:
            print(pid)
        else:
            print("No process exists.")

    elif args.operation == "start":
        options = {
            "bind": f"{HOST}:{PORT}",
            "capture_output": not STDOUT,
            "daemon": DAEMON,
            "errorlog": LOGFILE,
            "pidfile": PIDFILE,
            "timeout": TIMEOUT,
            "workers": WORKERS,
            # "worker_class": "uvicorn.workers.UvicornWorker",
        }

        msg = f"NEST Server is now running at http://{HOST}:{PORT}."
        print(msg)
        print("Use CTRL + C to stop this service.")
        print(len(msg) * "-")

        StandaloneApplication("nest_server.main:app", options).run()

    elif args.operation == "stop":
        pid = load_pid(PIDFILE)

        if pid:
            subprocess.run(f"kill {pid}", shell=True, executable="/bin/bash", check=True)
            print(f"NEST Server running at http://{HOST}:{PORT} has stopped.")
        else:
            print(f"NEST Server is not running at http://{HOST}:{PORT}.")

    elif args.operation == "version":
        print(__version__)
