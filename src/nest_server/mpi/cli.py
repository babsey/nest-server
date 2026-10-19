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

from nest_server import __version__

HOST = os.getenv("NEST_SERVER_HOST", "127.0.0.1")
NUM_PROCESSES = int(os.getenv("NEST_SERVER_MPI_NUM_PROCESSES", "1"))
PORT = int(os.getenv("NEST_SERVER_PORT", "52425"))
LOGFILE = os.getenv("NEST_SERVER_MPI_LOGFILE", "/tmp/nest-server-mpi.log")

filepath = Path(__file__).parent.resolve() / "runner.py"


def main() -> None:
    global HOST, PORT, NUM_PROCESSES

    parser = argparse.ArgumentParser(description="A MPI server for the NEST Simulator", add_help=False)
    parser.add_argument(
        "operation",
        choices=["log", "pid", "start", "stop", "version"],
    )

    parser.add_argument(
        "-h", "--host", type=str, help="use hostname/IP address <HOST> for the server [default: 127.0.0.1]"
    )
    parser.add_argument("-n", "--np", type=int, help="number of processes to run [default: 1]")
    parser.add_argument("-p", "--port", type=int, help="use port <PORT> for opening the socket [default: 52425]")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.host:
        HOST = args.host

    if args.np:
        NUM_PROCESSES = args.np

    if args.port:
        PORT = args.port

    match args.operation:
        case "log":
            subprocess.run(f"tail -f {LOGFILE}", shell=True, executable="/bin/bash", check=True)

        case "pid":
            try:
                subprocess.run(
                    f"pgrep -fo '{filepath} --host {HOST} --port {PORT}'",
                    shell=True,
                    executable="/bin/bash",
                    check=True,
                )
            except Exception:  # noqa: BLE001
                print("No such process")

        case "start":
            with open(LOGFILE, "w") as logfile:
                subprocess.run(
                    f"mpirun -n {NUM_PROCESSES} {filepath} --host {HOST} --port {PORT}",
                    shell=True,
                    executable="/bin/bash",
                    check=True,
                    stdout=logfile,
                )

        case "stop":
            try:
                subprocess.run(
                    f"pgrep -fo '{filepath} --host {HOST} --port {PORT}' | xargs kill",
                    shell=True,
                    executable="/bin/bash",
                    check=True,
                )
                print(f"NEST Server MPI running at http://{HOST}:{PORT} has stopped.")
            except Exception:  # noqa: BLE001
                print(f"NEST Server MPI is not running at http://{HOST}:{PORT}.")

        case "version":
            print(__version__)
