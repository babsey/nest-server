# state.py
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

try:
    from mpi4py.MPI import Comm
except ImportError:
    Comm = object

mpi_comm = None


def get_mpi_comm() -> Comm | None:
    return mpi_comm


def has_mpi_comm() -> bool:
    return mpi_comm is not None


def set_mpi_comm(comm: Comm) -> None:
    global mpi_comm
    mpi_comm = comm
