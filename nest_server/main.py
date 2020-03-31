import os
import optparse
import datetime
import inspect

import flask
from flask import json, Flask, request, jsonify
from flask_cors import CORS, cross_origin

import nest
import numpy as np

from .api.initializer import init_data, get_arguments
from .api.client import api_client
from .api.capture import Capturing
from . import scripts

from . import __version__


app = Flask(__name__)
CORS(app)

nest_calls = dir(nest)
nest_calls = list(filter(lambda x: not x.startswith('_'), nest_calls))
nest_calls.sort()


# --------------------------
# General request
# --------------------------

@app.route('/', methods=['GET'])
def index():
  data = init_data(request)
  data['response'] = {
      'server': {
          'version': __version__,
          'git': {
              'ref': 'http://www.github.com/babsey/nest-server',
              'tag': 'v' + '.'.join(__version__.split('.')[:-1])
          }
      },
      'simulator': {
          'version': nest.version(),
      },
      'status': 'ok'
  }
  return jsonify(data)


# --------------------------
# exec
# --------------------------

@app.route('/exec', methods=['GET', 'POST'])
@cross_origin()
def nest_exec():
  data = init_data(request)
  args, kwargs = get_arguments(request, data)
  with Capturing() as stdout:
    try:
      source = kwargs.get('source', '')
      globals = {'__builtins__': None}
      locals = {
        'list': list,
        'nest': nest,
        'np': np,
        'print': print,
        'set': set,
      }
      exec(source, globals, locals)
      if 'return' in kwargs:
        if isinstance(kwargs['return'], list):
          response_data = {}
          for variable in kwargs['return']:
            response_data[variable] = locals.get(variable, None)
        else:
          response_data = locals.get(kwargs['return'], None)
        response_serialized = nest.hl_api.serializable(response_data)
        response_json = json.dumps(response_serialized)
        data['response']['data'] = response_serialized
      data['response']['status'] = 'ok'
    except nest.kernel.NESTError as e:
      print('NESTError:', e)
      data['response'] = {
          'data': None,
          'error': {
              'name': getattr(e, 'errorname'),
              'message': getattr(e, 'errormessage').split(':')[-1]
          },
          'status': 'error'
      }
    except Exception as e:
      print(e)
      data['response'] = {
          'data': None,
          'error': {
              'name': 'Error',
              'message': str(e)
          },
          'status': 'error'
      }
  data['response']['stdout'] = '\n'.join(stdout)
  return jsonify(data)


# --------------------------
# RESTful API
# --------------------------

@app.route('/api/nest', methods=['GET'])
@cross_origin()
def router_nest():
  data = init_data(request)
  args, kwargs = get_arguments(request, data)
  api_client(request, call, data, *args, **kwargs)
  data['response']['status'] = 'ok'
  return jsonify(**data)


@app.route('/api/nest/<call>', methods=['GET', 'POST'])
@cross_origin()
def router_nest_call(call):
  data = init_data(request, call)
  args, kwargs = get_arguments(request, data)
  if call in nest_calls:
    call = getattr(nest, call)
    api_client(request, call, data, *args, **kwargs)
    data['response']['status'] = 'ok'
  else:
    data['response'] = {
        'error': 'The request cannot be called in NEST.',
        'status': 'error'
    }

  data_json = json.dumps(data)
  data_json = data_json.replace('Infinity', '1e+9999')
  response = app.response_class(
      response=data_json,
      status=200,
      mimetype='application/json'
  )
  return response


# --------------------------
# Scripts
# --------------------------

@app.route('/script/<filename>/<call>', methods=['POST', 'OPTIONS'])
@cross_origin()
def script(filename, call):
  data = init_data(request, call)
  try:
    script = getattr(scripts, filename)
    func = getattr(script, call)
    data['response'] = func(request.get_json())
    data['response']['status'] = 'ok'
  except nest.kernel.NESTError as e:
    print('NESTError:', e)
    data['response'] = {
        'error': {
            'name': getattr(e, 'errorname'),
            'message': getattr(e, 'errormessage').split(':')[-1]
        },
        'status': 'error'
    }
  except Exception as e:
    print(e)
    data['response'] = {
        'error': {
            'name': 'Error',
            'message': str(e)
        },
        'status': 'error'
    }
  return jsonify(data)


@app.route('/source', methods=['GET'])
@cross_origin()
def inspect_files():
  data = init_data(request)
  try:
    source = inspect.getsource(scripts)
    data['response'] = {
        'source': source,
        'status': 'ok'
    }
  except Exception as e:
    print(e)
    data['response'] = {
        'error': {
            'name': 'Error',
            'message': str(e)
        },
        'status': 'error'
    }
  return jsonify(data)


@app.route('/source/<filename>', methods=['GET'])
@cross_origin()
def inspect_script(filename):
  data = init_data(request)
  data['request']['filename'] = filename
  try:
    script = getattr(scripts, filename)
    source = inspect.getsource(script)
    data['response'] = {
        'source': source,
        'status': 'ok'
    }
  except Exception as e:
    print(e)
    data['response'] = {
        'error': {
            'name': 'Error',
            'message': str(e)
        },
        'status': 'error'
    }
  return jsonify(data)


@app.route('/source/<filename>/<call>', methods=['GET'])
@cross_origin()
def inspect_func(filename, call):
  data = init_data(request, call)
  args, kwargs = get_arguments(request, data)
  data['request']['filename'] = filename
  try:
    script = getattr(scripts, filename)
    func = getattr(script, call)
    source = inspect.getsource(func)
    data['response'] = {
        'source': source,
        'status': 'ok'
    }
  except Exception as e:
    print(e)
    data['response'] = {
        'error': {
            'name': 'Error',
            'message': str(e)
        },
        'status': 'error'
    }
  return jsonify(data)


if __name__ == "__main__":
  parser = optparse.OptionParser("usage: python main.py [options]")
  parser.add_option("-H", "--host", dest="hostname",
                    default="127.0.0.1", type="string",
                    help="specify hostname to run on")
  parser.add_option("-p", "--port", dest="port", default=5000,
                    type="int", help="port to run on")
  (options, args) = parser.parse_args()
  app.run(host=options.hostname, port=options.port)
