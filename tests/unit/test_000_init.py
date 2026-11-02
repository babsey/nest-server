import importlib
from importlib import metadata

import nest_server


def test_version_matches_metadata():
    assert nest_server.__version__ == metadata.version("nest-server")


def test_metadata_not_exported():
    assert not hasattr(nest_server, "metadata")


def test_version_fallback(monkeypatch):
    def fake_version(name):
        raise metadata.PackageNotFoundError(name)

    monkeypatch.setattr(metadata, "version", fake_version)
    try:
        importlib.reload(nest_server)
        assert nest_server.__version__ == "unknown"
    finally:
        monkeypatch.undo()
        importlib.reload(nest_server)
