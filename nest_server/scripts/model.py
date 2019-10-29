import nest
import os
import subprocess

from pynestml.frontend.pynestml_frontend import to_nest, install_nest
from . import converter

__all__ = [
    'install',
]

root_path = '/tmp'
models_path = os.path.join(root_path, 'models')
build_path = os.path.join(root_path, 'models-build')
nest_install_dir = '/home/spreizer/opt/nest-simulator'


def bashCommand(command):
  process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
  output, error = process.communicate()
  return {'output': output, 'error': error}


def deleteModels():
  return bashCommand('rm -f %s/*' % models_path)


def createModelDir():
  return bashCommand('mkdir -p %s' % models_path)


def install(data):

  # save nestml models to files
  filename = os.path.join(models_path, data['neuron'])
  data_nestml_format = converter.json_to_nestml_format(data)
  converter.write_file(filename, data_nestml_format)

  to_nest(models_path, build_path, module_name='nestmlmodule')
  install_nest(build_path, nest_install_dir)

  return {'data': data}


createModelDir()
