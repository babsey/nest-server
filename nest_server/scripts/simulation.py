import datetime
import nest
import nest.topology as tp
import numpy as np

from . import serialize
from . import restriction

__all__ = [
    'run',
]


def get_nodes(node):
  try:
    nodes = nest.GetNodes(node)[0]
  except:
    nodes = node
  return nodes


def log(message):
  # print(message)
  return (str(datetime.datetime.now()), 'server', message)


def is_spatial(node):
  if 'spatial' not in node:
    return
  return len(node['spatial'].keys()) > 0


def get_model(node, models):
  if node['model'] in models:
    return models[node['model']]['existing']
  else:
    return node['model']


def run(data):
  # print(data)
  restriction.checkIfRestricted(data)
  logs = []

  logs.append(log('Get request'))
  simulation = data['simulation']
  simtime = simulation.get('time', 1000.0)
  kernel = simulation['kernel']

  network = data['network']
  models = network.get('models', [])
  nodes = network['nodes']
  connections = network['connections']

  records = []
  nodes_obj = []

  logs.append(log('Reset kernel'))
  nest.ResetKernel()

  logs.append(log('Set seed in numpy random'))
  np.random.seed(int(simulation.get('random_seed', 0)))

  logs.append(log('Set kernel status'))
  local_num_threads = int(kernel.get('local_num_threads', 1))
  rng_seeds = np.random.randint(0, 1000, local_num_threads).tolist()
  resolution = float(kernel.get('resolution', 1.0))
  kernel_dict = {
      'local_num_threads': local_num_threads,
      'resolution': resolution,
      'rng_seeds': rng_seeds,
  }
  nest.SetKernelStatus(kernel_dict)
  data['kernel'] = kernel_dict

  logs.append(log('Collect all recordables for multimeter'))
  for idx, node in enumerate(nodes):
    model = get_model(node, models)
    if model != 'multimeter':
      continue

    if 'record_from' in node['params']:
      continue

    recs = list(filter(lambda conn: conn['source'] == idx, connections))
    if len(recs) == 0:
      continue

    recordable_models = [get_model(nodes[conn['target']], models) for conn in recs]
    recordable_models_set = list(set(recordable_models))
    assert len(recordable_models_set) == 1

    recordables = nest.GetDefaults(recordable_models_set[0], 'recordables')
    node['params']['record_from'] = list(map(str, recordables))

  logs.append(log('Copy models'))
  for model in models:
    params_serialized = serialize.model_params(model['existing'], model['params'])
    nest.CopyModel(model['existing'], model['new'], params_serialized)

  logs.append(log('Create nodes'))
  for idx, node in enumerate(nodes):
    # nodes[idx]['idx'] = idx
    params_serialized = serialize.model_params(node['model'], node['params'])
    if is_spatial(node):
      specs = node['spatial']
      specs['elements'] = node['model']
      obj = tp.CreateLayer(serialize.layer(specs))
      nest.SetStatus(nest.GetNodes(obj)[0], params_serialized)
      if 'positions' in specs:
        positions = specs['positions']
      else:
        positions = tp.GetPosition(get_nodes(obj))
        specs['positions'] = positions
      positions = np.round(positions, decimals=2).astype(float)
    else:
      n = int(node.get('n', 1))
      obj = nest.Create(node['model'], n, params_serialized)
      element_type = nest.GetStatus(obj, 'element_type')[0]
      if str(element_type) == 'recorder':
        model = nest.GetDefaults(str(nest.GetStatus(obj, 'model')[0]), 'type_id')
        record = {
            'recorder': {
                'idx': idx,
                'model': model,
            }
        }
        records.append(nest.hl_api.serializable(record))
    nodes_obj.append(obj)

  logs.append(log('Connect nodes'))
  for connection in connections:
    source = nodes[connection['source']]
    target = nodes[connection['target']]
    source_obj = nodes_obj[connection['source']]
    target_obj = nodes_obj[connection['target']]
    if is_spatial(source) and is_spatial(target):
      projections = connection['projections']
      tp.ConnectLayers(source_obj, target_obj, serialize.projections(projections))
    else:
      conn_spec = connection.get('conn_spec', 'all_to_all')
      syn_spec = connection.get('syn_spec', 'static_synapse')

      # NEST 2.18
      source_nodes = get_nodes(source_obj)
      target_nodes = get_nodes(target_obj)

      if (len(connection.get('tgt_idx', [])) > 0 and len(connection.get('src_idx', [])) > 0):
        tgt_idx = connection['tgt_idx']
        if len(tgt_idx) > 0:
          if isinstance(tgt_idx[0], int):
            source = source_nodes
            target = np.array(target_nodes)[tgt_idx].tolist()
            nest.Connect(source_nodes, target, serialize.conn(conn_spec), serialize.syn(syn_spec))
          else:
            for idx in range(len(tgt_idx)):
              target = np.array(target_nodes)[tgt_idx[idx]].tolist()
              src_idx = connection['src_idx']
              if len(src_idx) > 0:
                source = np.array(source_nodes)[src_idx[idx]].tolist()
              else:
                source = [source_nodes[idx]]
              nest.Connect(source, target, serialize.conn(conn_spec), serialize.syn(syn_spec))
      else:
        nest.Connect(source_nodes, target_nodes, serialize.conn(conn_spec), serialize.syn(syn_spec))
      # NEST 3
      # nest.Connect(source_obj, target_obj, serialize.conn(conn_spec), serialize.syn(syn_spec))

  logs.append(log('Start simulation'))
  nest.Simulate(float(simtime))
  logs.append(log('End simulation'))

  logs.append(log('Serialize recording data'))
  ndigits = int(-1 * np.log10(resolution))

  activities = []
  for idx, record in enumerate(records):
    if record['recorder']['model'] == 'spike_detector':
      neuron, rec = 'source', 'target'
    else:
      rec, neuron = 'source', 'target'
    nodeIds = []
    nodePositions = []
    for connection in connections:
      if connection[rec] == record['recorder']['idx']:
        node = nodes[connection[neuron]]
        nodeIds.extend(list(get_nodes(nodes_obj[connection[neuron]])))
        if is_spatial(node):
          nodePositions.extend(node['spatial']['positions'])

    recorder_obj = nodes_obj[record['recorder']['idx']]

    activity = {
      'events': nest.GetStatus(recorder_obj, 'events')[0],
      'nodeIds': nodeIds,
      'nodePositions': nodePositions,
    }
    activities.append(activity)

  response = {
      'kernel': {
          'time': nest.GetKernelStatus('time')
      },
      'activities': nest.hl_api.serializable(activities)
  }
  return {'data': response, 'logs': logs}
