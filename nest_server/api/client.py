import inspect
import nest

from .serializer import serialize
from .decorator import get_or_error

__all__ = [
    'api_client',
]


@get_or_error
def api_client(request, call, data, *args, **kwargs):
  """ API Client to call function in NEST.
  """
  if callable(call):
    data['request']['call'] = call.__name__
    if str(kwargs.get('return_doc', 'false')) == 'true':
      response = call.__doc__
    elif str(kwargs.get('return_source', 'false')) == 'true':
      response = inspect.getsource(call)
    else:
      response = call(*args, **serialize(call.__name__, kwargs))
  else:
    data['request']['call'] = call
    response = call
  data['response']['data'] = nest.hl_api.serializable(response)
  return data
