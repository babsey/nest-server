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

import nest

from nest_server.logger import mpi_master_log
from nest_server.mpi.helpers import combine
from nest_server.mpi.state import mpi_comm


def mpi_receive_response_gather(call_name: str, master_response):
    if mpi_comm is None:
        return

    mpi_master_log(call_name, "waiting for response gather")
    response = mpi_comm.gather(nest.serialize_data(master_response), root=0)
    mpi_master_log(call_name, f"received response gather, data={response}")

    return combine(response)


def mpi_send_bcast(call_name: str, args: list, kwargs: dict) -> None:
    if mpi_comm is None:
        return

    assert mpi_comm.Get_rank() == 0

    mpi_master_log(call_name, "sending call bcast")
    mpi_comm.bcast(call_name, root=0)

    data = (args, kwargs)
    mpi_master_log(call_name, f"sending data bcast, data={data}")
    mpi_comm.bcast(data, root=0)

    # mpi_master_log(call_name, "sending bcast")
    # mpi_comm.bcast((call_name, args, kwargs), root=0)
