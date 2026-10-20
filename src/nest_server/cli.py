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

import os
import subprocess

import click
from gunicorn.app.wsgiapp import WSGIApplication

from nest_server import __version__
from nest_server.helpers import str2bool

DAEMON = str2bool(os.getenv("NEST_SERVER_DAEMON"))
HOST = os.getenv("NEST_SERVER_HOST", "127.0.0.1")
LOGFILE = os.getenv("NEST_SERVER_LOGFILE", "/tmp/nest-server.log")
PIDFILE = os.getenv("NEST_SERVER_PIDFILE", "/tmp/nest-server.pid")
PORT = int(os.getenv("NEST_SERVER_PORT", "52425"))
STDOUT = str2bool(os.getenv("NEST_SERVER_STDOUT"))
TIMEOUT = int(os.getenv("NEST_SERVER_TIMEOUT", "30"))
WORKERS = int(os.getenv("NEST_SERVER_WORKERS", "1"))

app = "nest_server.main:create_app()"
cli = "nest-server"


class StandaloneApplication(WSGIApplication):
    def __init__(self, app_uri, options=None):
        self.options = options or {}
        self.app_uri = app_uri
        super().__init__()

    def load_config(self) -> None:
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)


@click.group()
def main():
    pass


@main.command()
def log():
    subprocess.run(f"tail -f {LOGFILE}", shell=True, executable="/bin/bash", check=True)


@main.command()
def pid():
    try:
        subprocess.run(f"pgrep -fo '{cli} start'", shell=True, executable="/bin/bash", check=True)
    except Exception:  # noqa: BLE001
        click.echo("No such process")


@main.command()
@click.option(
    "--daemon",
    "-d",
    is_flag=True,
    default=DAEMON,
    help="run NEST Server in the background, i.e. daemonize the server process",
)
@click.option("--host", "-h", default=HOST, help=f"use hostname/IP address for the server [default: {HOST}]")
@click.option("--port", "-p", default=PORT, help=f"use port for opening the socket [default: {PORT}]")
@click.option("--outputs", "-o", is_flag=True, default=STDOUT, help="print NEST outputs to the console")
@click.option(
    "--timeout",
    "-t",
    default=TIMEOUT,
    help=f"workers silent for more than this many seconds are killed and restarted [default: {TIMEOUT}]",
)
@click.option(
    "--workers",
    "-w",
    default=WORKERS,
    help=f"the number of worker processes for handling requests [default: {WORKERS}]",
)
def start(daemon: bool, host: str, outputs: bool, port: int, timeout: int, workers: int):
    options = {
        "bind": f"{host}:{port}",
        "capture_output": not outputs,
        "daemon": daemon,
        "errorlog": LOGFILE,
        "pidfile": PIDFILE,
        "timeout": timeout,
        "workers": workers,
        # "worker_class": "uvicorn.workers.UvicornWorker",
    }

    msg = f"NEST Server is now running at http://{host}:{port}."
    click.echo(msg)
    click.echo("Use CTRL + C to stop this service.")
    click.echo(len(msg) * "-")

    StandaloneApplication(app, options).run()


@main.command()
@click.option("--host", "-h", default=HOST, help=f"use hostname/IP address for the server [default: {HOST}]")
@click.option("--port", "-p", default=PORT, help=f"use port for opening the socket [default: {PORT}]")
def stop(host: str, port: int):
    try:
        subprocess.run(f"pgrep -fo '{cli} start' | xargs kill", shell=True, executable="/bin/bash", check=True)
        click.echo(f"NEST Server running at http://{host}:{port} has stopped.")
    except Exception:  # noqa: BLE001
        click.echo(f"NEST Server is not running at http://{host}:{port}.")


@main.command()
def version():
    click.echo(__version__)


if __name__ == "__main__":
    main()
