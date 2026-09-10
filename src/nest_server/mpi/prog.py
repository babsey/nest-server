#!/usr/bin/env python3

"""A MPI Server for the NEST Simulator.

Usage:
  prog --help
  mpirun -n N prog [--host HOST] [--port PORT]

Options:
  -h --help     display usage information and exit
  --host HOST   use hostname/IP address HOST for server [default: 127.0.0.1]
  --port PORT   use port PORT for opening the socket [default: 52425]
"""

# prog.py
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

from docopt import docopt
from mpi4py import MPI

if __name__ == "__main__":
    opt = docopt(__doc__)

import logging
import os
import time

import nest
from flask.logging import default_handler

import nest_server.main as nest_server

logger = logging.getLogger(__name__)
logger.addHandler(default_handler)
logger.setLevel(os.getenv("NEST_SERVER_MPI_LOGGER_LEVEL", "INFO"))

HOST = os.getenv("NEST_SERVER_HOST", "127.0.0.1")
PORT = os.getenv("NEST_SERVER_PORT", "52425")

comm = MPI.COMM_WORLD.Clone()
rank = comm.Get_rank()


def log(call_name, msg):
    msg = f"==> WORKER {rank}/{time.time():.7f} ({call_name}): {msg}"
    logger.debug(msg)


if rank == 0:
    logger.info("==> Starting NEST Server Master on rank 0")
    nest_server.set_mpi_comm(comm)
    nest_server.run_mpi_app(host=opt.get("--host", HOST), port=opt.get("--port", PORT))

else:
    logger.info(f"==> Starting NEST Server Worker on rank {rank}")
    nest_server.set_mpi_comm(comm)

    while True:
        log("spinwait", "waiting for call bcast")
        call_name = comm.bcast(None, root=0)

        log(call_name, "received call bcast, waiting for data bcast")
        data = comm.bcast(None, root=0)

        log(call_name, f"received data bcast, data={data}")
        args, kwargs = data

        # log("spinwait", "waiting for bcast")
        # call_name, args, kwargs = comm.bcast(None, root=0)
        # log(call_name, f"received bcast, data={(args, kwargs)}")

        if call_name == "exec":
            response = nest_server.do_exec(args, kwargs)
        else:
            call, args, kwargs = nest_server.nestify(call_name, args, kwargs)
            log(call_name, f"local call, args={args}, kwargs={kwargs}")

            # The following exception handler is useful if an error
            # occurs simulataneously on all processes. If only a
            # subset of processes raises an exception, a deadlock due
            # to mismatching MPI communication calls is inevitable on
            # the next call.
            try:
                if call_name == "GetStatus":
                    nodes_or_conns = kwargs.get("nodes_or_conns", args[0])

                    keys = kwargs.get("keys", None)
                    if len(args) >= 2:
                        keys = args[1]

                    response = nodes_or_conns.get(keys) if keys else nodes_or_conns.get()

                elif call_name == "SetStatus":
                    nodes_or_conns = kwargs.get("nodes_or_conns", args[0])

                    params = kwargs.get("params", {})
                    if len(args) >= 2:
                        params = args[1]

                    response = nodes_or_conns.set(params)

                else:
                    response = call(*args, **kwargs)

            except Exception as e:  # noqa: BLE001
                logger.error(f"Failed to execute call: {e}")
                response = None
                continue

        log(call_name, f"local call - response={response}")
        response = nest.serialize_data(response)

        log(call_name, f"sending response gather, data={response}")
        comm.gather(response, root=0)
