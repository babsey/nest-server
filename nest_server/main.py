import os
import optparse
import datetime

import flask
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

import nest
import nest.topology as topo

from .api import initializer as api_init
from .api.client import api_client
from . import scripts

from .environments import VERSION


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
        'server': {
            'version': VERSION,
            'git': {
                'ref': 'http://www.github.com/babsey/nest-server',
                'tag': 'v' + '.'.join(VERSION.split('.')[:-1])
            }
        },
        'simulator': {
            'env': dict(filter(lambda item: 'NEST_' in item[0], os.environ.items())),
            'version': nest.version().split(' ')[1],
        },
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
# Scripts
# --------------------------

@app.route('/script/<filename>/<call>', methods=['POST', 'OPTIONS'])
@cross_origin()
def script(filename, call):
    # print(request.get_json())
    try:
        script = scripts.__dict__[filename]
        response = script.__dict__[call](request.get_json())
    except Exception as e:
        print(e.__dict__)
        error = {
            'name': e.__dict__['errorname'],
            'message': e.__dict__['errormessage'].split(':')[-1]
        }
        response = {'error': error}
    return jsonify(response)


if __name__ == "__main__":
    parser = optparse.OptionParser("usage: python main.py [options]")
    parser.add_option("-H", "--host", dest="hostname",
                      default="127.0.0.1", type="string",
                      help="specify hostname to run on")
    parser.add_option("-p", "--port", dest="port", default=5000,
                      type="int", help="port to run on")
    (options, args) = parser.parse_args()
    app.run(host=options.hostname, port=options.port)
