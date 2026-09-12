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


def master_receive_gather(master_log, comm, call_name: str, response):
    if comm is None:
        return

    # Check if rank is master
    assert comm.Get_rank() == 0

    master_log(call_name, "waiting for response gather")
    master_response = comm.gather(response, root=0)
    master_log(call_name, f"received response gather, data={master_response}")

    return master_response


def master_send_bcast(master_log, comm, call_name: str, args: list, kwargs: dict) -> None:
    if comm is None:
        return

    # Check if rank is master
    assert comm.Get_rank() == 0

    master_log(call_name, "sending call bcast")
    comm.bcast(call_name, root=0)

    data = (args, kwargs)
    master_log(call_name, f"sending data bcast, data={data}")
    comm.bcast(data, root=0)

    # master_log(call_name, "sending bcast")
    # comm.bcast((call_name, args, kwargs), root=0)


def worker_receive_bcast(worker_log, comm):
    if comm is None:
        return

    # Check if rank is not master
    assert comm.Get_rank() > 0

    worker_log("spinwait", "waiting for call bcast")
    call_name = comm.bcast(None, root=0)

    worker_log(call_name, "received call bcast, waiting for data bcast")
    data = comm.bcast(None, root=0)

    worker_log(call_name, f"received data bcast, data={data}")
    args, kwargs = data

    # worker_log("spinwait", "waiting for bcast")
    # call_name, args, kwargs = comm.bcast(None, root=0)
    # worker_log(call_name, f"received bcast, data={(args, kwargs)}")

    return call_name, args, kwargs


def worker_send_gather(worker_log, comm, call_name: str, response) -> None:
    if comm is None:
        return

    # Check if rank is not master
    assert comm.Get_rank() > 0

    worker_log(call_name, f"sending response gather, data={response}")
    comm.gather(response, root=0)
