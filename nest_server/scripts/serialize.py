import nest
import nest.topology as tp
import numpy as np

__all__ = [
    'model_params',
    'parameter',
    'conn',
    'syn',
    'events',
    'layer',
    'projections',
]


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


def model_params(model, params):
  if len(params) == 0:
    return {}
  param_defaults = nest.GetDefaults(model)
  return _paramify(params, param_defaults)


def parameter(specs):
  if isinstance(specs, dict):
    specs['specs'] = dict([(key, float(val)) for (key, val) in specs['specs'].items()])
    return tp.CreateParameter(**specs)
  else:
    return float(specs)


def conn(specs):
  if isinstance(specs, str):
    return specs
  if len(specs) == 0:
    return 'all_to_all'
  return specs


def syn(specs):
  if isinstance(specs, str):
    return specs
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
  newSpecs['center'] = np.round(specs['center'], decimals=2).astype(float).tolist()
  newSpecs['extent'] = np.round(specs['extent'], decimals=2).astype(float).tolist()
  if 'positions' in specs:
    positions = np.round(specs['positions'], decimals=2).astype(float).tolist()
    newSpecs['positions'] = positions
  else:
    newSpecs['rows'] = specs['rows']
    newSpecs['columns'] = specs['columns']
  return newSpecs


def mask(masktype, specs):
  if 'rectangular' in masktype:
    newSpecs = {
        'lower_left': np.array(specs['lower_left'], dtype=float).tolist(),
        'upper_right': np.array(specs['upper_right'], dtype=float).tolist(),
        'azimuth_angle': float(specs['azimuth_angle']),
    }
  elif 'circular' in masktype:
    newSpecs = {
        'radius': float(specs['radius'])
    }
  elif 'doughnut' in masktype:
    newSpecs = {
        'inner_radius': float(specs['inner_radius']),
        'outer_radius': float(specs['outer_radius']),
    }
  elif 'elliptical' in masktype:
    newSpecs = {
        'major_axis': float(specs['major_axis']),
        'minor_axis': float(specs['minor_axis']),
        'azimuth_angle': float(specs['azimuth_angle']),
        # 'anchor': np.array(specs['anchor']).tolist(),
    }
  else:
    newSpecs = {}
  return tp.CreateMask(masktype=masktype, specs=newSpecs)


def projections(specs):
  newSpecs = {}
  newSpecs['connection_type'] = specs.get('connection_type', 'divergent')
  if 'kernel' in specs:
    newSpecs['kernel'] = parameter(specs['kernel'])
  if 'number_of_connections' in specs:
    newSpecs['number_of_connections'] = int(specs['number_of_connections'])
  if 'mask' in specs:
    newSpecs['mask'] = mask(specs['mask']['masktype'], specs['mask']['specs'])
  newSpecs['allow_autapses'] = bool(specs.get('allow_autapses', True))
  newSpecs['allow_multapses'] = bool(specs.get('allow_multapses', True))
  newSpecs['weights'] = parameter(specs.get('weights', 1.))
  newSpecs['delays'] = parameter(specs.get('delay', 1.))
  return newSpecs
