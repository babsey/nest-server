import nest
import os
import shutil
import subprocess
import time

from pynestml.frontend.pynestml_frontend import to_nest, install_nest
from . import converter

__all__ = [
    'install',
]

root_path = '/tmp'
models_path = os.path.join(root_path, 'nest-models')
build_path = os.path.join(root_path, 'nest-models-build')
nest_install_dir = '/home/spreizer/opt/nest-3'


def bashCommand(command):
  process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
  output, error = process.communicate()
  return {'output': output, 'error': error}


def removeFiles(folder):
  for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
      if os.path.isfile(file_path) or os.path.islink(file_path):
        os.unlink(file_path)
      elif os.path.isdir(file_path):
        shutil.rmtree(file_path)
    except Exception as e:
      print('Failed to delete %s. Reason: %s' % (file_path, e))


def deleteModels():
  removeFiles(models_path)


def deleteModelsBuild():
  removeFiles(build_path)


def createModelDir():
  return bashCommand('mkdir -p %s' % models_path)


def install(data):
  deleteModels()
  deleteModelsBuild()

  for model in data['models']:
    # save nestml models to files
    print(model['neuron'])
    filename = os.path.join(models_path, model['neuron'])
    nestml = converter.json_to_nestml_format(model)
    converter.write_file(filename, nestml)

  to_nest(models_path, build_path, module_name=data['module_name']+'module')
  install_nest(build_path, nest_install_dir)

  return {'data': data}
