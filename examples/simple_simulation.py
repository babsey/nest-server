import requests
import json


def nest_api(call, url='http://localhost:5000/api/nest/', *args, **kwargs):
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  req = requests.post(url + call, json.dumps(kwargs), headers=headers)
  data = req.json()
  response = data['response']
  elapsed = req.elapsed.total_seconds()
  unit = 's'
  if elapsed < 1000:
    elapsed *= 1000
    unit = 'ms'
  print('{:11s} ... {} \t{:.1f} {}'.format(call, response['status'], elapsed, unit))
  if (response['status'] == 'error'):
    print(' - {}'.format(response['msg']))
  return response['data']



print(35*'-')
nest_api('ResetKernel')
neurons = nest_api('Create', model="iaf_psc_alpha", n=10)
pg = nest_api('Create', model="poisson_generator", params={"rate": 10.})
vm = nest_api('Create', model="voltmeter")

nest_api('Connect', pre=pg, post=neurons)
nest_api('Connect', pre=vm, post=neurons)

nest_api('Simulate', t=1000.)
events = nest_api('GetStatus', nodes=vm, keys='n_events')[0]

print(35*'-')
print('Number of events:', events)
