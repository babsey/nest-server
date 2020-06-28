import inspect
import io
import os
import optparse
from RestrictedPython import compile_restricted, safe_globals
import sys

import flask
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

import nest
import nest.topology as topo

from werkzeug.exceptions import abort
from werkzeug.wrappers import Response

from .api.initializer import get_arguments
from .api.client import api_client
from .exec.helpers import clean_code, get_modules
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


# -------------------------------
# Execute Python script (caution)
# -------------------------------

class Capturing(list):
  """ Monitor stdout contents i.e. print.
  """

  def __enter__(self):
    self._stdout = sys.stdout
    sys.stdout = self._stringio = io.StringIO()
    return self

  def __exit__(self, *args, **kwargs):
    self.extend(self._stringio.getvalue().splitlines())
    del self._stringio    # free up some memory
    sys.stdout = self._stdout

@app.route('/exec', methods=['GET', 'POST'])
@cross_origin()
def route_exec():
  """ Route to execute script in Python.
  """
  try:
    args, kwargs = get_arguments(request)
    source_code = kwargs.get('source', '')
    source_cleaned = clean_code(source_code)
    byte_code = compile_restricted(source_cleaned, '<inline>', 'exec')
    locals = get_modules(source_code)
    with Capturing() as stdout:
      exec(byte_code, safe_globals, locals)
    response = {
        'stdout': '\n'.join(stdout),
    }
    if 'return' in kwargs:
      if isinstance(kwargs['return'], list):
        data = {}
        for variable in kwargs['return']:
          data[variable] = locals.get(variable, None)
      else:
        data = locals.get(kwargs['return'], None)
      response['data'] = nest.hl_api.serializable(data)
    return jsonify(response)
  except nest.kernel.NESTError as e:
      abort(Response(getattr(e, 'errormessage'), 400))
  except Exception as e:
      abort(Response(str(e), 400))


# --------------------------
# RESTful API
# --------------------------

@app.route('/api/nest', methods=['GET'])
@app.route('/api/nest/', methods=['GET'])
@cross_origin()
def router_nest():
  return jsonify(nest_calls)


@app.route('/api/nest/<call>', methods=['GET', 'POST'])
@cross_origin()
def router_nest_call(call):
  args, kwargs = get_arguments(request)
  call = getattr(nest, call)
  response = api_client(call, args, kwargs)
  return jsonify(response)


@app.route('/api/topo', methods=['GET'])
@app.route('/api/topo/', methods=['GET'])
@app.route('/api/nest_topology', methods=['GET'])
@app.route('/api/nest_topology/', methods=['GET'])
@cross_origin()
def router_topo():
  return jsonify(topo_calls)


@app.route('/api/topo/<call>', methods=['GET', 'POST'])
@app.route('/api/nest_topology/<call>', methods=['GET', 'POST'])
@cross_origin()
def router_topo_call(call):
  args, kwargs = get_arguments(request)
  call = getattr(topo, call)
  response = api_client(call, args, kwargs)
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
    return jsonify(response)
  except nest.kernel.NESTError as e:
    abort(Response(getattr(e, 'errormessage').split(':')[-1], 400))
  except Exception as e:
    abort(Response(str(e), 400))


@app.route('/source', methods=['GET'])
@cross_origin()
def inspect_files():
  try:
    source = inspect.getsource(scripts)
    response = {
        'source': source,
    }
    return jsonify(response)
  except Exception as e:
    abort(Response(str(e), 400))


@app.route('/source/<filename>', methods=['GET'])
@cross_origin()
def inspect_script(filename):
  try:
    script = getattr(scripts, filename)
    source = inspect.getsource(script)
    response = {
        'source': source,
    }
    return jsonify(response)
  except Exception as e:
    abort(Response(str(e), 400))


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
    return jsonify(response)
  except Exception as e:
    abort(Response(str(e), 400))


if __name__ == "__main__":
  parser = optparse.OptionParser("usage: python main.py [options]")
  parser.add_option("-H", "--host", dest="hostname",
                    default="127.0.0.1", type="string",
                    help="specify hostname to run on")
  parser.add_option("-p", "--port", dest="port", default=5000,
                    type="int", help="port to run on")
  (options, args) = parser.parse_args()
  app.run(host=options.hostname, port=options.port)
