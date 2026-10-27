# NEST Server -- A Python-based API server for the NEST Simulator

This repository contains a REST-based interface to talk to the [NEST Simulator](http://nest-simulator.org).

### Quick start

Install NEST Server with pip

```
pip install nest-server
```

Start NEST Server

```
nest-server start
```

### Command options

Entering `nest-server start --help` shows the help message such as:

```
Usage: nest-server start [OPTIONS]

Options:
-d, --daemon           Run NEST Server in the background, i.e. daemonize the
                        server process
-h, --host TEXT        Use hostname/IP address for the server [default:
                        127.0.0.1]
-p, --port INTEGER     Use port for opening the socket [default: 52425]
-o, --outputs          Print NEST outputs to the console
-t, --timeout INTEGER  Workers silent for more than this many seconds are
                        killed and restarted [default: 30]
-w, --workers INTEGER  The number of worker processes for handling requests
                        [default: 1]
--help                 Show this message and exit.
```

### Default environment variables

```
NEST_SERVER_DAEMON=false
NEST_SERVER_HOST="127.0.0.1"
NEST_SERVER_LOGFILE="/tmp/nest-server.log"
NEST_SERVER_PORT=52425
NEST_SERVER_STDOUT=false
NEST_SERVER_TIMEOUT=30
NEST_SERVER_WORKERS=1

NEST_SERVER_ACCESS_TOKEN=""
NEST_SERVER_DISABLE_AUTH=false
NEST_SERVER_DISABLE_RESTRICTION=false
NEST_SERVER_CORS_ORIGINS="http://localhost:*,http://127.0.0.1:*"
NEST_SERVER_ENABLE_EXEC_CALL=false
NEST_SERVER_MODULES="import nest"
```

### Development mode

We recommend to use virtual environment, e.g. with `uv`:

Install nest-client as an editable package

```
uv pip install -e .
```

Run nest-server in an virtual environment

```
uv run nest-server start
```

See more commands in `Makefile`.


### References

- [Documentation](https://nest-simulator.readthedocs.io/en/latest/interface_nest/nest_server.html)
- [NEST Simulator](http://nest-simulator.org) via its REST-based interface
