import nest

from werkzeug.exceptions import abort
from werkzeug.wrappers import Response


__all__ = [
    'get_or_error',
]


def get_or_error(func):

  def func_wrapper(request, call, data, *args, **kwargs):
    try:
      return func(request, call, data, *args, **kwargs)
    except nest.kernel.NESTError as e:
      abort(Response(getattr(e, 'errormessage'), 400))
    except Exception as e:
      abort(Response(str(e), 400))
  return func_wrapper
