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
Entering ```nest-server``` without sub-command prints the documentation:

```
NEST Server
-----------
Usage: nest-server log|status|start|stop|restart [-d] [-h <HOST>] [-o] [-p <PORT>] [-t <TIMEOUT>] [-w <WORKERS>]

Commands:
  log         display the server output log
  status      display the status of all server instances
  start       start a server instance on <HOST>:<PORT>
  stop        stop a server instance on <HOST>:<PORT>
  restart     restart (i.e. stop and start) a server instance on <HOST>:<PORT>

Options:
  -d                 daemonize the server process
  -h <HOST>          use hostname/IP address <HOST> for the server [default: 127.0.0.1]
  -o                 print NEST outputs to the console
  -p <PORT>          use port <PORT> for opening the socket [default: 52425]
  -t <TIMEOUT>       workers silent for more than this many seconds are killed and restarted [default: 30]
  -w <WORKERS>       the number of worker processes for handling requests [default: 1]
```

### Default environment variables

```
# nest-server
NEST_SERVER_DAEMON=0
NEST_SERVER_HOST="127.0.0.1"
NEST_SERVER_LOGFILE="/tmp/nest-server.log"
NEST_SERVER_PORT=52425
NEST_SERVER_STDOUT=0
NEST_SERVER_TIMEOUT=30
NEST_SERVER_WORKERS=1

# main.py
NEST_SERVER_ACCESS_TOKEN=""
NEST_SERVER_DISABLE_AUTH=0
NEST_SERVER_DISABLE_RESTRICTED=0
NEST_SERVER_CORS_ORIGINS="http://localhost:*,http://127.0.0.1:*"
NEST_SERVER_ENABLE_EXEC_CALL=0
NEST_SERVER_MODULES="import nest"
```


### Development mode

We recommend to use virtual environment with ```uv```:

Install dependencies
```
uv pip install -r requirements.txt
```

Install nest-server as an editable package
```
uv pip install -e .
```

Run nest-server
```
uv run nest-server start
```