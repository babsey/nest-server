import nest


__all__ = [
    'serialize',
]


def NodeCollection(kwargs):
    """ Get Node Collection as arguments for NEST functions.
    """
    keys = ['nodes', 'source', 'target', 'pre', 'post']
    for key in keys:
        if key in kwargs:
            kwargs[key] = nest.NodeCollection(kwargs[key])
    return kwargs


def serialize(call, kwargs):
    """ Serialize arguments with keywords for call functions in NEST.
    """
    kwargs = NodeCollection(kwargs)
    if call.startswith('Set'):
        status = {}
        if call == 'SetDefaults':
            status = nest.GetDefaults(kwargs['model'])
        elif call == 'SetKernelStatus':
            status = nest.GetKernelStatus()
        elif call == 'SetStructuralPlasticityStatus':
            status = nest.GetStructuralPlasticityStatus(kwargs['params'])
        elif call == 'SetStatus':
            status = nest.GetStatus(kwargs['nodes'])
        for key, val in kwargs['params'].items():
            if key in status:
                kwargs['params'][key] = type(status[key])(val)
    return kwargs
