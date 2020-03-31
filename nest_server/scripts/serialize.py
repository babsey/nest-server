import nest
import numpy as np

__all__ = [
    'model',
    'node',
    'connection',
    'events',
]


# -----
# Model
# -----


def _model_paramify(params, defaults):
  _params = {}
  for pkey, pval in params.items():
    if pkey == 'model':
      _params[pkey] = pval
    elif isinstance(pval, dict):
      _params[pkey] = _model_paramify(pval, defaults[pkey])
    elif pkey in defaults:
      if isinstance(defaults[pkey], np.ndarray):
        _params[pkey] = np.array(pval, dtype = defaults[pkey].dtype)
      else:
        ptype = type(defaults[pkey])
        _params[pkey] = ptype(pval)
  return _params


def _model_params(spec):
  if 'params' not in spec:
    return None
  if len(spec['params']) == 0:
    return None
  model_defaults = nest.GetDefaults(spec['existing'])
  return _model_paramify(spec['params'], model_defaults)


def model(spec):
  return spec['existing'], spec['new'], _model_params(spec)


# ----
# Node
# ----


def _n(spec):
  if ('positions' not in spec):
    return int(spec.get('n', 1))
  if (spec['positions'] != None):
    return int(spec.get('n', 1))
  if 'spatial' in spec['positions']:
    if 'free' in spec['positions']['spatial']:
      return int(spec.get('n', 1))
  return 1


def _parse_float(spec):
  return dict([(key, float(val)) for (key, val) in spec.items()])


def _create_parameter(param):
  if isinstance(param, dict):
    param['specs'] = _parse_float(param['specs'])
    return nest.CreateParameter(**param)
  else:
    return float(param)


def _node_params(spec):
  if 'params' not in spec:
    return None
  if len(spec['params']) == 0:
    return None
  params = dict([(key, _create_parameter(val)) for (key, val) in spec['params'].items()])
  return params


def _positions(spec):
  if 'positions' in spec:
    positions = spec['positions']
    if isinstance(positions, list):
      pos = np.array(positions, dtype=float).tolist()
      return nest.spatial.free(pos)
    elif isinstance(positions, dict):
      if positions['spatial'] == 'free':
        pos = positions['pos']
        if isinstance(pos, list):
          pos = np.array(pos, dtype=float).tolist()
        elif isinstance(pos, dict):
          random_spec = pos['random_spec']
          pos = nest.random.__dict__[pos['random']](**random_spec)
        spatial_spec = {
            'pos': pos,
            'extent': positions.get('extent', None),
            'edge_wrap': positions.get('edge_wrap', False),
            'num_dimension': positions.get('num_dimension', None),
        }
      elif positions['spatial'] == 'grid':
        spatial_spec = {
            'shape': positions['shape'],
            'center': positions.get('center', None),
            'extent': positions.get('extent', None),
            'edge_wrap': positions.get('edge_wrap', False),
        }
      return nest.spatial.__dict__[positions['spatial']](**spatial_spec)
  return None


def node(spec):
  return spec['model'], _n(spec), _node_params(spec), _positions(spec)


# ----------
# Connection
# ----------


def _conn_spec(spec):
  conn_spec = spec.get('conn_spec', 'all_to_all')
  if isinstance(conn_spec, str):
    return conn_spec
  if 'mask' in conn_spec:
    mask = {}
    mask[conn_spec['mask']['masktype']] = _parse_float(conn_spec['mask']['specs'])
    conn_spec['mask'] = mask
  # conn_spec['allow_autapses'] = bool(conn_spec.get('allow_autapses', True))
  # conn_spec['allow_multapses'] = bool(conn_spec.get('allow_multapses', True))
  return conn_spec


def _syn_spec(spec):
  syn_spec = spec.get('syn_spec', 'static_synapse')
  if isinstance(syn_spec, str):
    return syn_spec
  synapse_model = syn_spec.get('synapse_model', 'static_synapse')
  model_defaults = nest.GetDefaults(synapse_model)
  return _model_paramify(syn_spec, model_defaults)


def connection(spec):
  return _conn_spec(spec), _syn_spec(spec)


# --------
# Recorder
# --------


def events(rec_obj):
  events = {}
  for eventKey, eventVal in rec_obj.get('events').items():
    events[eventKey] = eventVal.tolist()
  return events
