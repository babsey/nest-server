import inspect
import nest

from .decorator import get_or_error

__all__ = [
    'api_client',
]


def NodeCollection(kwargs):
  if 'nodes' in kwargs:
    kwargs['nodes'] = nest.NodeCollection(kwargs['nodes'])
  if 'source' in kwargs:
    kwargs['source'] = nest.NodeCollection(kwargs['source'])
  if 'target' in kwargs:
    kwargs['target'] = nest.NodeCollection(kwargs['target'])
  if 'pre' in kwargs:
    kwargs['pre'] = nest.NodeCollection(kwargs['pre'])
  if 'post' in kwargs:
    kwargs['post'] = nest.NodeCollection(kwargs['post'])
  return kwargs


@get_or_error
def api_client(request, call, data, *args, **kwargs):

  if callable(call):
    data['request']['call'] = call.__name__

    if str(kwargs.get('return_doc', 'false')) == 'true':
      response = call.__doc__
    elif str(kwargs.get('return_source', 'false')) == 'true':
      response = inspect.getsource(call)
    else:
      kwargs = NodeCollection(kwargs)
      if call.__name__ == 'SetKernelStatus':
        kernelStatus = nest.GetKernelStatus()
        for paramKey, paramVal in kwargs['params'].items():
          kwargs['params'][paramKey] = type(kernelStatus[paramKey])(paramVal)
      elif call.__name__ == 'SetStatus':
        status = nest.GetStatus(kwargs['nodes'])
        for paramKey, paramVal in kwargs['params'].items():
          kwargs['params'][paramKey] = type(status[paramKey])(paramVal)
      response = call(*args, **kwargs)
  else:
    response = call

  data['response']['data'] = nest.hl_api.serializable(response)
  return data
