import numpy as np
import neo as n
import quantities as pq
import elephant.statistics as stats


__all__ = [
    'group_times',
    'spikes',
    'spikes_time_histogram',
]


def group_times(data):
  # print('Group times')
  times = np.array(data['events']['times'])
  senders = np.array(data['events']['senders'])
  times_grp = [times[senders == sender].tolist() for sender in np.unique(senders)]
  return {'data': times_grp}


def spikes(data):
  if data == None:
    return {}
  # print('Calc statistics of spikes')
  statistics = {
      'mean_firing_rate': [],
      'isi': [],
      'cv_isi': [],
  }

  if 'time' in data:
    t_start = float(data['time'].get('start', 0.)) * pq.ms
    t_stop = float(data['time'].get('stop', 1000.)) * pq.ms
  else:
    t_start = 0. * pq.ms
    t_stop = 1. * pq.s

  times_grp = group_times(data)['data']
  for times in times_grp:
    spiketrain = n.SpikeTrain(times * pq.ms, t_start=t_start, t_stop=t_stop)
    mean_firing_rate = stats.mean_firing_rate(spiketrain) * 1000.
    if len(times) > 2:
      isi = stats.isi(spiketrain).data.tolist()
      cv_isi = stats.cv(isi).data.tolist()
    else:
      isi = []
      cv_isi = -1.
    statistics['mean_firing_rate'].append(mean_firing_rate.data.tolist())
    statistics['isi'].append(isi)
    statistics['cv_isi'].append(cv_isi)

  return {'data': statistics}


def spikes_time_histogram(data):

  statistics = {
      'time_histogram': [],
  }

  t_start = data['time'].get('start', 0.) * pq.ms
  t_stop = data['time'].get('stop', 1000.) * pq.ms
  binsize = data['histogram'].get('binsize', 50.) * pq.ms
  output = data['histogram'].get('output', 'counts')

  # times_grp = group_times(data)['data']
  # spiketrains = [n.SpikeTrain(times * pq.ms, t_start=t_start, t_stop=t_stop) for times in times_grp]
  # hist = stats.time_histogram(spiketrains, binsize, output=output)
  times = data['events']['times']
  spiketain = n.SpikeTrain(times * pq.ms, t_start=t_start, t_stop=t_stop)
  hist = stats.time_histogram([spiketrain], binsize, output=output)
  statistics = {
      'times': hist.times.data.tolist(),
      'values': hist.T[0].data.tolist()
  }

  return {'data': statistics}
