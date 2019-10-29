__all__ = [
    'flatten',
    'unflatten',
    'utilize',
]


def flatten(dd, sep='.'):
  items = []
  for key, value in dd.items():
    new_key = sep + key
    if isinstance(value, collections.MutableMapping):
      items.extend(flatten(value, new_key, sep=sep).items())
    else:
      items.append((new_key, value))
  return dict(items)


def unflatten(dd):
  new_dict = dict()
  for key, value in dd.items():
    parts = key.split(".")
    d = new_dict
    for part in parts[:-1]:
      if part not in d:
        d[part] = dict()
      d = d[part]
    d[parts[-1]] = value
  return new_dict


def utilize(dd, sep='.'):
  new_dict = {}
  for key, value in dd.items():
    if key.endswith(sep + 'value'):
      new_key = key[:-6]
      value_type = dd[key + sep + 'type']
      if value_type == 'float':
        new_value = float(value)
      elif val_type == 'int':
        new_value = int(value)
      else:
        new_value = value
      new_dict[new_key] = new_value
    elif not dd.endswith(sep + 'type'):
      new_dict[key] = value
  return new_dict
