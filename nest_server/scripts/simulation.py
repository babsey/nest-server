import datetime
import nest
import nest.topology as tp
import numpy as np

from . import serialize
from . import restriction

__all__ = [
    'run',
]


def getNodes(collection, meta):
  if isSpatial(meta):
    nodes = nest.GetNodes(collection)[0]
  else:
    nodes = collection
  return nodes


def log(message):
  # print(message)
  return (str(datetime.datetime.now()), 'server', message)


def isSpatial(node):
    return len(node['spatial'].keys()) > 0


def run(data):
  # print(data)
  restriction.checkIfRestricted(data)
  logs = []

  logs.append(log('Get request'))
  simtime = data.get('time', 1000.0)
  kernel = data.get('kernel', {})
  models = data['models']
  collections = data['collections']
  connectomes = data['connectomes']
  records = []
  collections_obj = []

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
  for idx, collection in enumerate(collections):
    model = models[collection['model']]
    if model['existing'] != 'multimeter':
      continue

    if 'record_from' in collection['params']:
      continue

    recs = list(filter(lambda conn: conn['source'] == idx, connectomes))
    if len(recs) == 0:
      continue

    recordable_models = []
    for conn in recs:
      recordable_model = models[collections[conn['target']]['model']]
      recordable_models.append(recordable_model['existing'])
    recordable_models_set = list(set(recordable_models))
    assert len(recordable_models_set) == 1

    recordables = nest.GetDefaults(recordable_models_set[0], 'recordables')
    collection['params']['record_from'] = list(map(str, recordables))

  logs.append(log('Copy models'))
  for new, model in models.items():
    params_serialized = serialize.model_params(model['existing'], model['params'])
    nest.CopyModel(model['existing'], new, params_serialized)

  logs.append(log('Create collections'))
  for idx, collection in enumerate(collections):
    collections[idx]['idx'] = idx
    if isSpatial(collection):
      specs = collection['spatial']
      specs['elements'] = collection['model']
      obj = tp.CreateLayer(serialize.layer(specs))
      if 'positions' in specs:
        positions = specs['positions']
      else:
        positions = tp.GetPosition(nest.GetNodes(obj)[0])
      positions = np.round(positions, decimals=2).astype(float)
      collections[idx]['spatial']['positions'] = positions.tolist()
      collections[idx]['n'] = positions.shape[0]
      collections[idx]['ndim'] = positions.ndim
      collections[idx]['global_ids'] = nest.GetNodes(obj)[0]
    else:
      n = int(collection.get('n', 1))
      obj = nest.Create(collection['model'], n, collection.get('params', {}))
      collections[idx]['global_ids'] = list(obj)
      element_type = nest.GetStatus(obj, 'element_type')[0]
      if str(element_type) == 'recorder':
        model = nest.GetDefaults(str(nest.GetStatus(obj, 'model')[0]), 'type_id')
        record = {
            'recorder': {
                'idx': idx,
                'global_id': nest.GetStatus(obj, 'global_id')[0],
                'model': model,
            }
        }
        records.append(nest.hl_api.serializable(record))
    collections_obj.append(obj)

  logs.append(log('Connect collections'))
  for connectome in connectomes:
    source = collections[connectome['source']]
    target = collections[connectome['target']]
    source_obj = collections_obj[connectome['source']]
    target_obj = collections_obj[connectome['target']]
    if isSpatial(source) and isSpatial(target):
      projections = connectome['projections']
      tp.ConnectLayers(source_obj, target_obj, serialize.projections(projections))
    else:
      conn_spec = connectome.get('conn_spec', 'all_to_all')
      syn_spec = connectome.get('syn_spec', 'static_synapse')
      # NEST 2.18
      source_nodes = getNodes(source_obj, source)
      target_nodes = getNodes(target_obj, target)
      if (len(connectome.get('tgt_idx', [])) > 0 and len(connectome.get('src_idx', [])) > 0):
        tgt_idx = connectome['tgt_idx']
        if len(tgt_idx) > 0:
          if isinstance(tgt_idx[0], int):
            source = source_nodes
            target = np.array(target_nodes)[tgt_idx].tolist()
            nest.Connect(source_nodes, target, serialize.conn(conn_spec), serialize.syn(syn_spec))
          else:
            for idx in range(len(tgt_idx)):
              target = np.array(target_nodes)[tgt_idx[idx]].tolist()
              src_idx = connectome['src_idx']
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
  data['kernel']['time'] = nest.GetKernelStatus('time')

  logs.append(log('Serialize recording data'))
  ndigits = int(-1 * np.log10(resolution))
  for idx, record in enumerate(records):
    records[idx]['idx'] = idx
    if record['recorder']['model'] == 'spike_detector':
      neuron, rec = 'source', 'target'
    else:
      rec, neuron = 'source', 'target'
    global_ids = []
    positions = []
    for connectome in connectomes:
      if connectome[rec] == record['recorder']['idx']:
        collection = collections[connectome[neuron]]
        global_ids.extend(collection['global_ids'])
        if isSpatial(collection):
          positions.extend(collection['spatial']['positions'])
    recorder_obj = collections_obj[record['recorder']['idx']]
    records[idx]['events'] = nest.GetStatus(recorder_obj, 'events')
    records[idx]['global_ids'] = global_ids
    records[idx]['positions'] = positions
  data['records'] = nest.hl_api.serializable(records)
  return {'data': data, 'logs': logs}
