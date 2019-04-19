#!/usr/bin/env python

import numpy as np
import nest


def _paramify(params, param_defaults):
    _params = {}
    for pkey, pval in params.items():
        if pkey == 'model':
            _params[pkey] = pval
        elif isinstance(pval, dict):
            _params[pkey] = _paramify(pval, param_defaults[pkey])
        elif pkey in param_defaults:
            ptype = type(param_defaults[pkey])
            if ptype == np.ndarray:
                _params[pkey] = np.array(
                    pval, dtype=param_defaults[pkey].dtype)
            else:
                _params[pkey] = ptype(pval)
    return _params


def parameter(model, params):
    if len(params) == 0:
        return {}
    param_defaults = nest.GetDefaults(model)
    return _paramify(params, param_defaults)


def conn(specs):
    if len(specs) == 0:
        return 'all_to_all'
    return specs


def syn(specs):
    if len(specs) == 0:
        return 'static_synapse'
    spec_defaults = nest.GetDefaults(specs.get('model', 'static_synapse'))
    return _paramify(specs, spec_defaults)


def events(recId, ndigits=0):
    events = {}
    for eventKey, eventVal in nest.GetStatus(recId, 'events')[0].items():
        events[eventKey] = eventVal.tolist()
    return events


def layer(specs):
    newSpecs = {'elements': specs['elements']}
    newSpecs['center'] = np.round(specs['center'], decimals=3).astype(float).tolist()
    newSpecs['extent'] = np.round(specs['extent'], decimals=3).astype(float).tolist()
    if len(specs['positions']) > 0:
        positions = np.round(specs['positions'], decimals=3).astype(float).tolist()
        newSpecs['positions'] = positions
    else:
        newSpecs['rows'] = specs['rows']
        newSpecs['columns'] = specs['columns']
    return newSpecs

def projections(specs):
    newSpecs = {}
    newSpecs['connection_type'] = specs.get('connection_type', 'divergent')
    if 'kernel' in specs:
        newSpecs['kernel'] = float(specs['kernel'])
    if 'number_of_connections' in specs:
        newSpecs['number_of_connections'] = int(specs['number_of_connections'])
        newSpecs['allow_autapses'] = bool(specs.get('allow_autapses', True))
        newSpecs['allow_multapses'] = bool(specs.get('allow_multapses', True))
    newSpecs['weights'] = float(specs.get('weights', 1.))
    newSpecs['delays'] = float(specs.get('delays', 1.))
    return newSpecs
