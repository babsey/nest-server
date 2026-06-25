from importlib import metadata

from nest_server.main import *

try:
    __version__ = metadata.version("nest-server")
except metadata.PackageNotFoundError:
    pass

del metadata
