try:
    import importlib_metadata
except ImportError:
    # Python >=3.8,<3.10
    import importlib.metadata as importlib_metadata

from .backend import ACEmailBackend as EmailBackend


__version__ = importlib_metadata.version(__name__)
