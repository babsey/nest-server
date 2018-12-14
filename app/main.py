#!/usr/bin/env python

import os
import optparse

import flask
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

import nest
import nest.topology as topo

try:
    from .rest_api import initializer as api_init
    from .rest_api.client import api_client
    from .simulation_scripts import simple_network as sim_client
except Exception: #ImportError
    from rest_api import initializer as api_init
    from rest_api.client import api_client
    from simulation_scripts import simple_network as sim_client

VERSION = "1.0.0"

app = Flask(__name__)
CORS(app)

nest_calls = dir(nest)
nest_calls = list(filter(lambda x: not x.startswith('_'), nest_calls))
nest_calls.sort()

topo_calls = dir(topo)
topo_calls = list(filter(lambda x: not x.startswith('_'), topo_calls))
topo_calls.sort()


# --------------------------
# General request
# --------------------------

@app.route('/', methods=['GET'])
def index():
    response = {
        'name': 'NEST server',
        'nest': {
            'env': dict(filter(lambda item: 'NEST' in item[0], os.environ.items())),
            'version': nest.version().split(' ')[1],
        },
        'ref': 'http://www.github.com/babsey/nest-server',
        'version': VERSION
    }
    return jsonify(response)

# --------------------------
# RESTful API
# --------------------------

@app.route('/api/nest', methods=['GET'])
@cross_origin()
def router_nest():
    data, args, kwargs = api_init.data_and_args(request)
    response = api_client(request, nest_calls, data)
    return jsonify(response)

@app.route('/api/nest/<call>', methods=['GET', 'POST'])
@cross_origin()
def router_nest_call(call):
    data, args, kwargs = api_init.data_and_args(request, call)
    if call in nest_calls:
        call = nest.__dict__[call]
        response = api_client(request, call, data, *args, **kwargs)
    else:
        data['response']['msg'] = 'The request cannot be called in NEST.'
        data['response']['status'] = 'error'
        response = data
    return jsonify(response)


@app.route('/api/topo', methods=['GET'])
@app.route('/api/nest_topology', methods=['GET'])
@cross_origin()
def router_topo():
    data, args, kwargs = api_init.data_and_args(request)
    response = api_client(request, topo_calls, data)
    return jsonify(response)


@app.route('/api/topo/<call>', methods=['GET', 'POST'])
@app.route('/api/nest_topology/<call>', methods=['GET', 'POST'])
@cross_origin()
def router_topo_call(call):
    data, args, kwargs = api_init.data_and_args(request, call)
    if call in topo_calls:
        call = topo.__dict__[call]
        response = api_client(request, call, data, *args, **kwargs)
    else:
        data['response']['msg'] = 'The request cannot be called in NEST Topology.'
        data['response']['status'] = 'error'
        response = data
    return jsonify(response)




# --------------------------
# NEST simulation request
# --------------------------

def simulate(simulation, data):
    try:
        response = {'data': simulation(data)}
    except Exception as e:
        response = {'error': str(e)}
    return jsonify(response)


@app.route('/simulate', methods=['POST', 'OPTIONS'])
@cross_origin()
def network_simulate():
    # return simulate(sim.run, request.get_json())
    return simulate(sim_client.simulate, request.get_json())


# @app.route('/network/resume', methods=['POST'])
# def network_resume():
#     return simulate(sim.resume, request.get_json())


if __name__ == "__main__":
    parser = optparse.OptionParser("usage: python main.py [options]")
    parser.add_option("-H", "--host", dest="hostname",
                      default="127.0.0.1", type="string",
                      help="specify hostname to run on")
    parser.add_option("-p", "--port", dest="port", default=5000,
                      type="int", help="port to run on")
    (options, args) = parser.parse_args()
    app.run(host=options.hostname, port=options.port)
