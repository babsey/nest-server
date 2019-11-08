import os
import optparse
import datetime
import inspect

import flask
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

import nest
import nest.topology as topo

from .api import initializer as api_init
from .api.client import api_client
from . import scripts

from . import __version__


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
          'version': __version__,
          'git': {
              'ref': 'http://www.github.com/babsey/nest-server',
              'tag': 'v' + '.'.join(__version__.split('.')[:-1])
          }
      },
      'simulator': {
          'version': nest.version().split('-')[1],
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
    call = getattr(nest, call)
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
    call = getattr(topo, call)
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
    script = getattr(scripts, filename)
    func = getattr(script, call)
    response = func(request.get_json())
  except nest.kernel.NESTError as e:
    print(e)
    error = {
        'name': getattr(e, 'errorname'),
        'message': getattr(e, 'errormessage').split(':')[-1]
    }
    response = {'error': error}
  except Exception as e:
    print(e)
    error = {
        'name': 'Error',
        'message': str(e)
    }
    response = {'error': error}
  return jsonify(response)


@app.route('/source', methods=['GET'])
@cross_origin()
def inspect_files():
  try:
    source = inspect.getsource(scripts)
    response = {
        'source': source,
    }
  except Exception as e:
    print(e)
    error = {
        'name': 'Error',
        'message': str(e)
    }
    response = {'error': error}
  return jsonify(response)


@app.route('/source/<filename>', methods=['GET'])
@cross_origin()
def inspect_script(filename):
  try:
    script = getattr(scripts, filename)
    source = inspect.getsource(script)
    response = {
        'source': source,
    }
  except Exception as e:
    print(e)
    error = {
        'name': 'Error',
        'message': str(e)
    }
    response = {'error': error}
  return jsonify(response)


@app.route('/source/<filename>/<call>', methods=['GET'])
@cross_origin()
def inspect_func(filename, call):
  try:
    script = getattr(scripts, filename)
    func = getattr(script, call)
    source = inspect.getsource(func)
    response = {
        'source': source,
    }
  except Exception as e:
    print(e)
    error = {
        'name': 'Error',
        'message': str(e)
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
