import importlib
import io
import nest
import numpy
import sys


__all__ = [
    'Capturing',
    'clean_code',
    'get_modules',
]

# Blacklist of modules according to Bandit (https://bandit.readthedocs.io).
_blacklist_modules = [
    'commands',
    'dsa',
    'jinja2',
    'mako',
    'os',
    'paramiko',
    'popen2',
    'requests',
    'rsa',
    'socket',
    'ssl',
    'subprocess',
    'sys',
]


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


def clean_code(source):
  codes = source.split('\n')
  code_cleaned = [code  if not (code.startswith('import') or code.startswith('from')) else '' for code in codes]
  return '\n'.join(code_cleaned)


def get_modules(source):
  modules = {'nest': nest}
  for line in source.split('\n'):
    code = line.split(' ')
    if code[0] == 'import' and code[1] not in _blacklist_modules:
      modules.update({code[-1]: importlib.import_module(code[1])})
  return modules
