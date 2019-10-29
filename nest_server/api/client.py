import inspect
import nest

from .decorator import get_or_error

__all__ = [
    'api_client',
]


@get_or_error
def api_client(request, call, data, *args, **kwargs):

    if callable(call):
        data['request']['call'] = call.__name__

        if str(kwargs.get('return_doc', 'false')) == 'true':
            response = call.__doc__
        if str(kwargs.get('return_source', 'false')) == 'true':
            response = inspect.getsource(call)
        else:
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

    data['response']['data'] = response

    return data
