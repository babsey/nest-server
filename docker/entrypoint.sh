#!/bin/bash

# NEST environment
source /opt/nest/bin/nest_vars.sh

# start NEST Server
nest-server start -h 0.0.0.0 -u nest
