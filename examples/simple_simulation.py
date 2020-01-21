import requests
import json


def nest_api(call, params={}):
  return requests.post(url + call, json.dumps(params), headers=headers).json()


url = 'http://localhost:5000/api/nest/'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

a = nest_api('ResetKernel')
b = nest_api('Create', {"model": "iaf_psc_alpha", "n": 10})
neurons = b['response']['data']

c = nest_api('Create', {"model": "poisson_generator", "params": {"rate": 10.}})
pg = c['response']['data']

e = nest_api('Create', {"model": "voltmeter"})
vm = e['response']['data']

f = nest_api('Connect', {"pre": pg, "post": neurons})
g = nest_api('Connect', {"pre": vm, "post": neurons})

h = nest_api('Simulate', {"t": 1000.})
i = nest_api('GetStatus', {"nodes": vm})

print(i['response']['data'][0]['n_events'])
