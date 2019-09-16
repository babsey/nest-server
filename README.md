# NEST Server

**A server with REST API and scripts for [NEST simulator](http://www.nest-simulator.org/)**

![nest-logo](http://www.nest-simulator.org/wp-content/uploads/2015/03/nest_logo.png)

### Introduction

NEST Server starts a server interacting with NEST Simulator.
It can be installed on a local machine, on a remote machine (e.g. server, cloud, cluster computer, supercomputer)
or in a session management (e.g. Docker, Singularity).

### Setup

To install NEST Server:
```
pip3 install nest-server
```

### Usage

To start NEST Server in terminal:
```
nest-server start [-h 127.0.0.1 -p 5000]
```

Alternatively, to start NEST Server in Python interface (e.g. IPython, Jupyter):
Note: Flask 0.12.4 is working with this.
```
from nest_server import app
app.run(host='127.0.0.1', port=5000)
```

### License [MIT](LICENSE)
