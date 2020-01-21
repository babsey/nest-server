import datetime
import numpy as np
import nest

from . import serialize

__all__ = [
    'run',
]


def getPositions(node):
  if 'spatial' in node:
    spatial = node['spatial']
    if ('positions' in spatial):
      specs = {
          'positions': spatial['positions'],
          'extent': spatial.get('extent', None),
          'edge_wrap': spatial.get('edge_wrap', False),
          'num_dimension': spatial.get('num_dimension', None),
      }
      return nest.spatial.free(**specs)
    else:
      specs = {
          'shape': spatial['shape'],
          'center': spatial.get('center', None),
          'extent': spatial.get('extent', None),
          'edge_wrap': spatial.get('edge_wrap', False)
      }
      return nest.spatial.grid(**specs)
  return None


def log(message):
  # print(message)
  return (str(datetime.datetime.now()), 'server', message)


def run(data):
  # print(data)
  logs = []

  logs.append(log('Get request'))
  simtime = data.get('time', 1000.0)
  kernel = data.get('kernel', {})
  models = data['models']
  nodes = data['collections']
  connections = data['connectomes']
  records = []
  nodes_obj = []

  logs.append(log('Reset kernel'))
  nest.ResetKernel()

  logs.append(log('Set seed in numpy random'))
  np.random.seed(int(data.get('random_seed', 0)))

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
    model = models[node['model']]
    if model['existing'] != 'multimeter':
      continue

    if 'record_from' in model['params']:
      continue

    recs = list(filter(lambda conn: conn['source'] == idx, connections))
    if len(recs) == 0:
      continue

    recordable_models = []
    for conn in recs:
      recordable_model = models[nodes[conn['target']]['model']]
      recordable_models.append(recordable_model['existing'])
    recordable_models_set = list(set(recordable_models))
    assert len(recordable_models_set) == 1

    recordables = nest.GetDefaults(recordable_models_set[0], 'recordables')
    model['params']['record_from'] = list(map(str, recordables))

  logs.append(log('Copy models'))
  for new, model in models.items():
    params_serialized = serialize.model_params(model['existing'], model['params'])
    nest.CopyModel(model['existing'], new, params_serialized)

  logs.append(log('Create nodes'))
  for idx, node in enumerate(nodes):
    nodes[idx]['idx'] = idx
    n = int(node.get('n', 1))
    positions = getPositions(node)
    node_obj = nest.Create(node['model'], n, positions=positions)
    nodes[idx]['global_ids'] = node_obj.tolist()
    if positions:
      positions = nest.GetPosition(obj)
      positions = np.round(positions, decimals=2).astype(float)
      nodes[idx]['spatial']['positions'] = positions.tolist()
      nodes[idx]['n'] = positions.shape[0]
      nodes[idx]['ndim'] = positions.ndim
    if node['element_type'] == 'recorder':
      model = models[node['model']]
      record = {
          'recorder': {
              'global_ids': list(obj),
              'idx': idx,
              'model': model['existing']
          }
      }
      if 'record_from' in model['params']:
        record['record_from'] = model['params']['record_from']
      records.append(record)
    nodes_obj.append(obj)

  logs.append(log('Connect nodes'))
  for connection in connections:
    source_obj = nodes_obj[connection['source']]
    target_obj = nodes_obj[connection['target']]
    conn_spec = serialize.conn(connection.get('conn_spec', 'all_to_all'))
    syn_spec = serialize.syn(connection.get('syn_spec', 'static_synapse'))
    if 'tgt_idx' in connection:
      tgt_idx = connection['tgt_idx']
      if len(tgt_idx) > 0:
        if isinstance(tgt_idx[0], int):
          nest.Connect(source_obj, target_obj[tgt_idx], conn_spec, syn_spec)
        else:
          for idx in range(len(tgt_idx)):
            if 'src_idx' in connection:
              source = source_obj[connection['src_idx'][idx]]
            else:
              source = [source_obj[idx]]
            target = target_obj[tgt_idx[idx]]
            nest.Connect(source, target, conn_spec, syn_spec)
    else:
      nest.Connect(source_obj, target_obj, conn_spec, syn_spec)

  logs.append(log('Start simulation'))
  nest.Simulate(float(simtime))

  logs.append(log('End simulation'))
  data['kernel']['time'] = nest.GetKernelStatus('time')

  logs.append(log('Serialize recording data'))
  ndigits = int(-1 * np.log10(resolution))
  for idx, record in enumerate(records):
    records[idx]['idx'] = idx
    if record['recorder']['model'] == 'spike_detector':
      neuron, recorder = 'source', 'target'
    else:
      recorder, neuron = 'source', 'target'
    global_ids = []
    for connection in connections:
      if connection[recorder] == record['recorder']['idx']:
        node = nodes[connection[neuron]]
        global_ids.extend(node['global_ids'])
      records[idx]['global_ids'] = global_ids
      recorder_obj = nodes_obj[record['recorder']['idx']]
      events = serialize.events(recorder_obj, ndigits)
      records[idx]['events'] = events
      records[idx]['senders'] = list(set(events['senders']))
  data['records'] = records

  return {'data': data, 'logs': logs}
