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

# worker.py
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

import os

import nest

from nest_server.kernel import do_call, do_exec, nestify
from nest_server.logger import logger, mpi_worker_log
from nest_server.main import create_app
from nest_server.mpi.state import set_mpi_comm

HOST = os.getenv("NEST_SERVER_HOST", "127.0.0.1")
PORT = int(os.getenv("NEST_SERVER_PORT", "52425"))

comm = MPI.COMM_WORLD.Clone()
rank = comm.Get_rank()

if rank == 0:
    logger.info("==> Starting NEST Server Master on rank 0")
    set_mpi_comm(comm)

    app = create_app()
    # NEST crashes with a segmentation fault if the number of threads is changed
    # from the outside. Calling run() with threaded=False prevents Flask from
    # performing such changes.
    app.run(host=opt.get("--host", HOST), port=opt.get("--port", PORT), threaded=False)

else:
    logger.info(f"==> Starting NEST Server Worker on rank {rank}")
    set_mpi_comm(comm)

    while True:
        mpi_worker_log(rank, "spinwait", "waiting for call bcast")
        call_name = comm.bcast(None, root=0)

        mpi_worker_log(rank, call_name, "received call bcast, waiting for data bcast")
        data = comm.bcast(None, root=0)

        mpi_worker_log(rank, call_name, f"received data bcast, data={data}")
        args, kwargs = data

        # mpi_worker_log("spinwait", "waiting for bcast")
        # call_name, args, kwargs = comm.bcast(None, root=0)
        # mpi_worker_log(call_name, f"received bcast, data={(args, kwargs)}")

        if call_name == "exec":
            response = do_exec(args, kwargs)
        else:
            call, args, kwargs = nestify(call_name, args, kwargs)
            mpi_worker_log(rank, call_name, f"local call, args={args}, kwargs={kwargs}")

            # The following exception handler is useful if an error
            # occurs simulataneously on all processes. If only a
            # subset of processes raises an exception, a deadlock due
            # to mismatching MPI communication calls is inevitable on
            # the next call.
            # try:
            response = do_call(call, args, kwargs)

            # except Exception as e:
            #     logger.error(f"Failed to execute call: {e}")
            #     response = None
            #     continue

        # mpi_worker_log(rank, call_name, f"local call - response={response}")
        response = nest.serialize_data(response)

        mpi_worker_log(rank, call_name, f"sending response gather, data={response}")
        comm.gather(response, root=0)
