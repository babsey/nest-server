#!/usr/bin/env python

import numpy as np
import nest
import nest.topology as tp
import datetime

from . import serialize


def _nodes(collection):
    if 'topology' in collection:
        nodes = nest.GetNodes(collection['obj'])[0]
    else:
        nodes = collection['obj']
    return nodes


def log(data, message):
    data['logs'].append((str(datetime.datetime.now()), 'server', message))


def simulate(request):
    data = request.get_json()
    data['logs'] = []
    print('Simulate %s (%s)' % (data.get('name', None), data['_id']))
    # print(data)

    log(data, 'Get request')
    simulation = data.get('simulation', {'time': 1000.0})
    kernel = data.get('kernel', {'time': 0.0})
    models = data['models']
    collections = data['collections']
    connectomes = data.get('connectomes', [])
    records = []

    log(data, 'Reset kernel')
    nest.ResetKernel()

    log(data, 'Set kernel status')
    np.random.seed(int(simulation.get('random_seed', 0)))
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

    log(data, 'Collect all recordables for multimeter')
    for idx, collection in enumerate(collections):
        model = models[collection['model']]
        if collection['element_type'] != 'recorder' or model['existing'] != 'multimeter':
            continue

        print(model['params'])
        if 'record_from' in model['params']:
            continue

        recs = list(filter(lambda conn: conn['pre'] == idx, connectomes))
        if len(recs) == 0:
            continue

        recordable_models = []
        for conn in recs:
            recordable_model = models[collections[conn['post']]['model']]
            recordable_models.append(recordable_model['existing'])
        recordable_models_set = list(set(recordable_models))
        assert len(recordable_models_set) == 1

        recordables = nest.GetDefaults(recordable_models_set[0], 'recordables')
        model['params']['record_from'] = list(map(str, recordables))

    log(data, 'Copy models')
    for new, model in models.items():
        params_serialized = serialize.parameter(
            model['existing'], model['params'])
        nest.CopyModel(model['existing'], new, params_serialized)

    log(data, 'Create collections')
    for idx, collection in enumerate(collections):
        assert idx == collection['idx']
        if 'topology' in collection:
            specs = collection['topology']
            specs['elements'] = collection['model']
            obj = tp.CreateLayer(serialize.layer(specs))
            if len(specs['positions']) > 0:
                positions = specs['positions']
            else:
                positions = tp.GetPosition(nest.GetNodes(obj)[0])
                positions = np.round(positions, decimals=3).astype(float).tolist()
                collections[idx]['topology']['positions'] = positions
            collections[idx]['n'] = len(positions)
            collections[idx]['ndim'] = len(positions[0])
            collections[idx]['global_ids'] = nest.GetNodes(obj)[0]
            collections[idx]['obj'] = obj
        else:
            n = int(collection.get('n', 1))
            obj = nest.Create(collection['model'], n)
            if collection['element_type'] == 'recorder':
                model = models[collection['model']]
                record = {
                    'recorder': {'idx': idx, 'model': model['existing']}
                }
                if 'record_from' in model['params']:
                    record['record_from'] = model['params']['record_from']
                records.append(record)
            collections[idx]['global_ids'] = list(obj)
            collections[idx]['obj'] = obj


    log(data, 'Connect collections')
    for connectome in connectomes:
        pre = collections[connectome['pre']]
        post = collections[connectome['post']]
        if ('topology' in pre) and ('topology' in post):
            projections = connectome['projections']
            tp.ConnectLayers(pre['obj'], post['obj'], serialize.projections(projections))
        else:
            conn_spec = connectome.get('conn_spec', 'all_to_all')
            syn_spec = connectome.get('syn_spec', 'static_synapse')
            nest.Connect(_nodes(pre), _nodes(post), serialize.conn(conn_spec), serialize.syn(syn_spec))

    log(data, 'Start simulation')
    nest.Simulate(float(simulation['time']))
    log(data, 'End simulation')
    data['kernel']['time'] = nest.GetKernelStatus('time')

    log(data, 'Serialize recording data')
    ndigits = int(-1 * np.log10(resolution))
    for idx, record in enumerate(records):
        recorderObj = collections[record['recorder']['idx']]['obj']
        events = serialize.events(recorderObj, ndigits)
        records[idx]['idx'] = idx
        records[idx]['events'] = events
    data['records'] = records

    log(data, 'Reset kernel')
    nest.ResetKernel()

    log(data, 'Delete objects')
    for collection in collections:
        del collection['obj']

    return data
