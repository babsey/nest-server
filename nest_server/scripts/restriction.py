import importlib
import os
import numpy as np


__all__ = [
    'checkIfRestricted',
]


def checkIfRestricted(data):
  importlib.reload(os)
  if (os.environ.get('NEST_DESKTOP_RESTRICTION', 0)):
    kernel = data.get('kernel', {})
    resolution = kernel.get('resolution', 1.)
    assert resolution >= 0.1, 'The resolution time is too small (min: 0.1 ms, current: {} ms.'.format(resolution)
    nodes = data['collections']
    nodesTotal = np.sum([n.get('n', 1) for n in nodes])
    assert nodesTotal <= 200, 'The network size is too big (max: 200, current: {}).'.format(nodesTotal)
    simtime = data.get('time', 1000.0)
    assert simtime <= 5000., 'The simulation time is too big (max: 5000 ms, current: {} ms).'.format(simtime)
