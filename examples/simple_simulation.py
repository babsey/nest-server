import requests
import json


def nest_api(call, url='http://localhost:5000/api/nest/', *args, **kwargs):
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  data = requests.post(url + call, json.dumps(kwargs), headers=headers).json()
  response = data['response']
  print('%s ... %s' %(call, response['status']))
  if (response['status'] == 'error'):
    print(' - %s' %response['msg'])
  return response['data']



nest_api('ResetKernel')
neurons = nest_api('Create', model="iaf_psc_alpha", n=10)
pg = nest_api('Create', model="poisson_generator", params={"rate": 10.})
vm = nest_api('Create', model="voltmeter")

nest_api('Connect', pre=pg, post=neurons)
nest_api('Connect', pre=vm, post=neurons)

nest_api('Simulate', t=1000.)
events = nest_api('GetStatus', nodes=vm, keys='n_events')[0]
print('Number of events:', events)
