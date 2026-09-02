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

filepath = Path(__file__).parent.resolve() / "main.py"


def main():
    global HOST, PORT, NUM_PROCESSES

    parser = argparse.ArgumentParser(description="A MPI server for the NEST Simulator", add_help=False)
    parser.add_argument(
        "operation",
        choices=[
            "start",
        ],
    )

    parser.add_argument(
        "-h", "--host", type=str, help="use hostname/IP address <HOST> for the server [default: 127.0.0.1]"
    )
    parser.add_argument("-n", "--n", type=int, help="number of processes to run [default: 1]")
    parser.add_argument("-p", "--port", type=int, help="use port <PORT> for opening the socket [default: 52425]")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.host:
        HOST = args.host

    if args.n:
        N = args.n

    if args.port:
        PORT = args.port

    if args.operation == "start":
        subprocess.run(
            f"mpirun -n {N} {filepath} --host={HOST} --port={PORT}",
            shell=True,
            executable="/bin/bash",
            check=True,
        )

    elif args.operation == "version":
        print(__version__)
