import importlib_metadata

from .backend import ACEmailBackend as EmailBackend


__version__ = importlib_metadata.version(__name__)
