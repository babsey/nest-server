from importlib import metadata

try:
    __version__ = metadata.version("nest-server")
except metadata.PackageNotFoundError:
    pass

del metadata
