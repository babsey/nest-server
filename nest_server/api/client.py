import inspect
import nest
import numpy as np

from .decorator import get_or_error

__all__ = [
    'api_client',
]


def serialize(call, args, kwargs):
  """ Serialize arguments with keywords for call functions in NEST.
  """
  if call.__name__.startswith('Set'):
    status = {}
    if call.__name__ == 'SetDefaults':
      status = nest.GetDefaults(kwargs['model'])
    elif call.__name__ == 'SetKernelStatus':
      status = nest.GetKernelStatus()
    elif call.__name__ == 'SetStructuralPlasticityStatus':
      status = nest.GetStructuralPlasticityStatus(kwargs['params'])
    elif call.__name__ == 'SetStatus':
      status = nest.GetStatus(kwargs['nodes'])
    for key, val in kwargs['params'].items():
      if key in status:
        kwargs['params'][key] = type(status[key])(val)
  return args, kwargs


@get_or_error
def api_client(call, args, kwargs):
  """ API Client to call function in NEST.
  """
  if callable(call):
    if 'inspect' in kwargs:
      response = {
          'data': getattr(inspect, kwargs['inspect'])(call)
      }
    else:
      args, kwargs = serialize(call, args, kwargs)
      response = call(*args, **kwargs)
  else:
    response = call
  serialized_response = nest.hl_api.serializable(response)

  if call == nest.GetDefaults:
    for (key, value) in serialized_response.items():
      if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
        serialized_response[key] = str(value)

  return serialized_response
