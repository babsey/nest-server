__all__ = [
    'init_data',
    'get_arguments',
]


def init_data(request, call=None):
    """ Create data variable in dictionary for JSON response.
    """
    url = request.url_rule.rule.split('/')[1]
    data = {
        'request': {
            'url': url,
        },
        'response': {}
    }
    if call:
        data['request']['call'] = call
    return data


def get_arguments(request, data):
    """ Get arguments from the request.
    """
    args, kwargs = [], {}
    if request.is_json:
        json = data['request']['json'] = request.get_json()
        if isinstance(json, list):
            args = json
        elif isinstance(json, dict):
            args = json.get('args', args)
            kwargs = json.get('kwargs', json)
    elif len(request.form) > 0:
        if 'args' in request.form:
            args = data['request']['form'] = request.form.getlist('args')
        else:
            kwargs = data['request']['form'] = request.form.to_dict()
    elif (len(request.args) > 0):
        if 'args' in request.args:
            args = data['request']['args'] = request.args.getlist('args')
        else:
            kwargs = data['request']['args'] = request.args.to_dict()
    return args, kwargs
