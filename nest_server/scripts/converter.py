import json

blocks = [
    'state',
    'initial_values',
    'equations',
    'parameters',
    'internals',
    'input',
    'update'
]


def load_json_file(filename):
  with open(filename, 'r') as f:
    lines = f.readlines()
  data_json = ''.join(lines)
  data = json.loads(data_json)
  return data


def write_block(header, content):
  return header + ':\n' + content + '\nend\n'


def json_to_nestml_format(data):
  s = ''
  if 'doc' in data:
    s += '/*\n' + data['doc'] + '\n*/\n'
  s += 'neuron %s:\n' % data['neuron']
  for block in blocks:
    if block in data:
      s += write_block(block, data[block])
  s += 'output: %s\n' % data['output']
  s += 'end\n'
  return s


def write_file(model, text):
  with open(model + '.nestml', 'w') as f:
    f.write(text)


if __name__ == '__main__':
  model = 'iaf_psc_alpha_generated'
  data = load_json_file(model + '.json')
  data_nestml_format = json_to_nestml_format(data)
  write_file(model, data_nestml_format)
