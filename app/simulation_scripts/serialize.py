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

def collection(model, params):
    if len(params) == 0:
        return {}
    param_defaults = nest.GetDefaults(model)
    return _paramify(params, param_defaults)

def conn(spec):
    if len(spec) == 0:
        return 'all_to_all'
    return spec

def syn(spec):
    if len(spec) == 0:
        return 'static_synapse'
    spec_defaults = nest.GetDefaults(spec.get('model', 'static_synapse'))
    return _paramify(spec, spec_defaults)

def events(recId, ndigits=0):
    events = {}
    for eventKey, eventVal in nest.GetStatus(recId, 'events')[0].items():
        events[eventKey] = eventVal.tolist()
    return events
