import importlib
import io
import nest
import numpy
import os
import sys


__all__ = [
    'Capturing',
    'clean_code',
    'get_globals',
]

MODULES = os.environ.get('NEST_SERVER_MODULES', 'nest,numpy as np').split(',')


class Capturing(list):
  """ Monitor stdout contents i.e. print.
  """

  def __enter__(self):
    self._stdout = sys.stdout
    sys.stdout = self._stringio = io.StringIO()
    return self

  def __exit__(self, *args):
    self.extend(self._stringio.getvalue().splitlines())
    del self._stringio    # free up some memory
    sys.stdout = self._stdout


def clean_code(source):
  codes = source.split('\n')
  code_cleaned = [code if not (code.startswith('import') or code.startswith('from')) else '' for code in codes]
  return '\n'.join(code_cleaned)


def get_globals():
  """ Get globals for exec function.
  """
  copied_globals = globals().copy()

  # Add modules to copied globals
  modules = dict()
  for module in MODULES:
    mm = module.split(' as ')
    modules[mm[-1]] = importlib.import_module(mm[0])
  copied_globals.update(modules)

  return copied_globals
