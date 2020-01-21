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

d = nest_api('Create', {"model": "voltmeter"})
vm = d['response']['data']

e = nest_api('Connect', {"pre": pg, "post": neurons})
f = nest_api('Connect', {"pre": vm, "post": neurons})

g = nest_api('Simulate', {"t": 1000.})
h = nest_api('GetStatus', {"nodes": vm})

print(h['response']['data'][0]['n_events'])
