# logger.py
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

import logging
import os
import time

from flask.logging import default_handler

# This ensures that the logging information shows up in the console running the server,
# even when Flask's event loop is running.
logger = logging.getLogger()
logger.addHandler(default_handler)
logger.setLevel(os.getenv("NEST_SERVER_LOGGER_LEVEL", "INFO"))


def log(call_name: str, msg: str) -> None:
    msg = f"({call_name}): {msg}"
    logger.debug(msg)


def mpi_master_log(call_name: str, msg: str) -> None:
    msg = f"==> MASTER 0/{time.time():.7f} ({call_name}): {msg}"
    logger.debug(msg)


def mpi_worker_log(rank: int, call_name: str, msg: str) -> None:
    msg = f"==> WORKER {rank}/{time.time():.7f} ({call_name}): {msg}"
    logger.debug(msg)
